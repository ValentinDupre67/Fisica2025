# config.py
"""
Archivo de configuración para los parámetros del Ball Tracker.
Configurado para usar SimpleBlobDetector de OpenCV.
Intentando detectar partes azules de una pelota de baloncesto.
"""
import numpy as np
import cv2 # Para FONT y SimpleBlobDetector_Params

# --- Rutas de Carpetas ---
VIDEO_INPUT_FOLDER = 'video/entrada'
VIDEO_OUTPUT_FOLDER = 'video/salida'

# --- Extensiones de Video Válidas ---
VALID_VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv')

# --- Parámetros de Detección (USANDO SimpleBlobDetector) ---
# Ajustando para detectar MANCHAS AZULES de una pelota de baloncesto.

# 1. Filtrado por Color/Intensidad
FILTER_BY_COLOR = True # Usando máscara HSV
BLOB_COLOR = 255       # Buscando blobs blancos en la máscara

# Rango HSV ajustado para el Azul de la imagen (RGB 18, 50, 93 -> OpenCV HSV ~[110, 207, 92])
# (Recuerda que aún puede necesitar ajuste fino para tu video específico)
LOWER_HSV = np.array([100, 120, 50], dtype=np.uint8)
UPPER_HSV = np.array([125, 255, 255], dtype=np.uint8)

# 2. Filtrado por Área
FILTER_BY_AREA = True
# Ajusta estos valores al área esperada de las MANCHAS AZULES en píxeles.
# Este rango puede necesitar ser más amplio que para una pelota completa.
MIN_AREA = 100    # Área mínima de una mancha azul (aumentado)
MAX_AREA = 8000  # Área máxima de una mancha azul (aumentado significativamente)

# 3. Filtrado por Circularidad
# DESACTIVADO: Las manchas azules no serán circulares.
FILTER_BY_CIRCULARITY = False
MIN_CIRCULARITY = 0.3  # Valor bajo, pero el filtro está desactivado arriba.
MAX_CIRCULARITY = 1.0

# 4. Filtrado por Convexidad
# DESACTIVADO: Las manchas azules pueden no ser convexas.
FILTER_BY_CONVEXITY = False
MIN_CONVEXITY = 0.5   # Valor bajo, pero el filtro está desactivado arriba.
MAX_CONVEXITY = 1.0

# 5. Filtrado por Inercia
# DESACTIVADO: La forma alargada de las manchas azules varía.
FILTER_BY_INERTIA = False
MIN_INERTIA_RATIO = 0.1 # Valor bajo, pero el filtro está desactivado arriba.
MAX_INERTIA_RATIO = 1.0

# --- Parámetros de Procesamiento ---
GAUSSIAN_BLUR_KERNEL_SIZE = (7, 7)
MORPH_ITERATIONS = 2 # Aumentado a 2 para intentar limpiar más la máscara azul

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
DEFAULT_OUTPUT_FILENAME_SUFFIX = '_tracking_data_blob_blue_patch.csv' # Sufijo descriptivo
OUTPUT_VIDEO_EXTENSION = '.mp4'
OUTPUT_VIDEO_CODEC = 'mp4v'

# --- Calibración de Escala ---
REFERENCE_OBJECT_HEIGHT_METERS = 0.32
REFERENCE_OBJECT_HEIGHT_PIXELS = 150 # ¡¡¡ AJUSTAR !!!
METERS_PER_PIXEL = (REFERENCE_OBJECT_HEIGHT_METERS / REFERENCE_OBJECT_HEIGHT_PIXELS
                    if REFERENCE_OBJECT_HEIGHT_PIXELS > 0 else 0)