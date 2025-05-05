# main.py
"""
Script principal con medición automática de tamaño en píxeles al seleccionar ROI
y solicitud del tamaño real en metros.
"""
import tracker
import data_processor
import plotter
import config


def run_tracker_analysis():
    print("Iniciando el análisis de seguimiento de baloncesto con medición automática de píxeles...")

    # --- Paso 1: Tracking y medición de píxeles ---
    raw_data, video_fps, ref_pixels = tracker.track_and_measure(
        config.VIDEO_PATH,
        config.TRACKER_TYPE,
        draw_bb=config.DRAW_BOUNDING_BOX,
        draw_center=config.DRAW_CENTER,
        draw_trail=config.DRAW_TRAIL,
        trail_length=config.TRAIL_LENGTH
    )

    if raw_data is None:
        print("Error en track_and_measure. Saliendo.")
        return

    # Pedir al usuario el tamaño real en metros
    try:
        ref_meters = float(input("Introduce el diámetro real de la pelota en metros (por ej. 0.24): "))
    except ValueError:
        print("Valor no válido. Usando tamaño por defecto de 0.24 m.")
        ref_meters = config.REFERENCE_OBJECT_SIZE_METERS

    print(f"Usando referencia: {ref_pixels:.1f} px = {ref_meters:.3f} m")

    # --- Paso 2: Procesar datos ---
    processed_df = data_processor.process_tracking_data(
        raw_data,
        video_fps,
        ref_pixels,
        ref_meters
    )
    if processed_df is None:
        print("Error en process_tracking_data. Saliendo.")
        return

    # --- Paso 3: Guardar CSV y graficar ---
    data_processor.save_data_to_csv(processed_df, config.OUTPUT_CSV)
    plotter.plot_kinematics(processed_df)


if __name__ == "__main__":
    run_tracker_analysis()