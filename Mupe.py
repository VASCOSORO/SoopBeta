import streamlit as st
import pygame
import random

# Inicializamos pygame sin la pantalla física, ya que lo manejaremos como un backend
pygame.init()

# Configuración de la pantalla (virtual)
screen_width = 800
screen_height = 400

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BEAR_COLOR = (150, 75, 0)  # Color del osito

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

def game_loop():
    st.write("Controlá al osito haciendo clic en el botón de 'Saltar'")

    bear = Bear()
    obstacle = Obstacle()
    score = 0

    game_over = False

    while not game_over:
        st.write(f"Score: {score}")

        # Control del osito con botón
        if st.button("Saltar") and not bear.is_jumping:
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

# Iniciar el juego
if st.button("Iniciar el juego"):
    game_loop()
