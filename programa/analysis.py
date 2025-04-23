# analysis.py
"""
Funciones para calcular velocidad y aceleración a partir de los datos de tracking,
y opcionalmente convertir a metros si la calibración está configurada.
"""
import pandas as pd
import numpy as np
# Importar el factor de conversión desde la configuración
from programa.config import METERS_PER_PIXEL

def calculate_kinematics(tracking_data_list):
    """
    Calcula velocidad y aceleración (en píxeles y metros) a partir de datos de tracking.

    Args:
    tracking_data_list (list): Lista de diccionarios producida por BallTracker.
                               [{'frame': f, 'x': x, 'y': y, 'time': t}, ...]

    Returns:
    pd.DataFrame: DataFrame con columnas originales y añadidas para dt, dx, dy,
                  vx, vy, ax, ay (en píxeles) y opcionalmente x_m, y_m, vx_m,
                  vy_m, ax_m, ay_m (en metros).
                  Retorna un DataFrame vacío si la lista de entrada está vacía.
    """
    # Definir todas las columnas posibles al inicio
    columns = ['frame', 'x', 'y', 'time', 'dt', 'dx', 'dy', 'vx', 'vy', 'dvx', 'dvy', 'ax', 'ay']
    if METERS_PER_PIXEL > 0:
        columns.extend(['x_m', 'y_m', 'vx_m', 'vy_m', 'ax_m', 'ay_m'])
    else: # Añadir columnas NaN si no hay conversión para consistencia
         columns.extend(['x_m', 'y_m', 'vx_m', 'vy_m', 'ax_m', 'ay_m'])


    if not tracking_data_list:
        print("Advertencia: Lista de datos de tracking vacía.")
        # Devolver DataFrame vacío con todas las columnas esperadas
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(tracking_data_list)

    # Inicializar todas las columnas calculadas con NaN
    for col in ['dt', 'dx', 'dy', 'vx', 'vy', 'dvx', 'dvy', 'ax', 'ay',
                'x_m', 'y_m', 'vx_m', 'vy_m', 'ax_m', 'ay_m']:
         if col not in df.columns: # Añadir si no existen (caso de conversión desactivada)
              df[col] = np.nan


    if len(df) < 2:
        print("No hay suficientes datos para calcular velocidad.")
        # El DataFrame ya tiene las columnas como NaN
        return df

    # Calcular diferencias (para todos menos el primero)
    df['dt'] = df['time'].diff()
    df['dx'] = df['x'].diff()
    df['dy'] = df['y'].diff()

    # Calcular velocidad (pixels/segundo) - Evitar división por cero
    # Usar .loc para evitar SettingWithCopyWarning y asegurar asignación
    mask_dt_valid = df['dt'] != 0
    df.loc[mask_dt_valid, 'vx'] = df.loc[mask_dt_valid, 'dx'] / df.loc[mask_dt_valid, 'dt']
    df.loc[mask_dt_valid, 'vy'] = df.loc[mask_dt_valid, 'dy'] / df.loc[mask_dt_valid, 'dt']
    # Los que tienen dt=0 o el primero quedan como NaN

    if len(df) < 3:
        print("No hay suficientes datos para calcular aceleración.")
         # El DataFrame ya tiene ax, ay como NaN
        # Calcular conversión a metros si es posible para posición y velocidad
        if METERS_PER_PIXEL > 0:
            print(f"Aplicando conversión a metros (factor: {METERS_PER_PIXEL:.6f} m/px)")
            df['x_m'] = df['x'] * METERS_PER_PIXEL
            df['y_m'] = df['y'] * METERS_PER_PIXEL # Y también se escala
            df['vx_m'] = df['vx'] * METERS_PER_PIXEL
            df['vy_m'] = df['vy'] * METERS_PER_PIXEL
        elif 'x_m' not in columns: # Solo imprimir advertencia si no se hizo antes
             print("Advertencia: No se realizó la conversión a metros. METERS_PER_PIXEL no es válido o es cero.")

        return df

    # Calcular diferencias de velocidad (para todos menos los dos primeros)
    df['dvx'] = df['vx'].diff()
    df['dvy'] = df['vy'].diff()

    # Calcular aceleración (pixels/segundo^2) - Reutilizar dt, asegurarse que sea válido
    mask_accel_valid = mask_dt_valid & ~df['dvx'].isnull() # dt válido y dvx calculado
    df.loc[mask_accel_valid, 'ax'] = df.loc[mask_accel_valid, 'dvx'] / df.loc[mask_accel_valid, 'dt']
    df.loc[mask_accel_valid, 'ay'] = df.loc[mask_accel_valid, 'dvy'] / df.loc[mask_accel_valid, 'dt']

    # --- Conversión a Metros ---
    if METERS_PER_PIXEL > 0:
        print(f"Aplicando conversión a metros (factor: {METERS_PER_PIXEL:.6f} m/px)")
        df['x_m'] = df['x'] * METERS_PER_PIXEL
        df['y_m'] = df['y'] * METERS_PER_PIXEL # Y también se escala
        df['vx_m'] = df['vx'] * METERS_PER_PIXEL
        df['vy_m'] = df['vy'] * METERS_PER_PIXEL
        df['ax_m'] = df['ax'] * METERS_PER_PIXEL
        df['ay_m'] = df['ay'] * METERS_PER_PIXEL
    elif 'x_m' not in columns: # Solo imprimir advertencia si no se hizo antes
        print("Advertencia: No se realizó la conversión a metros. METERS_PER_PIXEL no es válido o es cero.")


    print("Cálculos de cinemática (píxeles y metros) completados.")
    # Seleccionar y reordenar columnas para el output final si se desea
    # final_columns = [...]
    # return df[final_columns]
    return df # Devolver todas las columnas calculadas