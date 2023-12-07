class Particle:
    def __init__(self, game, p_type, pos, velocity=[0, 0], frame=0):
        # Inicializa una partícula con un tipo, posición, velocidad y un frame inicial opcional
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self.game.assets['particle/' + p_type].copy()
        self.animation.frame = frame
    
    def update(self):
        # Actualiza la posición de la partícula y verifica si la animación ha terminado
        kill = False
        if self.animation.done:
            kill = True
        
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        
        self.animation.update()
        
        # Devuelve True si la partícula debe ser eliminada
        return kill
    
    def render(self, surf, offset=(0, 0)):
        # Renderiza la partícula en la superficie de juego
        img = self.animation.img()
        surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))
    