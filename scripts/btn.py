import pygame

SIZE_BUTTON = (200,50)

def show_text(surface,text,cordanate, font, font_color):
    sup_text = font.render(text, True, font_color)
    rect_text = sup_text.get_rect()
    rect_text.center = cordanate
    surface.blit(sup_text, rect_text)

# Crear boton
def create_botton(screen,color, rect, text, font):
    botton_menu_font = font
    pygame.draw.rect(screen, color, rect, border_radius= 10)
    render_btn = botton_menu_font.render(f"{text}", True, (255,255,255))
    rect_text_btn = render_btn.get_rect()
    rect_text_btn.center = rect.center
    screen.blit(render_btn, rect_text_btn)