# main.py
"""
Script principal para el seguimiento de baloncesto, procesamiento de datos y visualización.
"""
import tracker
import data_processor
import plotter
import config # Importa la configuración

def run_tracker_analysis():
    """Función principal que ejecuta todo el proceso."""
    print("Iniciando el análisis de seguimiento de baloncesto...")

    # --- Paso 1: Realizar el seguimiento del objeto ---
    print(f"\nUsando el video: {config.VIDEO_PATH}")
    print(f"Usando el tracker: {config.TRACKER_TYPE}")
    # Ejecutar el tracker para obtener datos crudos y FPS
    raw_data, video_fps = tracker.track_object_in_video(
        config.VIDEO_PATH,
        config.TRACKER_TYPE,
        draw_bb=config.DRAW_BOUNDING_BOX,
        draw_center=config.DRAW_CENTER,
        draw_trail=config.DRAW_TRAIL,
        trail_length=config.TRAIL_LENGTH
    )

    if raw_data is None or video_fps is None:
        print("El proceso de seguimiento falló o fue cancelado. Saliendo.")
        return # Salir si el tracking no funcionó

    if not raw_data:
        print("El tracker no devolvió ningún dato. Saliendo.")
        return

    print(f"\nSeguimiento completado. Se obtuvieron {len(raw_data)} puntos de datos crudos.")

    # --- Paso 2: Procesar los datos ---
    print("\nProcesando los datos de seguimiento...")
    print(f"Usando objeto de referencia: {config.REFERENCE_OBJECT_SIZE_PIXELS} píxeles = {config.REFERENCE_OBJECT_SIZE_METERS} metros")
    processed_df = data_processor.process_tracking_data(
        raw_data,
        video_fps,
        config.REFERENCE_OBJECT_SIZE_PIXELS,
        config.REFERENCE_OBJECT_SIZE_METERS
    )

    if processed_df is None or processed_df.empty:
        print("El procesamiento de datos falló o no generó resultados válidos. Saliendo.")
        return

    print("Procesamiento de datos completado.")

    # --- Paso 3: Guardar los datos procesados en CSV ---
    print(f"\nIntentando guardar los datos procesados en: {config.OUTPUT_CSV}")
    save_success = data_processor.save_data_to_csv(processed_df, config.OUTPUT_CSV)
    if not save_success:
        print("Advertencia: No se pudieron guardar los datos en CSV.")
        # Continuar de todos modos para mostrar gráficos si es posible

    # --- Paso 4: Generar y mostrar gráficos ---
    print("\nGenerando gráficos de cinemática...")
    plotter.plot_kinematics(processed_df)

    print("\nAnálisis de seguimiento de baloncesto finalizado.")

# --- Punto de Entrada del Script ---
if __name__ == "__main__":
    # Verificar dependencias (opcional pero útil)
    try:
        import cv2
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        print(f"OpenCV version: {cv2.__version__}")
        print(f"Pandas version: {pd.__version__}")
        print(f"NumPy version: {np.__version__}")
        print(f"Matplotlib version: {plt.matplotlib.__version__}")
         # Comprobar si se necesita opencv-contrib-python
        if hasattr(cv2, 'legacy'):
            print("Módulo 'legacy' de OpenCV encontrado (necesario para algunos trackers).")
        if config.TRACKER_TYPE in ['BOOSTING', 'TLD', 'MEDIANFLOW', 'MOSSE'] and not hasattr(cv2, 'legacy'):
             print(f"Advertencia: El tracker {config.TRACKER_TYPE} podría requerir 'opencv-contrib-python'. Instálalo con: pip install opencv-contrib-python")

    except ImportError as e:
        print(f"Error: Falta una dependencia - {e}")
        print("Asegúrate de instalar todas las bibliotecas necesarias:")
        print("pip install opencv-python pandas numpy matplotlib")
        # Potencialmente también: pip install opencv-contrib-python
        exit()

    run_tracker_analysis()