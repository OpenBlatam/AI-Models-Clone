#!/usr/bin/env python3
"""
PyTorch Example - Using Official Documentation References
========================================================

Ejemplo práctico de PyTorch usando las referencias de documentación oficial.
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from torch.cuda.amp import autocast, GradScaler
from official_docs_reference import OfficialDocsReference

class SimpleModel(nn.Module):
    def __init__(self, input_size=10, hidden_size=50, output_size=1):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

def create_dataloader():
    """Crear DataLoader siguiendo las mejores prácticas de PyTorch."""
    # Generar datos de ejemplo
    X = torch.randn(1000, 10)
    y = torch.randn(1000, 1)
    
    dataset = TensorDataset(X, y)
    
    # Usar configuración recomendada por la documentación oficial
    dataloader = DataLoader(
        dataset,
        batch_size=32,
        shuffle=True,
        num_workers=4,  # Multiprocessing
        pin_memory=True,  # Transferencia más rápida a GPU
        persistent_workers=True,  # Reducir overhead de workers
        drop_last=True  # Tamaños de batch consistentes
    )
    
    return dataloader

def train_with_amp():
    """Entrenamiento con Mixed Precision siguiendo las mejores prácticas."""
    ref = OfficialDocsReference()
    
    # Obtener referencia de AMP
    amp_ref = ref.get_api_reference("pytorch", "mixed_precision")
    print(f"Usando: {amp_ref.name}")
    print(f"Descripción: {amp_ref.description}")
    
    # Configurar modelo y datos
    model = SimpleModel()
    dataloader = create_dataloader()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    # Inicializar GradScaler (mejor práctica oficial)
    scaler = GradScaler()
    
    print("\n🚀 Iniciando entrenamiento con AMP...")
    
    model.train()
    for epoch in range(5):
        total_loss = 0
        for batch_idx, (data, target) in enumerate(dataloader):
            optimizer.zero_grad()
            
            # Forward pass con autocast (mejor práctica oficial)
            with autocast():
                output = model(data)
                loss = criterion(output, target)
            
            # Backward pass con scaling (mejor práctica oficial)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            
            total_loss += loss.item()
            
            if batch_idx % 10 == 0:
                print(f"Epoch {epoch+1}, Batch {batch_idx}, Loss: {loss.item():.4f}")
        
        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1} completado. Loss promedio: {avg_loss:.4f}")
    
    print("✅ Entrenamiento completado!")
    return model

def save_checkpoint(model, optimizer, epoch, loss):
    """Guardar checkpoint siguiendo las mejores prácticas."""
    ref = OfficialDocsReference()
    
    # Obtener referencia de checkpointing
    checkpoint_ref = ref.get_api_reference("pytorch", "model_checkpointing")
    print(f"\n💾 Guardando checkpoint usando: {checkpoint_ref.name}")
    
    # Crear checkpoint con toda la información necesaria
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
        'model_config': {
            'input_size': 10,
            'hidden_size': 50,
            'output_size': 1
        }
    }
    
    # Guardar checkpoint
    torch.save(checkpoint, 'model_checkpoint.pth')
    print("✅ Checkpoint guardado exitosamente!")

def load_checkpoint(model, optimizer):
    """Cargar checkpoint siguiendo las mejores prácticas."""
    try:
        checkpoint = torch.load('model_checkpoint.pth')
        
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        print(f"✅ Checkpoint cargado desde epoch {checkpoint['epoch']}")
        print(f"   Loss: {checkpoint['loss']:.4f}")
        
        return checkpoint['epoch'], checkpoint['loss']
    except FileNotFoundError:
        print("⚠️  No se encontró checkpoint, iniciando desde cero")
        return 0, float('inf')

def validate_code():
    """Validar código usando el sistema de referencias."""
    ref = OfficialDocsReference()
    
    # Código de ejemplo
    code = """
import torch
from torch.cuda.amp import autocast, GradScaler
from torch.utils.data import DataLoader

scaler = GradScaler()
dataloader = DataLoader(dataset, num_workers=4, pin_memory=True)

with autocast():
    output = model(input)
    loss = loss_fn(output, target)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
"""
    
    print("\n🔍 Validando código de PyTorch...")
    validation = ref.validate_code_snippet(code, "pytorch")
    
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
    print("🔥 EJEMPLO PRÁCTICO DE PYTORCH")
    print("Usando referencias de documentación oficial")
    print("=" * 60)
    
    # Validar código
    validate_code()
    
    # Entrenar modelo con AMP
    model = train_with_amp()
    
    # Guardar checkpoint
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    save_checkpoint(model, optimizer, epoch=5, loss=0.001)
    
    # Cargar checkpoint
    load_checkpoint(model, optimizer)
    
    print("\n🎉 ¡Ejemplo completado exitosamente!")
    print("El código sigue las mejores prácticas oficiales de PyTorch.")

if __name__ == "__main__":
    main() 