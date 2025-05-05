# config.py
"""
Archivo de configuración para el tracker de baloncesto.
"""

# --- Parámetros de Video y Salida ---
VIDEO_PATH = './video/entrada/PeloAz.mp4'  # ¡¡¡IMPORTANTE: Cambia esto a la ruta de tu video!!!
OUTPUT_CSV = 'tracking_data_processed.csv'

# --- Parámetros de Tracking ---
# Opciones comunes: 'BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT'
# CSRT y KCF suelen ser buenas opciones generales. CSRT es más preciso pero más lento.
# MOSSE es muy rápido pero menos preciso.
# GOTURN requiere modelos preentrenados adicionales.
TRACKER_TYPE = 'CSRT'

# --- Parámetros de Conversión Píxel a Metros ---
# ¡¡¡MUY IMPORTANTE!!! Debes medir esto en tu video.
# Mide el tamaño (p.ej., diámetro) de tu objeto de referencia EN PÍXELES
# en un frame del video, idealmente en la misma profundidad donde se moverá la pelota.
REFERENCE_OBJECT_SIZE_PIXELS = 1000 # Ejemplo: Mediste que el objeto mide 50 píxeles

# Tamaño real del objeto de referencia en METROS.
# Ejemplo: Diámetro oficial de una pelota de baloncesto FIBA talla 7 es ~0.24 metros
REFERENCE_OBJECT_SIZE_METERS = 2.24

# --- Parámetros de Visualización ---
DRAW_BOUNDING_BOX = True
DRAW_CENTER = True
DRAW_TRAIL = True # Poner en True para dibujar la trayectoria (puede ralentizar)
TRAIL_LENGTH = 50 # Cuántos puntos mantener en la trayectoria