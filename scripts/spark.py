import math

import pygame

class Spark:
    def __init__(self, pos, angle, speed):
         # Inicializa una chispa con una posición, ángulo y velocidad
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed
        
    def update(self):
        # Actualiza la posición de la chispa basándose en su ángulo y velocidad
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed
        
        # Reduce gradualmente la velocidad de la chispa
        self.speed = max(0, self.speed - 0.1)
        # Devuelve True si la chispa ha perdido toda su velocidad y debe ser eliminada
        return not self.speed
    
    def render(self, surf, offset=(0, 0)):
        # Renderiza la chispa en la superficie de juego
        render_points = [
            (self.pos[0] + math.cos(self.angle) * self.speed * 3 - offset[0], self.pos[1] + math.sin(self.angle) * self.speed * 3 - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[0], self.pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi) * self.speed * 3 - offset[0], self.pos[1] + math.sin(self.angle + math.pi) * self.speed * 3 - offset[1]),
            (self.pos[0] + math.cos(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[0], self.pos[1] + math.sin(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[1]),
        ]
        
        # Dibuja un polígono que representa la chispa en la superficie
        pygame.draw.polygon(surf, (255, 255, 255), render_points)