# config.py
"""
Archivo de configuración para los parámetros del Ball Tracker.
"""
import numpy as np
import cv2 # Solo para FONT, opcional

# --- Rutas de Carpetas ---
VIDEO_INPUT_FOLDER = 'video/entrada' # Carpeta donde buscar el video de entrada
VIDEO_OUTPUT_FOLDER = 'video/salida' # Carpeta donde guardar resultados (CSV y Video)

# --- Extensiones de Video Válidas ---
VALID_VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv')

# --- Parámetros de Detección ---
# Ajustar estos rangos según la iluminación y el color exacto de la pelota
LOWER_WHITE_HSV = np.array([0, 10, 170], dtype=np.uint8) # Aumentado V minimo
UPPER_WHITE_HSV = np.array([180, 60, 255], dtype=np.uint8) # Aumentado S maximo un poco
# Ajustar áreas según el tamaño de la pelota en el video
MIN_CONTOUR_AREA = 80   # Reducido ligeramente por si la pelota está lejos
MAX_CONTOUR_AREA = 6000 # Aumentado por si está cerca

# --- Parámetros de Procesamiento ---
GAUSSIAN_BLUR_KERNEL_SIZE = (9, 9) # Puede ser impar. (11, 11) es bastante fuerte.
MORPH_ITERATIONS = 2 # Número de veces que se aplican erode/dilate o open/close

# --- Parámetros de Visualización (en pantalla) ---
DISPLAY_SIZE = (960, 540) # Tamaño de la ventana de visualización (ancho, alto) o None para original
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.6
FONT_COLOR_INFO = (255, 255, 255) # Blanco
FONT_COLOR_DETECTED = (0, 255, 0) # Verde
FONT_COLOR_NOT_DETECTED = (0, 0, 255) # Rojo
FONT_THICKNESS = 1
CIRCLE_RADIUS = 8 # Radio del círculo dibujado sobre la pelota detectada
CIRCLE_COLOR = (0, 255, 0) # Verde
CIRCLE_THICKNESS = 2

# --- Parámetros de Salida ---
DEFAULT_OUTPUT_FILENAME_SUFFIX = '_tracking_data.csv'
OUTPUT_VIDEO_EXTENSION = '.mp4' # Extensión para el video de salida
# Códec para el video. 'mp4v' es común para .mp4, 'XVID' para .avi.
# Puede necesitar instalar códecs en el sistema.
OUTPUT_VIDEO_CODEC = 'mp4v'

# --- Calibración de Escala (¡IMPORTANTE: Medir en el video!) ---
# Altura real del objeto de referencia en metros
REFERENCE_OBJECT_HEIGHT_METERS = 0.32 # Botella de 32 cm
# Altura del mismo objeto medida en píxeles en el video (¡AJUSTAR ESTE VALOR!)
# Medir la altura de la botella en píxeles en un frame representativo del video.
# Puedes usar un editor de imágenes o añadir código temporal en el tracker para medir.
REFERENCE_OBJECT_HEIGHT_PIXELS = 150 # ¡¡¡ VALOR DE EJEMPLO !!! ¡¡¡ DEBES MEDIRLO !!!
# Factor de conversión (calculado automáticamente si ambos valores son > 0)
METERS_PER_PIXEL = (REFERENCE_OBJECT_HEIGHT_METERS / REFERENCE_OBJECT_HEIGHT_PIXELS
                    if REFERENCE_OBJECT_HEIGHT_PIXELS > 0 else 0)