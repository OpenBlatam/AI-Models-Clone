"""
ARQUITECTURA DE TRANSFORMERS CAUSALES - Guía Técnica Completa
==============================================================

Explicación clara y técnica de la arquitectura de transformers causales,
con pseudocódigo Python detallado y ejemplos paso a paso.

Autor: Expert AI
Fecha: 2024
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple
from math import sqrt


# ============================================================================
# PARTE 1: EXPLICACIÓN TÉCNICA DE COMPONENTES
# ============================================================================

"""
═══════════════════════════════════════════════════════════════════════════
ARQUITECTURA DE TRANSFORMERS CAUSALES
═══════════════════════════════════════════════════════════════════════════

Los transformers causales (GPT, ChatGPT) procesan secuencias autoregresivamente:
- Cada token solo puede ver tokens anteriores (máscara causal)
- Se usan para generación de lenguaje
- Permiten predecir el siguiente token en una secuencia

FLUJO GENERAL:
Tokens → Embeddings → + Positional Encoding → [Bloque Transformer]×N → Logits

Cada BLOQUE TRANSFORMER contiene:
  1. Multi-Head Self-Attention (con máscara causal)
  2. Feed-Forward Network
  3. Layer Normalization (Pre-LN)
  4. Residual Connections

═══════════════════════════════════════════════════════════════════════════
1. EMBEDDINGS DE TOKENS
═══════════════════════════════════════════════════════════════════════════

PROBLEMA: Tokens son IDs numéricos discretos (ej: "El"=42, "gato"=156)
SOLUCIÓN: Convertirlos en vectores continuos densos que capturen significado

CÓMO FUNCIONA:
  - Matriz de embeddings: E ∈ R^(vocab_size × d_model)
  - Cada token se mapea a un vector de d_model dimensiones
  - Estos vectores se aprenden durante el entrenamiento
  - Tokens semánticamente similares tienen vectores cercanos

EJEMPLO:
  Input:  [42, 156]  # ["El", "gato"]
  Output: [[0.3, -0.1, 0.8, ..., 0.2],  # Embedding de "El" (512 dims)
           [0.2, 0.5, -0.3, ..., 0.1]]  # Embedding de "gato" (512 dims)
  
  Shape: (seq_len=2, d_model=512)

═══════════════════════════════════════════════════════════════════════════
2. POSITIONAL ENCODING
═══════════════════════════════════════════════════════════════════════════

PROBLEMA: Los embeddings no tienen información de posición
          "El gato" ≠ "gato El" (mismo significado, orden diferente)

SOLUCIÓN: Añadir información explícita de posición a cada token

TIPOS:
  a) Sinusoidal (fijo):
     PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
     PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
  
  b) Learned (aprendido, más común en GPT):
     PE = Embedding(max_seq_len, d_model)

APLICACIÓN:
  x_final = token_embedding + positional_encoding
  
  Cada posición tiene un encoding único

═══════════════════════════════════════════════════════════════════════════
3. SELF-ATTENTION
═══════════════════════════════════════════════════════════════════════════

PROPÓSITO: Permitir que cada token "mire" otros tokens relevantes
           para construir representaciones contextuales ricas

ANALOGÍA: Cuando lees "él duerme", buscas "él" para saber de quién hablas.
          Self-attention hace lo mismo automáticamente.

COMPONENTES:
  - Query (Q): "¿Qué información estoy buscando?"
  - Key (K):   "¿Qué información tengo disponible?"
  - Value (V): "¿Qué información proporciono?"

PROCESO:
  1. Q, K, V = proyecciones lineales de x
  2. scores = Q · K^T / √d_k
  3. scores_masked = scores + máscara causal
  4. attention_weights = softmax(scores_masked)
  5. output = attention_weights · V

FÓRMULA:
  Attention(Q, K, V) = softmax(QK^T / √d_k + Mask_causal) · V

EJEMPLO CONCRETO:
  Secuencia: "El gato duerme"
  
  Token "duerme" (posición 2):
    - Score con "El" (pos 0):    0.2
    - Score con "gato" (pos 1):  0.7  (alta atención: "gato duerme")
    - Score con "duerme" (pos 2): 0.1
  
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
  FFN(x) = GELU(x·W_1 + b_1)·W_2 + b_2
  
  - Expansión:  d_model → d_ff  (ej: 512 → 2048, 4x)
  - Activación: GELU
  - Contracción: d_ff → d_model  (ej: 2048 → 512)

DIFERENCIA CON ATTENTION:
  - Attention: captura RELACIONES entre tokens (global)
  - FFN: TRANSFORMA información de cada token (local)

═══════════════════════════════════════════════════════════════════════════
6. LAYER NORMALIZATION
═══════════════════════════════════════════════════════════════════════════

PROPÓSITO: Normalizar activaciones para estabilizar el entrenamiento

FÓRMULA:
  μ = mean(x)  # Media sobre features
  σ² = var(x)   # Varianza
  LayerNorm(x) = γ · (x - μ) / (√(σ² + ε)) + β
  
  Donde γ, β son parámetros aprendibles

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
  
  El "1" permite que el gradiente fluya directamente

VENTAJAS:
  ✅ Evita vanishing gradients en redes profundas
  ✅ Permite aprender funciones identidad fácilmente
  ✅ Facilita refinamientos incrementales

═══════════════════════════════════════════════════════════════════════════
8. MÁSCARA CAUSAL
═══════════════════════════════════════════════════════════════════════════

PROPÓSITO: Bloquear atención a tokens futuros (solo ver anteriores)

IMPLEMENTACIÓN:
  Máscara triangular inferior:
    mask[i][j] = 0    si j ≤ i  (permite atención)
    mask[i][j] = -∞  si j > i   (bloquea atención futura)

VISUALIZACIÓN (seq_len=4):
  [  0,  -∞,  -∞,  -∞]  ← token 0: solo se ve a sí mismo
  [  0,   0,  -∞,  -∞]  ← token 1: ve tokens 0, 1
  [  0,   0,   0,  -∞]  ← token 2: ve tokens 0, 1, 2
  [  0,   0,   0,   0]  ← token 3: ve todos los anteriores

POR QUÉ ES NECESARIA:
  - Permite generación autoregresiva (predecir siguiente token)
  - Evita "hacer trampa" usando información del futuro
  - Esencial para modelos de lenguaje (GPT, ChatGPT)
"""


# ============================================================================
# PARTE 2: IMPLEMENTACIÓN EN PSEUDOCÓDIGO PYTHON
# ============================================================================

class PositionalEncoding(nn.Module):
    """Añade información de posición a los embeddings."""
    
    def __init__(self, d_model: int, max_seq_len: int, learned: bool = True):
        super().__init__()
        if learned:
            self.pos_embedding = nn.Embedding(max_seq_len, d_model)
        else:
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
    
    Proceso:
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
        self.d_k = d_model // n_heads
        
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
    
    Este es el ejemplo principal que muestra el flujo completo.
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
    print("Guía Técnica Completa con Ejemplos")
    print("="*70)
    
    # Ejecutar ejemplos principales
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

