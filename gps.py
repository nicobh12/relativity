import pygame
import math
import sys
from ui_elements import Button

# ---------------------------------------
# Parámetros
# ---------------------------------------
WIDTH, HEIGHT = 900, 700
CENTER = (WIDTH // 2 - 120, HEIGHT // 2)

# distancia típica GPS ~ 26,600 km de altitud
GPS_MIN = 1.5e7       # mínimo (m)
GPS_MAX = 3.5e7       # máximo (m)

# masas: 0.5 a 3 masas terrestres
MASS_MIN = 0.5
MASS_MAX = 3.0

COLOR_BG = (8, 10, 20)
COLOR_TEXT = (230, 230, 230)


# ----------------------------------------------------
# Clase Slider sencilla
# ----------------------------------------------------
class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, start_val, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.label = label
        self.dragging = False

        # posición inicial en píxeles
        self.handle_x = x + int((start_val - min_val) / (max_val - min_val) * w)

        self.font = pygame.font.SysFont("arial", 20)

    def draw(self, screen):
        # línea
        pygame.draw.line(screen, (180, 180, 180),
                         (self.rect.x, self.rect.y + self.rect.height // 2),
                         (self.rect.x + self.rect.width, self.rect.y + self.rect.height // 2), 4)

        # handle
        pygame.draw.circle(screen, (120, 200, 255),
                           (self.handle_x, self.rect.y + self.rect.height // 2), 10)

        # label
        label = self.font.render(
            f"{self.label}: {self.value:.2f}", True, (230, 230, 230))
        screen.blit(label, (self.rect.x, self.rect.y - 24))

    def update(self, event):
        mx, my = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if abs(mx - self.handle_x) < 12 and abs(my - (self.rect.y + self.rect.height // 2)) < 12:
                self.dragging = True

        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        if event.type == pygame.MOUSEMOTION and self.dragging:
            # actualizar handle
            self.handle_x = max(self.rect.x, min(mx, self.rect.x + self.rect.width))

            # convertir a valor
            t = (self.handle_x - self.rect.x) / self.rect.width
            self.value = self.min_val + t * (self.max_val - self.min_val)


# ----------------------------------------------------
# Simulador GPS
# ----------------------------------------------------
class GPSSim:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        pygame.font.init()
        self.font = pygame.font.SysFont("arial", 20)
        self.info_font = pygame.font.SysFont("arial", 18)

        # sliders
        self.mass_slider = Slider(WIDTH - 260, 40, 200, 20, MASS_MIN, MASS_MAX, 1.0, "Masa (Tierras)")
        self.dist_slider = Slider(WIDTH - 260, 120, 200, 20, GPS_MIN, GPS_MAX, 2.6e7, "Distancia (m)")

        # ángulo del satélite
        self.theta = 0.0

        # cargar imágenes, o dibujar formas si no existen
        self.planet_img = self.safe_load("earth.png", radius=70)
        self.sat_img = self.safe_load("sat.png", radius=18)

    # carga png o crea círculo si no existe
    def safe_load(self, path, radius):
        try:
            img = pygame.image.load(path).convert_alpha()
            return img
        except:
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (100, 150, 255), (radius, radius), radius)
            return surf

    def run(self):
        running = True

        while running:
            self.screen.fill(COLOR_BG)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

                # sliders
                self.mass_slider.update(event)
                self.dist_slider.update(event)

            # -----------------------------------------
            # Actualizar dinámica
            # -----------------------------------------
            self.theta += 0.01

            # tamaño del planeta según masa
            mass = self.mass_slider.value
            base_size = 160
            scale = 0.6 + 0.4 * (mass - MASS_MIN) / (MASS_MAX - MASS_MIN)
            planet_size = int(base_size * scale)
            planet_img = pygame.transform.smoothscale(self.planet_img, (planet_size, planet_size))

            # posición del planeta
            planet_rect = planet_img.get_rect(center=CENTER)
            self.screen.blit(planet_img, planet_rect)

            # distancia visual del satélite
            dist = self.dist_slider.value
            visual_r = 120 + 140 * (dist - GPS_MIN) / (GPS_MAX - GPS_MIN)

            # coordenadas del satélite
            sx = CENTER[0] + visual_r * math.cos(self.theta)
            sy = CENTER[1] + visual_r * math.sin(self.theta)

            # dibujar satélite
            sat_rect = self.sat_img.get_rect(center=(sx, sy))
            self.screen.blit(self.sat_img, sat_rect)

            # -----------------------------------------
            # Cálculo físico: correcciones relativistas
            # -----------------------------------------
            G = 6.674e-11
            M = mass * 5.97e24
            r = dist

            # Relatividad general (curvatura gravitacional)
            GR = - (3 * G * M) / (r * 3e8**2)

            # Relatividad especial (velocidad del satélite)
            v = math.sqrt(G * M / r)
            SR = - (v**2) / (2 * 3e8**2)

            total = (GR + SR) * 86400 * 1e9  # nanosegundos por día

            # -----------------------------------------
            # Recuadro informativo
            # -----------------------------------------
            info_box = pygame.Surface((420, 260), pygame.SRCALPHA)
            pygame.draw.rect(info_box, (30, 30, 50, 180), (0, 0, 420, 260), border_radius=12)

            text = [
                f"Corrección relativista total: {total:+.2f} ns/día",
                "",
                f"GR (curvatura gravitacional): {GR*86400*1e9:+.2f} ns/día",
                f"SR (velocidad del satélite): {SR*86400*1e9:+.2f} ns/día",
                "",
                "Explicación:",
                " • La gravedad más intensa hace que los relojes en órbita",
                "   avancen más rápido que en la superficie (GR).",
                " • La velocidad del satélite hace que su reloj avance",
                "   más lento (SR).",
                " • La suma produce un desfase que debe corregirse para",
                "   que el GPS mantenga precisión en las coordenadas."
            ]

            y = 10
            for line in text:
                img = self.info_font.render(line, True, COLOR_TEXT)
                info_box.blit(img, (10, y))
                y += 20

            self.screen.blit(info_box, (WIDTH - 420 - 20, HEIGHT - 300))

            # sliders
            self.mass_slider.draw(self.screen)
            self.dist_slider.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)
