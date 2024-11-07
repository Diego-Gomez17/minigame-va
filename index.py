import cv2
import mediapipe as mp
import random
import time
from screeninfo import get_monitors

import tkinter as tk
from tkinter import messagebox

# Obtén el tamaño de la pantalla principal
monitor = get_monitors()[0]
screen_width = monitor.width
screen_height = monitor.height

# Configuración del juego
num_circles = 10
circle_radius = 30
score = 0
circles = [] 

# Inicialización de MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Genera posiciones aleatorias para los círculos
for _ in range(num_circles):
    x = random.randint(circle_radius, screen_width - circle_radius)
    y = random.randint(circle_radius, screen_height - circle_radius)
    circles.append((x, y))

# Inicialización de la cámara
cap = cv2.VideoCapture(0)

# Configura la ventana de OpenCV para pantalla completa
cv2.namedWindow("Mini Juego", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Mini Juego", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

start_time = time.time()
game_duration = 30  # Duración del juego en segundos

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Voltea la imagen para que actúe como un espejo
    frame = cv2.flip(frame, 1)

    # Redimensiona el frame para que coincida con el tamaño de la pantalla
    frame = cv2.resize(frame, (screen_width, screen_height))

    # Convierte el marco de BGR a RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame) 

    # Dibuja los círculos en la pantalla
    for (cx, cy) in circles:
        cv2.circle(frame, (cx, cy), circle_radius, (0, 255, 0), -1)

    # Si se detecta una mano
    if results.multi_hand_landmarks: 
        for hand_landmarks in results.multi_hand_landmarks:
            # Obtén las coordenadas de la punta del dedo índice
            index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_x = int(index_finger.x * screen_width)
            index_y = int(index_finger.y * screen_height)

            # Dibuja la mano
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Verifica si la punta del dedo índice toca algún círculo
            for (cx, cy) in circles:
                distance = ((index_x - cx) ** 2 + (index_y - cy) ** 2) ** 0.5
                if distance < circle_radius:
                    score += 1
                    circles.remove((cx, cy))  # Elimina el círculo tocado
                    break  # Sal de la búsqueda para evitar contar múltiples círculos

    # Verifica el tiempo del juego
    elapsed_time = time.time() - start_time
    if elapsed_time > game_duration:
        break

    # Muestra el puntaje en la pantalla
    cv2.putText(frame, f"Score: {score}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Muestra el cuadro en la ventana de OpenCV
    cv2.imshow("Mini Juego", frame)

    # Presiona 'q' para salir
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Termina el juego y muestra la puntuación final
cap.release()
cv2.destroyAllWindows()
print(f"Tu puntuación final: {score}")

# Crea una ventana emergente para mostrar el puntaje final usando tkinter
root = tk.Tk()
root.withdraw()  # Oculta la ventana principal de tkinter

messagebox.showinfo("Juego Terminado", f"Tu puntuación final: {score}")

root.destroy()


