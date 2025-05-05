# tracker.py
"""
Módulo para realizar el seguimiento de objetos en un video usando OpenCV.
Se ha reforzado la creación del tracker CSRT y validación del ROI.
"""
import cv2
import sys
import time  # Para obtener timestamps más precisos

# Diccionario para crear trackers de OpenCV
# Ahora CSRT usa explícitamente legacy si está disponible
TRACKER_TYPES = {
    'BOOSTING': lambda: cv2.legacy.TrackerBoosting_create(),
    'MIL': lambda: cv2.TrackerMIL_create(),
    'KCF': lambda: cv2.legacy.TrackerKCF_create(),
    'TLD': lambda: cv2.legacy.TrackerTLD_create(),
    'MEDIANFLOW': lambda: cv2.legacy.TrackerMedianFlow_create(),
    'MOSSE': lambda: cv2.legacy.TrackerMOSSE_create(),
    'CSRT': lambda: cv2.legacy.TrackerCSRT_create() if hasattr(cv2, 'legacy') else cv2.TrackerCSRT_create()
}

def create_tracker(tracker_type):
    """Crea una instancia del tracker especificado con fallback para legacy."""
    if tracker_type in TRACKER_TYPES:
        try:
            tracker = TRACKER_TYPES[tracker_type]()
            print(f"Tracker {tracker_type} creado.")
            return tracker
        except Exception as e:
            print(f"Error al crear tracker {tracker_type}: {e}")
            sys.exit(1)
    else:
        print(f"Error: Tipo de tracker '{tracker_type}' no válido.")
        print("Tipos válidos:", list(TRACKER_TYPES.keys()))
        sys.exit(1)


def track_object_in_video(video_path, tracker_type_name, draw_bb=True, draw_center=True, draw_trail=False, trail_length=50):
    """
    Realiza el seguimiento de un objeto seleccionado en un video.
    Ahora valida el ROI y garantiza que esté dentro de los límites.
    """
    tracker = create_tracker(tracker_type_name)

    # Abrir el video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: No se pudo abrir el video en {video_path}")
        return None, None

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    print(f"Video FPS: {fps:.2f}")

    # Leer el primer frame
    ok, frame = cap.read()
    if not ok or frame is None:
        print("Error: No se pudo leer el primer frame del video.")
        cap.release()
        return None, None

    # --- Selección del Objeto (ROI) ---
    bbox = cv2.selectROI("Selecciona la Pelota y presiona ENTER", frame, False)
    cv2.destroyWindow("Selecciona la Pelota y presiona ENTER")

    # Validar ROI
    if not bbox or bbox == (0, 0, 0, 0):
        print("Selección cancelada o inválida.")
        cap.release()
        return None, None

    x, y, w, h = [int(v) for v in bbox]
    h_frame, w_frame = frame.shape[:2]
    if w <= 0 or h <= 0:
        print("Error: ROI seleccionada con ancho o alto cero.")
        cap.release()
        return None, None
    if x < 0 or y < 0 or x + w > w_frame or y + h > h_frame:
        print("Error: ROI fuera de los límites del frame.")
        cap.release()
        return None, None

    print(f"ROI inicial seleccionada: {(x, y, w, h)}")

    # Inicializar el tracker
    try:
        ok = tracker.init(frame, (x, y, w, h))
        if not ok:
            print("Error: Falló la inicialización del tracker con el ROI seleccionado.")
            cap.release()
            return None, None
        print("Tracker inicializado correctamente.")
    except Exception as e:
        print(f"Error durante la inicialización del tracker: {e}")
        cap.release()
        return None, None

    raw_tracking_data = []
    frame_count = 0
    trail_points = []

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Fin del video o error al leer frame.")
            break

        frame_count += 1
        timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        timer = cv2.getTickCount()
        ok, bbox = tracker.update(frame)
        processing_fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

        if ok:
            x, y, w, h = [int(v) for v in bbox]
            cx, cy = x + w // 2, y + h // 2
            raw_tracking_data.append((timestamp_ms, cx, cy, w, h))
            if draw_bb:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            if draw_center:
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
            if draw_trail:
                trail_points.append((cx, cy))
                if len(trail_points) > trail_length:
                    trail_points.pop(0)
                for i in range(1, len(trail_points)):
                    if trail_points[i - 1] is None:
                        continue
                    thickness = int(i / len(trail_points) * 5) + 1
                    cv2.line(frame, trail_points[i - 1], trail_points[i], (0, 0, 255), thickness)
            label_status, color_status = "Tracking", (0, 255, 0)
        else:
            raw_tracking_data.append((timestamp_ms, None, None, None, None))
            if draw_trail:
                trail_points.append(None)
                if len(trail_points) > trail_length:
                    trail_points.pop(0)
            label_status, color_status = "Tracking Failure", (0, 0, 255)

        cv2.putText(frame, f"Tracker: {tracker_type_name}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Status: {label_status}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_status, 2)
        cv2.putText(frame, f"FPS: {processing_fps:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Frame: {frame_count}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Salida solicitada por el usuario.")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Video y ventanas cerradas.")
    return raw_tracking_data, fps
