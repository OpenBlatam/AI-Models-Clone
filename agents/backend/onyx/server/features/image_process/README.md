# Advanced Image Processing System

Sistema avanzado de procesamiento de imágenes con optimización GPU, mixed precision training y funciones de pérdida avanzadas.

## Características Principales

### 🚀 Optimización Avanzada
- **GPU Utilization**: Detección automática de CUDA/MPS/CPU
- **Mixed Precision Training**: Uso de FP16 para aceleración
- **Gradient Accumulation**: Batch sizes efectivos más grandes
- **Memory Management**: Limpieza automática y profiling de memoria

### 🎯 Funciones de Pérdida Avanzadas
- **Perceptual Loss**: Usando extractores de características pre-entrenados
- **Frequency Domain Loss**: Preservación de frecuencias en dominio espectral
- **SSIM Loss**: Índice de similitud estructural
- **Edge Preserving Loss**: Preservación de bordes con operadores Sobel
- **Contrast Enhancement Loss**: Mejora de contraste local

### 📡 Optimización de Radio Frecuencia
- **Frequency Band Optimization**: Optimización por bandas de frecuencia
- **Adaptive Filtering**: Filtros adaptativos en dominio espectral
- **High-Frequency Enhancement**: Mejora selectiva de frecuencias altas

## Instalación

```bash
pip install -r requirements.txt
```

## Uso Básico

### Sistema de Optimización

```python
from advanced_optimization_system import AdvancedOptimizationSystem

# Inicializar sistema
opt_system = AdvancedOptimizationSystem()

# Optimizar modelo
training_history = opt_system.optimize_model(
    model, train_loader, val_loader, epochs=100
)

# Encontrar batch size óptimo
optimal_batch = opt_system.optimize_batch_size(model, sample_data)
```

### Funciones de Pérdida

```python
from advanced_loss_functions import AdvancedLossFunctions

loss_functions = AdvancedLossFunctions()

# Pérdida adaptativa combinando múltiples funciones
total_loss = loss_functions.adaptive_loss(pred, target, {
    'mse': 1.0,
    'frequency': 0.5,
    'ssim': 0.3,
    'edge': 0.2
})

# Pérdida en dominio de frecuencia
freq_loss = loss_functions.frequency_domain_loss(pred, target, alpha=0.7)
```

### Optimización de Radio Frecuencia

```python
from advanced_loss_functions import RadioFrequencyOptimizer

rf_optimizer = RadioFrequencyOptimizer()

# Optimizar respuesta de frecuencia
optimized_image = rf_optimizer.optimize_frequency_response(
    image, target_response
)

# Crear filtros de frecuencia
lowpass_filter = rf_optimizer.create_frequency_filter(
    64, 64, 'lowpass', cutoff_freq=0.1
)
```

## Configuración

### Parámetros de Optimización

```python
optimization_config = {
    'mixed_precision': True,           # Habilitar FP16
    'gradient_accumulation_steps': 4,  # Pasos de acumulación
    'max_grad_norm': 1.0,             # Clipping de gradientes
    'learning_rate': 1e-4,            # Tasa de aprendizaje
    'weight_decay': 1e-5,             # Decay de pesos
    'scheduler_patience': 10,         # Paciencia del scheduler
    'scheduler_factor': 0.5           # Factor de reducción LR
}
```

### Bandas de Frecuencia

```python
frequency_bands = {
    'low': (0.0, 0.1),      # Frecuencias bajas
    'mid': (0.1, 0.5),      # Frecuencias medias
    'high': (0.5, 1.0)      # Frecuencias altas
}

band_weights = {
    'low': 1.0,              # Peso para frecuencias bajas
    'mid': 1.5,              # Peso para frecuencias medias
    'high': 2.0              # Peso para frecuencias altas
}
```

## Características Técnicas

### Mixed Precision Training
- Uso automático de `autocast` y `GradScaler`
- Reducción de uso de memoria GPU
- Aceleración de entrenamiento

### Memory Management
- Profiling automático de memoria
- Limpieza de caché GPU
- Optimización de batch size

### Frequency Domain Processing
- Transformadas FFT 2D optimizadas
- Filtros adaptativos por bandas
- Preservación de fase y magnitud

## Ejemplos de Uso

### Entrenamiento Completo

```python
# Configurar sistema
opt_system = AdvancedOptimizationSystem(device='auto')

# Crear data loaders
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

# Entrenar modelo
history = opt_system.optimize_model(
    model=your_model,
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=100
)

# Guardar mejor modelo
opt_system.save_checkpoint(model, optimizer, epoch, best_val_loss)
```

### Evaluación de Pérdidas

```python
# Evaluar diferentes funciones de pérdida
losses = {
    'MSE': F.mse_loss(pred, target),
    'Frequency': loss_functions.frequency_domain_loss(pred, target),
    'SSIM': loss_functions.structural_similarity_loss(pred, target),
    'Edge': loss_functions.edge_preserving_loss(pred, target),
    'Contrast': loss_functions.contrast_enhancement_loss(pred, target)
}

for loss_name, loss_value in losses.items():
    print(f"{loss_name}: {loss_value:.6f}")
```

## Rendimiento

### GPU Memory Usage
- Monitoreo automático de memoria
- Optimización de batch size
- Limpieza de caché

### Training Speed
- Mixed precision: 2-3x más rápido
- Gradient accumulation: Batch sizes efectivos más grandes
- Memory optimization: Mejor utilización de GPU

## Troubleshooting

### Problemas Comunes

1. **Out of Memory**
   - Reducir batch size
   - Habilitar gradient accumulation
   - Usar mixed precision

2. **Training Instability**
   - Ajustar learning rate
   - Modificar gradient clipping
   - Cambiar loss weights

3. **Poor Convergence**
   - Revisar loss weights
   - Ajustar frequency bands
   - Modificar optimizer parameters

## Contribuir

1. Fork el proyecto
2. Crear feature branch
3. Commit cambios
4. Push al branch
5. Crear Pull Request

## Licencia

MIT License - ver LICENSE para detalles.


