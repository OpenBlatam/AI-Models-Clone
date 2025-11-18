"""
ARQUITECTURA DE TRANSFORMERS CAUSALES - Explicación Mejorada
============================================================

Explicación técnica clara y completa de la arquitectura de transformers causales,
con implementación en pseudocódigo Python y ejemplos paso a paso.

Autor: Expert AI
Fecha: 2024
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional
from math import sqrt


# ============================================================================
# PARTE 1: EXPLICACIÓN TÉCNICA DE COMPONENTES
# ============================================================================

"""
┌─────────────────────────────────────────────────────────────────────────────┐
│ ARQUITECTURA DE TRANSFORMERS CAUSALES - COMPONENTES CLAVE                  │
└─────────────────────────────────────────────────────────────────────────────┘

Los transformers causales (como GPT) procesan secuencias de tokens de manera
autoregresiva, donde cada token solo puede usar información de tokens anteriores.

FLUJO GENERAL:
Input Tokens → Embeddings → Positional Encoding → [Bloque Transformer]×N → Output

Cada BLOQUE TRANSFORMER contiene:
  1. Multi-Head Self-Attention (con máscara causal)
  2. Feed-Forward Network
  3. Layer Normalization (Pre-LN)
  4. Residual Connections

───────────────────────────────────────────────────────────────────────────────
1. EMBEDDINGS DE TOKENS
───────────────────────────────────────────────────────────────────────────────

PROPÓSITO: Convertir tokens discretos (IDs numéricos) en vectores continuos densos
             que capturen información semántica.

FUNCIONAMIENTO:
  - Cada token del vocabulario (vocab_size) se mapea a un vector de d_model dimensiones
  - Estos vectores se aprenden durante el entrenamiento
  - Tokens semánticamente similares tienen embeddings cercanos en el espacio vectorial

MATEMÁTICAMENTE:
  E ∈ R^(vocab_size × d_model)  # Matriz de embeddings
  token_embedding = E[token_id]  # Lookup: O(1)

EJEMPLO:
  token_id = 42 ("El") → embedding = [0.3, -0.1, 0.8, ..., 0.2]  (512 dims)
  token_id = 156 ("gato") → embedding = [0.2, 0.5, -0.3, ..., 0.1]  (512 dims)

───────────────────────────────────────────────────────────────────────────────
2. POSITIONAL ENCODING (PE)
───────────────────────────────────────────────────────────────────────────────

PROPÓSITO: Inyectar información sobre la posición de cada token en la secuencia.
           Los transformers no tienen memoria recurrente como RNNs, así que necesitan
           información explícita de posición.

TIPOS:
  a) Sinusoidal (fijo, original Transformer):
     PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
     PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
  
  b) Learned (aprendido, más común en GPT):
     PE = Embedding(max_seq_len, d_model)  # Se aprende durante entrenamiento

APLICACIÓN:
  x_final = token_embedding + positional_encoding
  
  Cada posición tiene un encoding único que permite al modelo distinguir:
  - "El gato" (pos 0, 1) vs "gato El" (pos 1, 0) → orden diferente

───────────────────────────────────────────────────────────────────────────────
3. SELF-ATTENTION (Mecanismo de Atención)
───────────────────────────────────────────────────────────────────────────────

PROPÓSITO: Permitir que cada token "preste atención" a otros tokens relevantes
           para construir representaciones contextuales ricas.

ANALOGÍA: Imagina que estás leyendo un texto. Cuando lees "él", tu cerebro
          automáticamente busca el sustantivo anterior para saber de quién hablas.
          Self-attention hace algo similar.

COMPONENTES:
  - Query (Q): "¿Qué información estoy buscando?"
  - Key (K): "¿Qué información tengo disponible?"
  - Value (V): "¿Qué información proporciono?"

PROCESO PASO A PASO:
  1. Cada token genera Q, K, V mediante proyecciones lineales:
     Q = x · W_Q,  K = x · W_K,  V = x · W_V
  
  2. Calcular scores de similitud:
     scores = Q · K^T / √d_k
  
  3. Aplicar máscara causal (solo tokens anteriores):
     scores_masked = scores + mask_causal
  
  4. Softmax para obtener pesos de atención:
     attention_weights = softmax(scores_masked)
  
  5. Combinar Values ponderados:
     output = attention_weights · V

FÓRMULA MATEMÁTICA:
  Attention(Q, K, V) = softmax(QK^T / √d_k + Mask_causal) · V

PROPIEDADES:
  - Cada token puede atender a múltiples tokens anteriores
  - Los pesos de atención indican qué tan relevante es cada token
  - La división por √d_k evita que scores sean muy grandes (estabiliza softmax)

───────────────────────────────────────────────────────────────────────────────
4. MULTI-HEAD ATTENTION
───────────────────────────────────────────────────────────────────────────────

PROPÓSITO: Ejecutar múltiples atenciones en paralelo, cada una capturando
           diferentes tipos de relaciones.

CONCEPTO:
  En lugar de una sola atención, tenemos n_heads atenciones simultáneas.
  Cada "cabeza" puede especializarse en diferentes aspectos:
  
  Head 1: Relaciones sintácticas (sujeto-verbo, adjetivo-sustantivo)
  Head 2: Relaciones semánticas (sinónimos, antónimos)
  Head 3: Dependencias a larga distancia (pronombres y sus referentes)
  Head 4: Relaciones de coherencia (conectores, transiciones)
  ... (y así sucesivamente)

IMPLEMENTACIÓN:
  1. Dividir d_model en n_heads partes de tamaño d_k = d_model / n_heads
  2. Cada head procesa su propia Q^h, K^h, V^h de dimensión d_k
  3. Calcular atención para cada head: Attention^h(Q^h, K^h, V^h)
  4. Concatenar todas las salidas: Concat(Attention^1, ..., Attention^n_heads)
  5. Proyección final: W_O · Concat(...)

VENTAJAS:
  - Paralelismo: todas las heads se calculan simultáneamente
  - Especialización: cada head aprende diferentes patrones
  - Riqueza: más información capturada que con una sola atención

EJEMPLO:
  d_model = 512, n_heads = 8 → d_k = 64 por head
  Cada head procesa 64 dimensiones, pero captura diferentes relaciones

───────────────────────────────────────────────────────────────────────────────
5. FEED-FORWARD NETWORK (FFN)
───────────────────────────────────────────────────────────────────────────────

PROPÓSITO: Aplicar transformaciones no lineales a cada posición de manera
           independiente, permitiendo que el modelo aprenda funciones complejas.

ARQUITECTURA:
  FFN(x) = Activation(xW_1 + b_1)W_2 + b_2
  
  Donde:
  - W_1: (d_model, d_ff) - Expansión (típicamente d_ff = 4 × d_model)
  - W_2: (d_ff, d_model) - Contracción
  - Activation: GELU (más común) o ReLU

CARACTERÍSTICAS:
  - Expansión: d_model → d_ff (ej: 512 → 2048) - espacio mayor para procesamiento
  - Contracción: d_ff → d_model (ej: 2048 → 512) - vuelve a dimensión original
  - Independiente por posición: cada token se procesa de forma paralela
  - No comparte información entre posiciones (a diferencia de attention)

POR QUÉ FUNCIONA:
  - Attention captura RELACIONES entre tokens (aspecto global)
  - FFN procesa y TRANSFORMA la información de cada token (aspecto local)
  - Juntos: relaciones globales + procesamiento local = representación rica

EJEMPLO:
  Input: [token_1, token_2, token_3]
  FFN procesa cada token independientemente:
    FFN(token_1) → output_1
    FFN(token_2) → output_2
    FFN(token_3) → output_3

───────────────────────────────────────────────────────────────────────────────
6. LAYER NORMALIZATION
───────────────────────────────────────────────────────────────────────────────

PROPÓSITO: Normalizar las activaciones para estabilizar el entrenamiento
           y acelerar la convergencia.

FÓRMULA:
  μ = mean(x)  # Media sobre dimensión de features
  σ² = var(x)   # Varianza sobre dimensión de features
  LayerNorm(x) = γ · (x - μ) / (√(σ² + ε)) + β
  
  Donde:
  - γ, β: parámetros aprendibles (scale y shift)
  - ε: pequeño valor (1e-5) para evitar división por cero

DIFERENCIA CON BATCH NORM:
  - BatchNorm: normaliza sobre el batch y la secuencia
  - LayerNorm: normaliza solo sobre la dimensión de features (por token)

ARQUITECTURAS:
  a) Pre-LN (más común en modelos modernos):
     x → LN → Attention → + x → LN → FFN → + x
     
  b) Post-LN (original Transformer):
     x → Attention → LN → + x → FFN → LN → + x

VENTAJAS DE PRE-LN:
  ✅ Gradientes más estables
  ✅ Permite entrenar modelos más profundos
  ✅ Convergencia más rápida
  ✅ Learning rates más altos

───────────────────────────────────────────────────────────────────────────────
7. RESIDUAL CONNECTIONS (Skip Connections)
───────────────────────────────────────────────────────────────────────────────

PROPÓSITO: Permitir que la información fluya directamente a través de capas,
           facilitando el entrenamiento de redes profundas.

FÓRMULA:
  output = input + sublayer(LayerNorm(input))

FLUJO DE GRADIENTES:
  ∂L/∂input = ∂L/∂output · (1 + ∂sublayer/∂input)
  
  El término "1" permite que el gradiente fluya directamente,
  evitando desvanecimiento de gradientes.

VENTAJAS:
  ✅ Gradiente puede fluir directamente (evita vanishing gradients)
  ✅ Permite que el modelo aprenda funciones identidad fácilmente
  ✅ Facilita aprendizaje de refinamientos incrementales
  ✅ Permite entrenar redes muy profundas (docenas de capas)

EJEMPLO:
  Si una subcapa no necesita hacer nada, puede aprender a hacer output ≈ 0
  Resultado: output = input + 0 = input (función identidad)
  Esto permite que el modelo decida cuánto transformar en cada capa

───────────────────────────────────────────────────────────────────────────────
8. MÁSCARA CAUSAL
───────────────────────────────────────────────────────────────────────────────

PROPÓSITO: En modelos autoregresivos, asegurar que cada token solo pueda
           acceder a información de tokens anteriores (no futuros).

IMPLEMENTACIÓN:
  Máscara triangular inferior:
    mask[i][j] = 0      si j ≤ i  (permite atención)
    mask[i][j] = -∞    si j > i   (bloquea atención futura)

APLICACIÓN:
  scores = QK^T / √d_k
  scores_masked = scores + mask_causal
  attention_weights = softmax(scores_masked)
  
  -∞ en softmax → probabilidad 0 (no atención)

VISUALIZACIÓN (seq_len=4):
  [  0,  -∞,  -∞,  -∞]  ← token 0 solo se ve a sí mismo
  [  0,   0,  -∞,  -∞]  ← token 1 ve tokens 0, 1
  [  0,   0,   0,  -∞]  ← token 2 ve tokens 0, 1, 2
  [  0,   0,   0,   0]  ← token 3 ve todos los tokens anteriores

POR QUÉ ES NECESARIA:
  - Permite generación autoregresiva: predecir siguiente token
  - Evita "hacer trampa": usar información del futuro para predecir presente
  - Esencial para modelos de lenguaje (GPT, ChatGPT, etc.)
"""


# ============================================================================
# PARTE 2: IMPLEMENTACIÓN EN PSEUDOCÓDIGO PYTHON
# ============================================================================

class PositionalEncoding(nn.Module):
    """
    Codificación posicional para transformers.
    
    Puede ser sinusoidal (fija) o aprendida (learned embeddings).
    Para modelos causales, permite distinguir posiciones relativas.
    """
    
    def __init__(self, d_model: int, max_seq_len: int, learned: bool = True):
        super().__init__()
        self.d_model = d_model
        self.learned = learned
        
        if learned:
            # Learned positional embeddings (más común en GPT)
            self.pos_embedding = nn.Embedding(max_seq_len, d_model)
        else:
            # Sinusoidal positional encoding (original Transformer)
            pe = self._create_sinusoidal_pe(max_seq_len, d_model)
            self.register_buffer('pe', pe)
    
    def _create_sinusoidal_pe(self, max_seq_len: int, d_model: int) -> torch.Tensor:
        """Crea positional encoding sinusoidal fijo."""
        pe = torch.zeros(max_seq_len, d_model)
        position = torch.arange(0, max_seq_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                            (-np.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe.unsqueeze(0)  # (1, max_seq_len, d_model)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Añade información posicional a los embeddings.
        
        :param x: Input embeddings de forma (batch_size, seq_len, d_model)
        :return: Embeddings con información posicional añadida
        """
        batch_size, seq_len, _ = x.shape
        
        if self.learned:
            positions = torch.arange(seq_len, device=x.device)
            pos_emb = self.pos_embedding(positions)  # (seq_len, d_model)
            return x + pos_emb.unsqueeze(0)  # Broadcasting
        else:
            return x + self.pe[:, :seq_len, :]


class CausalMultiHeadAttention(nn.Module):
    """
    Multi-Head Self-Attention con máscara causal.
    
    Permite que cada token atienda a todos los tokens anteriores,
    capturando relaciones contextuales de manera eficiente.
    """
    
    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % n_heads == 0, "d_model debe ser divisible por n_heads"
        
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads  # Dimensión por cabeza
        
        # Proyecciones lineales para Q, K, V
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        
        # Proyección de salida (concatena todas las heads)
        self.W_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        self.scale = 1.0 / sqrt(self.d_k)
    
    def create_causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """
        Crea máscara causal triangular inferior.
        
        Máscara[i][j] = 0 si j <= i (permite atención)
        Máscara[i][j] = -inf si j > i (bloquea atención futura)
        """
        mask = torch.triu(torch.ones(seq_len, seq_len, device=device), diagonal=1)
        return mask.masked_fill(mask == 1, float('-inf'))
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass de multi-head attention.
        
        Proceso:
        1. Proyecciones Q, K, V
        2. Reshape para multi-head
        3. Calcular scores de atención
        4. Aplicar máscara causal
        5. Softmax para pesos de atención
        6. Aplicar a Values
        7. Concatenar heads y proyectar
        
        :param x: Input de forma (batch_size, seq_len, d_model)
        :return: Tuple de (output, attention_weights)
        """
        batch_size, seq_len, _ = x.shape
        
        # PASO 1: Proyecciones lineales para Q, K, V
        Q = self.W_q(x)  # (batch, seq_len, d_model)
        K = self.W_k(x)
        V = self.W_v(x)
        
        # PASO 2: Reshape para multi-head
        # Dividir d_model en n_heads partes de tamaño d_k
        Q = Q.view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        # Forma ahora: (batch, n_heads, seq_len, d_k)
        
        # PASO 3: Calcular scores de atención
        # Q @ K^T: Para cada posición, calcula similitud con todas las demás
        scores = torch.matmul(Q, K.transpose(-2, -1)) * self.scale
        # scores: (batch, n_heads, seq_len, seq_len)
        
        # PASO 4: Aplicar máscara causal
        causal_mask = self.create_causal_mask(seq_len, x.device)
        scores = scores.masked_fill(causal_mask == float('-inf'), float('-inf'))
        # Ahora cada posición solo puede atender a posiciones anteriores
        
        # PASO 5: Softmax para obtener pesos de atención
        attention_weights = F.softmax(scores, dim=-1)
        # Normaliza los scores a probabilidades (suma = 1 por fila)
        attention_weights = self.dropout(attention_weights)
        
        # PASO 6: Aplicar atención a Values
        # Multiplicar pesos por Values: combinación ponderada
        attn_output = torch.matmul(attention_weights, V)
        # attn_output: (batch, n_heads, seq_len, d_k)
        
        # PASO 7: Concatenar todas las heads
        attn_output = attn_output.transpose(1, 2).contiguous()
        # (batch, seq_len, n_heads, d_k)
        attn_output = attn_output.view(batch_size, seq_len, self.d_model)
        # (batch, seq_len, d_model) - todas las heads concatenadas
        
        # PASO 8: Proyección de salida
        output = self.W_o(attn_output)
        # (batch, seq_len, d_model)
        
        return output, attention_weights


class FeedForwardNetwork(nn.Module):
    """
    Feed-Forward Network: Transformación no lineal por posición.
    
    Procesa cada posición de manera independiente, aplicando
    transformaciones no lineales complejas.
    """
    
    def __init__(self, d_model: int, d_ff: int, activation: str = "gelu", dropout: float = 0.1):
        super().__init__()
        
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        
        if activation == "gelu":
            self.activation = nn.GELU()
        elif activation == "relu":
            self.activation = nn.ReLU()
        else:
            raise ValueError(f"Activation {activation} no soportada")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass del FFN.
        
        Proceso: Expansión → Activación → Contracción
        
        :param x: Input de forma (batch_size, seq_len, d_model)
        :return: Output de forma (batch_size, seq_len, d_model)
        """
        # Expansión: d_model → d_ff (típicamente 4x)
        x = self.linear1(x)
        x = self.activation(x)
        x = self.dropout(x)
        
        # Contracción: d_ff → d_model
        x = self.linear2(x)
        x = self.dropout(x)
        
        return x


class TransformerBlock(nn.Module):
    """
    Bloque completo de Transformer Causal.
    
    Combina multi-head attention y feed-forward network
    con layer normalization y residual connections.
    
    Arquitectura Pre-LN:
    x → LN → Attention → + x → LN → FFN → + x → output
    """
    
    def __init__(self, d_model: int, n_heads: int, d_ff: int, 
                 dropout: float = 0.1, pre_norm: bool = True):
        super().__init__()
        
        self.pre_norm = pre_norm
        
        # Sub-capas
        self.attention = CausalMultiHeadAttention(d_model, n_heads, dropout)
        self.ffn = FeedForwardNetwork(d_model, d_ff, activation="gelu", dropout=dropout)
        
        # Layer Normalization (Pre-LN: antes de cada subcapa)
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass del bloque Transformer.
        
        Arquitectura Pre-LN:
        x → LN → Attention → + x (residual) → LN → FFN → + x (residual) → output
        
        :param x: Input embeddings de forma (batch_size, seq_len, d_model)
        :return: Output de forma (batch_size, seq_len, d_model)
        """
        # SUB-BLOQUE 1: Multi-Head Self-Attention
        if self.pre_norm:
            # Pre-LN: Normalizar antes de la atención
            x_norm = self.ln1(x)
            attn_output, _ = self.attention(x_norm)
        else:
            # Post-LN: Atención primero, luego normalizar
            attn_output, _ = self.attention(x)
            attn_output = self.ln1(attn_output)
        
        attn_output = self.dropout(attn_output)
        
        # Residual connection: x + attn_output
        x = x + attn_output
        
        # SUB-BLOQUE 2: Feed-Forward Network
        if self.pre_norm:
            # Pre-LN: Normalizar antes del FFN
            x_norm = self.ln2(x)
            ffn_output = self.ffn(x_norm)
        else:
            # Post-LN: FFN primero, luego normalizar
            ffn_output = self.ffn(x)
            ffn_output = self.ln2(ffn_output)
        
        ffn_output = self.dropout(ffn_output)
        
        # Residual connection: x + ffn_output
        x = x + ffn_output
        
        return x


class CausalTransformer(nn.Module):
    """
    Modelo completo de Transformer Causal (estilo GPT).
    
    Arquitectura:
    - Token Embeddings
    - Positional Encoding
    - Stack de N bloques Transformer
    - Layer Normalization final
    - Proyección a vocabulario
    """
    
    def __init__(self, vocab_size: int, d_model: int, n_heads: int,
                 n_layers: int, d_ff: int, max_seq_len: int, 
                 dropout: float = 0.1):
        super().__init__()
        
        self.d_model = d_model
        self.vocab_size = vocab_size
        
        # 1. TOKEN EMBEDDINGS
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        
        # 2. POSITIONAL ENCODING
        self.pos_encoding = PositionalEncoding(d_model, max_seq_len, learned=True)
        
        # 3. STACK DE BLOQUES TRANSFORMER
        self.blocks = nn.ModuleList([
            TransformerBlock(d_model, n_heads, d_ff, dropout)
            for _ in range(n_layers)
        ])
        
        # 4. LAYER NORMALIZATION FINAL
        self.ln_final = nn.LayerNorm(d_model)
        
        # 5. PROYECCIÓN A VOCABULARIO
        self.output_projection = nn.Linear(d_model, vocab_size)
        
        self.dropout = nn.Dropout(dropout)
        
        # Inicialización de pesos
        self._init_weights()
    
    def _init_weights(self):
        """Inicialización de pesos para estabilidad del entrenamiento."""
        nn.init.normal_(self.token_embedding.weight, mean=0.0, std=0.02)
        
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.normal_(module.weight, mean=0.0, std=0.02)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        """
        Forward pass completo del modelo.
        
        Proceso:
        1. Token IDs → Embeddings
        2. + Positional Encoding
        3. Procesar a través de N bloques Transformer
        4. Layer Normalization final
        5. Proyección a vocabulario → Logits
        
        :param token_ids: IDs de tokens de forma (batch_size, seq_len)
        :return: Logits de forma (batch_size, seq_len, vocab_size)
        """
        batch_size, seq_len = token_ids.shape
        
        # PASO 1: TOKEN EMBEDDINGS
        x = self.token_embedding(token_ids)
        # x: (batch_size, seq_len, d_model)
        
        # PASO 2: POSITIONAL ENCODING
        x = self.pos_encoding(x)
        x = self.dropout(x)
        
        # PASO 3: PROCESAR A TRAVÉS DE TODOS LOS BLOQUES
        for block in self.blocks:
            # Cada bloque refina la representación
            x = block(x)
        
        # PASO 4: NORMALIZACIÓN FINAL
        x = self.ln_final(x)
        
        # PASO 5: PROYECCIÓN A VOCABULARIO
        logits = self.output_projection(x)
        # logits: (batch_size, seq_len, vocab_size)
        # logits[i][j][k] = score del token k del vocabulario en posición j
        
        return logits


# ============================================================================
# PARTE 3: EJEMPLO PASO A PASO
# ============================================================================

def ejemplo_procesamiento_bloque():
    """
    Ejemplo detallado de cómo un bloque Transformer procesa un input.
    """
    print("="*70)
    print("EJEMPLO: CÓMO UN BLOQUE TRANSFORMER PROCESA UN INPUT")
    print("="*70)
    
    # Configuración
    batch_size = 1
    seq_len = 4
    d_model = 128
    n_heads = 4
    d_ff = 512
    
    print(f"\n📊 CONFIGURACIÓN:")
    print(f"  - Secuencia: {seq_len} tokens")
    print(f"  - d_model: {d_model}")
    print(f"  - n_heads: {n_heads}")
    print(f"  - d_k: {d_model // n_heads} (por head)")
    print(f"  - d_ff: {d_ff}")
    
    # Simular input (en práctica vendría de embeddings + PE)
    x = torch.randn(batch_size, seq_len, d_model)
    print(f"\n🔤 INPUT:")
    print(f"  Shape: {x.shape}")
    print(f"  Representa embeddings de {seq_len} tokens, cada uno con {d_model} dimensiones")
    
    # Crear bloque transformer
    block = TransformerBlock(d_model, n_heads, d_ff, dropout=0.0)
    
    print(f"\n{'─'*70}")
    print("PROCESAMIENTO PASO A PASO:")
    print(f"{'─'*70}")
    
    # PASO 1: Layer Normalization
    print(f"\n1️⃣  LAYER NORMALIZATION (Pre-LN)")
    print(f"   x_norm = LayerNorm(x)")
    print(f"   Normaliza cada token sobre su dimensión de features")
    x_norm = block.ln1(x)
    print(f"   Shape: {x_norm.shape}")
    
    # PASO 2: Multi-Head Attention
    print(f"\n2️⃣  MULTI-HEAD SELF-ATTENTION")
    print(f"   a) Proyecciones Q, K, V:")
    Q = block.attention.W_q(x_norm)
    K = block.attention.W_k(x_norm)
    V = block.attention.W_v(x_norm)
    print(f"      Q, K, V shape: {Q.shape}")
    
    print(f"   b) Reshape para {n_heads} heads:")
    Q_reshaped = Q.view(batch_size, seq_len, n_heads, d_model // n_heads).transpose(1, 2)
    print(f"      Q reshaped: {Q_reshaped.shape}")
    
    print(f"   c) Calcular scores: Q @ K^T / √d_k")
    scores = torch.matmul(Q_reshaped, K.view(batch_size, seq_len, n_heads, d_model // n_heads)
                          .transpose(1, 2).transpose(-2, -1)) / sqrt(d_model // n_heads)
    print(f"      Scores shape: {scores.shape}")
    print(f"      Matriz de atención: cada fila es un token, cada columna es a quién atiende")
    
    print(f"   d) Aplicar máscara causal:")
    mask = block.attention.create_causal_mask(seq_len, x.device)
    print(f"      Token 0 puede atender a: posición 0")
    print(f"      Token 1 puede atender a: posiciones 0, 1")
    print(f"      Token 2 puede atender a: posiciones 0, 1, 2")
    print(f"      Token 3 puede atender a: posiciones 0, 1, 2, 3")
    
    # Ejecutar atención completa
    attn_output, attn_weights = block.attention(x_norm)
    print(f"   e) Output de atención:")
    print(f"      Shape: {attn_output.shape}")
    print(f"      Cada token ahora contiene información contextual de tokens anteriores")
    
    # PASO 3: Residual + LayerNorm
    print(f"\n3️⃣  RESIDUAL CONNECTION")
    print(f"   x = x + attention_output")
    print(f"   Permite que información fluya directamente")
    x_after_attn = x + attn_output
    print(f"   Shape: {x_after_attn.shape}")
    
    # PASO 4: Feed-Forward
    print(f"\n4️⃣  FEED-FORWARD NETWORK")
    print(f"   Expansión: {d_model} → {d_ff} → {d_model}")
    x_norm2 = block.ln2(x_after_attn)
    ffn_output = block.ffn(x_norm2)
    print(f"   Transformación no lineal por posición")
    print(f"   Shape: {ffn_output.shape}")
    
    # PASO 5: Residual final
    print(f"\n5️⃣  RESIDUAL CONNECTION FINAL")
    print(f"   x = x + ffn_output")
    x_final = x_after_attn + ffn_output
    print(f"   Output final shape: {x_final.shape}")
    
    # Procesar con el bloque completo
    print(f"\n{'─'*70}")
    print("PROCESAMIENTO COMPLETO:")
    print(f"{'─'*70}")
    output = block(x)
    print(f"✅ Input:  {x.shape}")
    print(f"✅ Output: {output.shape}")
    print(f"\nCada token ahora tiene:")
    print(f"  ✓ Información contextual de todos los tokens anteriores")
    print(f"  ✓ Representación semántica enriquecida")
    print(f"  ✓ Listo para ser procesado por el siguiente bloque o para predicción")
    
    return output


def visualizar_mascara_causal():
    """Visualiza cómo funciona la máscara causal."""
    print("\n" + "="*70)
    print("VISUALIZACIÓN: MÁSCARA CAUSAL")
    print("="*70)
    
    seq_len = 5
    mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1)
    mask = mask.masked_fill(mask == 1, float('-inf'))
    mask = mask.masked_fill(mask == 0, 0.0)
    
    print(f"\nMáscara causal para secuencia de longitud {seq_len}:")
    print(f"(0 = permite atención, -inf = bloquea atención)")
    print()
    
    for i in range(seq_len):
        row = []
        for j in range(seq_len):
            if mask[i][j].item() == float('-inf'):
                row.append("  X  ")  # Bloqueado
            else:
                row.append("  ✓  ")  # Permitido
        print(f"Token {i}: {' '.join(row)}")
        print(f"         ↑ puede atender a estas posiciones")
    
    print("\n📝 Interpretación:")
    print("  - Token 0: Solo se ve a sí mismo (primera posición)")
    print("  - Token 1: Ve tokens 0 y 1 (puede usar contexto anterior)")
    print("  - Token 2: Ve tokens 0, 1, 2 (acumula más contexto)")
    print("  - Token 3: Ve tokens 0, 1, 2, 3 (contexto completo hasta ahora)")
    print("  - Token 4: Ve todos los tokens anteriores (máximo contexto)")


def diagrama_flujo_completo():
    """Diagrama del flujo completo de un transformer causal."""
    print("\n" + "="*70)
    print("DIAGRAMA: FLUJO COMPLETO DE TRANSFORMER CAUSAL")
    print("="*70)
    
    diagrama = """
    INPUT: Token IDs [batch, seq_len]
           │
           ▼
    ┌─────────────────────────────────────┐
    │  TOKEN EMBEDDINGS                     │
    │  [batch, seq_len] → [batch, seq_len, │
    │                       d_model]        │
    └─────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  + POSITIONAL ENCODING               │
    │  Añade información de posición       │
    └─────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  BLOQUE TRANSFORMER 1                │
    │  ┌───────────────────────────────┐  │
    │  │ LayerNorm                      │  │
    │  │ ↓                              │  │
    │  │ Multi-Head Self-Attention      │  │
    │  │ - Q, K, V projections          │  │
    │  │ - Causal mask (solo anterior) │  │
    │  │ - n_heads en paralelo          │  │
    │  │ ↓                              │  │
    │  │ + Residual (x + attn_output)  │  │
    │  │ ↓                              │  │
    │  │ LayerNorm                      │  │
    │  │ ↓                              │  │
    │  │ Feed-Forward Network           │  │
    │  │ - Linear: d_model → d_ff       │  │
    │  │ - GELU activation              │  │
    │  │ - Linear: d_ff → d_model      │  │
    │  │ ↓                              │  │
    │  │ + Residual (x + ffn_output)  │  │
    │  └───────────────────────────────┘  │
    └─────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  BLOQUE TRANSFORMER 2                │
    │  (mismo proceso, representación      │
    │   más refinada)                      │
    └─────────────────────────────────────┘
           │
           ▼
           ...
           │
           ▼
    ┌─────────────────────────────────────┐
    │  BLOQUE TRANSFORMER N                │
    └─────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  LAYER NORMALIZATION FINAL          │
    └─────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  OUTPUT PROJECTION                  │
    │  [batch, seq_len, d_model] →        │
    │  [batch, seq_len, vocab_size]       │
    └─────────────────────────────────────┘
           │
           ▼
    OUTPUT: Logits [batch, seq_len, vocab_size]
            (probabilidades de cada token)
    """
    
    print(diagrama)


# ============================================================================
# EJECUCIÓN DEL EJEMPLO
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ARQUITECTURA DE TRANSFORMERS CAUSALES - EXPLICACIÓN MEJORADA")
    print("="*70)
    
    # Ejecutar ejemplos
    ejemplo_procesamiento_bloque()
    visualizar_mascara_causal()
    diagrama_flujo_completo()
    
    print("\n" + "="*70)
    print("RESUMEN TÉCNICO")
    print("="*70)
    print("""
    COMPONENTES CLAVE:
    
    1. EMBEDDINGS: Tokens discretos → vectores continuos densos
    2. POSITIONAL ENCODING: Información de posición en la secuencia
    3. SELF-ATTENTION: Relaciones entre tokens (causal: solo anteriores)
    4. MULTI-HEAD: Múltiples atenciones en paralelo (diferentes aspectos)
    5. FEED-FORWARD: Transformación no lineal por posición
    6. LAYER NORM: Normalización para estabilidad
    7. RESIDUALS: Conexiones directas para flujo de información
    8. MÁSCARA CAUSAL: Bloquea atención a tokens futuros
    
    PROPÓSITO:
    - Cada token adquiere representación contextual rica
    - Captura dependencias a larga distancia
    - Permite generación autoregresiva (GPT-style)
    - Procesamiento paralelo eficiente
    
    VENTAJAS:
    ✅ Paralelismo: procesa toda la secuencia simultáneamente
    ✅ Contexto: cada token ve toda la secuencia anterior
    ✅ Escalabilidad: modelos profundos (muchos bloques)
    ✅ Eficiencia: atención es más eficiente que RNNs para secuencias largas
    
    COMPLEJIDAD:
    - Tiempo: O(n² · d) para atención, O(n · d²) para FFN
    - Espacio: O(n²) para attention weights, O(n · d) para activaciones
    - Parámetros: ~12d² por bloque + vocab_size · d
    """)

