import pygame
import math
import sys

# ---------------------
# Parámetros físicos
# ---------------------
ECCENTRICITY = 0.21       # excentricidad artificial (la real es 0.2056)
A = 220                    # semieje mayor en pixeles
CENTER = (450, 350)       # centro pantalla


class PerihelioSim:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.theta = 0
        self.speed = 0.01         # velocidad angular base
        self.precession = 0.02    # cuanto precesa por vuelta (ajustable)

        self.orbit_points = []

    def polar_orbit(self, theta):
        """Relativistic-like orbit with artificial precession."""
        e = ECCENTRICITY

        # aplicamos precesión progresiva sobre theta
        revs = theta / (2 * math.pi)
        theta_rel = theta + self.precession * revs

        # elipse polar clásica
        r = (A * (1 - e**2)) / (1 + e * math.cos(theta_rel))

        x = CENTER[0] + int(r * math.cos(theta_rel))
        y = CENTER[1] + int(r * math.sin(theta_rel))
        return x, y

    def draw_orbit(self):
        for p in self.orbit_points:
            pygame.draw.circle(self.screen, (255, 200, 0), p, 1)

    def run(self):
        running = True

        while running:
            self.screen.fill((10, 10, 20))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Controles
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        running = False
                        return

                    # Velocidad
                    if event.key == pygame.K_UP:
                        self.speed *= 1.2
                    
                    if event.key == pygame.K_DOWN:
                        self.speed *= 0.8

                    # Precesión
                    if event.key == pygame.K_RIGHT:
                        self.precession += 0.01
                    
                    if event.key == pygame.K_LEFT:
                        self.precession -= 0.01
                        if self.precession < 0:
                            self.precession = 0

            # Actualizar ángulo
            self.theta += self.speed

            # Calcular nueva posición
            pos = self.polar_orbit(self.theta)
            self.orbit_points.append(pos)

            # Dibujar trayectoria
            self.draw_orbit()

            # Planeta
            pygame.draw.circle(self.screen, (120, 200, 255), pos, 6)

            # Sol
            pygame.draw.circle(self.screen, (255, 180, 70), CENTER, 22)

            # UI de texto
            font = pygame.font.SysFont("arial", 22)
            txt1 = font.render(f"Velocidad = {self.speed:.4f}", True, (255, 255, 255))
            txt2 = font.render(f"Precesión = {self.precession:.4f}", True, (255, 255, 255))
            txt3 = font.render("ESC = salir", True, (200, 200, 200))
            txt4 = font.render("Arriba/Abajo = velocidad", True, (200, 200, 200))
            txt5 = font.render("Izq/Der = precesión", True, (200, 200, 200))

            self.screen.blit(txt1, (20, 20))
            self.screen.blit(txt2, (20, 45))
            self.screen.blit(txt3, (20, 80))
            self.screen.blit(txt4, (20, 105))
            self.screen.blit(txt5, (20, 130))

            pygame.display.flip()
            self.clock.tick(60)
