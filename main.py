# main.py
"""
Script principal para ejecutar el seguimiento de la pelota,
el análisis cinemático y la generación de gráficos.
Busca automáticamente un video en la carpeta especificada en config.py.
"""
import argparse
import time
import os # Para manejo de archivos y carpetas
import sys # Para salir del script con sys.exit()

# Importar componentes del proyecto y configuración
from programa.tracker import BallTracker
from programa.analysis import calculate_kinematics
from programa.plotting import plot_kinematics
from programa.config import (VIDEO_INPUT_FOLDER, VIDEO_OUTPUT_FOLDER,
    VALID_VIDEO_EXTENSIONS, DEFAULT_OUTPUT_FILENAME_SUFFIX,
    OUTPUT_VIDEO_EXTENSION) # Nueva importación

def find_video_file(input_folder, valid_extensions):
    """
    Busca exactamente un archivo de video en la carpeta especificada.

    Args:
    input_folder (str): Ruta a la carpeta de entrada.
    valid_extensions (tuple): Tupla con las extensiones de video válidas (ej: ('.mp4', '.avi')).

    Returns:
    str: La ruta completa al archivo de video encontrado.
    None: Si no se encuentra exactamente un archivo de video.
    """

    if not os.path.isdir(input_folder):
        print(f"Error: La carpeta de entrada '{input_folder}' no existe.")
        return None

    video_files_found = []
    try:
        for filename in os.listdir(input_folder):
            # Comprobar si la extensión es válida (insensible a mayúsculas/minúsculas)
            if filename.lower().endswith(valid_extensions):
                video_files_found.append(filename)
    except OSError as e:
        print(f"Error al leer la carpeta '{input_folder}': {e}")
        return None


    if len(video_files_found) == 0:
        print(f"Error: No se encontraron archivos de video ({'/'.join(valid_extensions)}) en la carpeta '{input_folder}'.")
        return None
    elif len(video_files_found) > 1:
        print(f"Error: Se encontró más de un archivo de video en '{input_folder}'.")
        print("Por favor, asegúrate de que haya solo un archivo de video en esa carpeta.")
        print("Archivos encontrados:")
        for vf in video_files_found:
            print(f"- {vf}")
        return None
    else:
        # Se encontró exactamente un archivo
        video_filename = video_files_found[0]
        full_path = os.path.join(input_folder, video_filename)
        print(f"Video encontrado: {full_path}")
        return full_path


def main():
    """Función principal que orquesta el proceso."""
    # Argument Parser
    parser = argparse.ArgumentParser(
        description='Rastrea una pelota blanca en un video encontrado en la carpeta '
                    f'"{VIDEO_INPUT_FOLDER}", analiza su movimiento y opcionalmente '
                    f'guarda un video con el tracking en "{VIDEO_OUTPUT_FOLDER}".'
    )
    parser.add_argument('--hide_video', action='store_true',
                        help='No mostrar la ventana de video durante el procesamiento.')
    parser.add_argument('--no_save_csv', action='store_true',
                        help='No guardar los datos en un archivo CSV en la carpeta '
                             f'"{VIDEO_OUTPUT_FOLDER}".')
    parser.add_argument('--no_save_video', action='store_true', # Nuevo argumento
                        help='No guardar el video con el tracking en la carpeta '
                             f'"{VIDEO_OUTPUT_FOLDER}".')
    parser.add_argument('--output_suffix', type=str, default=DEFAULT_OUTPUT_FILENAME_SUFFIX,
                        help=f'Sufijo para el archivo CSV de salida (por defecto: {DEFAULT_OUTPUT_FILENAME_SUFFIX}).')

    args = parser.parse_args()

    start_time = time.time()

    # --- Encontrar el archivo de video ---
    print(f"--- Buscando video en '{VIDEO_INPUT_FOLDER}' ---")
    video_full_path = find_video_file(VIDEO_INPUT_FOLDER, VALID_VIDEO_EXTENSIONS)

    if video_full_path is None:
        sys.exit(1) # Salir si no se encontró el video correctamente

    # --- Preparar nombres y carpeta de salida ---
    video_filename_base = os.path.splitext(os.path.basename(video_full_path))[0]
    output_csv_full_path = None
    output_video_full_path = None # Inicializar

    # Crear carpeta de salida si es necesario (para CSV o Video)
    should_create_output_folder = not args.no_save_csv or not args.no_save_video
    if should_create_output_folder:
        try:
            os.makedirs(VIDEO_OUTPUT_FOLDER, exist_ok=True)
            print(f"Carpeta de salida: '{VIDEO_OUTPUT_FOLDER}'")

            # Construir ruta CSV si se va a guardar
            if not args.no_save_csv:
                output_csv_filename = video_filename_base + args.output_suffix
                output_csv_full_path = os.path.join(VIDEO_OUTPUT_FOLDER, output_csv_filename)

            # Construir ruta Video si se va a guardar
            if not args.no_save_video:
                # Usar extensión definida en config.py
                output_video_filename = video_filename_base + '_tracked' + OUTPUT_VIDEO_EXTENSION
                output_video_full_path = os.path.join(VIDEO_OUTPUT_FOLDER, output_video_filename)

        except OSError as e:
            print(f"Error al crear la carpeta de salida '{VIDEO_OUTPUT_FOLDER}': {e}")
            print("Los resultados (CSV y/o Video) no se guardarán.")
            args.no_save_csv = True # Forzar no guardar si no se puede crear la carpeta
            args.no_save_video = True


    # --- Iniciar Tracking ---
    print("\n--- Iniciando Tracking ---")
    tracker = BallTracker()
    # Pasar la ruta del video de salida al tracker
    tracking_data = tracker.track(video_full_path,
                                  output_video_path=output_video_full_path, # Pasar la ruta
                                  show_video=not args.hide_video)

    if tracking_data is None:
        print("Error fatal durante la inicialización del tracker (¿problema con el archivo?).")
        sys.exit(1)

    if not tracking_data:
        print("No se detectaron puntos de la pelota. No se realizará análisis ni guardado.")
        end_time = time.time()
        print(f"\nProceso terminado en {end_time - start_time:.2f} segundos (sin detección).")
        return # Salir si no hay datos

    # --- Calcular Cinemática ---
    print("\n--- Calculando Cinemática ---")
    # Pasar los FPS reales obtenidos del video para cálculos más precisos
    # (Asumiendo que analysis.py puede usarlo, si no, se usa el 'time' ya calculado)
    # kinematics_df = calculate_kinematics(tracking_data, fps=tracker.fps) # Modificación opcional en analysis.py
    kinematics_df = calculate_kinematics(tracking_data) # Usando la versión actual de analysis.py

    # --- Mostrar DataFrame (opcional) ---
    print("\nDataFrame con datos cinemáticos (primeras 5 filas):")
    print(kinematics_df.head())

    # --- Guardar Resultados CSV ---
    if not args.no_save_csv and output_csv_full_path: # Verificar que la ruta se construyó
        try:
            kinematics_df.to_csv(output_csv_full_path, index=False, float_format='%.5f')
            print(f"\nDatos CSV guardados exitosamente en: {output_csv_full_path}")
        except Exception as e:
            print(f"\nError al guardar el archivo CSV en {output_csv_full_path}: {e}")
    elif not args.no_save_csv:
         print("\nNo se guardó el archivo CSV (no se pudo determinar la ruta o crear la carpeta).")


    # --- Generar Gráficos ---
    # Verificar si hay datos suficientes para graficar (al menos velocidad)
    if 'vx' in kinematics_df.columns and not kinematics_df['vx'].isnull().all():
        print("\n--- Generando Gráficos ---")
        # Asumiendo que plotting.py existe y tiene la función plot_kinematics
        try:
            from programa.plotting import plot_kinematics
            # Pasar el nombre base para guardar los gráficos con nombre relacionado
            plot_kinematics(kinematics_df, output_folder=VIDEO_OUTPUT_FOLDER, base_filename=video_filename_base)
        except ImportError:
            print("Advertencia: No se encontró el módulo 'programa.plotting'. No se generarán gráficos.")
        except Exception as e:
            print(f"Error al generar gráficos: {e}")
    else:
        print("\nNo hay suficientes datos cinemáticos para generar gráficos.")


    end_time = time.time()
    print(f"\nProceso completado exitosamente en {end_time - start_time:.2f} segundos.")


if __name__ == "__main__":
    main()