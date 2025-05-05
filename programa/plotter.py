# plotter.py
"""
Módulo para generar gráficos de los datos de cinemática procesados.
"""
import matplotlib.pyplot as plt
import pandas as pd

def plot_kinematics(data_df):
    """
    Genera gráficos de posición, velocidad y aceleración a lo largo del tiempo.

    Args:
        data_df (pandas.DataFrame): DataFrame con columnas 'time_s',
                                   'x_m', 'y_m', 'vx', 'vy', 'ax', 'ay'.
    """
    if data_df is None or data_df.empty:
        print("No hay datos válidos para graficar.")
        return

    if not all(col in data_df.columns for col in ['time_s', 'x_m', 'y_m', 'vx', 'vy', 'ax', 'ay']):
        print("Error: El DataFrame no contiene todas las columnas necesarias para graficar.")
        print("Columnas esperadas: time_s, x_m, y_m, vx, vy, ax, ay")
        print("Columnas presentes:", data_df.columns)
        return

    time = data_df['time_s'].values

    # Crear figura con 3 subplots (uno para posición, uno para velocidad, uno para aceleración)
    fig, axs = plt.subplots(3, 1, figsize=(10, 12), sharex=True) # Compartir eje X (tiempo)
    fig.suptitle('Análisis Cinemático de la Pelota de Baloncesto', fontsize=16)

    # --- Gráfico de Posición ---
    axs[0].plot(time, data_df['x_m'], label='Posición X (m)', color='blue')
    axs[0].plot(time, data_df['y_m'], label='Posición Y (m)', color='red')
    axs[0].set_ylabel('Posición (m)')
    axs[0].set_title('Posición vs Tiempo')
    axs[0].legend()
    axs[0].grid(True)
    # Recordatorio: Y=0 es arriba, Y positivo es hacia abajo (convención de imagen)

    # --- Gráfico de Velocidad ---
    axs[1].plot(time, data_df['vx'], label='Velocidad X (m/s)', color='blue')
    axs[1].plot(time, data_df['vy'], label='Velocidad Y (m/s)', color='red')
    axs[1].set_ylabel('Velocidad (m/s)')
    axs[1].set_title('Velocidad vs Tiempo')
    axs[1].legend()
    axs[1].grid(True)

    # --- Gráfico de Aceleración ---
    axs[2].plot(time, data_df['ax'], label='Aceleración X (m/s²)', color='blue')
    axs[2].plot(time, data_df['ay'], label='Aceleración Y (m/s²)', color='red')
    axs[2].set_ylabel('Aceleración (m/s²)')
    axs[2].set_title('Aceleración vs Tiempo')
    axs[2].legend()
    axs[2].grid(True)

    # Añadir etiqueta común al eje X
    axs[2].set_xlabel('Tiempo (s)')

    # Ajustar espaciado y mostrar gráfico
    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Ajustar para título principal
    print("Mostrando gráficos...")
    plt.show()
    print("Gráficos cerrados.")