import random

import pygame

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        # Inicializa una entidad con su tipo, posición, tamaño y otras propiedades
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')
        
        self.last_movement = [0, 0]
    
    def rect(self):
        # Devuelve un objeto Rect que representa la posición y el tamaño de la entidad
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        # Establece la acción de la entidad y actualiza la animación correspondiente
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
        
    def update(self, tilemap, movement=(0, 0)):
        # Actualiza la posición de la entidad y maneja las colisiones con el tilemap
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        # Maneja las colisiones en el eje X
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        # Maneja las colisiones en el eje Y
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
                
        # Determina la dirección de la entidad
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
            
        self.last_movement = movement
        
        # Aplica la gravedad
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        # Detiene la entidad si hay colisiones en el suelo o el techo
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
            
        self.animation.update()
        
    def render(self, surf, offset=(0, 0)):
        # Renderiza la entidad en la superficie del juego
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        
class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        # Inicializa un enemigo con su tipo, posición y tamaño, además de propiedades específicas
        super().__init__(game, 'enemy', pos, size)
        
        self.walking = 0
        
    def update(self, tilemap, movement=(0, 0)):
        # Actualiza el enemigo, maneja su comportamiento y dispara proyectiles
        if self.walking:
            # Comportamiento al caminar
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                # Disparar proyectiles cuando deja de caminar
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16):
                    if (self.flip and dis[0] < 0):
                        # Disparar proyectiles hacia la izquierda
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                    if (not self.flip and dis[0] > 0):
                        # Disparar proyectiles hacia la derecha
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
        elif random.random() < 0.01:
            # Lógica para activar algo con probabilidad del 1%
            # Comienza a caminar aleatoriamente
            self.walking = random.randint(30, 120)
        
        super().update(tilemap, movement=movement)
        
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
            
        # Maneja la colisión con el jugador
        if abs(self.game.player.dashing) >= 50:
            # Verifica si la magnitud del "dash" del jugador es mayor o igual a 50
            if self.rect().colliderect(self.game.player.rect()):
                # Efecto de golpe y pantalla temblorosa
                self.game.screenshake = max(16, self.game.screenshake)
                self.game.sfx['hit'].play()

                # Indica que la colisión ocurrió y se debería eliminar al enemigo
                return True
            
    def hit(self):
        # Maneja el impacto del enemigo
        self.game.sfx['hit'].play()
        return True
            
    def render(self, surf, offset=(0, 0)):
        # Renderiza al enemigo y su arma en la superficie del juego
        super().render(surf, offset=offset)
        
        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))


class Boss(PhysicsEntity):
    def __init__(self, game, pos, size):
        # Inicializa al jefe con su tipo, posición, tamaño y propiedades específicas
        super().__init__(game, 'boss', pos, size)
        self.walking = 0
        
    def update(self, tilemap, movement=(0, 0)):
    # Actualiza el enemigo, maneja su comportamiento y dispara proyectiles
        if self.walking:
            # Comportamiento al caminar
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 100)):
                if (self.collisions['right'] or self.collisions['left']):
                    if not self.collisions['right'] and not self.collisions['left']:
                        self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.7 if self.flip else 0.7, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                # Disparar proyectiles cuando deja de caminar
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16):
                    if (self.flip and dis[0] < 0):
                        # Disparar proyectiles hacia la izquierda
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx - 9, self.rect().centery], -1.5, 0])
                    elif (not self.flip and dis[0] > 0):
                        # Disparar proyectiles hacia la derecha
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx + 9, self.rect().centery], 1.5, 0])

        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)
        
        super().update(tilemap, movement=movement)
        
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
            
        # Maneja la colisión con el jugador
        if abs(self.game.player.dashing) >= 50:
            # Verifica si la magnitud del "dash" del jugador es mayor o igual a 50
            if self.rect().colliderect(self.game.player.rect()):
                # Efecto de golpe y pantalla temblorosa
                self.game.screenshake = max(16, self.game.screenshake)
                self.game.sfx['hit'].play()
                # Indica que la colisión ocurrió y se debería eliminar al enemigo
                return True

    def hit(self):
        # Maneja el impacto del enemigo
        self.game.sfx['hit'].play()
        return True

    def render(self, surf, offset=(0, 0)):
        # Renderiza al enemigo
        super().render(surf, offset=offset)

class Coin():
    def __init__(self, game, pos):
        self.game = game
        self.pos = pos
        self.collected = False
        self.image = self.game.assets['coin']

    def rect(self):
        # Devuelve un objeto Rect que representa la posición y el tamaño de la moneda
        return pygame.Rect(self.pos[0], self.pos[1], 20, 20)
    
    def collect(self):
        # Realiza acciones cuando la moneda es recogida por el jugador
        self.collected = True
        self.game.player.score += 100
        self.game.sfx['coin'].play(0)
        self.game.sfx['coin'].set_volume(0.2)

    def render(self, surf, offset=(0, 0)):
        # Renderiza la moneda en la pantalla
        coin_rect = self.rect()
        coin_rect.x -= offset[0]
        coin_rect.y -= offset[1]

        # Dibuja la imagen en lugar de un rectángulo
        surf.blit(self.image, (coin_rect.x, coin_rect.y))

class Life():
    def __init__(self, game, pos):
        self.game = game
        self.pos = pos
        self.collected = False
        self.image = self.game.assets['life']

    def rect(self):
        # Devuelve un objeto Rect que representa la posición y el tamaño de la moneda
        return pygame.Rect(self.pos[0], self.pos[1], 16, 16)
    
    def collect(self):
        # Realiza acciones cuando la vida es recogida por el jugador
        self.collected = True
        self.game.player.lives += 1
        self.game.sfx['coin'].play(0)
        self.game.sfx['coin'].set_volume(0.2)

    def render(self, surf, offset=(0, 0)):
        # Renderiza la vida en la pantalla
        life_rect = self.rect()
        life_rect.x -= offset[0]
        life_rect.y -= offset[1]

        # Dibuja la imagen en lugar de un rectángulo
        surf.blit(self.image, (life_rect.x, life_rect.y))

class Spike():
    def __init__(self, game, pos):
        self.game = game
        self.pos = pos
        self.collected = False
        self.image = self.game.assets['spike']

    def rect(self):
        # Devuelve un objeto Rect que representa la posición y el tamaño de la moneda
        return pygame.Rect(self.pos[0], self.pos[1], 16, 16)
    
    def collect(self):
        self.collected = True
        self.game.player.lives -= 1
        self.game.sfx['hit'].play(0)
        self.game.sfx['hit'].set_volume(0.2)

    def render(self, surf, offset=(0, 0)):
        # Renderiza la moneda en la pantalla
        spike_rect = self.rect()
        spike_rect.x -= offset[0]
        spike_rect.y -= offset[1]

        # Dibuja la imagen en lugar de un rectángulo
        surf.blit(self.image, (spike_rect.x, spike_rect.y))
                  
class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        # Inicializa al jugador con su tipo, posición, tamaño y propiedades específicas
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0
        self.lives = 3
        self.score = 0
    
    def update(self, tilemap, movement=(0, 0)):
        # Actualiza al jugador, maneja la lógica de salto, deslizamiento en la pared y dash
        super().update(tilemap, movement=movement)
        
        self.air_time += 1
        
        # Maneja la cuenta de tiempo en el aire y la muerte del jugador
        if self.air_time > 120:
            if not self.game.dead:
                self.game.screenshake = max(16, self.game.screenshake)
            self.game.dead += 1
        
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
            
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            # Deslizamiento en la pared
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')
        
        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        
        # Maneja el dash del jugador y crea efectos visuales
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
                
        # Frena la velocidad en el eje X
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def shoot(self):
        # Maneja el disparo del jugador y crea un proyectil
        if not self.game.dead and not self.wall_slide:
            self.game.sfx['shoot'].play()
            projectile_pos = [self.rect().centerx + (8 if not self.flip else -8), self.rect().centery]
            projectile_speed = 2 if not self.flip else -2
            self.game.projectiles.append([projectile_pos, projectile_speed, 0])

    def render(self, surf, offset=(0, 0)):
        # Renderiza al jugador, excluyendo la renderización si está en mitad de un dash
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)
            
    def jump(self):
        # Maneja el salto del jugador y devuelve True si se realizó un salto
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
                
        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True
    
    def dash(self):
        # Maneja el dash del jugador y reproduce el sonido correspondiente
        if not self.dashing:
            self.game.sfx['dash'].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60