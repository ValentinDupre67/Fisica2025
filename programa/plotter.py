# plotter.py
"""
Gráficos separados de cinemática.
"""
import matplotlib.pyplot as plt

def plot_kinematics(data_df):
    """
    Genera gráficos separados para posición (altura sobre el piso), velocidad y aceleración.
    Altura se normaliza para que el piso (máxima y_m) sea cero.
    Se crean 3 filas (posición, velocidad, aceleración) y 2 columnas (X, Y).

    Args:
        data_df (pandas.DataFrame): Columnas 'time_s', 'x_m', 'y_m', 'vx', 'vy', 'ax', 'ay'.
    """
    if data_df is None or data_df.empty:
        print("No hay datos válidos para graficar.")
        return

    # Verificar columnas
    cols = ['time_s', 'x_m', 'y_m', 'vx', 'vy', 'ax', 'ay']
    if not all(c in data_df.columns for c in cols):
        print("Error: faltan columnas para graficar. Se requieren:", cols)
        return

    t = data_df['time_s'].values

    # Calcular altura relativa: piso = max(y_m)
    ground = data_df['y_m'].max()
    height = ground - data_df['y_m']  # en metros, 0 en piso, positivo arriba

    # Velocidad Y cartesiana (derivada de altura)
    vy_rel = -data_df['vy']
    ay_rel = -data_df['ay']

    # Crear grid
    fig, axs = plt.subplots(3, 2, figsize=(12, 10), sharex=True)
    fig.suptitle('Análisis Cinemático Separado', fontsize=16)

    # --- Posición/Altura ---
    axs[0, 0].plot(t, data_df['x_m'])
    axs[0, 0].set_ylabel('Posición X (m)')
    axs[0, 0].set_title('Posición X vs Tiempo')
    axs[0, 0].grid(True)

    axs[0, 1].plot(t, height)
    axs[0, 1].set_ylabel('Altura (m)')
    axs[0, 1].set_title('Altura vs Tiempo')
    axs[0, 1].set_ylim(0, height.max() * 1.05)
    axs[0, 1].grid(True)

    # --- Velocidad ---
    axs[1, 0].plot(t, data_df['vx'])
    axs[1, 0].set_ylabel('Velocidad X (m/s)')
    axs[1, 0].set_title('Velocidad X vs Tiempo')
    axs[1, 0].grid(True)

    axs[1, 1].plot(t, vy_rel)
    axs[1, 1].set_ylabel('Velocidad Y (m/s)')
    axs[1, 1].set_title('Velocidad Y vs Tiempo')
    axs[1, 1].grid(True)

    # --- Aceleración ---
    axs[2, 0].plot(t, data_df['ax'])
    axs[2, 0].set_ylabel('Aceleración X (m/s²)')
    axs[2, 0].set_title('Aceleración X vs Tiempo')
    axs[2, 0].grid(True)

    axs[2, 1].plot(t, ay_rel)
    axs[2, 1].set_ylabel('Aceleración Y (m/s²)')
    axs[2, 1].set_title('Aceleración Y vs Tiempo')
    axs[2, 1].grid(True)

    # Etiqueta eje X
    for ax in axs[2]:
        ax.set_xlabel('Tiempo (s)')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    print("Mostrando gráficos con altura normalizada...")
    # Guardar el plot en un archivo PNG antes de mostrarlo
    output_path = 'kinematics_plot.png'
    fig.savefig(output_path)
    print(f"Gráfico guardado en '{output_path}'")
    plt.show()
    print("Gráficos cerrados.")