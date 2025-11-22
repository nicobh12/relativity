import pygame
import sys
from ui_elements import Button
from perihelio import PerihelioSim
from gps import GPSSim


pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador de Relatividad General")

FONT = pygame.font.SysFont("arial", 36)
SMALL = pygame.font.SysFont("arial", 24)


def main_menu():
    clock = pygame.time.Clock()

    # Botones
    perihelio_btn = Button(WIDTH//2 - 150, 300, 300, 60, "Perihelio de Mercurio")
    gps_btn = Button(WIDTH//2 - 150, 400, 300, 60, "Navegación por GPS")

    running = True
    while running:
        screen.fill((20, 20, 30))

        # Título
        title = FONT.render("Simulador de Relatividad General", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))

        # Dibujar botones
        perihelio_btn.draw(screen)
        gps_btn.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if perihelio_btn.is_hovered():
                    PerihelioSim(screen).run()

                if gps_btn.is_hovered():
                    GPSSim(screen).run()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main_menu()
