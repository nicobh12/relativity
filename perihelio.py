import pygame
import math
import sys

# ---------------------
# Parámetros visuales / físicos
# ---------------------
ECCENTRICITY = 0.3      # Eccentricidad real de Mercurio
A = 200                    # semieje mayor en pixeles
SCREEN_CENTER = (450, 350)

# Colores
COLOR_BG = (8, 10, 20)
COLOR_SOL = (255, 180, 70)
COLOR_NEWTON = (220, 220, 220, 70)
COLOR_REL = (60, 220, 140)
COLOR_PLANET = (100, 200, 255)
COLOR_TEXT = (230, 230, 230)

MAX_TRAIL_POINTS = 6000


class PerihelioSim:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # dinámica
        self.theta = 0.0          # ángulo orbital del planeta
        self.phi_rel = 0.0        # ángulo de precesión relativista
        self.speed = 0.01         # velocidad orbital

        # Ahora precision controla DIRECTAMENTE la precesión:
        # precision=1 → casi sin precesión
        # precision=0 → precesión enorme
        self.precision = 1.0      

        # visibilidad
        self.show_newton = True
        self.show_rel = True
        self.show_planet_newton = False
        self.show_planet_rel = True

        # trails
        self.trail_newton = []
        self.trail_rel = []

        pygame.font.init()
        self.font = pygame.font.SysFont("arial", 20)

    # ----------------------------------------------------------
    # Función clave: punto de la elipse con precesión rotada
    # ----------------------------------------------------------
    def ellipse_point_with_precession(self, f1, phi, theta, a=A, e=ECCENTRICITY):
        """
        Genera un punto de una elipse rotada.
        """
        r = (a * (1 - e * e)) / (1 + e * math.cos(theta - phi))

        x = f1[0] + r * math.cos(theta)
        y = f1[1] + r * math.sin(theta)
        return int(x), int(y)

    def clear_trails(self):
        self.trail_newton.clear()
        self.trail_rel.clear()

    # ----------------------------------------------------------
    # Main loop
    # ----------------------------------------------------------
    def run(self):
        running = True

        while running:
            self.screen.fill(COLOR_BG)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        return

                    # velocidad orbital
                    if event.key == pygame.K_UP:
                        self.speed *= 1.3
                    if event.key == pygame.K_DOWN:
                        self.speed *= 0.75

                    # controlar precesión: derecha aumenta precisión (menos precesión)
                    if event.key == pygame.K_RIGHT:
                        self.precision = min(1.0, self.precision + 0.05)
                    if event.key == pygame.K_LEFT:
                        self.precision = max(0.0, self.precision - 0.05)

                    # toggles
                    if event.key == pygame.K_1:
                        self.show_newton = not self.show_newton
                    if event.key == pygame.K_2:
                        self.show_rel = not self.show_rel
                    if event.key == pygame.K_n:
                        self.show_planet_newton = not self.show_planet_newton
                    if event.key == pygame.K_r:
                        self.show_planet_rel = not self.show_planet_rel
                    if event.key == pygame.K_c:
                        self.clear_trails()

            # ----------------------------------------------
            # Actualizar dinámica orbital
            # ----------------------------------------------
            self.theta += self.speed

            # ----------------------------------------------
            # NUEVA precesión simple y estable:
            # precesión máxima cuando precision = 0
            # precesión mínima cuando precision = 1
            # ----------------------------------------------
            base_precession = 0.0007            # velocidad base de rotación de la elipse
            factor = (1.0 - self.precision) * 25  # amplificador
            self.phi_rel += base_precession * factor

            # ----------------------------------------------
            # Newton (sin rotación)
            # ----------------------------------------------
            x_new, y_new = self.ellipse_point_with_precession(
                SCREEN_CENTER, 0.0, self.theta
            )
            self.trail_newton.append((x_new, y_new))
            if len(self.trail_newton) > MAX_TRAIL_POINTS:
                self.trail_newton.pop(0)

            # ----------------------------------------------
            # Relativista (la elipse rota)
            # ----------------------------------------------
            x_rel, y_rel = self.ellipse_point_with_precession(
                SCREEN_CENTER, self.phi_rel, self.theta
            )
            self.trail_rel.append((x_rel, y_rel))
            if len(self.trail_rel) > MAX_TRAIL_POINTS:
                self.trail_rel.pop(0)

            # ----------------------------------------------
            # Sol
            # ----------------------------------------------
            pygame.draw.circle(self.screen, COLOR_SOL, SCREEN_CENTER, 20)

            # ----------------------------------------------
            # Newton (puntos suaves)
            # ----------------------------------------------
            if self.show_newton:
                surfN = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                for i, (px, py) in enumerate(self.trail_newton):
                    if i % 5 == 0:
                        pygame.draw.circle(surfN, COLOR_NEWTON, (px, py), 2)
                self.screen.blit(surfN, (0, 0))

            # ----------------------------------------------
            # Relativista
            # ----------------------------------------------
            if self.show_rel and len(self.trail_rel) > 2:
                pygame.draw.lines(self.screen, COLOR_REL, False, self.trail_rel, 2)

            # planetas
            if self.show_planet_newton:
                pygame.draw.circle(self.screen, (200, 200, 200), (x_new, y_new), 6)

            if self.show_planet_rel:
                pygame.draw.circle(self.screen, COLOR_PLANET, (x_rel, y_rel), 7)

            # ----------------------------------------------
            # Texto
            # ----------------------------------------------
            lines = [
                f"Velocidad (Up/Down): {self.speed:.4f}",
                f"Precision (Left/Right): {self.precision:.2f}",
                "1: Toggle Newton   2: Toggle Relativista",
                "N: planeta Newton  R: planeta Rel",
                "C: limpiar         ESC: menu"
            ]
            y = 10
            for line in lines:
                t = self.font.render(line, True, COLOR_TEXT)
                self.screen.blit(t, (10, y))
                y += 22

            pygame.display.flip()
            self.clock.tick(60)


# -----------------------------------------------------------
# Para probar directamente el módulo:
# -----------------------------------------------------------
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((900, 700))
    sim = PerihelioSim(screen)
    sim.run()
