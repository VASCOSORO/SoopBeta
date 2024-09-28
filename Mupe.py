import streamlit as st
import numpy as np
import pygame
import random
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase

# Inicializamos pygame sin la pantalla física
pygame.init()

# Configuración de la pantalla virtual (dentro de Streamlit)
screen_width = 800
screen_height = 400

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BEAR_COLOR = (150, 75, 0)

# Definir el personaje (osito)
class Bear:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = 100
        self.y = screen_height - self.height - 10
        self.vel_y = 0
        self.gravity = 1
        self.is_jumping = False
    
    def update(self):
        if self.is_jumping:
            self.vel_y += self.gravity
            self.y += self.vel_y
            if self.y >= screen_height - self.height - 10:
                self.y = screen_height - self.height - 10
                self.is_jumping = False
                self.vel_y = 0

# Definir los obstáculos
class Obstacle:
    def __init__(self):
        self.width = 20
        self.height = random.randint(30, 70)
        self.x = screen_width
        self.y = screen_height - self.height - 10
        self.speed = 5

    def update(self):
        self.x -= self.speed
        if self.x < -self.width:
            self.x = screen_width
            self.height = random.randint(30, 70)
            self.y = screen_height - self.height - 10

# Procesador de audio para detectar volumen
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.volume_threshold = 0.1  # Umbral de volumen para detectar el "salto"
        self.jump_detected = False

    def recv(self, frame):
        audio_data = frame.to_ndarray()
        volume = np.linalg.norm(audio_data) / len(audio_data)
        if volume > self.volume_threshold:
            self.jump_detected = True
        else:
            self.jump_detected = False
        return frame

def game_loop(audio_processor):
    st.write("Controlá al osito con el nivel de tu voz")

    bear = Bear()
    obstacle = Obstacle()
    score = 0
    game_over = False

    while not game_over:
        st.write(f"Score: {score}")

        # Control del osito con el nivel de voz
        if audio_processor.jump_detected and not bear.is_jumping:
            bear.vel_y = -15
            bear.is_jumping = True

        # Actualizar y dibujar (simulado)
        bear.update()
        obstacle.update()

        # Detectar colisión
        if bear.x < obstacle.x + obstacle.width and bear.x + bear.width > obstacle.x and bear.y + bear.height > obstacle.y:
            st.write("Game Over!")
            game_over = True

        score += 1

# Configurar WebRTC para capturar audio y usar el procesador
webrtc_ctx = webrtc_streamer(
    key="audio",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

# Inicializar el juego solo si el procesador de audio está activo
if webrtc_ctx.state.playing and webrtc_ctx.audio_processor:
    if st.button("Iniciar el juego"):
        game_loop(webrtc_ctx.audio_processor)
