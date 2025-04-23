# tracker.py
"""
Contiene la clase BallTracker responsable de procesar el video
y detectar la posición de la pelota.
"""
import cv2
import numpy as np
import time # Solo para la interrupción por 'q'
import os # Para obtener info del path

# Importar configuración
from programa.config import (LOWER_WHITE_HSV, UPPER_WHITE_HSV, MIN_CONTOUR_AREA,
    MAX_CONTOUR_AREA, GAUSSIAN_BLUR_KERNEL_SIZE, MORPH_ITERATIONS,
    DISPLAY_SIZE, FONT, FONT_SCALE, FONT_COLOR_INFO,
    FONT_COLOR_DETECTED, FONT_COLOR_NOT_DETECTED, FONT_THICKNESS,
    CIRCLE_RADIUS, CIRCLE_COLOR, CIRCLE_THICKNESS,
    OUTPUT_VIDEO_CODEC, OUTPUT_VIDEO_EXTENSION) # Nuevas importaciones

class BallTracker:
    """
    Clase para rastrear una pelota blanca en un video usando OpenCV.
    """
    def __init__(self):
        """Inicializa el tracker con los parámetros de configuración."""
        self.lower_hsv = LOWER_WHITE_HSV
        self.upper_hsv = UPPER_WHITE_HSV
        self.min_area = MIN_CONTOUR_AREA
        self.max_area = MAX_CONTOUR_AREA
        self.blur_ksize = GAUSSIAN_BLUR_KERNEL_SIZE
        self.morph_iter = MORPH_ITERATIONS
        self.display_size = DISPLAY_SIZE

        self.cap = None
        self.fps = 30 # Valor por defecto
        self.frame_width = 0
        self.frame_height = 0
        self.video_writer = None # Para guardar el video de salida

    def _setup_video_capture(self, video_path):
        """Abre el video, obtiene FPS y dimensiones."""
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print(f"Error: No se pudo abrir el video en: {video_path}")
            return False

        fps_read = self.cap.get(cv2.CAP_PROP_FPS)
        if fps_read and fps_read > 0:
            self.fps = fps_read
        else:
            print(f"Advertencia: No se pudo obtener FPS. Usando {self.fps} FPS.")

        # Obtener dimensiones del frame
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if self.frame_width == 0 or self.frame_height == 0:
             print(f"Advertencia: No se pudieron obtener las dimensiones del video.")
             # Podríamos intentar leer un frame para obtenerlas, pero por ahora solo advertimos

        print(f"Video abierto: {video_path} | FPS: {self.fps:.2f} | Tamaño: {self.frame_width}x{self.frame_height}")
        return True

    def _setup_video_writer(self, output_path):
        """Configura el VideoWriter para guardar el video procesado."""
        if not output_path or self.frame_width == 0 or self.frame_height == 0:
            print("Advertencia: No se guardará el video de salida (ruta no especificada o dimensiones inválidas).")
            self.video_writer = None
            return

        # Asegurarse de que la carpeta de salida exista (aunque main.py ya lo hace)
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except OSError as e:
                print(f"Error al crear directorio para video de salida '{output_dir}': {e}")
                self.video_writer = None
                return

        # Determinar el códec basado en la configuración
        fourcc = cv2.VideoWriter_fourcc(*OUTPUT_VIDEO_CODEC)
        try:
            self.video_writer = cv2.VideoWriter(output_path, fourcc, self.fps, (self.frame_width, self.frame_height))
            if not self.video_writer.isOpened():
                 print(f"Error: No se pudo abrir VideoWriter para: {output_path}")
                 self.video_writer = None
            else:
                 print(f"Video de salida configurado en: {output_path} con códec {OUTPUT_VIDEO_CODEC}")
        except Exception as e:
            print(f"Excepción al crear VideoWriter: {e}")
            self.video_writer = None


    def _preprocess_frame(self, frame):
        """Aplica desenfoque y conversión a HSV."""
        blurred = cv2.GaussianBlur(frame, self.blur_ksize, 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        return hsv

    def _find_ball_contour(self, hsv_frame):
        """Encuentra el contorno de la pelota basado en HSV y área."""
        mask = cv2.inRange(hsv_frame, self.lower_hsv, self.upper_hsv)
        # Aplicar morfología (erosión y dilatación) para eliminar ruido
        kernel = np.ones((5,5),np.uint8) # Kernel para morfología
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=self.morph_iter)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=self.morph_iter)
        # mask = cv2.erode(mask, None, iterations=self.morph_iter) # Original
        # mask = cv2.dilate(mask, None, iterations=self.morph_iter) # Original


        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_contour = None
        max_found_area = 0

        if contours:
            for contour in contours:
                area = cv2.contourArea(contour)
                # Filtrar por área
                if self.min_area < area < self.max_area:
                     # Opcional: Filtrar por circularidad si es necesario
                     # perimeter = cv2.arcLength(contour, True)
                     # if perimeter == 0: continue
                     # circularity = 4 * np.pi * (area / (perimeter * perimeter))
                     # if 0.7 < circularity < 1.3: # Ajustar umbrales de circularidad
                    if area > max_found_area: # Quedarse con el más grande dentro del rango
                        max_found_area = area
                        best_contour = contour

        return best_contour, mask

    def _get_ball_position(self, contour):
        """Calcula el centroide (x, y) del contorno."""
        if contour is None:
            return None

        M = cv2.moments(contour)
        if M["m00"] != 0:
            center_x = int(M["m10"] / M["m00"])
            center_y = int(M["m01"] / M["m00"])
            return (center_x, center_y)
        return None

    def _draw_visualization(self, frame_to_draw, mask, frame_number, timestamp, position):
        """
        Dibuja la información de tracking en el frame para visualización y/o guardado.
        Modifica frame_to_draw directamente.
        Retorna el frame combinado para mostrar si show_video es True.
        """
        # Dibujar en el frame original (que se guardará en el video)
        if position:
            x, y = position
            cv2.circle(frame_to_draw, (x, y), CIRCLE_RADIUS, CIRCLE_COLOR, CIRCLE_THICKNESS)
            cv2.putText(frame_to_draw, f"Pos (px): ({x}, {y})", (10, 50), FONT, FONT_SCALE, FONT_COLOR_DETECTED, FONT_THICKNESS)
        else:
            cv2.putText(frame_to_draw, "Pelota no detectada", (10, 50), FONT, FONT_SCALE, FONT_COLOR_NOT_DETECTED, FONT_THICKNESS)

        cv2.putText(frame_to_draw, f"Frame: {frame_number} Time: {timestamp:.2f}s FPS: {self.fps:.1f}", (10, 30), FONT, FONT_SCALE, FONT_COLOR_INFO, FONT_THICKNESS)

        # Preparar frames para mostrar en pantalla (si show_video es True)
        display_frame = frame_to_draw # Usar el frame ya modificado
        display_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) # Convertir máscara a BGR para hstack

        # Redimensionar para visualización si se especifica
        if self.display_size:
            # Asegurarse de que display_size tenga ancho y alto
            if len(self.display_size) == 2 and self.display_size[0] > 0 and self.display_size[1] > 0:
                try:
                    display_frame_resized = cv2.resize(display_frame, self.display_size, interpolation=cv2.INTER_AREA)
                    display_mask_resized = cv2.resize(display_mask, self.display_size, interpolation=cv2.INTER_NEAREST) # Nearest para la máscara
                    # Combinar frame redimensionado y máscara redimensionada
                    combined_display = np.hstack((display_frame_resized, display_mask_resized))
                except Exception as e:
                    print(f"Error al redimensionar para display: {e}")
                    # Fallback: mostrar solo el frame original sin redimensionar
                    combined_display = display_frame
            else:
                 print(f"Advertencia: DISPLAY_SIZE {self.display_size} inválido. Mostrando tamaño original.")
                 combined_display = np.hstack((display_frame, display_mask)) # Combinar originales si resize falla
        else:
            # Combinar frame original y máscara original si no hay display_size
            combined_display = np.hstack((display_frame, display_mask))

        return combined_display


    def track(self, video_path, output_video_path=None, show_video=True):
        """
        Procesa el video, rastrea la pelota, guarda el video de salida y retorna los datos.

        Args:
        video_path (str): Ruta al archivo de video de entrada.
        output_video_path (str, optional): Ruta para guardar el video con tracking.
                                           Si es None, no se guarda video. Defaults to None.
        show_video (bool): Si es True, muestra la ventana de visualización.

        Returns:
        list: Una lista de diccionarios, cada uno representando un punto
              detectado {'frame': int, 'x': int, 'y': int, 'time': float}.
              Retorna None si el video no se puede abrir.
              Retorna lista vacía si no se detecta la pelota.
        """
        if not self._setup_video_capture(video_path):
            return None # Error al abrir el video

        # Configurar el escritor de video si se proporcionó una ruta
        if output_video_path:
            # Asegurarse de que la extensión sea la correcta según config
            base, _ = os.path.splitext(output_video_path)
            output_video_path_corrected = base + OUTPUT_VIDEO_EXTENSION
            self._setup_video_writer(output_video_path_corrected)
        else:
            self.video_writer = None

        tracking_data = []
        frame_number = 0

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Fin del video o error al leer frame.")
                break

            timestamp = frame_number / self.fps if self.fps > 0 else 0

            # Crear una copia para dibujar, así el frame original no se modifica
            # si se necesitara para otra cosa (aunque aquí no parece ser el caso)
            frame_to_draw_on = frame.copy()

            hsv_frame = self._preprocess_frame(frame) # Usar frame original para procesar
            ball_contour, mask = self._find_ball_contour(hsv_frame)
            ball_position = self._get_ball_position(ball_contour)

            if ball_position:
                tracking_data.append({
                    'frame': frame_number,
                    'x': ball_position[0],
                    'y': ball_position[1], # Coordenada Y (generalmente aumenta hacia abajo en OpenCV)
                    'time': timestamp
                })

            # Dibujar visualizaciones en frame_to_draw_on
            # Esta función ahora también prepara el frame combinado para mostrar
            combined_display_frame = self._draw_visualization(frame_to_draw_on, mask, frame_number, timestamp, ball_position)

            # Escribir el frame con dibujos en el video de salida (si está configurado)
            if self.video_writer is not None and self.video_writer.isOpened():
                try:
                    self.video_writer.write(frame_to_draw_on) # Escribir el frame con las anotaciones
                except Exception as e:
                    print(f"Error al escribir frame {frame_number} en el video: {e}")
                    # Considerar cerrar el writer si hay errores persistentes
                    # self.video_writer.release()
                    # self.video_writer = None

            # Mostrar la ventana de visualización si está habilitado
            if show_video:
                cv2.imshow("Tracking - Pelota Blanca ('q' para salir)", combined_display_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Procesamiento interrumpido por el usuario.")
                    break

            frame_number += 1

        # --- Limpieza ---
        self.cap.release()
        if self.video_writer is not None and self.video_writer.isOpened():
            print("Liberando escritor de video...")
            self.video_writer.release()
        if show_video:
            cv2.destroyAllWindows()

        if not tracking_data:
            print("Advertencia: No se detectó la pelota en ningún frame.")
        else:
            print(f"Tracking completado. Se registraron {len(tracking_data)} puntos.")

        return tracking_data