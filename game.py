import os
import sys
import math
import random

import pygame

from pygame.locals import *
from scripts.btn import *
from scripts.pause import *
from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Enemy, Coin, Life
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark

class Game:
    def __init__(self):
        #----------------------------------------------------------------------INICIALIZACION DEL JUEGO--------------------------------------------------------------#
        pygame.init()
        pygame.display.set_caption('Game')

        # Pantalla
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))

        # Reloj
        self.clock = pygame.time.Clock()

        # Variable para rastrear el tiempo
        self.start_time = pygame.time.get_ticks()

        # Carga una fuente de texto
        self.font = pygame.font.Font('data/fonts/retro_gaming.ttf', 12)
        self.menu_font = pygame.font.Font('data/fonts/retro_gaming.ttf', 32)
        # Selector de nivel y banderas
        self.show_coins = 0
        self.menu_selected = 0
        self.level = 0
        self.menu_active = True
        self.GO = True
        self.game_over_active = False
        self.spawn_timer = 0
        
        # Carga de imágenes y sonidos utilizados en el juego
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'background': load_image('background.png'),
            'menu': load_image('menu.png'),
            'gameOver': load_image('game_over.png'),
            'clouds': load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
            'coin' : load_image('coin.png'),
            'life' : load_image('Life.png'),
            'face' : pygame.transform.scale(pygame.image.load('data/images/face.png'), (32,32))
        }

        # Configuración de efectos de sonido y música
        self.sfx = {
            'jump' : pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash' : pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit' : pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot' : pygame.mixer.Sound('data/sfx/shoot.wav'),
            'coin' : pygame.mixer.Sound('data/sfx/buff.mp3'),
            #'ambience' : pygame.mixer.Sound('data/sfx/ambience.wav'),
        }

        # Setero volumen efectos
        #self.sfx['ambience'].set_volume(0.1)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)
        
        # Configuración de las nubes en el fondo del juego
        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        # Inicialización del jugador y el mapa
        self.player = Player(self, (50, 50), (8, 15))
        self.tilemap = Tilemap(self, tile_size=16)
        # Controla la dirección del movimiento del jugador
        self.movement = [False, False] 
        
        # Inicialización del menu
        self.show_menu()

        # Inicialización del puntaje al comienzo del juego
        self.player.score = 0
        self.current_score = 0
        
        # Variables para el efecto de pantalla temblorosa (screenshake)
        self.screenshake = 0

     # ----------------------------------------------------------------------RESET DE NIVEL-------------------------------------------------------------------#
    def reset_game(self):
        self.menu_active = True
        self.GO = False
        self.game_over_active = False
        self.start_time = pygame.time.get_ticks()
        self.menu_selected = 0
        self.show_menu()
        self.player.lives = 3
        self.player.score = 0
        self.current_score = 0
        self.level = 0
        self.show_coins = 0

        # ------------------------------------------------------------------ CARGAR NIVEL-----------------------------------------------------------------------#
    def load_level(self, map_id):
        # Carga de un nuevo nivel desde un archivo JSON
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        #Reloj
        self.start_time = pygame.time.get_ticks()
        
        # Identificación de posiciones para generación de partículas (hojas)
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        # Creación de enemigos y posición inicial del jugador
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))

        # Creación de monedas
        self.coins = []
        for coin_spawn in self.tilemap.extract([('spawners', 2)]):
            self.coins.append(Coin(self, coin_spawn['pos']))

        self.life = []
        for life_spawn in self.tilemap.extract([('spawners', 3)]):
            self.life.append(Life(self, life_spawn['pos']))
                    
        # Inicialización de listas para proyectiles, partículas y chispas
        self.projectiles = []
        self.particles = []
        self.sparks = []
        
        # Posición de inicio y transición   
        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30


        # ------------------------------------------------ MENU-----------------------------------------------------------------#

    def show_menu(self):
        # Carga de música de fondo y ajuste de volumen
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)
        while self.menu_active:
            self.clock.tick(60)

            # Botones
            rect_start = pygame.Rect(220, 100, SIZE_BUTTON[0], SIZE_BUTTON[1])
            rect_leave = pygame.Rect(220, 350, SIZE_BUTTON[0], SIZE_BUTTON[1])
            rect_steating = pygame.Rect(220, 280, SIZE_BUTTON[0], SIZE_BUTTON[1])
            rect_1 = pygame.Rect(220, 200, SIZE_BUTTON[1], SIZE_BUTTON[1])
            rect_2 = pygame.Rect(300, 200, SIZE_BUTTON[1], SIZE_BUTTON[1])
            rect_3 = pygame.Rect(380, 200, SIZE_BUTTON[1], SIZE_BUTTON[1])

            # Menu eventos
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    quit()

                if e.type == MOUSEBUTTONDOWN:
                    if e.button == 1:
                        if rect_start.collidepoint(e.pos):
                            self.load_level(0)  # Carga el nivel 1
                            self.menu_active = False
                        elif rect_leave.collidepoint(e.pos):
                            pygame.quit() # Libera los recursos de pygame
                            sys.exit()
                        elif rect_1.collidepoint(e.pos):
                            self.load_level(0)  # Carga el nivel 1
                            self.menu_active = False
                        elif rect_2.collidepoint(e.pos):
                            self.load_level(1)  # Carga el nivel 2
                            self.menu_active = False
                        elif rect_3.collidepoint(e.pos):
                            self.load_level(2)  # Carga el nivel 3
                            self.menu_active = False
                        elif rect_steating.collidepoint(e.pos):
                            opcion_in_game(pause_music=False, screen=self.screen) # Menu de sonidos

            # Botones y fondo
            self.screen.blit(self.assets['menu'], (0, 0))
            create_botton(self.screen, (150,100,250), rect_start, text="Start", font=self.menu_font)
            create_botton(self.screen, (150,100,250), rect_1, text="1", font=self.menu_font)
            create_botton(self.screen, (150,100,250), rect_2, text="2", font=self.menu_font)
            create_botton(self.screen, (150,100,250), rect_3, text="3", font=self.menu_font)
            create_botton(self.screen, (150,100,250), rect_steating, text="Seating", font=self.menu_font)
            create_botton(self.screen, (150,100,250), rect_leave, text="Leave", font=self.menu_font)

            pygame.display.flip()

    #----------------------------------------------------------------------- PAUSA--------------------------------------------------------------------#

    def pause_game(self):
        pause_in_game(pause_music=False)
        pygame.mixer.music.unpause()
        self.start_time
 
    #------------------------------------------------------------------------JUEGO--------------------------------------------------------------------#

    def run(self):
        # Reproducción de sonido de ambiente
        #self.sfx['ambience'].play(-1)

        while True:
            # Activacion de pantalla fin de juego
            if self.game_over_active:
                self.game_over()
                self.GO = True
            else:           

                # Captura de eventos de teclado
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            self.movement[0] = True
                        if event.key == pygame.K_RIGHT:
                            self.movement[1] = True
                        if event.key == pygame.K_UP:
                            if self.player.jump():
                                self.sfx['jump'].play()
                        if event.key == pygame.K_x:
                            self.player.dash()
                        if event.key == pygame.K_z:
                            self.player.shoot()
                        if event.key == pygame.K_p:
                            self.pause_game()
                        if event.key == pygame.K_o:
                            opcion_in_game(pause_music=False, screen=self.screen)
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT:
                            self.movement[0] = False
                        if event.key == pygame.K_RIGHT:
                            self.movement[1] = False

                #---------------------------- TIME ----- SCORE ---------------------------#

                # Calcula el tiempo transcurrido en segundos
                elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000

                # Renderiza el temporizador como texto
                timer_text = self.font.render(f'{elapsed_time:.0f}', True, (255, 255, 255))

                # Muestra el temporizador en la esquina superior izquierda
                self.display.blit(timer_text, (150, 5))
                # Score actulizado
                score_text = self.font.render(f'Score: {self.player.score}', True, (255, 255, 255))
                self.display.blit(score_text, (40, 5))

                # --------------------------------------------------CAMARA/PANTALLA-------------------------------------------------#

                # Cálculo del desplazamiento de la pantalla centrado en el jugador (Camara)
                self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
                self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
                render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

                # Actualización del efecto de pantalla temblorosa
                self.screenshake = max(0, self.screenshake - 1)

                # Creación de una máscara de la pantalla para efecto de transición    
                display_mask = pygame.mask.from_surface(self.display)
                display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
                
                # Aplicación del efecto de transición en la pantalla
                for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    self.display_2.blit(display_sillhouette, offset)

                # Aplicación de efecto de transición en la pantalla
                if self.transition:
                    transition_surf = pygame.Surface(self.display.get_size())
                    pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                    transition_surf.set_colorkey((255, 255, 255))
                    self.display.blit(transition_surf, (0, 0))
                    
                self.display_2.blit(self.display, (0, 0))
                screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
                self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)

                #----------------------PANTALLA------------------------------#
                # Limpieza y preparación de la pantalla de juego
                self.display.fill((0, 0, 0, 0))
                self.display_2.blit(self.assets['background'], (0, 0))

                #---------------------------------NUBES-----------------------------------#

                # Actualización y renderización de nubes en el fondo
                self.clouds.update()
                self.clouds.render(self.display_2, offset=render_scroll)
                
                #-------------------------TERRENO------------------------------#

                # Renderización del mapa de tiles
                self.tilemap.render(self.display, offset=render_scroll)

                # ----------------------------------------------------JUGADOR------------------------------------------------#

                self.display.blit(self.assets['face'], (5, 5))

                # Actualización y renderización del jugador
                if not self.dead:
                    self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                    self.player.render(self.display, offset=render_scroll)

                # BALAS
                # Actualización y renderización de proyectiles
                for projectile in self.projectiles.copy():
                    projectile[0][0] += projectile[1]
                    projectile[2] += 1
                    img = self.assets['projectile'].convert_alpha()
                    self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))

                    # Verifica colisiones con el mapa de tiles
                    if self.tilemap.solid_check(projectile[0]):
                        # Elimina el proyectil y genera chispas
                        self.projectiles.remove(projectile)
                        for i in range(4):
                            self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                    elif projectile[2] > 360:
                        # Elimina el proyectil si ha superado un tiempo máximo de vida
                        self.projectiles.remove(projectile)
                    elif abs(self.player.dashing) < 50:
                        # Verifica colisiones con los enemigos
                        for enemy in self.enemies.copy():
                            if enemy.rect().colliderect(pygame.Rect(projectile[0][0] - 4, projectile[0][1] - 4, 8, 8)):
                                # Elimina el proyectil y reduce la vida del enemigo
                                self.projectiles.remove(projectile)
                                if enemy.hit():
                                    # Aumenta la puntuación del jugador y elimina al enemigo
                                    self.player.score += 50
                                    self.enemies.remove(enemy)
                                break
                
                # Comprobación de la condición de victoria (sin enemigos)
                if not len(self.enemies):
                    self.transition += 1
                    if self.transition > 30:
                        # Carga del siguiente nivel al finalizar la transición
                        self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1)
                        self.load_level(self.level)
                if self.transition < 0:
                    self.transition += 1
                
                # Gestión del estado después de la muerte del jugador
                if self.dead or elapsed_time >= 60:
                    self.dead += 1
                    if self.dead >= 10:
                        self.transition = min(30, self.transition + 1)
                    if self.dead > 40:
                        # Disminuir las vidas y reiniciar el nivel después de cierto tiempo tras la muerte
                        self.player.lives -= 1
                        if self.player.lives <= 0:
                            self.game_over_active = True  # Cambia el estado a Game Over
                        else:
                            self.load_level(self.level)

                #--------------------------------------------------VIDAS----------------------------------------------#

                for life in self.life.copy():
                    if not life.collected:
                        life.render(self.display, offset=render_scroll)
                        if self.player.rect().colliderect(life.rect()):
                            life.collect()
                self.life = [life for life in self.life if not life.collected]
                # Muestra las vidas en la esquina superior derecha
                self.display.blit(self.assets['life'], (287, 5))
                lives_text = self.font.render(f'{self.player.lives}', True, (255, 255, 255))
                self.display.blit(lives_text, (302,5))

                #--------------------------------------------------MONEDAS----------------------------------------------#
                # Actualización y renderzización de monedas
                for coin in self.coins.copy():
                    if not coin.collected:
                        coin.render(self.display, offset=render_scroll)
                        if self.player.rect().colliderect(coin.rect()):
                            coin.collect()
                            self.show_coins += 1
                self.coins = [coin for coin in self.coins if not coin.collected]

                self.display.blit(self.assets['coin'], (280, 15))
                lives_text = self.font.render(f'{self.show_coins}', True, (255, 255, 255))
                self.display.blit(lives_text, (302,23))


                #-----------------------------------------------------ENEMIGOS------------------------------------------------------#

                # Actualización y renderización de enemigos
                for enemy in self.enemies.copy():
                    kill = enemy.update(self.tilemap, (0, 0))
                    enemy.render(self.display, offset=render_scroll)
                    if kill:
                        self.player.score += 50
                        self.enemies.remove(enemy)

                # BALAS ENEMIGAS
                # Actualización y renderización de proyectiles
                for projectile in self.projectiles.copy():
                    projectile[0][0] += projectile[1]
                    projectile[2] += 1
                    img = self.assets['projectile']
                    self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))

                    # Verifica colisiones con el mapa de tiles
                    if self.tilemap.solid_check(projectile[0]):
                        # Elimina el proyectil y genera chispas
                        self.projectiles.remove(projectile)
                        for i in range(4):
                            self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                    elif projectile[2] > 360:
                        # Elimina el proyectil si ha superado un tiempo máximo de vida
                        self.projectiles.remove(projectile)
                    elif abs(self.player.dashing) < 50:
                        # Verifica colisiones con el jugador
                        if self.player.rect().collidepoint(projectile[0]):
                            # Elimina el proyectil, reduce la vida del jugador y crea efectos visuales
                            self.projectiles.remove(projectile)
                            self.dead += 1
                            self.sfx['hit'].play()
                            self.screenshake = max(16, self.screenshake)
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                                self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

                #--------------------------------------------------PARTICULAS---------------------------------------------------------------#

                # Generación de partículas (hojas) en los spawners de árboles
                for rect in self.leaf_spawners:
                    if random.random() * 49999 < rect.width * rect.height:
                        pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                        self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

                # Actualización y renderización de partículas
                for spark in self.sparks.copy():
                    kill = spark.update()
                    spark.render(self.display, offset=render_scroll)
                    if kill:
                        self.sparks.remove(spark)
                
                # Actualización y renderización de partículas
                for particle in self.particles.copy():
                    kill = particle.update()
                    particle.render(self.display, offset=render_scroll)
                    if particle.type == 'leaf':
                        particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                    if kill:
                        self.particles.remove(particle)

                    
                pygame.display.update()
                self.clock.tick(60)


    #----------------------------------------------------------------------GAME OVER-----------------------------------------------------------------------#

    def game_over(self):
        while self.GO:
            self.clock.tick(60)
            # Botones
            rect_restart = pygame.Rect(220, 100, SIZE_BUTTON[0], SIZE_BUTTON[1])
            rect_leave = pygame.Rect(220, 350, SIZE_BUTTON[0], SIZE_BUTTON[1])

            # Menu eventos
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    quit()

                if e.type == MOUSEBUTTONDOWN:
                    if e.button == 1:
                        if rect_restart.collidepoint(e.pos):
                            self.reset_game() # Llama a la función de reinicio
                        elif rect_leave.collidepoint(e.pos):
                            pygame.quit()
                            sys.exit()

            # Boton Start y Leave
            self.screen.blit(self.assets['gameOver'], (0, 0))
            create_botton(self.screen, (150,100,250), rect_restart, text="Restart", font=self.menu_font)
            create_botton(self.screen, (150,100,250), rect_leave, text="Leave", font=self.menu_font)

            pygame.display.flip()

Game().run()