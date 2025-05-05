import cv2
import sys
import os
import numpy as np
import pandas as pd

# ----------------------------------------
# CONFIGURACIÓN
# ----------------------------------------
video_path       = "./video/entrada/PeloAz.mp4"
output_path      = "./video_salida.mp4"
tracker_types    = ['BOOSTING','MIL','KCF','TLD','MEDIANFLOW','GOTURN','MOSSE','CSRT']
tracker_type     = tracker_types[7]    # CSRT
mostrar_ventana  = True                # True para selectROI + imshow, False para sólo archivo
bbox_defecto     = (287, 23, 86, 320)  # Sólo usado si mostrar_ventana=False
delay_segmento_s = 0.0                 # 0.2 segundos antes de pedir ROI

# Parámetros de conversión
px_to_m = 0.01       # metros por píxel (calibrar según vídeo)

# Colores para vectores
color_pos = (255, 0, 0)    # Azul: posición (flecha)
color_vel = (0, 255, 0)    # Verde: velocidad
color_acc = (0, 0, 255)    # Rojo: aceleración

# Factor de escala unificado
scale_vel = 10.0    # escala velocidad
scale_acc = 10.0    # escala aceleración

# Comprueba versión de OpenCV
(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

# Crea el tracker
if int(minor_ver) < 3:
    tracker = cv2.Tracker_create(tracker_type)
else:
    if   tracker_type == 'BOOSTING':    tracker = cv2.TrackerBoosting_create()
    elif tracker_type == 'MIL':         tracker = cv2.TrackerMIL_create()
    elif tracker_type == 'KCF':         tracker = cv2.TrackerKCF_create()
    elif tracker_type == 'TLD':         tracker = cv2.TrackerTLD_create()
    elif tracker_type == 'MEDIANFLOW':  tracker = cv2.TrackerMedianFlow_create()
    elif tracker_type == 'GOTURN':      tracker = cv2.TrackerGOTURN_create()
    elif tracker_type == 'MOSSE':       tracker = cv2.TrackerMOSSE_create()
    elif tracker_type == 'CSRT':        tracker = cv2.TrackerCSRT_create()

# Abre el vídeo
target = cv2.VideoCapture(video_path)
if not target.isOpened():
    print("No se pudo abrir el video:", video_path)
    sys.exit()

# Propiedades
width     = int(target.get(cv2.CAP_PROP_FRAME_WIDTH))
height    = int(target.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps_input = target.get(cv2.CAP_PROP_FPS) or 30.0
frames_a_saltar = int(fps_input * delay_segmento_s)

dt = 1.0 / fps_input  # tiempo entre frames

# Almacenamiento de datos
data = []  # lista de dicts por frame

# VideoWriter
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out    = cv2.VideoWriter(output_path, fourcc, fps_input, (width, height))

# Salta primeros frames
for _ in range(frames_a_saltar):
    ret, _ = target.read()
    if not ret:
        print("El vídeo es más corto que", delay_segmento_s, "segundos")
        sys.exit()

# Lee frame para ROI
ok, frame_roi = target.read()
if not ok:
    print("No se pudo leer el frame para selección de ROI")
    sys.exit()

# Selección de ROI
if mostrar_ventana:
    cv2.imshow("Selecciona la pelota (0.2s)", frame_roi)
    bbox = cv2.selectROI("Selecciona la pelota (0.2s)", frame_roi, False)
    cv2.destroyWindow("Selecciona la pelota (0.2s)")
else:
    bbox = bbox_defecto

# Inicializa tracker
tracker.init(frame_roi, bbox)

# Variables de cinemática
dt = 1.0 / fps_input
prev_center = None
prev_velocity = np.array([0.0, 0.0])
frame_idx = 0

# Procesa y almacena datos
def store_frame(frame_idx, center, velocity, acceleration):
    vx_m = velocity[0] * px_to_m
    vy_m = velocity[1] * px_to_m
    ax_m = acceleration[0] * px_to_m
    ay_m = acceleration[1] * px_to_m
    data.append({
        'frame': frame_idx,
        'x_px': center[0], 'y_px': center[1],
        'vx_px_s': velocity[0], 'vy_px_s': velocity[1],
        'ax_px_s2': acceleration[0], 'ay_px_s2': acceleration[1],
        'vx_m_s': vx_m, 'vy_m_s': vy_m,
        'ax_m_s2': ax_m, 'ay_m_s2': ay_m
    })

# Primer frame
tx = int(bbox[0] + bbox[2]/2)
ty = int(bbox[1] + bbox[3]/2)
store_frame(frame_idx, np.array([tx, ty]), np.array([0.0,0.0]), np.array([0.0,0.0]))
out.write(frame_roi)
frame_idx += 1

# Bucle principal
while True:
    ok, frame = target.read()
    if not ok: break

    ok, bbox = tracker.update(frame)
    cx = int(bbox[0] + bbox[2]/2)
    cy = int(bbox[1] + bbox[3]/2)
    center = np.array([cx, cy], dtype=float)

    # Cinemática
    if prev_center is not None:
        velocity = (center - prev_center) / dt
        acceleration = (velocity - prev_velocity) / dt
    else:
        velocity = prev_velocity.copy()
        acceleration = np.array([0.0, 0.0])

    # Almacena datos con conversión
    store_frame(frame_idx, center, velocity, acceleration)

    # Dibujo vectores
    cv2.arrowedLine(frame, (0,0), (cx,cy), color_pos, 2, tipLength=0.05)
    end_vel = (int(cx + velocity[0]*scale_vel/fps_input), int(cy + velocity[1]*scale_vel/fps_input))
    end_acc = (int(cx + acceleration[0]*scale_acc/fps_input**2), int(cy + acceleration[1]*scale_acc/fps_input**2))
    cv2.arrowedLine(frame, (cx,cy), end_vel, color_vel, 2, tipLength=0.2)
    cv2.arrowedLine(frame, (cx,cy), end_acc, color_acc, 2, tipLength=0.2)

    prev_center = center
    prev_velocity = velocity
    frame_idx += 1

    out.write(frame)

# Limpieza
target.release()
out.release()
if mostrar_ventana: cv2.destroyAllWindows()

# Genera DataFrame y CSV
df = pd.DataFrame(data)
csv_dir = "./csv_output"
os.makedirs(csv_dir, exist_ok=True)
csv_path = os.path.join(csv_dir, 'datos_por_frame.csv')
df.to_csv(csv_path, index=False)

print(f"✅ CSV guardado en: {csv_path}")
print(f"✅ Proceso completado. Video guardado en: {output_path}")
