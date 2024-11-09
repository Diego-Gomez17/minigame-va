import cv2
import mediapipe as mp
import random
import time
from screeninfo import get_monitors
import tkinter as tk
from tkinter import messagebox

# Obtén el tamaño de la pantalla principal
monitor = get_monitors()[0]
screen_width = 1280
screen_height = 720
print( screen_width,",",screen_height)



# Configuración del juego
circle_radius = 30
score = 0
circles = []
current_letter_index = 0  # Track the current letter to be clicked

# Palabras del juego
words = ["python", "circle", "random", "camera", "vision", "screen", "letter"]
selected_word = random.choice(words)  # Seleccionar una palabra aleatoria
letters = list(selected_word)  # Convertir la palabra en una lista de letras

def show_score():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter
    messagebox.showinfo("Puntaje final", f"Puntuación: {score} de {len(letters)} letras correctas")
    root.destroy()

# Inicialización de MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Función para crear círculos con letras en posiciones aleatorias
def create_circle():
    global circles, letters
    circles = []  # Reiniciar los círculos
    for letter in letters:
        # Generar coordenadas que aseguren que el círculo estará completamente visible
        x = random.randint(circle_radius, screen_width - circle_radius)
        y = random.randint(circle_radius, screen_height - circle_radius)
        circles.append((x, y, letter))

# Función para mostrar los círculos y letras
def draw_circles(frame):
    for x, y, letter in circles:
        cv2.circle(frame, (x, y), circle_radius, (255, 0, 0), -1)
        cv2.putText(frame, letter.upper(), (x - 10, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# Función principal del juego
def main_game():
    global score, current_letter_index
    cap = cv2.VideoCapture(0)

    # Ajustar la resolución de la cámara a la resolución de la pantalla
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)
    
    # Configura la ventana de OpenCV para pantalla completa
    cv2.namedWindow("Juego de Letras", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Juego de Letras", cv2.WINDOW_NORMAL, cv2.WINDOW_NORMAL)

    start_time = time.time()
    create_circle()  # Genera los círculos inicialmente
    
    while time.time() - start_time < 30:  # Duración del juego (10 segundos)
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convertir la imagen a RGB para MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        # Dibujar los círculos con letras en la pantalla
        draw_circles(frame)
        
        # Detección de manos y verificación de toque en círculos
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                finger_x = int(index_finger_tip.x * screen_width)
                finger_y = int(index_finger_tip.y * screen_height)
                
                # Verificar si se toca el círculo correcto
                if current_letter_index < len(circles):
                    cx, cy, letter = circles[current_letter_index]
                    if (finger_x - cx) ** 2 + (finger_y - cy) ** 2 < circle_radius ** 2:
                        score += 1
                        current_letter_index += 1  # Avanzar a la siguiente letra
                        if current_letter_index >= len(circles):  # Todas las letras tocadas
                            show_score()
                            cap.release()
                            cv2.destroyAllWindows()
                            return

        # Redimensionar el frame para ajustarlo a la resolución de la pantalla
        frame_resized = cv2.resize(frame, (screen_width, screen_height))

        # Mostrar el frame redimensionado en pantalla
        cv2.imshow("Juego de Letras", frame_resized)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Mostrar puntaje si el tiempo termina
    #show_score()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main_game()