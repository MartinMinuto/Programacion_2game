import pygame
import sys
from scripts.btn import *
from pygame.locals import *

# Pausa en el juego
def pause_in_game(pause_music=True):
    paused_text = pygame.font.SysFont(None, 100).render("Paused", True, (255, 255, 255))
    text_rect = paused_text.get_rect(center=(320, 240))

    pygame.mixer.music.pause()  # Pausa la música

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key == K_p:
                    pygame.mixer.music.unpause()  # Despausa la música
                    return

        # Renderiza el texto de pausa en el centro de la pantalla
        pygame.display.get_surface().blit(paused_text, text_rect)
        pygame.display.flip()

def opcion_in_game(screen, pause_music=True):
    paused_text = pygame.font.Font('data/fonts/retro_gaming.ttf', 40).render("Music", True, (0, 0, 0))
    text_rect = paused_text.get_rect(center=(320, 40))
    text_leave = pygame.font.Font('data/fonts/retro_gaming.ttf', 40).render("Press 'O' for leave", True, (0, 0, 0))
    text_leave_rect = paused_text.get_rect(center=(160, 440))
    rect_start = pygame.Rect(100, 150, SIZE_BUTTON[0], SIZE_BUTTON[1])
    rect_stop = pygame.Rect(340, 150, SIZE_BUTTON[0], SIZE_BUTTON[1])
    backgroud = pygame.transform.scale(pygame.image.load("data/images/music_menu.jpg"), (640,480))

    music_started = False  # Bandera para controlar si la música ha comenzado

    while True:
        screen.fill((255, 255, 255))  # Fondo blanco
        screen.blit(backgroud, (0,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_o:
                    pygame.mixer.music.unpause()
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect_start.collidepoint(event.pos):
                    if not music_started:
                        pygame.mixer.music.load('data/music.wav') 
                        pygame.mixer.music.set_volume(0.5)
                        pygame.mixer.music.play(-1)
                        music_started = True

                elif rect_stop.collidepoint(event.pos):
                    pygame.mixer.music.stop()  # Detiene la música
                    music_started = False

        # Crea los botones en la pantalla
        create_botton(screen, (150, 100, 250), rect_start, text="Start music", font=pygame.font.Font('data/fonts/retro_gaming.ttf', 24))
        create_botton(screen, (150, 100, 250), rect_stop, text="Stop music", font=pygame.font.Font('data/fonts/retro_gaming.ttf', 24))

        # Renderiza el texto de pausa en el centro de la pantalla
        pygame.display.get_surface().blit(paused_text, text_rect)
        pygame.display.get_surface().blit(text_leave, text_leave_rect)
        pygame.display.flip()
