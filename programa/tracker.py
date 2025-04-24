# tracker.py
"""
Contiene la clase BallTracker responsable de procesar el video
y detectar la posición de la pelota usando SimpleBlobDetector de OpenCV.
"""
import cv2
import numpy as np
import time
import os

# Importar configuración
from programa.config import (GAUSSIAN_BLUR_KERNEL_SIZE, MORPH_ITERATIONS, DISPLAY_SIZE,
    FONT, FONT_SCALE, FONT_COLOR_INFO, FONT_COLOR_DETECTED,
    FONT_COLOR_NOT_DETECTED, FONT_THICKNESS, CIRCLE_COLOR, CIRCLE_THICKNESS,
    OUTPUT_VIDEO_CODEC, OUTPUT_VIDEO_EXTENSION,
    # Parámetros Blob Detector
    FILTER_BY_COLOR, BLOB_COLOR, LOWER_YELLOW_HSV, UPPER_YELLOW_HSV,
    FILTER_BY_AREA, MIN_AREA, MAX_AREA,
    FILTER_BY_CIRCULARITY, MIN_CIRCULARITY, MAX_CIRCULARITY,
    FILTER_BY_CONVEXITY, MIN_CONVEXITY, MAX_CONVEXITY,
    FILTER_BY_INERTIA, MIN_INERTIA_RATIO, MAX_INERTIA_RATIO)

class BallTracker:
    """
    Clase para rastrear una pelota usando SimpleBlobDetector de OpenCV.
    """
    def __init__(self):
        """Inicializa el tracker y configura el SimpleBlobDetector."""
        # Parámetros de preprocesamiento
        self.blur_ksize = GAUSSIAN_BLUR_KERNEL_SIZE
        self.morph_iter = MORPH_ITERATIONS

        # Parámetros de visualización
        self.display_size = DISPLAY_SIZE

        # Variables de estado
        self.cap = None
        self.fps = 30
        self.frame_width = 0
        self.frame_height = 0
        self.video_writer = None

        # --- Configurar SimpleBlobDetector ---
        params = cv2.SimpleBlobDetector_Params()

        # Cambiar umbrales (no los usamos si filtramos por color antes)
        # params.minThreshold = 10
        # params.maxThreshold = 200

        # Filtrar por Color/Intensidad
        params.filterByColor = FILTER_BY_COLOR # Usamos True para detectar en máscara HSV
        if FILTER_BY_COLOR:
             # Si filtramos por color HSV antes, le decimos al detector que busque
             # blobs de color "blanco" (255) en la máscara binaria resultante.
             params.blobColor = 255
        else:
             # Si no usamos máscara HSV, detecta en escala de grises.
             # BLOB_COLOR (0 o 255) define si busca oscuros o claros.
             params.blobColor = BLOB_COLOR

        # Filtrar por Área
        params.filterByArea = FILTER_BY_AREA
        params.minArea = MIN_AREA
        params.maxArea = MAX_AREA

        # Filtrar por Circularidad
        params.filterByCircularity = FILTER_BY_CIRCULARITY
        params.minCircularity = MIN_CIRCULARITY
        params.maxCircularity = MAX_CIRCULARITY

        # Filtrar por Convexidad
        params.filterByConvexity = FILTER_BY_CONVEXITY
        params.minConvexity = MIN_CONVEXITY
        params.maxConvexity = MAX_CONVEXITY

        # Filtrar por Inercia (Ratio)
        params.filterByInertia = FILTER_BY_INERTIA
        params.minInertiaRatio = MIN_INERTIA_RATIO
        params.maxInertiaRatio = MAX_INERTIA_RATIO

        # Crear el detector con los parámetros
        # Para OpenCV 3 y 4+
        ver = (cv2.__version__).split('.')
        if int(ver[0]) < 3 :
            self.detector = cv2.SimpleBlobDetector(params)
        else :
            self.detector = cv2.SimpleBlobDetector_create(params)

        print("SimpleBlobDetector inicializado con los siguientes filtros:")
        print(f"  Filter by Color: {params.filterByColor} (Blob Color: {params.blobColor if not FILTER_BY_COLOR else 'N/A - Using HSV Mask'})")
        print(f"  Filter by Area: {params.filterByArea} (Min: {params.minArea}, Max: {params.maxArea})")
        print(f"  Filter by Circularity: {params.filterByCircularity} (Min: {params.minCircularity}, Max: {params.maxCircularity})")
        print(f"  Filter by Convexity: {params.filterByConvexity} (Min: {params.minConvexity}, Max: {params.maxConvexity})")
        print(f"  Filter by Inertia: {params.filterByInertia} (Min: {params.minInertiaRatio}, Max: {params.maxInertiaRatio})")
        if FILTER_BY_COLOR:
             print(f"  Usando máscara HSV con rango: {LOWER_YELLOW_HSV} a {UPPER_YELLOW_HSV}")


    def _setup_video_capture(self, video_path):
        """Abre el video, obtiene FPS y dimensiones."""
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print(f"Error: No se pudo abrir el video en: {video_path}")
            return False
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Video abierto: {video_path} | FPS: {self.fps:.2f} | Tamaño: {self.frame_width}x{self.frame_height}")
        return True

    def _setup_video_writer(self, output_path):
        """Configura el VideoWriter."""
        if not output_path or self.frame_width == 0 or self.frame_height == 0:
            self.video_writer = None; return
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*OUTPUT_VIDEO_CODEC)
        self.video_writer = cv2.VideoWriter(output_path, fourcc, self.fps, (self.frame_width, self.frame_height))
        if self.video_writer.isOpened():
            print(f"Video de salida configurado en: {output_path}")
        else:
            print(f"Error: No se pudo abrir VideoWriter para: {output_path}")
            self.video_writer = None

    def _preprocess_and_detect(self, frame):
        """Preprocesa el frame y detecta blobs."""
        # Aplicar desenfoque
        blurred = cv2.GaussianBlur(frame, self.blur_ksize, 0)

        # Crear máscara HSV si se eligió filtrar por color
        if FILTER_BY_COLOR:
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, LOWER_YELLOW_HSV, UPPER_YELLOW_HSV)

            # Limpiar la máscara con operaciones morfológicas
            kernel = np.ones((5,5),np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=self.morph_iter)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=self.morph_iter)

            # El detector buscará blobs blancos en esta máscara
            # ¡Importante! SimpleBlobDetector espera que los blobs a detectar sean BLANCOS
            # y el fondo NEGRO. Nuestra máscara ya está así.
            image_to_detect_on = mask
            # Guardamos la máscara para visualización opcional
            self.current_mask = mask

        else:
            # Si no filtramos por color HSV, detectar en escala de grises
            gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
            # Si BLOB_COLOR es 0 (negro), invertimos la imagen
            # porque el detector busca blobs BLANCOS por defecto cuando filterByColor=True
            # aunque aquí filterByColor=False, parece funcionar mejor buscando blancos.
            # Si buscas objetos oscuros (blobColor=0), invierte la imagen gris.
            if BLOB_COLOR == 0:
                 image_to_detect_on = cv2.bitwise_not(gray)
            else:
                 image_to_detect_on = gray
            self.current_mask = None # No hay máscara explícita

        # Detectar blobs
        keypoints = self.detector.detect(image_to_detect_on)

        # Seleccionar el mejor keypoint (blob) si se detectan varios
        # Estrategia simple: el más grande (o podrías usar el más circular, etc.)
        best_keypoint = None
        if keypoints:
            # Ordenar por tamaño (área) descendente
            keypoints = sorted(keypoints, key=lambda kp: kp.size, reverse=True)
            best_keypoint = keypoints[0] # Tomar el más grande

        return best_keypoint # Retorna el KeyPoint o None

    def _draw_visualization(self, frame_to_draw, frame_number, timestamp, keypoint):
        """Dibuja la información de tracking (keypoint y texto) en el frame."""
        position = None
        radius = 0 # Aproximado

        if keypoint is not None:
            # Extraer posición (x, y) y tamaño (diámetro/2) del keypoint
            x = int(keypoint.pt[0])
            y = int(keypoint.pt[1])
            radius = int(keypoint.size / 2)
            position = (x, y)

            # Dibujar el keypoint detectado (OpenCV dibuja un círculo con cruz)
            # frame_to_draw = cv2.drawKeypoints(frame_to_draw, [keypoint], np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            # O dibujar nuestro propio círculo
            cv2.circle(frame_to_draw, position, radius, CIRCLE_COLOR, CIRCLE_THICKNESS)

            cv2.putText(frame_to_draw, f"Pos (px): ({x}, {y}) Sz: {keypoint.size:.1f}", (10, 50), FONT, FONT_SCALE, FONT_COLOR_DETECTED, FONT_THICKNESS)
        else:
            cv2.putText(frame_to_draw, "Pelota no detectada", (10, 50), FONT, FONT_SCALE, FONT_COLOR_NOT_DETECTED, FONT_THICKNESS)

        cv2.putText(frame_to_draw, f"Frame: {frame_number} Time: {timestamp:.2f}s FPS: {self.fps:.1f}", (10, 30), FONT, FONT_SCALE, FONT_COLOR_INFO, FONT_THICKNESS)

        # Preparar frame para mostrar en pantalla
        display_frame = frame_to_draw
        # Opcional: Mostrar la máscara si se usó
        display_combined = display_frame
        if self.current_mask is not None and self.display_size:
             mask_colored = cv2.cvtColor(self.current_mask, cv2.COLOR_GRAY2BGR)
             # Redimensionar ambos para combinar
             if len(self.display_size) == 2 and self.display_size[0] > 0 and self.display_size[1] > 0:
                  try:
                       display_frame_resized = cv2.resize(display_frame, self.display_size, interpolation=cv2.INTER_AREA)
                       mask_resized = cv2.resize(mask_colored, self.display_size, interpolation=cv2.INTER_NEAREST)
                       display_combined = np.hstack((display_frame_resized, mask_resized))
                  except Exception as e:
                       print(f"Error al redimensionar/combinar para display: {e}")
                       if len(self.display_size) == 2 and self.display_size[0] > 0 and self.display_size[1] > 0:
                           try: # Intenta redimensionar solo el frame
                               display_combined = cv2.resize(display_frame, self.display_size, interpolation=cv2.INTER_AREA)
                           except: pass # Usa original si todo falla
                       else: display_combined = display_frame # Usa original si display_size es inválido
             else: # Si display_size es inválido, mostrar solo frame original
                  display_combined = display_frame

        elif self.display_size: # Redimensionar solo el frame si no hay máscara
             if len(self.display_size) == 2 and self.display_size[0] > 0 and self.display_size[1] > 0:
                  try:
                       display_combined = cv2.resize(display_frame, self.display_size, interpolation=cv2.INTER_AREA)
                  except Exception as e:
                       print(f"Error al redimensionar para display: {e}")
             else:
                  print(f"Advertencia: DISPLAY_SIZE {self.display_size} inválido. Mostrando tamaño original.")


        return display_combined # Retorna el frame listo para mostrar

    def track(self, video_path, output_video_path=None, show_video=True):
        """
        Procesa el video, rastrea la pelota usando SimpleBlobDetector, guarda video
        y retorna datos.
        """
        if not self._setup_video_capture(video_path): return None

        if output_video_path:
            base, _ = os.path.splitext(output_video_path)
            output_video_path_corrected = base + OUTPUT_VIDEO_EXTENSION
            self._setup_video_writer(output_video_path_corrected)
        else: self.video_writer = None

        tracking_data = []
        frame_number = 0

        while True:
            ret, frame = self.cap.read()
            if not ret: break

            timestamp = frame_number / self.fps if self.fps > 0 else 0

            # Preprocesar y detectar el blob (pelota)
            best_keypoint = self._preprocess_and_detect(frame)

            # Crear copia para dibujar
            frame_to_draw_on = frame.copy()

            # Dibujar visualización
            display_output_frame = self._draw_visualization(frame_to_draw_on, frame_number, timestamp, best_keypoint)

            # Guardar datos si se detectó
            if best_keypoint is not None:
                tracking_data.append({
                    'frame': frame_number,
                    'x': int(best_keypoint.pt[0]),
                    'y': int(best_keypoint.pt[1]),
                    'time': timestamp
                })

            # Escribir video de salida
            if self.video_writer is not None and self.video_writer.isOpened():
                # Escribir el frame CON las anotaciones
                self.video_writer.write(frame_to_draw_on)

            # Mostrar ventana
            if show_video:
                cv2.imshow("Tracking (Blob Detector) - Pelota ('q' para salir)", display_output_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'): break

            frame_number += 1

        # --- Limpieza ---
        self.cap.release()
        if self.video_writer is not None: self.video_writer.release()
        if show_video: cv2.destroyAllWindows()

        if not tracking_data: print("Advertencia: No se detectó la pelota en ningún frame usando Blob Detector.")
        else: print(f"Tracking (Blob Detector) completado. Se registraron {len(tracking_data)} puntos.")

        return tracking_data