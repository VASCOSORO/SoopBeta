import streamlit as st
import numpy as np
import random
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase

# Definir el personaje (osito)
class Bear:
    def __init__(self):
        self.y = 0
        self.is_jumping = False
        self.gravity = 1
        self.vel_y = 0
        self.jump_strength = -10

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.vel_y = self.jump_strength

    def update(self):
        if self.is_jumping:
            self.vel_y += self.gravity
            self.y += self.vel_y
            if self.y >= 0:  # El suelo es la posición 0
                self.y = 0
                self.is_jumping = False
                self.vel_y = 0

# Definir los obstáculos
class Obstacle:
    def __init__(self):
        self.position = random.randint(5, 10)

    def move(self):
        self.position -= 1
        if self.position < 0:
            self.position = random.randint(5, 10)  # Reaparece en otra posición

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

# Bucle principal del juego
def game_loop(audio_processor):
    bear = Bear()
    obstacle = Obstacle()
    score = 0
    game_over = False

    while not game_over:
        st.write(f"Score: {score}")
        st.write(f"Posición del osito: {bear.y}")
        st.write(f"Posición del obstáculo: {obstacle.position}")

        # Control del osito con el nivel de voz
        if audio_processor.jump_detected:
            bear.jump()

        # Actualizar estado del juego
        bear.update()
        obstacle.move()

        # Detectar colisión
        if obstacle.position == 0 and bear.y == 0:
            st.write("Game Over!")
            game_over = True

        score += 1
        st.write("---")
        st.experimental_rerun()  # Actualizar la interfaz en cada ciclo

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
