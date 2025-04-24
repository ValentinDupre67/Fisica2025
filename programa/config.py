# config.py
"""
Archivo de configuración para los parámetros del Ball Tracker.
Configurado para usar SimpleBlobDetector de OpenCV.
"""
import numpy as np
import cv2 # Para FONT y SimpleBlobDetector_Params

# --- Rutas de Carpetas ---
VIDEO_INPUT_FOLDER = 'video/entrada'
VIDEO_OUTPUT_FOLDER = 'video/salida'

# --- Extensiones de Video Válidas ---
VALID_VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv')

# --- Parámetros de Detección (USANDO SimpleBlobDetector) ---
# ¡¡¡ ESTOS PARÁMETROS REQUIEREN AJUSTE FINO PARA TU VIDEO !!!

# 1. Filtrado por Color/Intensidad (Opcional pero recomendado)
#    El detector puede funcionar en escala de grises o sobre una máscara de color.
#    Si usamos una máscara de color (amarillo), filtramos antes.
#    Si no, podemos filtrar por intensidad del blob (blobColor).
FILTER_BY_COLOR = True # True para usar máscara HSV, False para detectar en grises
BLOB_COLOR = 255       # Si FILTER_BY_COLOR=False, busca blobs blancos (255) o negros (0) en escala de grises.
                       # Si FILTER_BY_COLOR=True, este valor se ignora (se usa la máscara).

# Rango HSV para Amarillo (si FILTER_BY_COLOR = True)
LOWER_YELLOW_HSV = np.array([20, 100, 100], dtype=np.uint8)
UPPER_YELLOW_HSV = np.array([35, 255, 255], dtype=np.uint8)

# 2. Filtrado por Área
FILTER_BY_AREA = True
# Ajusta estos valores al área esperada de tu pelota de golf en píxeles
MIN_AREA = 50    # Área mínima en píxeles cuadrados
MAX_AREA = 1500  # Área máxima en píxeles cuadrados

# 3. Filtrado por Circularidad (Qué tan parecido a un círculo es)
#    Valor = 4 * pi * Area / (Perímetro^2). 1 es un círculo perfecto.
FILTER_BY_CIRCULARITY = True
MIN_CIRCULARITY = 0.6  # Mínimo (más bajo permite formas menos circulares)
MAX_CIRCULARITY = 1.0  # Máximo (generalmente 1.0 o un poco más)

# 4. Filtrado por Convexidad (Área del Blob / Área de su envolvente convexa)
#    1 es perfectamente convexo.
FILTER_BY_CONVEXITY = True
MIN_CONVEXITY = 0.80   # Mínimo (más bajo permite formas con "muescas")
MAX_CONVEXITY = 1.0    # Máximo

# 5. Filtrado por Inercia (Qué tan alargado es el blob)
#    Valor entre 0 y 1. 0 es una línea, 1 es un círculo.
FILTER_BY_INERTIA = True
MIN_INERTIA_RATIO = 0.4 # Mínimo (más bajo permite formas más alargadas)
MAX_INERTIA_RATIO = 1.0 # Máximo

# --- Parámetros de Procesamiento ---
# Desenfoque antes de la máscara HSV (si se usa) o antes de la detección en grises
GAUSSIAN_BLUR_KERNEL_SIZE = (7, 7) # Puede ser útil un blur menor aquí
# Iteraciones morfológicas para limpiar la máscara HSV (si se usa)
MORPH_ITERATIONS = 1

# --- Parámetros de Visualización ---
DISPLAY_SIZE = (960, 540)
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.6
FONT_COLOR_INFO = (255, 255, 255)
FONT_COLOR_DETECTED = (0, 255, 0) # Verde
FONT_COLOR_NOT_DETECTED = (0, 0, 255) # Rojo
FONT_THICKNESS = 1
CIRCLE_COLOR = (0, 255, 0) # Verde
CIRCLE_THICKNESS = 2

# --- Parámetros de Salida ---
DEFAULT_OUTPUT_FILENAME_SUFFIX = '_tracking_data_blob.csv' # Sufijo diferente
OUTPUT_VIDEO_EXTENSION = '.mp4'
OUTPUT_VIDEO_CODEC = 'mp4v'

# --- Calibración de Escala ---
REFERENCE_OBJECT_HEIGHT_METERS = 0.32
REFERENCE_OBJECT_HEIGHT_PIXELS = 150 # ¡¡¡ AJUSTAR !!!
METERS_PER_PIXEL = (REFERENCE_OBJECT_HEIGHT_METERS / REFERENCE_OBJECT_HEIGHT_PIXELS
                    if REFERENCE_OBJECT_HEIGHT_PIXELS > 0 else 0)