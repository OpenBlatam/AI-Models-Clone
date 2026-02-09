from __future__ import annotations

import torch
from torch import nn


class ImageClassifier(nn.Module):
    def __init__(self, input_channels: int = 3, num_classes: int = 10) -> None:
        super().__init__()
        self.feature_extractor = nn.Sequential(
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.GELU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.GELU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )
        self.classification_head = nn.Linear(64, num_classes)

    def forward(self, input_images: torch.Tensor) -> torch.Tensor:
        extracted_features = self.feature_extractor(input_images)
        class_logits = self.classification_head(extracted_features)
        return class_logits


def compute_accuracy(predicted_class_logits: torch.Tensor, reference_labels: torch.Tensor) -> float:
    predicted_class_indices = predicted_class_logits.argmax(dim=-1)
    num_correct_predictions = (predicted_class_indices == reference_labels).sum().item()
    num_total_predictions = reference_labels.numel()
    return num_correct_predictions / max(num_total_predictions, 1)


def train_step_with_amp(
    neural_network: nn.Module,
    input_batch_images: torch.Tensor,
    input_batch_labels: torch.Tensor,
    parameter_optimizer: torch.optim.Optimizer,
    loss_function: nn.Module,
    gradient_scaler: torch.cuda.amp.GradScaler,
    max_gradient_norm: float = 1.0,
) -> tuple[float, float]:
    parameter_optimizer.zero_grad(set_to_none=True)

    with torch.cuda.amp.autocast(enabled=torch.cuda.is_available(), dtype=(torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16)):
        predicted_class_logits = neural_network(input_batch_images)
        loss_value = loss_function(predicted_class_logits, input_batch_labels)

    gradient_scaler.scale(loss_value).backward()
    gradient_scaler.unscale_(parameter_optimizer)
    nn.utils.clip_grad_norm_(neural_network.parameters(), max_gradient_norm)
    gradient_scaler.step(parameter_optimizer)
    gradient_scaler.update()

    batch_accuracy = compute_accuracy(predicted_class_logits.detach(), input_batch_labels)
    return float(loss_value.item()), float(batch_accuracy)


if __name__ == "__main__":
    torch.manual_seed(7)
    execution_device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")

    model_config_num_classes = 10
    image_classifier = ImageClassifier(num_classes=model_config_num_classes).to(execution_device)
    parameter_optimizer = torch.optim.AdamW(image_classifier.parameters(), lr=3e-4, weight_decay=0.01)
    loss_function = nn.CrossEntropyLoss()
    gradient_scaler = torch.cuda.amp.GradScaler(enabled=torch.cuda.is_available())

    synthetic_images = torch.randn(512, 3, 64, 64, device=execution_device)
    synthetic_labels = torch.randint(0, model_config_num_classes, (512,), device=execution_device)

    loss_value, batch_accuracy = train_step_with_amp(
        neural_network=image_classifier,
        input_batch_images=synthetic_images,
        input_batch_labels=synthetic_labels,
        parameter_optimizer=parameter_optimizer,
        loss_function=loss_function,
        gradient_scaler=gradient_scaler,
        max_gradient_norm=1.0,
    )

    print({"loss": round(loss_value, 4), "accuracy": round(batch_accuracy, 4)})



