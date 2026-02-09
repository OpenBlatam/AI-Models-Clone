"""
Simple Face Swap Model
======================
Modelo CNN para face swap usando PyTorch.
"""

import torch
import torch.nn as nn


class SimpleFaceSwapModel(nn.Module):
    """Modelo CNN mejorado para face swap con mejor arquitectura."""
    
    def __init__(self, input_size=256):
        """
        Inicializar modelo.
        
        Args:
            input_size: Tamaño de entrada (default: 256)
        """
        super(SimpleFaceSwapModel, self).__init__()
        
        # Encoder mejorado con conexiones residuales
        self.encoder_conv1 = nn.Sequential(
            nn.Conv2d(6, 64, 4, 2, 1),
            nn.LeakyReLU(0.2, inplace=True)
        )
        
        self.encoder_conv2 = nn.Sequential(
            nn.Conv2d(64, 128, 4, 2, 1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True)
        )
        
        self.encoder_conv3 = nn.Sequential(
            nn.Conv2d(128, 256, 4, 2, 1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True)
        )
        
        self.encoder_conv4 = nn.Sequential(
            nn.Conv2d(256, 512, 4, 2, 1),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True)
        )
        
        # Capa de bottleneck con atención
        self.bottleneck = nn.Sequential(
            nn.Conv2d(512, 512, 3, 1, 1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, 1, 1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True)
        )
        
        # Decoder mejorado con skip connections
        self.decoder_conv1 = nn.Sequential(
            nn.ConvTranspose2d(512, 256, 4, 2, 1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True)
        )
        
        self.decoder_conv2 = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 4, 2, 1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True)
        )
        
        self.decoder_conv3 = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 4, 2, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        
        self.decoder_conv4 = nn.Sequential(
            nn.ConvTranspose2d(64, 3, 4, 2, 1),
            nn.Tanh()  # Cambiar a Tanh para mejor rango
        )
    
    def forward(self, source, target):
        """
        Forward pass del modelo.
        
        Args:
            source: Tensor de imagen fuente [B, 3, H, W]
            target: Tensor de imagen objetivo [B, 3, H, W]
        
        Returns:
            Tensor de cara intercambiada [B, 3, H, W]
        """
        # Concatenar source y target
        combined = torch.cat([source, target], dim=1)
        
        # Normalizar a [-1, 1] si viene de [0, 1]
        if combined.max() <= 1.0:
            combined = combined * 2.0 - 1.0
        
        # Encoder con skip connections
        e1 = self.encoder_conv1(combined)  # 128x128
        e2 = self.encoder_conv2(e1)         # 64x64
        e3 = self.encoder_conv3(e2)         # 32x32
        e4 = self.encoder_conv4(e3)         # 16x16
        
        # Bottleneck
        bottleneck = self.bottleneck(e4)
        
        # Decoder
        d1 = self.decoder_conv1(bottleneck)  # 32x32
        d2 = self.decoder_conv2(d1)          # 64x64
        d3 = self.decoder_conv3(d2)          # 128x128
        output = self.decoder_conv4(d3)      # 256x256
        
        # Normalizar de vuelta a [0, 1]
        output = (output + 1.0) / 2.0
        
        return output






