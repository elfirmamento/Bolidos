import cv2
import numpy as np
from collections import deque
import os
import time
from scipy.spatial.distance import cdist

def detect_meteors(video_path, output_folder, speed_factor=1, brightness_threshold=34, min_line_length=70, max_line_gap=10, trail_length=3, motion_threshold=30, curvature_threshold=0.1, velocity_threshold=100,threshold=25, min_area=300, brightness_delta_threshold=10):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = 1 / (fps * speed_factor)

    _, first_frame = cap.read()
    avg_frame = np.float32(first_frame)
    prev_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)

    frame_queue = deque(maxlen=trail_length)

    frame_count = 0
    events = []
    last_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Detección de cambios significativos
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_diff = cv2.absdiff(prev_frame, gray)
        _, motion_thresh = cv2.threshold(frame_diff, motion_threshold, 255, cv2.THRESH_BINARY)

        # Actualizar el frame anterior
        prev_frame = gray

        cv2.accumulateWeighted(frame, avg_frame, 0.01)
        background = cv2.convertScaleAbs(avg_frame)

        diff = cv2.absdiff(frame, background)
        _, thresh = cv2.threshold(diff, brightness_threshold, 255, cv2.THRESH_BINARY)
        edges = cv2.Canny(thresh, 50, 150, apertureSize=3)

        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=min_line_length, maxLineGap=max_line_gap)

        mask = np.zeros_like(frame)

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]

                # Calcular la curvatura de la línea
                curvature = np.abs((y2 - y1) / (x2 - x1 + 0.001))

                # Calcular la velocidad de la línea
                line_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                line_velocity = line_length / (1 / fps)

                # Verificar si la línea cumple con los criterios de meteoro
                if curvature < curvature_threshold and line_velocity > velocity_threshold:
                    cv2.line(mask, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    area = line_length
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2

                    # Verificar si hay movimiento significativo en la región de la línea
                    roi = motion_thresh[min(y1,y2):max(y1,y2), min(x1,x2):max(x1,x2)]
                    if np.sum(roi) > 0:
                        # Verificar si hay un destello repentino de brillo
                        brightness_delta = np.abs(int(gray[center_y, center_x]) - int(prev_frame[center_y, center_x]))
                        if brightness_delta > brightness_delta_threshold:
                            event = {
                                'frame': frame_count,
                                'time': frame_count / fps,
                                'area': area,
                                'position': (center_x, center_y),
                                'start': (x1, y1),
                                'end': (x2, y2),
                                'curvature': curvature,
                                'velocity': line_velocity,
                                'brightness_delta': brightness_delta
                            }
                            events.append(event)

                            # Guardar imagen del evento
                            event_image = frame.copy()
                            cv2.line(event_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.circle(event_image, (center_x, center_y), 5, (0, 0, 255), -1)
                            image_filename = f"{output_folder}/event_{frame_count}.jpg"
                            cv2.imwrite(image_filename, event_image)

        frame_queue.append(mask)

        combined_mask = np.zeros_like(frame)
        for i, past_frame in enumerate(frame_queue):
            alpha = (i + 1) / len(frame_queue)
            combined_mask = cv2.addWeighted(combined_mask, 1, past_frame, alpha, 0)

        result = cv2.addWeighted(frame, 1, combined_mask, 0.5, 0)

        # Mostrar la máscara de movimiento
        cv2.imshow('Motion Detection', motion_thresh)
        cv2.imshow('Meteor Detection', result)

        # Control de velocidad
        time_elapsed = time.time() - last_time
        if time_elapsed < frame_interval:
            time.sleep(frame_interval - time_elapsed)
        last_time = time.time()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Guardar información de eventos en un archivo
    with open(f"{output_folder}/events_info.txt", "w") as f:
        for event in events:
            f.write(f"Frame: {event['frame']}, Time: {event['time']:.2f}s, Area: {event['area']:.2f}, Position: {event['position']}, Curvature: {event['curvature']:.2f}, Velocity: {event['velocity']:.2f}, Brightness Delta: {event['brightness_delta']}\n")

    return events

# Uso del programa
video_path = 'video5.mp4'
output_folder = 'eventos_detectados'
speed_factor = 1  # Reproducir a velocidad normal

detected_events = detect_meteors(video_path, output_folder, speed_factor=speed_factor)

print(f"Se detectaron {len(detected_events)} eventos de meteoros.")
print(f"Las imágenes y la información de los eventos se han guardado en la carpeta: {output_folder}")
