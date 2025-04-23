# plotting.py
"""
Funciones para generar gráficos de los datos cinemáticos usando Matplotlib.
"""
import matplotlib.pyplot as plt
import pandas as pd # Solo para type hinting si se usa

def plot_kinematics(df: pd.DataFrame):
    """
    Genera y muestra gráficos de posición, velocidad y aceleración.

    Args:
        df (pd.DataFrame): DataFrame que contiene los datos cinemáticos
                           (time, x, y, vx, vy, ax, ay).
    """
    if df.empty:
        print("DataFrame vacío, no se pueden generar gráficos.")
        return

    # --- Gráfico de Posición ---
    fig_pos, axs_pos = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
    fig_pos.suptitle('Posición vs Tiempo')

    axs_pos[0].plot(df['time'], df['x'], marker='.', linestyle='-', label='X (px)')
    axs_pos[0].set_ylabel('Posición X (px)')
    axs_pos[0].set_xlabel('Tiempo (s)')
    axs_pos[0].grid(True)
    axs_pos[0].legend()

    axs_pos[1].plot(df['time'], df['y'], marker='.', linestyle='-', color='orange', label='Y (px)')
    axs_pos[1].set_ylabel('Posición Y (px)')
    axs_pos[1].set_xlabel('Tiempo (s)')
    axs_pos[1].grid(True)
    axs_pos[1].legend()

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Ajustar para el supertítulo
    plt.show()

    # --- Gráfico de Velocidad ---
    if 'vx' in df.columns and df['vx'].notna().any():
        fig_vel, axs_vel = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
        fig_vel.suptitle('Velocidad vs Tiempo')

        axs_vel[0].plot(df['time'], df['vx'], marker='.', linestyle='-', label='Vx (px/s)')
        axs_vel[0].set_ylabel('Velocidad X (px/s)')
        axs_vel[0].set_xlabel('Tiempo (s)')
        axs_vel[0].grid(True)
        axs_vel[0].legend()

        axs_vel[1].plot(df['time'], df['vy'], marker='.', linestyle='-', color='orange', label='Vy (px/s)')
        axs_vel[1].set_ylabel('Velocidad Y (px/s)')
        axs_vel[1].set_xlabel('Tiempo (s)')
        axs_vel[1].grid(True)
        axs_vel[1].legend()

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()
    else:
        print("No se graficó la velocidad (datos insuficientes o NaN).")

    # --- Gráfico de Aceleración ---
    if 'ax' in df.columns and df['ax'].notna().any():
        fig_acc, axs_acc = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
        fig_acc.suptitle('Aceleración vs Tiempo')

        axs_acc[0].plot(df['time'], df['ax'], marker='.', linestyle='-', label='Ax (px/s^2)')
        axs_acc[0].set_ylabel('Aceleración X (px/s^2)')
        axs_acc[0].set_xlabel('Tiempo (s)')
        axs_acc[0].grid(True)
        axs_acc[0].legend()

        axs_acc[1].plot(df['time'], df['ay'], marker='.', linestyle='-', color='orange', label='Ay (px/s^2)')
        axs_acc[1].set_ylabel('Aceleración Y (px/s^2)')
        axs_acc[1].set_xlabel('Tiempo (s)')
        axs_acc[1].grid(True)
        axs_acc[1].legend()

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()
    else:
        print("No se graficó la aceleración (datos insuficientes o NaN).")