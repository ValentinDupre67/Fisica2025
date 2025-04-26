# plotting.py
"""
Funciones para generar y guardar gráficos de los datos cinemáticos usando Matplotlib.
"""
import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_kinematics(df: pd.DataFrame, output_folder: str, base_filename: str):
    """
    Genera y guarda gráficos de posición, velocidad y aceleración en formato PNG.

    Args:
        df (pd.DataFrame): DataFrame con los datos cinemáticos.
        output_folder (str): Carpeta donde guardar las imágenes.
        base_filename (str): Nombre base de los archivos de salida.
    """
    if df.empty:
        print("DataFrame vacío, no se pueden generar gráficos.")
        return

    os.makedirs(output_folder, exist_ok=True)

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

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    pos_output_path = os.path.join(output_folder, f"{base_filename}_position.png")
    plt.savefig(pos_output_path)
    print(f"Gráfico de posición guardado en: {pos_output_path}")
    plt.close(fig_pos)

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
        vel_output_path = os.path.join(output_folder, f"{base_filename}_velocity.png")
        plt.savefig(vel_output_path)
        print(f"Gráfico de velocidad guardado en: {vel_output_path}")
        plt.close(fig_vel)
    else:
        print("No se graficó la velocidad (datos insuficientes o NaN).")

    # --- Gráfico de Aceleración ---
    if 'ax' in df.columns and df['ax'].notna().any():
        fig_acc, axs_acc = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
        fig_acc.suptitle('Aceleración vs Tiempo')

        axs_acc[0].plot(df['time'], df['ax'], marker='.', linestyle='-', label='Ax (px/s²)')
        axs_acc[0].set_ylabel('Aceleración X (px/s²)')
        axs_acc[0].set_xlabel('Tiempo (s)')
        axs_acc[0].grid(True)
        axs_acc[0].legend()

        axs_acc[1].plot(df['time'], df['ay'], marker='.', linestyle='-', color='orange', label='Ay (px/s²)')
        axs_acc[1].set_ylabel('Aceleración Y (px/s²)')
        axs_acc[1].set_xlabel('Tiempo (s)')
        axs_acc[1].grid(True)
        axs_acc[1].legend()

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        acc_output_path = os.path.join(output_folder, f"{base_filename}_acceleration.png")
        plt.savefig(acc_output_path)
        print(f"Gráfico de aceleración guardado en: {acc_output_path}")
        plt.close(fig_acc)
    else:
        print("No se graficó la aceleración (datos insuficientes o NaN).")