# data_processor.py
"""
Módulo para procesar los datos de seguimiento: conversión de unidades,
cálculo de velocidad/aceleración y guardado en CSV.
"""
import pandas as pd
import numpy as np

def process_tracking_data(raw_data, fps, ref_pixels, ref_meters):
    """
    Procesa los datos crudos del tracker, convierte a metros y calcula cinemática.

    Args:
        raw_data (list): Lista de tuplas (timestamp_ms, x_px, y_px, w_px, h_px).
                         Puede contener None si el tracking falló.
        fps (float): Frames por segundo del video (usado si dt no se puede calcular bien).
        ref_pixels (float): Tamaño del objeto de referencia en píxeles.
        ref_meters (float): Tamaño del objeto de referencia en metros.

    Returns:
        pandas.DataFrame: DataFrame con columnas [time_s, x_m, y_m, vx, vy, ax, ay]
                          o None si hay error o no hay datos válidos.
    """
    if not raw_data:
        print("Error: No hay datos crudos para procesar.")
        return None
    if ref_pixels <= 0 or ref_meters <= 0:
         print("Error: Los tamaños de referencia deben ser positivos.")
         return None

    # Crear DataFrame inicial
    df = pd.DataFrame(raw_data, columns=['timestamp_ms', 'x_px', 'y_px', 'w_px', 'h_px'])

    # Eliminar filas donde el tracking falló (valores None)
    df.dropna(subset=['x_px', 'y_px'], inplace=True)

    if df.empty:
        print("Error: No quedaron datos válidos después de eliminar fallos de tracking.")
        return None

    # --- Conversión de unidades y tiempo ---
    df['time_s'] = df['timestamp_ms'] / 1000.0

    # Calcular factor de conversión
    # Si ref_pixels es 0, esto dará infinito. Ya chequeado arriba.
    pixels_per_meter = ref_pixels / ref_meters
    print(f"Factor de conversión: {pixels_per_meter:.2f} píxeles/metro")

    # Convertir coordenadas de píxeles a metros
    # Origen (0,0) se mantiene en la esquina superior izquierda.
    # Eje Y positivo sigue siendo hacia abajo (convención OpenCV/imagen).
    # Si quieres Y positivo hacia arriba, invierte y_m: df['y_m'] = (frame_height_pixels - df['y_px']) / pixels_per_meter
    df['x_m'] = df['x_px'] / pixels_per_meter
    df['y_m'] = df['y_px'] / pixels_per_meter # Y positivo hacia abajo

    # --- Cálculo de Velocidad y Aceleración ---
    # Calcular diferencia de tiempo entre mediciones consecutivas válidas
    df['dt'] = df['time_s'].diff()

    # Llenar el primer NaN en dt con un valor estimado (1/fps) o 0
    # Usar 1/fps es una aproximación razonable si los frames son regulares.
    if fps > 0:
        df['dt'].fillna(1.0/fps, inplace=True)
    else: # Si no tenemos FPS válidos
         df['dt'].fillna(0, inplace=True) # No ideal, pero evita errores

    # Asegurarse de que dt no sea cero para evitar división por cero
    df.loc[df['dt'] <= 0, 'dt'] = 1e-6 # Reemplazar 0 o negativos con un valor muy pequeño


    # Calcular velocidad (diferencia finita central podría ser más precisa, pero 'diff' es más simple)
    # v = delta_posicion / delta_tiempo
    df['vx'] = df['x_m'].diff() / df['dt']
    df['vy'] = df['y_m'].diff() / df['dt']

    # Calcular aceleración
    # a = delta_velocidad / delta_tiempo
    df['ax'] = df['vx'].diff() / df['dt']
    df['ay'] = df['vy'].diff() / df['dt']

    # Llenar NaNs iniciales resultantes de .diff()
    # Podemos llenarlos con 0 o usar 'bfill' (backfill) si se prefiere
    df.fillna(0, inplace=True) # Rellenar todos los NaNs restantes con 0

    print("Datos procesados:")
    print(df[['time_s', 'x_m', 'y_m', 'vx', 'vy', 'ax', 'ay']].head())

    # Seleccionar y devolver las columnas relevantes
    processed_df = df[['time_s', 'x_m', 'y_m', 'vx', 'vy', 'ax', 'ay']].copy()

    return processed_df


def save_data_to_csv(dataframe, filename):
    """Guarda un DataFrame de pandas en un archivo CSV."""
    if dataframe is None or dataframe.empty:
        print("No hay datos procesados para guardar en CSV.")
        return False
    try:
        dataframe.to_csv(filename, index=False, float_format='%.4f')
        print(f"Datos procesados guardados exitosamente en '{filename}'")
        return True
    except Exception as e:
        print(f"Error al guardar el archivo CSV '{filename}': {e}")
        return False