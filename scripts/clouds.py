import random

class Cloud:
    def __init__(self, pos, img, speed, depth):
        # Inicializa una nube con su posición, imagen, velocidad y profundidad
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth
    
    def update(self):
        # Actualiza la posición de la nube basándose en su velocidad
        self.pos[0] += self.speed
        
    def render(self, surf, offset=(0, 0)):
        # Renderiza la nube en la superficie del juego, aplicando un efecto de desplazamiento parallax
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width(), render_pos[1] % (surf.get_height() + self.img.get_height()) - self.img.get_height()))
        
class Clouds:
    def __init__(self, cloud_images, count=16):
        # Inicializa un conjunto de nubes con imágenes aleatorias y parámetros específicos
        self.clouds = []
        
        for i in range(count):
            # Crea nubes con posiciones aleatorias, imágenes aleatorias, velocidades y profundidades aleatorias
            self.clouds.append(Cloud((random.random() * 99999, random.random() * 99999), random.choice(cloud_images), random.random() * 0.05 + 0.05, random.random() * 0.6 + 0.2))
        
        # Ordena las nubes por profundidad para garantizar el efecto parallax
        self.clouds.sort(key=lambda x: x.depth)
    
    def update(self):
        # Actualiza todas las nubes en el conjunto
        for cloud in self.clouds:
            cloud.update()
    
    def render(self, surf, offset=(0, 0)):
        # Renderiza todas las nubes en la superficie del juego
        for cloud in self.clouds:
            cloud.render(surf, offset=offset)