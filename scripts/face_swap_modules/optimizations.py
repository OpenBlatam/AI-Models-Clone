"""
Optimizations Module
===================
Funciones optimizadas con Numba JIT para máximo rendimiento.
"""

import numpy as np
from typing import Optional

# Intentar importar Numba para optimización
try:
    from numba import jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Fallback sin decorador
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    prange = range


@jit(nopython=True, parallel=True, cache=True)
def fast_gaussian_blur_1d(arr: np.ndarray, sigma: float) -> np.ndarray:
    """Blur gaussiano 1D optimizado con Numba."""
    n = len(arr)
    result = np.zeros_like(arr)
    kernel_size = int(6 * sigma + 1)
    if kernel_size % 2 == 0:
        kernel_size += 1
    half = kernel_size // 2
    
    # Crear kernel gaussiano
    kernel = np.zeros(kernel_size)
    for i in range(kernel_size):
        x = i - half
        kernel[i] = np.exp(-0.5 * (x / sigma) ** 2)
    kernel_sum = np.sum(kernel)
    kernel = kernel / kernel_sum
    
    # Aplicar convolución
    for i in prange(n):
        val = 0.0
        for j in range(kernel_size):
            idx = i + j - half
            if idx >= 0 and idx < n:
                val += arr[idx] * kernel[j]
        result[i] = val
    
    return result


@jit(nopython=True, parallel=True, cache=True)
def fast_bilateral_filter_grayscale(
    image: np.ndarray,
    d: int,
    sigma_color: float,
    sigma_space: float
) -> np.ndarray:
    """Filtro bilateral optimizado para imágenes en escala de grises."""
    h, w = image.shape
    result = np.zeros_like(image, dtype=np.float64)
    
    half_d = d // 2
    
    for i in prange(h):
        for j in prange(w):
            pixel_value = image[i, j]
            weight_sum = 0.0
            filtered_value = 0.0
            
            for di in range(-half_d, half_d + 1):
                for dj in range(-half_d, half_d + 1):
                    ni = i + di
                    nj = j + dj
                    
                    if ni >= 0 and ni < h and nj >= 0 and nj < w:
                        neighbor_value = image[ni, nj]
                        
                        # Peso espacial
                        spatial_dist = np.sqrt(float(di * di + dj * dj))
                        spatial_weight = np.exp(-0.5 * (spatial_dist / sigma_space) ** 2)
                        
                        # Peso de color
                        color_dist = abs(float(pixel_value - neighbor_value))
                        color_weight = np.exp(-0.5 * (color_dist / sigma_color) ** 2)
                        
                        # Peso combinado
                        weight = spatial_weight * color_weight
                        filtered_value += neighbor_value * weight
                        weight_sum += weight
            
            if weight_sum > 0:
                result[i, j] = filtered_value / weight_sum
            else:
                result[i, j] = pixel_value
    
    return result.astype(image.dtype)


@jit(nopython=True, parallel=True, cache=True)
def fast_histogram_matching(
    source: np.ndarray,
    target_hist: np.ndarray,
    target_cdf: np.ndarray
) -> np.ndarray:
    """Matching de histogramas optimizado."""
    result = np.zeros_like(source)
    source_flat = source.flatten()
    result_flat = result.flatten()
    
    # Calcular CDF del source
    source_hist = np.zeros(256)
    for i in prange(len(source_flat)):
        val = int(source_flat[i])
        if val >= 0 and val < 256:
            source_hist[val] += 1
    
    source_hist = source_hist / (len(source_flat) + 1e-10)
    source_cdf = np.zeros(256)
    source_cdf[0] = source_hist[0]
    for i in range(1, 256):
        source_cdf[i] = source_cdf[i - 1] + source_hist[i]
    
    # Mapear valores
    for i in prange(len(source_flat)):
        val = int(source_flat[i])
        if val >= 0 and val < 256:
            source_cdf_val = source_cdf[val]
            # Encontrar valor más cercano en target_cdf
            best_match = 0
            min_diff = abs(source_cdf_val - target_cdf[0])
            for j in range(1, 256):
                diff = abs(source_cdf_val - target_cdf[j])
                if diff < min_diff:
                    min_diff = diff
                    best_match = j
            result_flat[i] = best_match
    
    return result.reshape(source.shape)


@jit(nopython=True, parallel=True, cache=True)
def fast_laplacian_variance(image: np.ndarray) -> float:
    """Calcula varianza de Laplacian (medida de nitidez) optimizada."""
    h, w = image.shape
    laplacian = np.zeros((h, w), dtype=np.float64)
    
    # Kernel Laplacian
    for i in prange(1, h - 1):
        for j in prange(1, w - 1):
            laplacian[i, j] = (
                -image[i - 1, j] - image[i + 1, j] -
                image[i, j - 1] - image[i, j + 1] +
                4 * image[i, j]
            )
    
    # Calcular varianza
    mean_val = 0.0
    count = 0
    for i in prange(h):
        for j in prange(w):
            mean_val += laplacian[i, j]
            count += 1
    mean_val = mean_val / count
    
    variance = 0.0
    for i in prange(h):
        for j in prange(w):
            diff = laplacian[i, j] - mean_val
            variance += diff * diff
    variance = variance / count
    
    return variance


@jit(nopython=True, parallel=True, cache=True)
def fast_mask_blending(
    source: np.ndarray,
    target: np.ndarray,
    mask: np.ndarray
) -> np.ndarray:
    """Blending rápido con máscara optimizado."""
    h, w = source.shape[:2]
    channels = source.shape[2] if len(source.shape) == 3 else 1
    
    if channels == 1:
        result = np.zeros((h, w), dtype=np.float64)
        for i in prange(h):
            for j in prange(w):
                m = mask[i, j]
                result[i, j] = source[i, j] * m + target[i, j] * (1.0 - m)
        return np.clip(result, 0, 255).astype(np.uint8)
    else:
        result = np.zeros((h, w, channels), dtype=np.float64)
        for i in prange(h):
            for j in prange(w):
                m = mask[i, j]
                for c in range(channels):
                    result[i, j, c] = source[i, j, c] * m + target[i, j, c] * (1.0 - m)
        return np.clip(result, 0, 255).astype(np.uint8)


@jit(nopython=True, cache=True)
def fast_color_space_convert_bgr_to_lab(b: float, g: float, r: float) -> tuple:
    """Conversión BGR a LAB optimizada para un pixel."""
    # Normalizar a [0, 1]
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0
    
    # A RGB
    if r_norm > 0.04045:
        r_norm = ((r_norm + 0.055) / 1.055) ** 2.4
    else:
        r_norm = r_norm / 12.92
    
    if g_norm > 0.04045:
        g_norm = ((g_norm + 0.055) / 1.055) ** 2.4
    else:
        g_norm = g_norm / 12.92
    
    if b_norm > 0.04045:
        b_norm = ((b_norm + 0.055) / 1.055) ** 2.4
    else:
        b_norm = b_norm / 12.92
    
    # A XYZ
    x = r_norm * 0.4124564 + g_norm * 0.3575761 + b_norm * 0.1804375
    y = r_norm * 0.2126729 + g_norm * 0.7151522 + b_norm * 0.0721750
    z = r_norm * 0.0193339 + g_norm * 0.1191920 + b_norm * 0.9503041
    
    # Normalizar por D65
    x = x / 0.95047
    z = z / 1.08883
    
    # A LAB
    if x > 0.008856:
        fx = x ** (1.0 / 3.0)
    else:
        fx = (7.787 * x) + (16.0 / 116.0)
    
    if y > 0.008856:
        fy = y ** (1.0 / 3.0)
    else:
        fy = (7.787 * y) + (16.0 / 116.0)
    
    if z > 0.008856:
        fz = z ** (1.0 / 3.0)
    else:
        fz = (7.787 * z) + (16.0 / 116.0)
    
    l = (116.0 * fy) - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    
    return (l, a, b)


def is_numba_available() -> bool:
    """Verifica si Numba está disponible."""
    return NUMBA_AVAILABLE








