# tracker.py
"""
Módulo para realizar el seguimiento de objetos en un video usando OpenCV,
con función adicional para medir automáticamente el tamaño de referencia en píxeles.
"""
import cv2
import sys
import time

# --- Función para crear trackers ---
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
    if tracker_type not in TRACKER_TYPES:
        print(f"Error: Tipo de tracker '{tracker_type}' no válido.")
        sys.exit(1)
    try:
        tracker = TRACKER_TYPES[tracker_type]()
        print(f"Tracker {tracker_type} creado.")
        return tracker
    except Exception as e:
        print(f"Error al crear tracker {tracker_type}: {e}")
        sys.exit(1)


def track_and_measure(video_path, tracker_type_name, draw_bb=True, draw_center=True, draw_trail=False, trail_length=50):
    # Abrir video y primer frame
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: no se pudo abrir el video '{video_path}'")
        return None, None, None
    fps = cap.get(cv2.CAP_PROP_FPS) or 59.0
    ok, frame = cap.read()
    if not ok or frame is None:
        print("Error: no se pudo leer el primer frame.")
        cap.release()
        return None, None, None

    # Seleccionar ROI para referencia y medición de píxeles
    bbox = cv2.selectROI("Selecciona la pelota y presiona ENTER", frame, False)
    cv2.destroyAllWindows()
    if not bbox or bbox == (0,0,0,0):
        print("ROI inválida o cancelada.")
        cap.release()
        return None, None, None
    x, y, w, h = [int(v) for v in bbox]
    ref_pixels = (w + h) / 2.0
    print(f"Medida de referencia: {ref_pixels:.1f} píxeles (promedio de w,h)")

    # Inicializar tracker
    tracker_instance = create_tracker(tracker_type_name)
    try:
        init_ok = tracker_instance.init(frame, bbox)
    except Exception as e:
        print(f"Error al inicializar tracker: {e}")
        cap.release()
        return None, None, None
    if not init_ok:
        print("Error: init del tracker falló.")
        cap.release()
        return None, None, None

    # Bucle de tracking
    raw_data = []
    trail = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
        ok, bb = tracker_instance.update(frame)
        if ok:
            x, y, w, h = [int(v) for v in bb]
            cx, cy = x + w//2, y + h//2
            raw_data.append((timestamp, cx, cy, w, h))
            if draw_bb:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255,0,0), 2)
            if draw_center:
                cv2.circle(frame, (cx, cy), 5, (0,255,0), -1)
        else:
            raw_data.append((timestamp, None, None, None, None))

        cv2.imshow("Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return raw_data, fps, ref_pixels


def track_object_in_video(*args, **kwargs):
    # Mantener compatibilidad si se usa elsewhere
    data = track_and_measure(*args, **kwargs)
    if data is None:
        return None, None
    raw, fps, _ = data
    return raw, fps
