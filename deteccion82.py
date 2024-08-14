import cv2
import numpy as np
import os
from datetime import datetime

def detect_events(video_path, output_folder, ignore_region_x=1800, ignore_region_y=1000, speed_multiplier=1):
    # Crear carpeta de eventos si no existe
    events_folder = os.path.join(output_folder, "Eventos")
    os.makedirs(events_folder, exist_ok=True)

    # Abrir el video
    cap = cv2.VideoCapture(video_path)

    # Obtener propiedades del video
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Preparar el primer frame
    ret, prev_frame = cap.read()
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    event_count = 0

    # Abrir archivo de log
    with open(os.path.join(output_folder, "eventos_log.txt"), "w") as log_file:
        for frame_num in range(1, frame_count):
            # Leer el siguiente frame
            ret, current_frame = cap.read()
            if not ret:
                break

            # Convertir a escala de grises
            current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

            # Calcular la diferencia entre frames
            frame_diff = cv2.absdiff(current_gray, prev_gray)

            # Aplicar umbral para detectar cambios significativos
            _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)

            # Crear una máscara para ignorar las regiones especificadas
            mask = np.ones_like(thresh)
            mask[:, ignore_region_x:] = 0
            mask[ignore_region_y:, :] = 0

            # Aplicar la máscara
            thresh = cv2.bitwise_and(thresh, thresh, mask=mask)

            # Encontrar contornos
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                # Filtrar contornos pequeños
                if cv2.contourArea(contour) > 50:
                    # Obtener bounding box
                    x, y, w, h = cv2.boundingRect(contour)

                    # Verificar si el contorno está completamente fuera de las regiones ignoradas
                    if x + w <= ignore_region_x and y + h <= ignore_region_y:
                        event_count += 1

                        # Calcular tiempo del evento
                        event_time = frame_num / fps

                        # Guardar información en el log
                        log_info = f"Evento {event_count}: Frame {frame_num}, Tiempo {event_time:.2f}s, Área {cv2.contourArea(contour):.2f}, Posición ({x}, {y})\n"
                        log_file.write(log_info)

                        # Guardar imagen del evento
                        event_image = current_frame.copy()
                        cv2.rectangle(event_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        event_filename = os.path.join(events_folder, f"evento_{event_count}.jpg")
                        cv2.imwrite(event_filename, event_image)

            # Mostrar frame con líneas de regiones ignoradas
            cv2.line(current_frame, (ignore_region_x, 0), (ignore_region_x, frame_height), (0, 0, 255), 2)
            cv2.line(current_frame, (0, ignore_region_y), (frame_width, ignore_region_y), (0, 0, 255), 2)
            cv2.imshow('Video', current_frame)

            # Control de reproducción
            wait_time = int(1000 / (fps * speed_multiplier))
            key = cv2.waitKey(wait_time) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('+'):
                speed_multiplier *= 1.5
            elif key == ord('-'):
                speed_multiplier /= 1.5

            # Actualizar frame anterior
            prev_gray = current_gray

    cap.release()
    cv2.destroyAllWindows()

# Ejemplo de uso
video_path = "video1.mp4"
output_folder = "eventos"
ignore_region_x = 1800  # Puedes modificar este valor según sea necesario
ignore_region_y = 1000  # Puedes modificar este valor según sea necesario
detect_events(video_path, output_folder, ignore_region_x, ignore_region_y)
