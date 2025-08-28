# 🎯 Advanced Loss Functions and Optimization Algorithms Guide

## Overview

This guide covers comprehensive loss functions and optimization algorithms for deep learning models, including advanced loss functions like focal loss, label smoothing, contrastive loss, and optimization strategies like AdamW, RAdam, and advanced learning rate scheduling.

## 🚀 Advanced Loss Functions

### **1. Focal Loss**

#### **Purpose**
Addresses class imbalance in classification tasks by down-weighting easy examples and focusing on hard examples.

#### **Implementation**
```python
class FocalLoss(nn.Module):
    def __init__(self, alpha: float = 1.0, gamma: float = 2.0, reduction: str = 'mean'):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
        
    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss
```

**Key Features**:
- ✅ **Alpha parameter**: Controls class balancing
- ✅ **Gamma parameter**: Controls focus on hard examples
- ✅ **Reduction options**: Mean, sum, or none
- ✅ **Best for**: Imbalanced datasets, object detection

**Usage Example**:
```python
# For binary classification with class imbalance
focal_loss = FocalLoss(alpha=1.0, gamma=2.0)
loss = focal_loss(predictions, targets)
```

### **2. Label Smoothing Loss**

#### **Purpose**
Improves generalization by preventing overconfidence in predictions.

#### **Implementation**
```python
class LabelSmoothingLoss(nn.Module):
    def __init__(self, classes: int, smoothing: float = 0.1, dim: int = -1):
        super().__init__()
        self.confidence = 1.0 - smoothing
        self.smoothing = smoothing
        self.cls = classes
        self.dim = dim
        
    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        pred = F.log_softmax(pred, dim=self.dim)
        with torch.no_grad():
            true_dist = torch.zeros_like(pred)
            true_dist.fill_(self.smoothing / (self.cls - 1))
            true_dist.scatter_(1, target.data.unsqueeze(1), self.confidence)
        return torch.mean(torch.sum(-true_dist * pred, dim=self.dim))
```

**Key Features**:
- ✅ **Smoothing factor**: Controls confidence reduction
- ✅ **Multi-class support**: Handles any number of classes
- ✅ **Best for**: Classification tasks, preventing overfitting

**Usage Example**:
```python
# For 10-class classification with 0.1 smoothing
label_smooth_loss = LabelSmoothingLoss(classes=10, smoothing=0.1)
loss = label_smooth_loss(predictions, targets)
```

### **3. Dice Loss**

#### **Purpose**
Optimized for segmentation tasks, especially when dealing with class imbalance.

#### **Implementation**
```python
class DiceLoss(nn.Module):
    def __init__(self, smooth: float = 1.0, square_denominator: bool = False, with_logits: bool = True):
        super().__init__()
        self.smooth = smooth
        self.square_denominator = square_denominator
        self.with_logits = with_logits
        
    def forward(self, input: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        if self.with_logits:
            input = torch.sigmoid(input)
            
        flat_input = input.view(-1)
        flat_target = target.view(-1)
        
        intersection = (flat_input * flat_target).sum()
        
        if self.square_denominator:
            denominator = (flat_input * flat_input).sum() + (flat_target * flat_target).sum()
        else:
            denominator = flat_input.sum() + flat_target.sum()
            
        loss = 1 - ((2 * intersection + self.smooth) / (denominator + self.smooth))
        return loss
```

**Key Features**:
- ✅ **Smooth parameter**: Prevents division by zero
- ✅ **Square denominator option**: Alternative normalization
- ✅ **Logits support**: Automatic sigmoid application
- ✅ **Best for**: Image segmentation, medical imaging

**Usage Example**:
```python
# For binary segmentation
dice_loss = DiceLoss(smooth=1.0, with_logits=True)
loss = dice_loss(predictions, targets)
```

### **4. Contrastive Loss**

#### **Purpose**
Learns representations by pulling similar samples closer and pushing different samples apart.

#### **Implementation**
```python
class ContrastiveLoss(nn.Module):
    def __init__(self, margin: float = 1.0, distance_metric: str = 'euclidean'):
        super().__init__()
        self.margin = margin
        self.distance_metric = distance_metric
        
    def forward(self, x1: torch.Tensor, x2: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        if self.distance_metric == 'euclidean':
            dist = F.pairwise_distance(x1, x2, p=2)
        elif self.distance_metric == 'cosine':
            dist = 1 - F.cosine_similarity(x1, x2)
        else:
            raise ValueError(f"Unsupported distance metric: {self.distance_metric}")
            
        loss = y * torch.pow(dist, 2) + (1 - y) * torch.pow(torch.clamp(self.margin - dist, min=0.0), 2)
        return loss.mean()
```

**Key Features**:
- ✅ **Margin parameter**: Controls separation distance
- ✅ **Distance metrics**: Euclidean or cosine distance
- ✅ **Binary labels**: 1 for similar, 0 for different
- ✅ **Best for**: Representation learning, similarity learning

**Usage Example**:
```python
# For representation learning
contrastive_loss = ContrastiveLoss(margin=1.0, distance_metric='euclidean')
loss = contrastive_loss(embeddings1, embeddings2, similarity_labels)
```

### **5. Triplet Loss**

#### **Purpose**
Learns embeddings by ensuring positive samples are closer than negative samples.

#### **Implementation**
```python
class TripletLoss(nn.Module):
    def __init__(self, margin: float = 1.0, distance_metric: str = 'euclidean'):
        super().__init__()
        self.margin = margin
        self.distance_metric = distance_metric
        
    def forward(self, anchor: torch.Tensor, positive: torch.Tensor, negative: torch.Tensor) -> torch.Tensor:
        if self.distance_metric == 'euclidean':
            pos_dist = F.pairwise_distance(anchor, positive, p=2)
            neg_dist = F.pairwise_distance(anchor, negative, p=2)
        elif self.distance_metric == 'cosine':
            pos_dist = 1 - F.cosine_similarity(anchor, positive)
            neg_dist = 1 - F.cosine_similarity(anchor, negative)
        else:
            raise ValueError(f"Unsupported distance metric: {self.distance_metric}")
            
        loss = torch.clamp(pos_dist - neg_dist + self.margin, min=0.0)
        return loss.mean()
```

**Key Features**:
- ✅ **Margin parameter**: Controls triplet separation
- ✅ **Distance metrics**: Euclidean or cosine distance
- ✅ **Three inputs**: Anchor, positive, and negative samples
- ✅ **Best for**: Face recognition, metric learning

**Usage Example**:
```python
# For face recognition
triplet_loss = TripletLoss(margin=1.0, distance_metric='euclidean')
loss = triplet_loss(anchor_emb, positive_emb, negative_emb)
```

### **6. Custom Loss Function**

#### **Purpose**
Combines multiple loss functions with configurable weights for complex training objectives.

#### **Implementation**
```python
class CustomLossFunction(nn.Module):
    def __init__(self, 
                 primary_loss: str = 'cross_entropy',
                 auxiliary_losses: List[str] = None,
                 loss_weights: List[float] = None,
                 **kwargs):
        super().__init__()
        self.primary_loss = primary_loss
        self.auxiliary_losses = auxiliary_losses or []
        self.loss_weights = loss_weights or [1.0] * (len(self.auxiliary_losses) + 1)
        
        # Initialize loss functions
        self.loss_functions = self._init_loss_functions(**kwargs)
        
    def forward(self, predictions: Dict[str, torch.Tensor], targets: Dict[str, torch.Tensor]) -> torch.Tensor:
        total_loss = 0.0
        
        # Primary loss
        if 'primary' in self.loss_functions:
            primary_pred = predictions.get('primary', predictions.get('logits', predictions.get('output')))
            primary_target = targets.get('primary', targets.get('labels', targets.get('target')))
            
            if primary_pred is not None and primary_target is not None:
                primary_loss = self.loss_functions['primary'](primary_pred, primary_target)
                total_loss += self.loss_weights[0] * primary_loss
                
        # Auxiliary losses
        for i, aux_loss_name in enumerate(self.auxiliary_losses):
            if aux_loss_name in self.loss_functions:
                aux_pred = predictions.get(aux_loss_name)
                aux_target = targets.get(aux_loss_name)
                
                if aux_pred is not None and aux_target is not None:
                    aux_loss = self.loss_functions[aux_loss_name](aux_pred, aux_target)
                    total_loss += self.loss_weights[i + 1] * aux_loss
                    
        return total_loss
```

**Key Features**:
- ✅ **Primary loss**: Main training objective
- ✅ **Auxiliary losses**: Additional training objectives
- ✅ **Configurable weights**: Balance between different losses
- ✅ **Flexible inputs**: Dictionary-based prediction and target handling
- ✅ **Best for**: Multi-task learning, complex objectives

**Usage Example**:
```python
# For multi-task learning
custom_loss = CustomLossFunction(
    primary_loss='cross_entropy',
    auxiliary_losses=['contrastive', 'l1'],
    loss_weights=[0.7, 0.2, 0.1]
)

# Prepare inputs
predictions = {
    'primary': classification_logits,
    'contrastive': embeddings,
    'l1': reconstruction_output
}
targets = {
    'primary': labels,
    'contrastive': similarity_labels,
    'l1': original_input
}

loss = custom_loss(predictions, targets)
```

## 🎯 Loss Function Factory

### **1. Factory Pattern**

#### **Purpose**
Provides a unified interface for creating and configuring loss functions.

#### **Implementation**
```python
class LossFunctionFactory:
    @staticmethod
    def create_loss_function(loss_type: str, **kwargs) -> nn.Module:
        if loss_type == 'cross_entropy':
            return nn.CrossEntropyLoss(**kwargs)
        elif loss_type == 'focal':
            return FocalLoss(**kwargs)
        elif loss_type == 'label_smoothing':
            return LabelSmoothingLoss(**kwargs)
        elif loss_type == 'dice':
            return DiceLoss(**kwargs)
        elif loss_type == 'contrastive':
            return ContrastiveLoss(**kwargs)
        elif loss_type == 'triplet':
            return TripletLoss(**kwargs)
        elif loss_type == 'mse':
            return nn.MSELoss(**kwargs)
        elif loss_type == 'l1':
            return nn.L1Loss(**kwargs)
        elif loss_type == 'bce':
            return nn.BCELoss(**kwargs)
        elif loss_type == 'bce_with_logits':
            return nn.BCEWithLogitsLoss(**kwargs)
        elif loss_type == 'kl_div':
            return nn.KLDivLoss(**kwargs)
        elif loss_type == 'custom':
            return CustomLossFunction(**kwargs)
        else:
            raise ValueError(f"Unsupported loss type: {loss_type}")
```

**Supported Loss Types**:
- ✅ Cross Entropy
- ✅ Focal Loss
- ✅ Label Smoothing
- ✅ Dice Loss
- ✅ Contrastive Loss
- ✅ Triplet Loss
- ✅ MSE Loss
- ✅ L1 Loss
- ✅ BCE Loss
- ✅ KL Divergence
- ✅ Custom Loss

**Usage Example**:
```python
# Create focal loss with custom parameters
focal_loss = LossFunctionFactory.create_loss_function(
    'focal', 
    alpha=2.0, 
    gamma=3.0
)

# Create custom loss function
custom_loss = LossFunctionFactory.create_loss_function(
    'custom',
    primary_loss='cross_entropy',
    auxiliary_losses=['contrastive'],
    loss_weights=[0.8, 0.2]
)
```

### **2. Default Configurations**

#### **Purpose**
Provides optimal default parameters for each loss function.

#### **Implementation**
```python
@staticmethod
def get_loss_function_config(loss_type: str) -> Dict[str, Any]:
    configs = {
        'cross_entropy': {'reduction': 'mean'},
        'focal': {'alpha': 1.0, 'gamma': 2.0, 'reduction': 'mean'},
        'label_smoothing': {'classes': 1000, 'smoothing': 0.1},
        'dice': {'smooth': 1.0, 'square_denominator': False, 'with_logits': True},
        'contrastive': {'margin': 1.0, 'distance_metric': 'euclidean'},
        'triplet': {'margin': 1.0, 'distance_metric': 'euclidean'},
        'mse': {'reduction': 'mean'},
        'l1': {'reduction': 'mean'},
        'bce': {'reduction': 'mean'},
        'bce_with_logits': {'reduction': 'mean'},
        'kl_div': {'reduction': 'batchmean'}
    }
    return configs.get(loss_type, {})
```

**Usage Example**:
```python
# Get default configuration for focal loss
focal_config = LossFunctionFactory.get_loss_function_config('focal')
print(focal_config)  # {'alpha': 1.0, 'gamma': 2.0, 'reduction': 'mean'}

# Create loss with default config
focal_loss = LossFunctionFactory.create_loss_function('focal', **focal_config)
```

## 🚀 Advanced Optimization Algorithms

### **1. Advanced Optimizer**

#### **Purpose**
Provides a unified interface for multiple optimization algorithms with consistent configuration.

#### **Implementation**
```python
class AdvancedOptimizer:
    def __init__(self, 
                 model: nn.Module,
                 optimizer_type: str = 'adamw',
                 learning_rate: float = 1e-4,
                 weight_decay: float = 0.01,
                 **kwargs):
        self.model = model
        self.optimizer_type = optimizer_type
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.kwargs = kwargs
        
        self.optimizer = self._create_optimizer()
        
    def _create_optimizer(self) -> torch.optim.Optimizer:
        if self.optimizer_type == 'adamw':
            return torch.optim.AdamW(
                self.model.parameters(),
                lr=self.learning_rate,
                weight_decay=self.weight_decay,
                **self.kwargs
            )
        elif self.optimizer_type == 'adam':
            return torch.optim.Adam(
                self.model.parameters(),
                lr=self.learning_rate,
                weight_decay=self.weight_decay,
                **self.kwargs
            )
        elif self.optimizer_type == 'sgd':
            return torch.optim.SGD(
                self.model.parameters(),
                lr=self.learning_rate,
                weight_decay=self.weight_decay,
                **self.kwargs
            )
        elif self.optimizer_type == 'radam':
            return torch.optim.RAdam(
                self.model.parameters(),
                lr=self.learning_rate,
                weight_decay=self.weight_decay,
                **self.kwargs
            )
        elif self.optimizer_type == 'adafactor':
            return torch.optim.Adafactor(
                self.model.parameters(),
                lr=self.learning_rate,
                weight_decay=self.weight_decay,
                **self.kwargs
            )
        else:
            raise ValueError(f"Unsupported optimizer type: {self.optimizer_type}")
```

**Supported Optimizers**:
- ✅ **AdamW**: Best for most deep learning tasks
- ✅ **Adam**: Good general-purpose optimizer
- ✅ **SGD**: With momentum and Nesterov acceleration
- ✅ **RAdam**: Rectified Adam for better convergence
- ✅ **Adafactor**: Memory-efficient alternative to Adam

**Usage Example**:
```python
# Create AdamW optimizer
optimizer = AdvancedOptimizer(
    model=model,
    optimizer_type='adamw',
    learning_rate=1e-4,
    weight_decay=0.01,
    betas=(0.9, 0.999),
    eps=1e-8
)

# Get the underlying optimizer
torch_optimizer = optimizer.get_optimizer()

# Use optimizer methods
optimizer.zero_grad()
optimizer.step()
current_lr = optimizer.get_lr()
```

### **2. Learning Rate Schedulers**

#### **Purpose**
Provides advanced learning rate scheduling strategies for better training convergence.

#### **Implementation**
```python
class LearningRateScheduler:
    def __init__(self, 
                 optimizer: torch.optim.Optimizer,
                 scheduler_type: str = 'cosine',
                 **kwargs):
        self.optimizer = optimizer
        self.scheduler_type = scheduler_type
        self.kwargs = kwargs
        
        self.scheduler = self._create_scheduler()
        
    def _create_scheduler(self):
        if self.scheduler_type == 'cosine':
            return torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                **self.kwargs
            )
        elif self.scheduler_type == 'cosine_warmup':
            return torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
                self.optimizer,
                **self.kwargs
            )
        elif self.scheduler_type == 'linear_warmup':
            return torch.optim.lr_scheduler.LinearLR(
                self.optimizer,
                **self.kwargs
            )
        elif self.scheduler_type == 'step':
            return torch.optim.lr_scheduler.StepLR(
                self.optimizer,
                **self.kwargs
            )
        elif self.scheduler_type == 'plateau':
            return torch.optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer,
                **self.kwargs
            )
        elif self.scheduler_type == 'exponential':
            return torch.optim.lr_scheduler.ExponentialLR(
                self.optimizer,
                **self.kwargs
            )
        elif self.scheduler_type == 'one_cycle':
            return torch.optim.lr_scheduler.OneCycleLR(
                self.optimizer,
                **self.kwargs
            )
        else:
            raise ValueError(f"Unsupported scheduler type: {self.scheduler_type}")
```

**Supported Schedulers**:
- ✅ **Cosine**: Smooth cosine annealing
- ✅ **Cosine Warmup**: Cosine with warm restarts
- ✅ **Linear Warmup**: Linear warmup followed by constant LR
- ✅ **Step**: Step-wise LR reduction
- ✅ **Plateau**: Reduce LR when validation metric plateaus
- ✅ **Exponential**: Exponential LR decay
- ✅ **One Cycle**: One cycle policy for fast training

**Usage Example**:
```python
# Create cosine annealing scheduler
scheduler = LearningRateScheduler(
    optimizer=optimizer,
    scheduler_type='cosine',
    T_max=100  # Total epochs
)

# Step the scheduler
scheduler.step()

# Get current learning rates
current_lrs = scheduler.get_last_lr()

# Save/load scheduler state
scheduler_state = scheduler.state_dict()
scheduler.load_state_dict(scheduler_state)
```

### **3. Optimizer Factory**

#### **Purpose**
Provides factory methods for creating optimizers and schedulers with optimal configurations.

#### **Implementation**
```python
class OptimizerFactory:
    @staticmethod
    def create_optimizer(model: nn.Module, 
                        optimizer_type: str = 'adamw',
                        learning_rate: float = 1e-4,
                        weight_decay: float = 0.01,
                        **kwargs) -> torch.optim.Optimizer:
        return AdvancedOptimizer(
            model, optimizer_type, learning_rate, weight_decay, **kwargs
        ).get_optimizer()
    
    @staticmethod
    def create_scheduler(optimizer: torch.optim.Optimizer,
                        scheduler_type: str = 'cosine',
                        **kwargs) -> LearningRateScheduler:
        return LearningRateScheduler(optimizer, scheduler_type, **kwargs)
    
    @staticmethod
    def get_optimizer_config(optimizer_type: str) -> Dict[str, Any]:
        configs = {
            'adamw': {'betas': (0.9, 0.999), 'eps': 1e-8},
            'adam': {'betas': (0.9, 0.999), 'eps': 1e-8},
            'sgd': {'momentum': 0.9, 'nesterov': True},
            'radam': {'betas': (0.9, 0.999), 'eps': 1e-8},
            'adafactor': {'eps': (1e-30, 1e-3), 'clip_threshold': 1.0}
        }
        return configs.get(optimizer_type, {})
    
    @staticmethod
    def get_scheduler_config(scheduler_type: str) -> Dict[str, Any]:
        configs = {
            'cosine': {'T_max': 100, 'eta_min': 0},
            'cosine_warmup': {'T_0': 10, 'T_mult': 2},
            'linear_warmup': {'start_factor': 0.1, 'total_iters': 10},
            'step': {'step_size': 30, 'gamma': 0.1},
            'plateau': {'mode': 'min', 'factor': 0.1, 'patience': 10},
            'exponential': {'gamma': 0.95},
            'one_cycle': {'max_lr': 1e-3, 'total_steps': 100}
        }
        return configs.get(scheduler_type, {})
```

**Usage Example**:
```python
# Create optimizer with default configuration
optimizer = OptimizerFactory.create_optimizer(
    model=model,
    optimizer_type='adamw',
    learning_rate=1e-4
)

# Create scheduler with default configuration
scheduler = OptimizerFactory.create_scheduler(
    optimizer=optimizer,
    scheduler_type='cosine'
)

# Get optimal configurations
opt_config = OptimizerFactory.get_optimizer_config('adamw')
sched_config = OptimizerFactory.get_scheduler_config('cosine')
```

## 🎯 Advanced Parameter Grouping

### **1. Parameter Grouper**

#### **Purpose**
Groups model parameters for different optimization strategies (e.g., different weight decay for different layer types).

#### **Implementation**
```python
class ParameterGrouper:
    @staticmethod
    def group_parameters(model: nn.Module, 
                        weight_decay: float = 0.01,
                        no_decay_keywords: List[str] = None) -> List[Dict[str, Any]]:
        if no_decay_keywords is None:
            no_decay_keywords = ['bias', 'LayerNorm.weight', 'LayerNorm.bias']
            
        optimizer_grouped_parameters = [
            {
                'params': [p for n, p in model.named_parameters() 
                          if not any(nd in n for nd in no_decay_keywords) and p.requires_grad],
                'weight_decay': weight_decay,
            },
            {
                'params': [p for n, p in model.named_parameters() 
                          if any(nd in n for nd in no_decay_keywords) and p.requires_grad],
                'weight_decay': 0.0,
            }
        ]
        
        return optimizer_grouped_parameters
    
    @staticmethod
    def group_by_layer_type(model: nn.Module, 
                           layer_types: Dict[str, Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if layer_types is None:
            layer_types = {
                'embedding': {'lr_mult': 0.1, 'weight_decay': 0.0},
                'transformer': {'lr_mult': 1.0, 'weight_decay': 0.01},
                'classifier': {'lr_mult': 10.0, 'weight_decay': 0.01}
            }
            
        grouped_parameters = []
        
        for layer_name, config in layer_types.items():
            params = []
            for name, param in model.named_parameters():
                if layer_name in name.lower() and param.requires_grad:
                    params.append(param)
                    
            if params:
                grouped_parameters.append({
                    'params': params,
                    'lr_mult': config.get('lr_mult', 1.0),
                    'weight_decay': config.get('weight_decay', 0.01)
                })
                
        return grouped_parameters
```

**Key Features**:
- ✅ **No-decay groups**: Excludes bias and normalization parameters from weight decay
- ✅ **Layer-specific grouping**: Different learning rates and weight decay for different layer types
- ✅ **Flexible configuration**: Customizable grouping strategies
- ✅ **Best for**: Transformer models, fine-tuning scenarios

**Usage Example**:
```python
# Group parameters for different weight decay strategies
param_groups = ParameterGrouper.group_parameters(
    model=model,
    weight_decay=0.01,
    no_decay_keywords=['bias', 'LayerNorm.weight', 'LayerNorm.bias']
)

# Create optimizer with grouped parameters
optimizer = torch.optim.AdamW(param_groups, lr=1e-4)

# Group by layer type for different learning rates
layer_groups = ParameterGrouper.group_by_layer_type(
    model=model,
    layer_types={
        'embedding': {'lr_mult': 0.1, 'weight_decay': 0.0},
        'transformer': {'lr_mult': 1.0, 'weight_decay': 0.01},
        'classifier': {'lr_mult': 10.0, 'weight_decay': 0.01}
    }
)
```

## 🔧 Enhanced Training Configuration

### **1. Configuration Updates**

#### **Purpose**
Extends the training configuration with loss and optimization options.

#### **Implementation**
```python
def update_training_config_with_loss_optimization():
    """Update training configuration with loss and optimization options."""
    
    # Add new fields to UltraTrainingConfig
    UltraTrainingConfig.loss_function = 'cross_entropy'
    UltraTrainingConfig.auxiliary_losses = []
    UltraTrainingConfig.loss_weights = [1.0]
    UltraTrainingConfig.optimizer_type = 'adamw'
    UltraTrainingConfig.learning_rate = 1e-4
    UltraTrainingConfig.weight_decay = 0.01
    UltraTrainingConfig.scheduler_type = 'cosine'
    UltraTrainingConfig.warmup_steps = 1000
    UltraTrainingConfig.max_lr = 1e-3
    UltraTrainingConfig.min_lr = 1e-6
    UltraTrainingConfig.use_parameter_grouping = True
    UltraTrainingConfig.no_decay_keywords = ['bias', 'LayerNorm.weight', 'LayerNorm.bias']
    
    logger.info("Training configuration updated with loss and optimization options")
```

**New Configuration Options**:
- ✅ **Loss function**: Primary loss function type
- ✅ **Auxiliary losses**: Additional loss functions
- ✅ **Loss weights**: Balancing weights for different losses
- ✅ **Optimizer type**: Choice of optimization algorithm
- ✅ **Learning rate**: Base learning rate
- ✅ **Weight decay**: L2 regularization strength
- ✅ **Scheduler type**: Learning rate scheduling strategy
- ✅ **Warmup steps**: Number of warmup steps
- ✅ **Parameter grouping**: Enable/disable parameter grouping
- ✅ **No-decay keywords**: Keywords for parameters without weight decay

## 🎯 Enhanced Trainer

### **1. EnhancedUltraOptimizedTrainer**

#### **Purpose**
Extends the base trainer with advanced loss functions and optimization algorithms.

#### **Key Features**:
- ✅ **Advanced loss functions**: Support for focal loss, label smoothing, etc.
- ✅ **Parameter grouping**: Different optimization strategies for different parameter types
- ✅ **Advanced schedulers**: Multiple learning rate scheduling strategies
- ✅ **Gradient monitoring**: Real-time gradient statistics
- ✅ **Enhanced logging**: Comprehensive training metrics

#### **Usage Example**:
```python
# Initialize enhanced trainer
trainer = EnhancedUltraOptimizedTrainer(model, config)

# Training automatically uses advanced loss and optimization
for epoch in range(num_epochs):
    avg_loss = trainer.train_epoch(dataloader, epoch)
    metrics = trainer.evaluate(dataloader)
    
    # Save checkpoints
    trainer.save_checkpoint(f"checkpoint_epoch_{epoch}.pt", epoch, metrics)
```

## 🧪 Testing and Validation

### **1. Loss Function Testing**

```python
def test_loss_functions():
    """Test various loss functions."""
    logger.info("Testing loss functions...")
    
    # Create sample data
    batch_size, num_classes = 32, 10
    predictions = torch.randn(batch_size, num_classes)
    targets = torch.randint(0, num_classes, (batch_size,))
    
    # Test different loss functions
    loss_functions = {
        'cross_entropy': nn.CrossEntropyLoss(),
        'focal': FocalLoss(alpha=1.0, gamma=2.0),
        'label_smoothing': LabelSmoothingLoss(classes=num_classes, smoothing=0.1),
        'mse': nn.MSELoss(),
        'l1': nn.L1Loss()
    }
    
    results = {}
    for name, loss_fn in loss_functions.items():
        try:
            loss = loss_fn(predictions, targets)
            results[name] = loss.item()
            logger.info(f"{name} loss: {loss.item():.4f}")
        except Exception as e:
            logger.error(f"Error testing {name} loss", error=str(e))
            results[name] = None
    
    return results
```

### **2. Optimizer Testing**

```python
def test_optimizers():
    """Test various optimizers."""
    logger.info("Testing optimizers...")
    
    # Create a simple model
    model = nn.Sequential(
        nn.Linear(10, 20),
        nn.ReLU(),
        nn.Linear(20, 5)
    )
    
    # Test different optimizers
    optimizers = {
        'adamw': torch.optim.AdamW(model.parameters(), lr=1e-4),
        'adam': torch.optim.Adam(model.parameters(), lr=1e-4),
        'sgd': torch.optim.SGD(model.parameters(), lr=1e-3, momentum=0.9),
        'radam': torch.optim.RAdam(model.parameters(), lr=1e-4)
    }
    
    # Test parameter access
    results = {}
    for name, optimizer in optimizers.items():
        try:
            lr = optimizer.param_groups[0]['lr']
            param_count = sum(p.numel() for p in model.parameters())
            results[name] = {'lr': lr, 'param_count': param_count}
            logger.info(f"{name}: lr={lr}, params={param_count}")
        except Exception as e:
            logger.error(f"Error testing {name} optimizer", error=str(e))
            results[name] = None
    
    return results
```

### **3. Integration Testing**

```python
def demonstrate_loss_optimization_integration():
    """Demonstrate integration of loss functions and optimization algorithms."""
    logger.info("Demonstrating loss and optimization integration...")
    
    # Create sample data and model
    batch_size, seq_len, hidden_dim = 32, 100, 128
    input_ids = torch.randint(0, 50000, (batch_size, seq_len))
    attention_mask = torch.ones(batch_size, seq_len)
    labels = torch.randint(0, 2, (batch_size,))
    
    model = CustomTransformerModel(
        vocab_size=50000,
        d_model=hidden_dim,
        n_layers=4,
        n_heads=8,
        d_ff=512,
        max_seq_len=seq_len,
        dropout=0.1,
        num_labels=2
    )
    
    # Test different combinations
    loss_functions = [
        ('cross_entropy', nn.CrossEntropyLoss()),
        ('focal', FocalLoss(alpha=1.0, gamma=2.0)),
        ('label_smoothing', LabelSmoothingLoss(classes=2, smoothing=0.1))
    ]
    
    optimizers = [
        ('adamw', torch.optim.AdamW(model.parameters(), lr=1e-4)),
        ('adam', torch.optim.Adam(model.parameters(), lr=1e-4)),
        ('sgd', torch.optim.SGD(model.parameters(), lr=1e-3, momentum=0.9))
    ]
    
    results = {}
    
    for loss_name, loss_fn in loss_functions:
        for opt_name, optimizer in optimizers:
            try:
                # Reset model
                for param in model.parameters():
                    param.data.normal_(0, 0.02)
                
                # Forward pass
                predictions = model(input_ids=input_ids, attention_mask=attention_mask)
                
                # Compute loss
                loss = loss_fn(predictions, labels)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                
                # Get gradient norm
                grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                
                # Optimizer step
                optimizer.step()
                
                results[f"{loss_name}_{opt_name}"] = {
                    'loss': loss.item(),
                    'grad_norm': grad_norm.item()
                }
                
                logger.info(f"{loss_name} + {opt_name}: loss={loss.item():.4f}, grad_norm={grad_norm.item():.4f}")
                
            except Exception as e:
                logger.error(f"Error testing {loss_name} + {opt_name}", error=str(e))
                results[f"{loss_name}_{opt_name}"] = None
    
    return results
```

## 📈 Best Practices

### **1. Loss Function Selection**

```python
# For different tasks
if task == 'classification':
    if class_imbalance:
        loss_fn = FocalLoss(alpha=1.0, gamma=2.0)
    else:
        loss_fn = nn.CrossEntropyLoss()
elif task == 'segmentation':
    loss_fn = DiceLoss(smooth=1.0, with_logits=True)
elif task == 'representation_learning':
    loss_fn = ContrastiveLoss(margin=1.0, distance_metric='euclidean')
elif task == 'multi_task':
    loss_fn = CustomLossFunction(
        primary_loss='cross_entropy',
        auxiliary_losses=['contrastive', 'l1'],
        loss_weights=[0.7, 0.2, 0.1]
    )
```

### **2. Optimizer Selection**

```python
# For different scenarios
if training_mode == 'stable':
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
elif training_mode == 'fast':
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=0.001)
elif training_mode == 'memory_efficient':
    optimizer = torch.optim.Adafactor(model.parameters(), lr=1e-4)
elif training_mode == 'fine_tuning':
    # Use parameter grouping
    param_groups = ParameterGrouper.group_parameters(model, weight_decay=0.01)
    optimizer = torch.optim.AdamW(param_groups, lr=1e-5)
```

### **3. Scheduler Selection**

```python
# For different training patterns
if training_pattern == 'stable':
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)
elif training_pattern == 'warmup':
    scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=10)
elif training_pattern == 'fast':
    scheduler = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=1e-3, total_steps=100)
elif training_pattern == 'adaptive':
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10, factor=0.5)
```

## 🔧 Implementation Checklist

- [ ] Implement basic loss functions (Focal, Label Smoothing, Dice)
- [ ] Add advanced loss functions (Contrastive, Triplet)
- [ ] Create custom loss function with auxiliary losses
- [ ] Implement loss function factory
- [ ] Add advanced optimizers (AdamW, RAdam, Adafactor)
- [ ] Implement learning rate schedulers
- [ ] Create optimizer factory
- [ ] Add parameter grouping strategies
- [ ] Enhance training configuration
- [ ] Create enhanced trainer class
- [ ] Add testing and validation functions
- [ ] Document best practices and usage examples

## 🔗 Additional Resources

- [PyTorch Loss Functions](https://pytorch.org/docs/stable/nn.html#loss-functions)
- [PyTorch Optimizers](https://pytorch.org/docs/stable/optim.html)
- [PyTorch Schedulers](https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate)
- [Focal Loss Paper](https://arxiv.org/abs/1708.02002)
- [Label Smoothing Paper](https://arxiv.org/abs/1906.02629)
- [AdamW Paper](https://arxiv.org/abs/1711.05101)
- [RAdam Paper](https://arxiv.org/abs/1908.03265)

This guide provides a comprehensive foundation for implementing advanced loss functions and optimization algorithms with production-ready features and best practices for deep learning models.

