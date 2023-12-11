import os
import pygame

BASE_IMG_PATH = 'data/images/'

def load_image(path):
    # Carga una imagen desde la ruta especificada y aplica transparencia
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path):
    # Carga una secuencia de imágenes desde un directorio y las devuelve como una lista
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        # Inicializa la animación con una secuencia de imágenes, duración de cada imagen y opción de bucle
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0
    
    def copy(self):
        # Crea una copia de la animación actual
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        # Actualiza el frame de la animación según la duración y opción de bucle
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self):
        # Devuelve la imagen correspondiente al frame actual de la animación
        return self.images[int(self.frame / self.img_duration)]