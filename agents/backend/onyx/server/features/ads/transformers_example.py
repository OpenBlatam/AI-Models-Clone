#!/usr/bin/env python3
"""
Transformers Example - Using Official Documentation References
============================================================

Ejemplo práctico de Transformers usando las referencias de documentación oficial.
"""

import torch
from transformers import AutoModel, AutoTokenizer, AutoModelForSequenceClassification
from transformers import Trainer, TrainingArguments
from torch.utils.data import Dataset, DataLoader
from official_docs_reference import OfficialDocsReference

class TextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        # Tokenización siguiendo las mejores prácticas
        encoding = self.tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def load_model_and_tokenizer():
    """Cargar modelo y tokenizer siguiendo las mejores prácticas."""
    ref = OfficialDocsReference()
    
    # Obtener referencia de model loading
    model_ref = ref.get_api_reference("transformers", "model_loading")
    print(f"Usando: {model_ref.name}")
    print(f"Descripción: {model_ref.description}")
    
    # Cargar modelo y tokenizer (mejor práctica oficial)
    model_name = "bert-base-uncased"
    
    print(f"\n📥 Cargando modelo: {model_name}")
    
    # Cargar tokenizer desde el mismo modelo
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Cargar modelo para clasificación de secuencias
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=2  # Clasificación binaria
    )
    
    print("✅ Modelo y tokenizer cargados exitosamente!")
    return model, tokenizer

def prepare_data():
    """Preparar datos de ejemplo."""
    # Datos de ejemplo para clasificación de sentimientos
    texts = [
        "I love this product, it's amazing!",
        "This is terrible, I hate it.",
        "The quality is good but expensive.",
        "Not worth the money at all.",
        "Excellent service and fast delivery.",
        "Poor customer support.",
        "Great value for money.",
        "Disappointed with the purchase.",
        "Highly recommended!",
        "Avoid this product."
    ]
    
    # Labels: 0 = negativo, 1 = positivo
    labels = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    
    return texts, labels

def tokenize_data(texts, tokenizer):
    """Tokenizar datos siguiendo las mejores prácticas."""
    ref = OfficialDocsReference()
    
    # Obtener referencia de tokenization
    tokenizer_ref = ref.get_api_reference("transformers", "tokenization")
    print(f"\n🔤 Usando: {tokenizer_ref.name}")
    print(f"Descripción: {tokenizer_ref.description}")
    
    print("Mejores prácticas de tokenización:")
    for practice in tokenizer_ref.best_practices:
        print(f"  ✓ {practice}")
    
    # Tokenización de batch siguiendo las mejores prácticas
    print(f"\n📝 Tokenizando {len(texts)} textos...")
    
    # Tokenización individual para el dataset
    tokenized_texts = []
    for text in texts:
        tokens = tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        tokenized_texts.append(tokens)
    
    print("✅ Tokenización completada!")
    return tokenized_texts

def train_with_trainer(model, tokenizer, texts, labels):
    """Entrenar usando Trainer siguiendo las mejores prácticas."""
    ref = OfficialDocsReference()
    
    # Obtener referencia de training
    training_ref = ref.get_api_reference("transformers", "training")
    print(f"\n🏋️ Usando: {training_ref.name}")
    print(f"Descripción: {training_ref.description}")
    
    # Crear dataset
    dataset = TextDataset(texts, labels, tokenizer)
    
    # Configurar argumentos de entrenamiento siguiendo las mejores prácticas
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        save_steps=100,
        eval_steps=100,
        evaluation_strategy="steps",
        save_strategy="steps",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        fp16=True,  # Mixed precision
        dataloader_num_workers=2,
        gradient_accumulation_steps=2,
        remove_unused_columns=False,
    )
    
    print("Configuración de entrenamiento:")
    print(f"  - Epochs: {training_args.num_train_epochs}")
    print(f"  - Batch size: {training_args.per_device_train_batch_size}")
    print(f"  - Mixed precision: {training_args.fp16}")
    print(f"  - Gradient accumulation: {training_args.gradient_accumulation_steps}")
    
    # Crear trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        eval_dataset=dataset,  # Usar el mismo dataset para demo
        tokenizer=tokenizer,
    )
    
    print("\n🚀 Iniciando entrenamiento...")
    trainer.train()
    
    print("✅ Entrenamiento completado!")
    return trainer

def predict_sentiment(model, tokenizer, text):
    """Predecir sentimiento de un texto."""
    model.eval()
    
    # Tokenizar texto de entrada
    inputs = tokenizer(
        text,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    )
    
    # Predicción
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predicted_class = torch.argmax(predictions, dim=1).item()
        confidence = predictions[0][predicted_class].item()
    
    sentiment = "Positivo" if predicted_class == 1 else "Negativo"
    return sentiment, confidence

def validate_code():
    """Validar código usando el sistema de referencias."""
    ref = OfficialDocsReference()
    
    # Código de ejemplo
    code = """
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("bert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

inputs = tokenizer(
    texts,
    padding=True,
    truncation=True,
    max_length=512,
    return_tensors="pt"
)
"""
    
    print("\n🔍 Validando código de Transformers...")
    validation = ref.validate_code_snippet(code, "transformers")
    
    if validation["valid"]:
        print("✅ Código válido según las mejores prácticas")
    else:
        print("❌ Código tiene problemas:")
        for issue in validation["issues"]:
            print(f"   - {issue}")
    
    if validation["recommendations"]:
        print("💡 Recomendaciones:")
        for rec in validation["recommendations"]:
            print(f"   - {rec}")

def main():
    """Función principal."""
    print("🤗 EJEMPLO PRÁCTICO DE TRANSFORMERS")
    print("Usando referencias de documentación oficial")
    print("=" * 60)
    
    # Validar código
    validate_code()
    
    # Cargar modelo y tokenizer
    model, tokenizer = load_model_and_tokenizer()
    
    # Preparar datos
    texts, labels = prepare_data()
    
    # Tokenizar datos
    tokenize_data(texts, tokenizer)
    
    # Entrenar modelo
    trainer = train_with_trainer(model, tokenizer, texts, labels)
    
    # Probar predicciones
    print("\n🎯 Probando predicciones:")
    test_texts = [
        "This is absolutely fantastic!",
        "I'm very disappointed with this.",
        "It's okay, nothing special."
    ]
    
    for text in test_texts:
        sentiment, confidence = predict_sentiment(model, tokenizer, text)
        print(f"  '{text}' → {sentiment} (confianza: {confidence:.2f})")
    
    print("\n🎉 ¡Ejemplo completado exitosamente!")
    print("El código sigue las mejores prácticas oficiales de Transformers.")

if __name__ == "__main__":
    main() 