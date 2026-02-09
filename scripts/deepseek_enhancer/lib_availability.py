"""
Library Availability Checker
============================
Verifica la disponibilidad de librerías opcionales.
"""

# Importar librerías avanzadas opcionales
try:
    from scipy import ndimage, signal
    from scipy.sparse import diags
    from scipy.fft import fft2, ifft2
    from scipy.optimize import minimize_scalar
    from scipy.ndimage import gaussian_filter, median_filter, uniform_filter
    from scipy.ndimage import binary_erosion, binary_dilation, binary_opening, binary_closing
    from scipy.ndimage import label, find_objects
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    # Fallbacks para funciones scipy
    fft2 = None
    ifft2 = None

try:
    from skimage import restoration, filters, exposure, color
    from skimage.feature import peak_local_maxima, corner_harris, corner_peaks
    from skimage.segmentation import felzenszwalb, slic, quickshift
    from skimage.morphology import disk, square, diamond, star
    from skimage.morphology import opening, closing, erosion, dilation
    from skimage.morphology import white_tophat, black_tophat
    from skimage.filters import gaussian, median, sobel, scharr, roberts, prewitt
    from skimage.filters import threshold_otsu, threshold_local, threshold_adaptive
    from skimage.transform import resize, rotate, warp, AffineTransform
    from skimage.measure import label as sk_label, regionprops
    from skimage.util import img_as_float, img_as_ubyte
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    from PIL.ImageFilter import GaussianBlur, UnsharpMask, MedianFilter, ModeFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from numba import jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Fallback para numba
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    prange = range






