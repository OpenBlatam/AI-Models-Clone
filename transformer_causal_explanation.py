"""
ARQUITECTURA DE TRANSFORMERS CAUSALES - Explicación Técnica Clara
==================================================================

Explicación clara y técnica de cómo funciona un modelo causal de transformers,
con pseudocódigo Python detallado y ejemplos paso a paso.

Un transformer causal procesa secuencias de manera autoregresiva:
- Cada token solo puede ver tokens anteriores (no futuros)
- Se usa para generación de lenguaje (GPT, ChatGPT, etc.)
- Permite predecir el siguiente token en una secuencia

AUTOR: Expert AI
FECHA: 2024
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple
from math import sqrt


# ============================================================================
# PARTE 1: EXPLICACIÓN DE COMPONENTES
# ============================================================================

"""
═══════════════════════════════════════════════════════════════════════════
1. EMBEDDINGS DE TOKENS
═══════════════════════════════════════════════════════════════════════════

PROBLEMA: Los tokens son IDs numéricos discretos (ej: "El" = 42, "gato" = 156)
SOLUCIÓN: Convertirlos en vectores continuos densos que capturen significado

CÓMO FUNCIONA:
  - Cada token del vocabulario tiene un vector de d_model dimensiones
  - Estos vectores se aprenden durante el entrenamiento
  - Tokens similares (semánticamente) tienen vectores cercanos

EJEMPLO:
  Input:  [42, 156, 789]  # ["El", "gato", "duerme"]
  Output: [[0.3, -0.1, 0.8, ..., 0.2],     # Embedding de "El"
           [0.2, 0.5, -0.3, ..., 0.1],     # Embedding de "gato"
           [0.1, -0.2, 0.6, ..., -0.3]]   # Embedding de "duerme"
  
  Shape: (seq_len=3, d_model=512)

═══════════════════════════════════════════════════════════════════════════
2. POSITIONAL ENCODING
═══════════════════════════════════════════════════════════════════════════

PROBLEMA: Los embeddings no tienen información de posición
          "El gato" ≠ "gato El" (mismo significado, orden diferente)

SOLUCIÓN: Añadir información explícita de posición a cada token

CÓMO FUNCIONA:
  - Cada posición tiene un encoding único
  - Se suma al embedding del token
  - Puede ser fijo (sinusoidal) o aprendido (embedding)

EJEMPLO:
  Token "El" en posición 0:  embedding + PE[0]
  Token "gato" en posición 1: embedding + PE[1]
  Token "duerme" en posición 2: embedding + PE[2]

RESULTADO: Cada token sabe su posición en la secuencia

═══════════════════════════════════════════════════════════════════════════
3. SELF-ATTENTION
═══════════════════════════════════════════════════════════════════════════

PROPÓSITO: Permitir que cada token "mire" otros tokens relevantes
           para construir una representación contextual rica

ANALOGÍA: Cuando lees "él duerme", automáticamente buscas "él" 
          para saber de quién hablas. Self-attention hace lo mismo.

COMPONENTES:
  - Query (Q): "¿Qué información estoy buscando?"
  - Key (K):   "¿Qué información tengo disponible?"
  - Value (V): "¿Qué información proporciono?"

PROCESO:
  1. Cada token genera Q, K, V:  Q = x·W_Q, K = x·W_K, V = x·W_V
  2. Calcula similitud: scores = Q · K^T / √d_k
  3. Aplica máscara causal (solo tokens anteriores)
  4. Softmax: pesos de atención (probabilidades)
  5. Combina Values: output = pesos · V

FÓRMULA:
  Attention(Q, K, V) = softmax(QK^T / √d_k + Mask) · V

EJEMPLO CONCRETO:
  Secuencia: "El gato duerme"
  
  Token "duerme" (posición 2):
    - Score con "El" (pos 0):    0.2  (baja atención)
    - Score con "gato" (pos 1):  0.7  (alta atención: "gato duerme")
    - Score con "duerme" (pos 2): 0.1  (atención a sí mismo)
  
  Output de "duerme" = 0.2·V_El + 0.7·V_gato + 0.1·V_duerme
  → Ahora contiene información contextual de "gato"

═══════════════════════════════════════════════════════════════════════════
4. MULTI-HEAD ATTENTION
═══════════════════════════════════════════════════════════════════════════

PROPÓSITO: Ejecutar múltiples atenciones en paralelo para capturar
           diferentes tipos de relaciones simultáneamente

CÓMO FUNCIONA:
  - Dividir d_model en n_heads partes (ej: 512 / 8 = 64 por head)
  - Cada head procesa su propia atención en paralelo
  - Concatenar todas las salidas

ESPECIALIZACIÓN:
  Head 1: Relaciones sintácticas (sujeto-verbo)
  Head 2: Relaciones semánticas (sinónimos)
  Head 3: Dependencias a larga distancia (pronombres)
  Head 4: Relaciones de coherencia (conectores)
  ... (cada head aprende diferentes patrones)

VENTAJAS:
  ✅ Paralelismo: todas las heads se calculan simultáneamente
  ✅ Riqueza: más información que una sola atención
  ✅ Especialización: cada head captura diferentes aspectos

═══════════════════════════════════════════════════════════════════════════
5. FEED-FORWARD NETWORK (FFN)
═══════════════════════════════════════════════════════════════════════════

PROPÓSITO: Aplicar transformaciones no lineales a cada posición
           independientemente (no comparte información entre posiciones)

ARQUITECTURA:
  FFN(x) = Activation(x·W_1 + b_1)·W_2 + b_2
  
  - Expansión:  d_model → d_ff  (ej: 512 → 2048, 4x más grande)
  - Activación: GELU o ReLU
  - Contracción: d_ff → d_model  (ej: 2048 → 512)

DIFERENCIA CON ATTENTION:
  - Attention: captura RELACIONES entre tokens (global)
  - FFN: TRANSFORMA información de cada token (local)

EJEMPLO:
  Input:  [token_1, token_2, token_3]
  FFN procesa cada uno independientemente:
    FFN(token_1) → output_1
    FFN(token_2) → output_2
    FFN(token_3) → output_3
  
  No hay interacción entre tokens (a diferencia de attention)

═══════════════════════════════════════════════════════════════════════════
6. LAYER NORMALIZATION
═══════════════════════════════════════════════════════════════════════════

PROPÓSITO: Normalizar activaciones para estabilizar el entrenamiento
           y acelerar la convergencia

FÓRMULA:
  μ = mean(x)  # Media sobre features
  σ² = var(x)   # Varianza
  LayerNorm(x) = γ · (x - μ) / (√(σ² + ε)) + β
  
  Donde γ, β son parámetros aprendibles

EFECTO:
  - Normaliza la distribución de activaciones
  - Permite learning rates más altos
  - Facilita entrenamiento de redes profundas

ARQUITECTURA PRE-LN (recomendada):
  x → LayerNorm → Attention → + x (residual)
  x → LayerNorm → FFN → + x (residual)

═══════════════════════════════════════════════════════════════════════════
7. RESIDUAL CONNECTIONS
═══════════════════════════════════════════════════════════════════════════

PROPÓSITO: Permitir que la información fluya directamente,
           evitando desvanecimiento de gradientes

FÓRMULA:
  output = input + sublayer(LayerNorm(input))

FLUJO DE GRADIENTES:
  ∂L/∂input = ∂L/∂output · (1 + ∂sublayer/∂input)
  
  El "1" permite que el gradiente fluya directamente,
  incluso si la subcapa no aprende nada útil.

VENTAJAS:
  ✅ Evita vanishing gradients en redes profundas
  ✅ Permite aprender funciones identidad fácilmente
  ✅ Facilita refinamientos incrementales

EJEMPLO:
  Si sublayer aprende output ≈ 0:
    output = input + 0 = input  (función identidad)
  → El modelo puede decidir cuánto transformar en cada capa

═══════════════════════════════════════════════════════════════════════════
8. MÁSCARA CAUSAL
═══════════════════════════════════════════════════════════════════════════

PROPÓSITO: Bloquear atención a tokens futuros (solo ver anteriores)

IMPLEMENTACIÓN:
  Máscara triangular inferior:
    mask[i][j] = 0    si j ≤ i  (permite atención)
    mask[i][j] = -∞  si j > i  (bloquea atención futura)

VISUALIZACIÓN (seq_len=4):
  [  0,  -∞,  -∞,  -∞]  ← token 0: solo se ve a sí mismo
  [  0,   0,  -∞,  -∞]  ← token 1: ve tokens 0, 1
  [  0,   0,   0,  -∞]  ← token 2: ve tokens 0, 1, 2
  [  0,   0,   0,   0]  ← token 3: ve todos los anteriores

APLICACIÓN:
  scores = QK^T / √d_k
  scores_masked = scores + mask  # -∞ bloquea futuros
  attention_weights = softmax(scores_masked)  # -∞ → probabilidad 0

POR QUÉ ES NECESARIA:
  - Permite generación autoregresiva (predecir siguiente token)
  - Evita "hacer trampa" usando información del futuro
  - Esencial para modelos de lenguaje (GPT, ChatGPT)
"""


# ============================================================================
# PARTE 2: IMPLEMENTACIÓN EN PSEUDOCÓDIGO
# ============================================================================

class PositionalEncoding(nn.Module):
    """Añade información de posición a los embeddings."""
    
    def __init__(self, d_model: int, max_seq_len: int, learned: bool = True):
        super().__init__()
        if learned:
            # Learned embeddings (más común en GPT)
            self.pos_embedding = nn.Embedding(max_seq_len, d_model)
        else:
            # Sinusoidal (original Transformer)
            pe = self._create_sinusoidal_pe(max_seq_len, d_model)
            self.register_buffer('pe', pe)
    
    def _create_sinusoidal_pe(self, max_seq_len: int, d_model: int) -> torch.Tensor:
        """Crea positional encoding sinusoidal."""
        pe = torch.zeros(max_seq_len, d_model)
        position = torch.arange(0, max_seq_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                            (-torch.log(torch.tensor(10000.0)) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe.unsqueeze(0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (batch, seq_len, d_model) → (batch, seq_len, d_model)"""
        seq_len = x.shape[1]
        if hasattr(self, 'pos_embedding'):
            positions = torch.arange(seq_len, device=x.device)
            return x + self.pos_embedding(positions).unsqueeze(0)
        else:
            return x + self.pe[:, :seq_len, :]


class CausalMultiHeadAttention(nn.Module):
    """
    Multi-Head Self-Attention con máscara causal.
    
    Proceso paso a paso:
    1. Proyecciones Q, K, V
    2. Reshape para multi-head
    3. Calcular scores de atención
    4. Aplicar máscara causal
    5. Softmax → pesos de atención
    6. Aplicar a Values
    7. Concatenar heads
    8. Proyección final
    """
    
    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % n_heads == 0
        
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads  # Dimensión por head
        
        # Proyecciones lineales
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        self.scale = 1.0 / sqrt(self.d_k)
    
    def create_causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """Máscara triangular inferior: bloquea tokens futuros."""
        mask = torch.triu(torch.ones(seq_len, seq_len, device=device), diagonal=1)
        return mask.masked_fill(mask == 1, float('-inf'))
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        x: (batch, seq_len, d_model)
        → output: (batch, seq_len, d_model)
        → attention_weights: (batch, n_heads, seq_len, seq_len)
        """
        batch_size, seq_len, _ = x.shape
        
        # 1. Proyecciones Q, K, V
        Q = self.W_q(x)  # (batch, seq_len, d_model)
        K = self.W_k(x)
        V = self.W_v(x)
        
        # 2. Reshape para multi-head
        # Dividir d_model en n_heads partes de tamaño d_k
        Q = Q.view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        # Ahora: (batch, n_heads, seq_len, d_k)
        
        # 3. Calcular scores de atención
        # Q @ K^T: similitud entre cada par de tokens
        scores = torch.matmul(Q, K.transpose(-2, -1)) * self.scale
        # scores: (batch, n_heads, seq_len, seq_len)
        
        # 4. Aplicar máscara causal
        causal_mask = self.create_causal_mask(seq_len, x.device)
        scores = scores.masked_fill(causal_mask == float('-inf'), float('-inf'))
        # Cada token solo puede atender a tokens anteriores
        
        # 5. Softmax → pesos de atención (probabilidades)
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # 6. Aplicar atención a Values
        # Combinación ponderada de Values según pesos de atención
        attn_output = torch.matmul(attention_weights, V)
        # attn_output: (batch, n_heads, seq_len, d_k)
        
        # 7. Concatenar todas las heads
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(batch_size, seq_len, self.d_model)
        # (batch, seq_len, d_model)
        
        # 8. Proyección final
        output = self.W_o(attn_output)
        
        return output, attention_weights


class FeedForwardNetwork(nn.Module):
    """Feed-Forward Network: transformación no lineal por posición."""
    
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.activation = nn.GELU()
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch, seq_len, d_model)
        → (batch, seq_len, d_model)
        """
        # Expansión: d_model → d_ff
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
    
    Arquitectura Pre-LN:
    x → LayerNorm → Attention → + x → LayerNorm → FFN → + x → output
    """
    
    def __init__(self, d_model: int, n_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.attention = CausalMultiHeadAttention(d_model, n_heads, dropout)
        self.ffn = FeedForwardNetwork(d_model, d_ff, dropout)
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Procesa input a través del bloque transformer.
        
        x: (batch, seq_len, d_model)
        → (batch, seq_len, d_model)
        """
        # SUB-BLOQUE 1: Multi-Head Attention
        # Pre-LN: normalizar antes de atención
        x_norm = self.ln1(x)
        attn_output, _ = self.attention(x_norm)
        attn_output = self.dropout(attn_output)
        
        # Residual connection
        x = x + attn_output
        
        # SUB-BLOQUE 2: Feed-Forward Network
        # Pre-LN: normalizar antes de FFN
        x_norm = self.ln2(x)
        ffn_output = self.ffn(x_norm)
        ffn_output = self.dropout(ffn_output)
        
        # Residual connection
        x = x + ffn_output
        
        return x


# ============================================================================
# PARTE 3: EJEMPLO PASO A PASO - CÓMO UN BLOQUE PROCESA UN INPUT
# ============================================================================

def ejemplo_procesamiento_bloque_transformer():
    """
    Ejemplo detallado paso a paso de cómo un bloque Transformer
    procesa un input.
    """
    print("="*70)
    print("EJEMPLO: CÓMO UN BLOQUE TRANSFORMER PROCESA UN INPUT")
    print("="*70)
    
    # Configuración
    batch_size = 1
    seq_len = 4
    d_model = 128
    n_heads = 4
    d_k = d_model // n_heads
    d_ff = 512
    
    print(f"\n📋 CONFIGURACIÓN:")
    print(f"   Secuencia: {seq_len} tokens")
    print(f"   d_model: {d_model}")
    print(f"   n_heads: {n_heads}")
    print(f"   d_k: {d_k} (dimensiones por head)")
    print(f"   d_ff: {d_ff}")
    
    # Simular input (en práctica vendría de embeddings + positional encoding)
    x = torch.randn(batch_size, seq_len, d_model)
    print(f"\n🔤 INPUT:")
    print(f"   Shape: {x.shape}")
    print(f"   Representa embeddings de {seq_len} tokens")
    print(f"   Cada token tiene {d_model} dimensiones")
    
    # Crear bloque transformer
    block = TransformerBlock(d_model, n_heads, d_ff, dropout=0.0)
    
    print(f"\n{'='*70}")
    print("PROCESAMIENTO PASO A PASO:")
    print(f"{'='*70}")
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 1: Layer Normalization
    # ──────────────────────────────────────────────────────────────────────
    print(f"\n1️⃣  LAYER NORMALIZATION (Pre-LN)")
    print(f"   ───────────────────────────────────")
    x_norm = block.ln1(x)
    print(f"   Input:  {x.shape}")
    print(f"   Output: {x_norm.shape}")
    print(f"   ✓ Normaliza cada token sobre su dimensión de features")
    print(f"   ✓ Estabiliza la distribución de activaciones")
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 2: Multi-Head Attention - Proyecciones Q, K, V
    # ──────────────────────────────────────────────────────────────────────
    print(f"\n2️⃣  MULTI-HEAD SELF-ATTENTION")
    print(f"   ───────────────────────────────────")
    
    print(f"\n   a) Proyecciones Q, K, V:")
    Q = block.attention.W_q(x_norm)
    K = block.attention.W_k(x_norm)
    V = block.attention.W_v(x_norm)
    print(f"      Q shape: {Q.shape}")
    print(f"      K shape: {K.shape}")
    print(f"      V shape: {V.shape}")
    print(f"      ✓ Cada token genera su propio Q, K, V")
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 3: Reshape para multi-head
    # ──────────────────────────────────────────────────────────────────────
    print(f"\n   b) Reshape para {n_heads} heads:")
    Q_reshaped = Q.view(batch_size, seq_len, n_heads, d_k).transpose(1, 2)
    print(f"      Q reshaped: {Q_reshaped.shape}")
    print(f"      ✓ Dividimos d_model={d_model} en {n_heads} heads de {d_k} dims cada una")
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 4: Calcular scores de atención
    # ──────────────────────────────────────────────────────────────────────
    print(f"\n   c) Calcular scores de atención:")
    K_reshaped = K.view(batch_size, seq_len, n_heads, d_k).transpose(1, 2)
    scores = torch.matmul(Q_reshaped, K_reshaped.transpose(-2, -1)) / sqrt(d_k)
    print(f"      Scores shape: {scores.shape}")
    print(f"      ✓ Matriz de atención: cada fila es un token, cada columna es a quién atiende")
    print(f"      ✓ scores[i][j] = qué tan similar es el token i con el token j")
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 5: Aplicar máscara causal
    # ──────────────────────────────────────────────────────────────────────
    print(f"\n   d) Aplicar máscara causal:")
    mask = block.attention.create_causal_mask(seq_len, x.device)
    print(f"      Máscara shape: {mask.shape}")
    print(f"      ✓ Token 0 puede atender a: posición 0")
    print(f"      ✓ Token 1 puede atender a: posiciones 0, 1")
    print(f"      ✓ Token 2 puede atender a: posiciones 0, 1, 2")
    print(f"      ✓ Token 3 puede atender a: posiciones 0, 1, 2, 3")
    print(f"      ✓ Bloquea atención a tokens futuros")
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 6: Ejecutar atención completa
    # ──────────────────────────────────────────────────────────────────────
    print(f"\n   e) Softmax y aplicar a Values:")
    attn_output, attn_weights = block.attention(x_norm)
    print(f"      Attention output shape: {attn_output.shape}")
    print(f"      Attention weights shape: {attn_weights.shape}")
    print(f"      ✓ Cada token ahora contiene información contextual")
    print(f"      ✓ Los pesos indican qué tan relevante es cada token anterior")
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 7: Residual connection
    # ──────────────────────────────────────────────────────────────────────
    print(f"\n3️⃣  RESIDUAL CONNECTION")
    print(f"   ───────────────────────────────────")
    x_after_attn = x + attn_output
    print(f"   x = x + attention_output")
    print(f"   Shape: {x_after_attn.shape}")
    print(f"   ✓ Permite que información fluya directamente")
    print(f"   ✓ Evita desvanecimiento de gradientes")
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 8: Feed-Forward Network
    # ──────────────────────────────────────────────────────────────────────
    print(f"\n4️⃣  FEED-FORWARD NETWORK")
    print(f"   ───────────────────────────────────")
    x_norm2 = block.ln2(x_after_attn)
    ffn_output = block.ffn(x_norm2)
    print(f"   Expansión: {d_model} → {d_ff}")
    print(f"   Activación: GELU")
    print(f"   Contracción: {d_ff} → {d_model}")
    print(f"   FFN output shape: {ffn_output.shape}")
    print(f"   ✓ Transformación no lineal por posición")
    print(f"   ✓ Cada token se procesa independientemente")
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 9: Residual connection final
    # ──────────────────────────────────────────────────────────────────────
    print(f"\n5️⃣  RESIDUAL CONNECTION FINAL")
    print(f"   ───────────────────────────────────")
    x_final = x_after_attn + ffn_output
    print(f"   x = x + ffn_output")
    print(f"   Output shape: {x_final.shape}")
    
    # ──────────────────────────────────────────────────────────────────────
    # RESULTADO FINAL
    # ──────────────────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("PROCESAMIENTO COMPLETO CON BLOQUE TRANSFORMER:")
    print(f"{'='*70}")
    output = block(x)
    print(f"\n✅ Input:  {x.shape}")
    print(f"✅ Output: {output.shape}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   Cada token ahora tiene:")
    print(f"   ✓ Información contextual de todos los tokens anteriores")
    print(f"   ✓ Representación semántica enriquecida")
    print(f"   ✓ Listo para ser procesado por el siguiente bloque")
    print(f"   ✓ O para ser usado en predicción del siguiente token")
    
    return output


def visualizar_mascara_causal():
    """Visualiza cómo funciona la máscara causal."""
    print("\n" + "="*70)
    print("VISUALIZACIÓN: MÁSCARA CAUSAL")
    print("="*70)
    
    seq_len = 5
    print(f"\nMáscara causal para secuencia de longitud {seq_len}:")
    print(f"(✓ = permite atención, X = bloquea atención)")
    print()
    
    for i in range(seq_len):
        row = []
        for j in range(seq_len):
            if j <= i:
                row.append("  ✓  ")
            else:
                row.append("  X  ")
        print(f"Token {i}: {' '.join(row)}")
        print(f"         ↑ puede atender a estas posiciones")
    
    print("\n📝 Interpretación:")
    print("  - Token 0: Solo se ve a sí mismo")
    print("  - Token 1: Ve tokens 0 y 1 (contexto limitado)")
    print("  - Token 2: Ve tokens 0, 1, 2 (más contexto)")
    print("  - Token 3: Ve tokens 0, 1, 2, 3 (contexto completo hasta ahora)")
    print("  - Token 4: Ve todos los tokens anteriores (máximo contexto)")


def diagrama_flujo_completo():
    """Diagrama del flujo completo."""
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
    │  │ Multi-Head Attention           │  │
    │  │ + Residual                     │  │
    │  │ LayerNorm                      │  │
    │  │ Feed-Forward                   │  │
    │  │ + Residual                     │  │
    │  └───────────────────────────────┘  │
    └─────────────────────────────────────┘
           │
           ▼
           ... (N bloques más)
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
    │  [batch, seq_len, vocab_size]        │
    └─────────────────────────────────────┘
           │
           ▼
    OUTPUT: Logits [batch, seq_len, vocab_size]
    """
    
    print(diagrama)


# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ARQUITECTURA DE TRANSFORMERS CAUSALES")
    print("Explicación Técnica Clara con Ejemplos")
    print("="*70)
    
    # Ejecutar ejemplos
    ejemplo_procesamiento_bloque_transformer()
    visualizar_mascara_causal()
    diagrama_flujo_completo()
    
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    print("""
    COMPONENTES CLAVE:
    
    1. EMBEDDINGS: Tokens discretos → vectores continuos densos
    2. POSITIONAL ENCODING: Información de posición
    3. SELF-ATTENTION: Relaciones entre tokens (causal: solo anteriores)
    4. MULTI-HEAD: Múltiples atenciones en paralelo
    5. FEED-FORWARD: Transformación no lineal por posición
    6. LAYER NORM: Normalización para estabilidad
    7. RESIDUALS: Conexiones directas para flujo de información
    8. MÁSCARA CAUSAL: Bloquea atención a tokens futuros
    
    FLUJO:
    Tokens → Embeddings → + PE → [Bloque Transformer]×N → Logits
    
    VENTAJAS:
    ✅ Paralelismo: procesa toda la secuencia simultáneamente
    ✅ Contexto: cada token ve toda la secuencia anterior
    ✅ Escalabilidad: modelos profundos (muchos bloques)
    ✅ Generación autoregresiva: predice siguiente token
    """)


# ============================================================================
# PARTE 4: CONTENIDO ADICIONAL - DETALLES MATEMÁTICOS Y AVANZADOS
# ============================================================================

def detalles_matematicos_completos():
    """Explicación detallada de las fórmulas matemáticas."""
    print("\n" + "="*70)
    print("DETALLES MATEMÁTICOS COMPLETOS")
    print("="*70)
    
    formulas = """
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 1. SELF-ATTENTION - Fórmula Completa                                │
    └─────────────────────────────────────────────────────────────────────┘
    
    Para cada token i en la secuencia:
    
    Q_i = x_i · W_Q    # Query: qué información busca el token i
    K_i = x_i · W_K    # Key: qué información tiene el token i
    V_i = x_i · W_V    # Value: qué información proporciona el token i
    
    Scores de atención:
    score_{i,j} = (Q_i · K_j^T) / √d_k
    
    Pesos de atención (con máscara causal):
    attn_{i,j} = softmax(score_{i,j} + mask_{i,j})
    
    Donde mask_{i,j} = 0 si j ≤ i, -∞ si j > i
    
    Output:
    output_i = Σ_j (attn_{i,j} · V_j)
    
    Matricialmente:
    Attention(Q, K, V) = softmax(QK^T / √d_k + Mask) · V
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 2. MULTI-HEAD ATTENTION - Procesamiento Paralelo                    │
    └─────────────────────────────────────────────────────────────────────┘
    
    Para cada head h ∈ [1, n_heads]:
    
    Q^h = X · W_Q^h    # d_model → d_k por head
    K^h = X · W_K^h
    V^h = X · W_V^h
    
    Attention^h = Attention(Q^h, K^h, V^h)
    
    Concatenación:
    MultiHead = Concat(Attention^1, ..., Attention^n_heads) · W_O
    
    Dimensión: Cada head procesa d_k = d_model / n_heads dimensiones
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 3. FEED-FORWARD NETWORK - Transformación No Lineal                  │
    └─────────────────────────────────────────────────────────────────────┘
    
    FFN(x) = GELU(x · W_1 + b_1) · W_2 + b_2
    
    Donde:
    - W_1: (d_model, d_ff) - Expansión
    - W_2: (d_ff, d_model) - Contracción
    - d_ff típicamente = 4 × d_model
    
    Variante GELU:
    GELU(x) = x · Φ(x) donde Φ es la función de distribución normal
    
    Aproximación: GELU(x) ≈ 0.5x(1 + tanh(√(2/π)(x + 0.044715x³)))
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 4. LAYER NORMALIZATION - Normalización de Features                  │
    └─────────────────────────────────────────────────────────────────────┘
    
    Para cada token x de d_model dimensiones:
    
    μ = (1/d_model) · Σ_{i=1}^{d_model} x_i
    σ² = (1/d_model) · Σ_{i=1}^{d_model} (x_i - μ)²
    
    LayerNorm(x) = γ · (x - μ) / (√(σ² + ε)) + β
    
    Donde:
    - γ: parámetro de escala aprendible
    - β: parámetro de desplazamiento aprendible
    - ε: pequeño valor (1e-5) para estabilidad numérica
    
    Normaliza sobre la dimensión de features, NO sobre la secuencia.
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 5. RESIDUAL CONNECTIONS - Flujo de Gradientes                       │
    └─────────────────────────────────────────────────────────────────────┘
    
    output = x + sublayer(LayerNorm(x))
    
    Gradiente:
    ∂L/∂x = ∂L/∂output · (1 + ∂sublayer/∂x)
    
    Ventajas:
    - El término "1" permite que el gradiente fluya directamente
    - Evita desvanecimiento de gradientes en redes profundas
    - Permite que sublayer aprenda refinamientos incrementales
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 6. POSITIONAL ENCODING SINUSOIDAL                                   │
    └─────────────────────────────────────────────────────────────────────┘
    
    PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
    PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
    
    Donde:
    - pos: posición del token en la secuencia
    - i: índice de la dimensión (0 ≤ i < d_model/2)
    - 10000: base de frecuencia (permite diferentes escalas)
    
    Propiedades:
    - Frecuencias diferentes para cada dimensión
    - Permite extrapolación a secuencias más largas
    - Relaciones relativas: PE(pos+k) puede expresarse en términos de PE(pos)
    """
    
    print(formulas)


def analisis_complejidad_computacional():
    """Análisis de complejidad computacional."""
    print("\n" + "="*70)
    print("ANÁLISIS DE COMPLEJIDAD COMPUTACIONAL")
    print("="*70)
    
    analisis = """
    NOTACIÓN:
    - n: longitud de la secuencia (seq_len)
    - d: dimensión del modelo (d_model)
    - h: número de heads (n_heads)
    - d_k: dimensión por head (d / h)
    - d_ff: dimensión del FFN (típicamente 4d)
    - b: batch size
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ COMPONENTE                    │ COMPLEJIDAD TEMPORAL                │
    └─────────────────────────────────────────────────────────────────────┘
    
    1. Token Embeddings:            O(n · d)
       - Lookup simple: O(1) por token
    
    2. Positional Encoding:          O(n · d)
       - Suma elemento a elemento
    
    3. Self-Attention (una head):   O(n² · d)
       - QK^T: O(n² · d_k)
       - Softmax: O(n²)
       - Attention · V: O(n² · d_k)
    
    4. Multi-Head Attention:        O(n² · d)
       - Misma complejidad que single-head (paralelo)
       - Dividido en h heads: O(n² · d_k) por head
    
    5. Feed-Forward Network:         O(n · d · d_ff)
       - Primera capa: O(n · d · d_ff)
       - Segunda capa: O(n · d_ff · d)
       - Total: O(n · d · d_ff) ≈ O(n · d²) si d_ff = 4d
    
    6. Layer Normalization:          O(n · d)
       - Media y varianza: O(n · d)
       - Normalización: O(n · d)
    
    7. Bloque Transformer completo: O(n² · d + n · d²)
       - Attention: O(n² · d) domina para n << d
       - FFN: O(n · d²) domina para n >> d
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ COMPLEJIDAD ESPACIAL (Memoria)                                       │
    └─────────────────────────────────────────────────────────────────────┘
    
    - Attention weights: O(n²) por head → O(h · n²) total
    - Activaciones: O(b · n · d)
    - Gradientes: O(b · n · d) (mismo tamaño que activaciones)
    
    CUENTO DE PARÁMETROS:
    
    - Token Embedding: vocab_size · d
    - Positional Embedding: max_seq_len · d
    - Attention (Q, K, V, O): 4 · d²
    - FFN: 2 · d · d_ff = 8 · d² (si d_ff = 4d)
    - Layer Norm: 2 · d (γ, β)
    
    Por bloque: ~12d² parámetros
    Modelo completo: vocab_size · d + n_layers · 12d²
    
    EJEMPLO (GPT-3 Small):
    - d = 768, n_layers = 12, vocab_size = 50,000
    - Parámetros ≈ 50k · 768 + 12 · 12 · 768² ≈ 125M parámetros
    """
    
    print(analisis)


def ejemplo_numerico_detallado():
    """Ejemplo numérico paso a paso con valores concretos."""
    print("\n" + "="*70)
    print("EJEMPLO NUMÉRICO DETALLADO")
    print("="*70)
    
    ejemplo = """
    CONFIGURACIÓN:
    - Secuencia: "El gato está durmiendo"
    - Vocabulario: 10,000 tokens
    - d_model = 512
    - n_heads = 8
    - d_k = 512 / 8 = 64 (por head)
    - d_ff = 2048
    - n_layers = 6
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ PASO 1: TOKENIZACIÓN                                               │
    └─────────────────────────────────────────────────────────────────────┘
    
    Texto: "El gato está durmiendo"
    Tokens: [42, 156, 789, 234, 567]
           [El, gato, está, durmiendo, <EOS>]
    
    Shape: (1, 5)  # batch_size=1, seq_len=5
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ PASO 2: TOKEN EMBEDDINGS                                           │
    └─────────────────────────────────────────────────────────────────────┘
    
    Embedding matrix: (10000, 512)
    
    Token 42 ("El"):
    embedding = [0.3, -0.1, 0.8, ..., 0.2]  # 512 dimensiones
    
    Token 156 ("gato"):
    embedding = [0.2, 0.5, -0.3, ..., 0.1]  # 512 dimensiones
    
    Resultado: (1, 5, 512)
    - Cada token es ahora un vector de 512 dimensiones
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ PASO 3: POSITIONAL ENCODING                                         │
    └─────────────────────────────────────────────────────────────────────┘
    
    Posición 0: PE_0 = [sin(0/10000^0), cos(0/10000^0), ...]
    Posición 1: PE_1 = [sin(1/10000^0), cos(1/10000^0), ...]
    ...
    
    Suma: embedding + PE
    Resultado: (1, 5, 512) - cada posición tiene información única
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ PASO 4: MULTI-HEAD ATTENTION (Bloque 1, Head 1)                    │
    └─────────────────────────────────────────────────────────────────────┘
    
    Input: (1, 5, 512)
    
    Proyecciones:
    - W_Q: (512, 512) → Q: (1, 5, 512)
    - W_K: (512, 512) → K: (1, 5, 512)
    - W_V: (512, 512) → V: (1, 5, 512)
    
    Reshape para multi-head:
    - Q: (1, 5, 512) → (1, 8, 5, 64)  # 8 heads, 64 dims cada una
    - K: (1, 5, 512) → (1, 8, 5, 64)
    - V: (1, 5, 512) → (1, 8, 5, 64)
    
    Scores de atención (Head 1):
    QK^T / √64: (1, 8, 5, 5)
    
    Ejemplo para token "está" (posición 2):
    - Score con "El" (pos 0): 0.8
    - Score con "gato" (pos 1): 0.9  (más relevante: "gato está")
    - Score con "está" (pos 2): 0.5  (sí mismo)
    - Score con "durmiendo" (pos 3): -inf (bloqueado por máscara)
    - Score con "<EOS>" (pos 4): -inf (bloqueado)
    
    Softmax:
    - "El": 0.15
    - "gato": 0.70  (mayor atención)
    - "está": 0.15
    
    Output (Head 1):
    output = 0.15·V_El + 0.70·V_gato + 0.15·V_está
    Shape: (1, 8, 5, 64)
    
    Concatenar todas las heads:
    (1, 5, 512)
    
    Proyección final W_O:
    (1, 5, 512)
    
    Residual + LayerNorm:
    output = x + attention_output
    (1, 5, 512)
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ PASO 5: FEED-FORWARD NETWORK                                       │
    └─────────────────────────────────────────────────────────────────────┘
    
    Input: (1, 5, 512)
    
    Primera capa (expansión):
    Linear: (512, 2048)
    Output: (1, 5, 2048)
    
    GELU activation:
    (1, 5, 2048)
    
    Segunda capa (contracción):
    Linear: (2048, 512)
    Output: (1, 5, 512)
    
    Residual + LayerNorm:
    output = x + ffn_output
    (1, 5, 512)
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ PASO 6: BLOQUES ADICIONALES                                         │
    └─────────────────────────────────────────────────────────────────────┘
    
    El mismo proceso se repite para los 6 bloques:
    - Bloque 1: Captura relaciones locales
    - Bloque 2: Captura relaciones más complejas
    - Bloque 3-6: Refina representaciones de alto nivel
    
    Cada bloque refina la representación:
    - Bloque 1 output: Información básica contextual
    - Bloque 6 output: Representación rica y compleja
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ PASO 7: PROYECCIÓN A VOCABULARIO                                   │
    └─────────────────────────────────────────────────────────────────────┘
    
    Input final: (1, 5, 512)
    
    LayerNorm final:
    (1, 5, 512)
    
    Output projection:
    Linear: (512, 10000)
    Output: (1, 5, 10000)
    
    Logits para cada posición:
    - Posición 0 ("El"): [logit_0, logit_1, ..., logit_9999]
    - Posición 1 ("gato"): [logit_0, logit_1, ..., logit_9999]
    ...
    
    Softmax → Probabilidades:
    - Posición 4 (después de "durmiendo"):
      P("profundamente") = 0.45
      P("tranquilamente") = 0.30
      P("<EOS>") = 0.15
      ...
    
    Predicción: Token más probable para siguiente posición.
    """
    
    print(ejemplo)


def comparacion_con_otras_arquitecturas():
    """Comparación con otras arquitecturas de modelos de lenguaje."""
    print("\n" + "="*70)
    print("COMPARACIÓN CON OTRAS ARQUITECTURAS")
    print("="*70)
    
    comparacion = """
    ┌─────────────────────────────────────────────────────────────────────┐
    │ TRANSFORMER vs RNN/LSTM                                              │
    └─────────────────────────────────────────────────────────────────────┘
    
    RNN/LSTM:
    - Procesamiento secuencial: O(n) tiempo, O(1) memoria por paso
    - Complejidad total: O(n) tiempo, pero no paralelizable
    - Problema: Vanishing/Exploding gradients en secuencias largas
    - Contexto: Solo ve tokens anteriores (limitado)
    
    Transformer:
    - Procesamiento paralelo: O(1) tiempo (paralelo), O(n²) memoria
    - Complejidad total: O(n²) tiempo, pero altamente paralelizable
    - Ventaja: Gradientes estables con residual connections
    - Contexto: Ve toda la secuencia anterior simultáneamente
    
    Conclusión: Transformer gana en paralelismo y contexto,
                pero requiere más memoria para secuencias largas.
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ TRANSFORMER CAUSAL vs BIDIRECCIONAL (BERT)                          │
    └─────────────────────────────────────────────────────────────────────┘
    
    Transformer Causal (GPT):
    - Atención solo a tokens anteriores
    - Uso: Generación de lenguaje (autoregresivo)
    - Entrenamiento: Predicción del siguiente token
    - Decodificación: Token por token (lento)
    
    Transformer Bidireccional (BERT):
    - Atención a todos los tokens (sin máscara causal)
    - Uso: Comprensión de lenguaje, clasificación
    - Entrenamiento: Masked Language Modeling (MLM)
    - Decodificación: Toda la secuencia a la vez (rápido)
    
    Diferencias clave:
    - Máscara: Causal vs Full attention
    - Objetivo: Next token prediction vs Masked token prediction
    - Aplicación: Generación vs Comprensión
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ TRANSFORMER vs CONVOLUTIONAL NEURAL NETWORKS                         │
    └─────────────────────────────────────────────────────────────────────┘
    
    CNN:
    - Receptive field fijo (kernel size)
    - Complejidad: O(n · k) donde k es el kernel size
    - Ventaja: Muy eficiente en memoria
    - Desventaja: Receptive field limitado
    
    Transformer:
    - Receptive field: toda la secuencia (en una capa)
    - Complejidad: O(n²)
    - Ventaja: Contexto completo desde el inicio
    - Desventaja: Cuadrático en memoria y tiempo
    
    Compromiso: CNN puede usar dilated convolutions para aumentar
                receptive field, pero sigue siendo limitado.
    """
    
    print(comparacion)


def optimizaciones_avanzadas():
    """Optimizaciones y variantes arquitectónicas modernas."""
    print("\n" + "="*70)
    print("OPTIMIZACIONES Y VARIANTES ARQUITECTÓNICAS")
    print("="*70)
    
    optimizaciones = """
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 1. FLASH ATTENTION (Optimización de Memoria)                        │
    └─────────────────────────────────────────────────────────────────────┘
    
    Problema: Attention tradicional requiere O(n²) memoria para
              almacenar todos los scores antes del softmax.
    
    Solución: Calcular atención en bloques (tiles), evitando almacenar
              toda la matriz de scores.
    
    Ventajas:
    - Reduce memoria de O(n²) a O(n)
    - Permite secuencias más largas
    - Acelera en GPUs modernas
    
    Trade-off: Ligeramente más lento pero mucho más eficiente en memoria.
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 2. SPARSE ATTENTION (Atención Dispersa)                             │
    └─────────────────────────────────────────────────────────────────────┘
    
    Concepto: No todos los tokens necesitan atención completa.
              Algunos patrones de atención pueden ser más eficientes.
    
    Variantes:
    - Local Attention: Solo tokens cercanos
    - Strided Attention: Cada token atiende a tokens con cierto stride
    - Random Attention: Algunos tokens aleatorios
    - Block Sparse: Atención en bloques
    
    Ejemplo (Sparse Transformer):
    - Local: token i atiende a [i-w, i+w]
    - Strided: token i atiende a tokens con stride s
    - Complejidad: O(n√n) en lugar de O(n²)
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 3. ROTARY POSITIONAL EMBEDDING (RoPE)                               │
    └─────────────────────────────────────────────────────────────────────┘
    
    Concepto: En lugar de sumar PE, rotar los embeddings de Q y K
              basándose en la posición.
    
    Ventajas:
    - Mejor extrapolación a secuencias más largas
    - Relaciones relativas más naturales
    - Usado en LLaMA, PaLM
    
    Fórmula:
    R_θ = [[cos(θ), -sin(θ)], [sin(θ), cos(θ)]]
    donde θ depende de la posición y dimensión
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 4. SWIGLU ACTIVATION (FFN Mejorado)                                 │
    └─────────────────────────────────────────────────────────────────────┘
    
    FFN tradicional: ReLU(xW_1 + b_1)W_2 + b_2
    
    SwiGLU: Swish(xW_1 + b_1) ⊙ (xW_2 + b_2)W_3 + b_3
    
    Donde:
    - Swish(x) = x · sigmoid(x)
    - ⊙: producto elemento a elemento (Hadamard)
    - Requiere 3 matrices en lugar de 2, pero mejor rendimiento
    
    Usado en: PaLM, LLaMA
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 5. PRE-LN vs POST-LN                                                │
    └─────────────────────────────────────────────────────────────────────┘
    
    Pre-LN (LayerNorm ANTES):
    x → LN → Attention → + x → LN → FFN → + x
    
    Post-LN (LayerNorm DESPUÉS):
    x → Attention → LN → + x → FFN → LN → + x
    
    Pre-LN (más común en modelos modernos):
    ✅ Gradientes más estables
    ✅ Permite entrenar modelos más profundos
    ✅ Convergencia más rápida
    
    Post-LN (original Transformer):
    ✅ Ligeramente mejor rendimiento en algunos casos
    ❌ Más difícil de entrenar en modelos profundos
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 6. GRADIENT CHECKPOINTING                                           │
    └─────────────────────────────────────────────────────────────────────┘
    
    Problema: Backpropagation requiere almacenar todas las activaciones,
              usando O(n_layers) memoria.
    
    Solución: Guardar solo algunos checkpoints, recalcular el resto
              durante backprop.
    
    Trade-off: Menos memoria, más tiempo de cómputo (recalcular).
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 7. MIXED PRECISION TRAINING                                         │
    └─────────────────────────────────────────────────────────────────────┘
    
    Concepto: Usar float16 para forward pass, float32 para gradientes
              y optimizador.
    
    Ventajas:
    - 2x menos memoria
    - 2x más rápido en GPUs modernas (Tensor Cores)
    
    Implementación: Gradient scaling para evitar underflow.
    """
    
    print(optimizaciones)


def mejores_practicas_implementacion():
    """Mejores prácticas para implementar transformers."""
    print("\n" + "="*70)
    print("MEJORES PRÁCTICAS DE IMPLEMENTACIÓN")
    print("="*70)
    
    practicas = """
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 1. INICIALIZACIÓN DE PESOS                                          │
    └─────────────────────────────────────────────────────────────────────┘
    
    ✅ Embeddings: Normal(0, 0.02)
    ✅ Capas lineales: Normal(0, 0.02)
    ✅ LayerNorm: β=0, γ=1 (inicialización estándar)
    
    Evitar:
    ❌ Inicialización Xavier/Kaiming (no optimizado para transformers)
    ❌ Pesos muy grandes (pueden causar gradientes explosivos)
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 2. ARQUITECTURA PRE-LN vs POST-LN                                   │
    └─────────────────────────────────────────────────────────────────────┘
    
    RECOMENDACIÓN: Pre-LN para modelos profundos
    
    Pre-LN:
    - Más estable para entrenamiento
    - Permite learning rates más altos
    - Mejor para modelos con muchos bloques
    
    Post-LN:
    - Ligeramente mejor rendimiento en algunos casos
    - Más difícil de entrenar
    - Requiere learning rate más bajo
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 3. OPTIMIZACIÓN DE MEMORIA                                          │
    └─────────────────────────────────────────────────────────────────────┘
    
    ✅ Gradient Checkpointing:
       - Guarda solo cada N bloques
       - Recalcula el resto durante backward
       - Trade-off: 33% más tiempo, 50% menos memoria
    
    ✅ Mixed Precision Training:
       - float16 para forward
       - float32 para loss y optimizador
       - Gradient scaling automático
    
    ✅ Flash Attention:
       - Implementación optimizada de atención
       - Reduce memoria de O(n²) a O(n)
    
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 4. DEBUGGING Y TROUBLESHOOTING                                      │
    └─────────────────────────────────────────────────────────────────────┘
    
    Problema común: NaN o Inf en loss
    ✅ Verificar:
       - Inicialización de pesos
       - Learning rate (muy alto → gradientes explosivos)
       - División por cero en layer norm (ε demasiado pequeño)
       - Overflow en softmax (valores muy grandes)
    
    Problema común: Modelo no aprende
    ✅ Verificar:
       - Gradientes fluyen (usar gradient clipping)
       - Learning rate (demasiado bajo)
       - Pre-LN vs Post-LN
       - Warmup de learning rate
    
    Problema común: Out of Memory
    ✅ Soluciones:
       - Reducir batch size
       - Reducir seq_len
       - Gradient checkpointing
       - Mixed precision
       - Model parallelism
    """
    
    print(practicas)


# Actualizar main para incluir todas las nuevas secciones
if __name__ == "__main__":
    print("\n" + "="*70)
    print("ARQUITECTURA DE TRANSFORMERS CAUSALES")
    print("Explicación Técnica Clara con Ejemplos")
    print("="*70)
    
    # Ejecutar ejemplos básicos
    ejemplo_procesamiento_bloque_transformer()
    visualizar_mascara_causal()
    diagrama_flujo_completo()
    
    # Ejecutar contenido adicional
    detalles_matematicos_completos()
    analisis_complejidad_computacional()
    ejemplo_numerico_detallado()
    comparacion_con_otras_arquitecturas()
    optimizaciones_avanzadas()
    mejores_practicas_implementacion()
    
    print("\n" + "="*70)
    print("RESUMEN COMPLETO")
    print("="*70)
    print("""
    COMPONENTES CLAVE:
    
    1. EMBEDDINGS: Tokens discretos → vectores continuos densos
    2. POSITIONAL ENCODING: Información de posición
    3. SELF-ATTENTION: Relaciones entre tokens (causal: solo anteriores)
    4. MULTI-HEAD: Múltiples atenciones en paralelo
    5. FEED-FORWARD: Transformación no lineal por posición
    6. LAYER NORM: Normalización para estabilidad
    7. RESIDUALS: Conexiones directas para flujo de información
    8. MÁSCARA CAUSAL: Bloquea atención a tokens futuros
    
    FLUJO:
    Tokens → Embeddings → + PE → [Bloque Transformer]×N → Logits
    
    COMPLEJIDAD:
    - Tiempo: O(n² · d) para atención, O(n · d²) para FFN
    - Espacio: O(n²) para attention weights, O(n · d) para activaciones
    - Parámetros: ~12d² por bloque + vocab_size · d
    
    OPTIMIZACIONES:
    - Flash Attention: Reduce memoria de O(n²) a O(n)
    - Sparse Attention: Reduce tiempo de O(n²) a O(n√n)
    - Mixed Precision: 2x más rápido, 2x menos memoria
    - Gradient Checkpointing: Menos memoria, más cómputo
    
    VENTAJAS:
    ✅ Paralelismo: procesa toda la secuencia simultáneamente
    ✅ Contexto: cada token ve toda la secuencia anterior
    ✅ Escalabilidad: modelos profundos (muchos bloques)
    ✅ Generación autoregresiva: predice siguiente token
    """)

