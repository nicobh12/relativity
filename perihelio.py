# perihelio.py
import pygame
import math
import random
import sys
from config import BACKGROUND, WHITE, YELLOW, RED

# ================================
# VISUAL CONSTANTS
# ================================
ECCENTRICITY = 0.3
A = 200
SCREEN_CENTER = (450, 350)

COLOR_SOL = YELLOW
COLOR_NEWTON = RED
COLOR_REL = (60, 220, 140)
COLOR_PLANET = (100, 200, 255)
COLOR_TEXT = WHITE
MAX_TRAIL_POINTS = 6000


# ================================
# PREMIUM BACKGROUND HELPERS
# ================================
def draw_radial_gradient(surface, center, radius, inner_color, outer_color):
    cx, cy = center
    for r in range(radius, 0, -1):
        t = r / radius
        color = (
            int(inner_color[0] * t + outer_color[0] * (1 - t)),
            int(inner_color[1] * t + outer_color[1] * (1 - t)),
            int(inner_color[2] * t + outer_color[2] * (1 - t)),
        )
        pygame.draw.circle(surface, color, (cx, cy), r)


def gen_stars(w, h, n=120):
    return [(random.randint(0, w), random.randint(0, h), random.choice([1, 1, 2])) for _ in range(n)]


def draw_stars(surface, stars, twinkle_phase):
    for x, y, s in stars:
        offset = 0.5 + 0.5 * math.sin((x * 12 + y * 7 + twinkle_phase) * 0.002)
        size = max(1, int(s * offset))
        pygame.draw.circle(surface, WHITE, (x, y), size)


def draw_sun_glow(surface, x, y):
    pygame.draw.circle(surface, COLOR_SOL, (x, y), 18)
    for r, a in ((30, 40), (50, 18), (80, 8)):
        glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (COLOR_SOL[0], COLOR_SOL[1], COLOR_SOL[2], a), (r, r), r)
        surface.blit(glow, (x - r, y - r))


# ================================
# UI COMPONENTS — ORIGINAL GPS SLIDER
# ================================
class Slider:
    def __init__(self, x, y, w, min_val, max_val, start_val, step=0.1, label="", ticks=None):
        # visible bar
        self.rect = pygame.Rect(x, y, w, 12)

        # BIG clickable area
        self.grab_rect = pygame.Rect(x, y - 12, w, 36)

        self.min = min_val
        self.max = max_val
        self.value = start_val
        self.label = label
        self.step = step
        self.grabbed = False
        self.ticks = ticks or []
        self.font = pygame.font.SysFont("arial", 18)

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.grab_rect.collidepoint(event.pos):     # ← use big hitbox
                self.grabbed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.grabbed = False

        elif event.type == pygame.MOUSEMOTION and self.grabbed:
            mx = max(self.rect.left, min(event.pos[0], self.rect.right))
            t = (mx - self.rect.left) / self.rect.width
            raw = self.min + t * (self.max - self.min)
            self.value = round(raw / self.step) * self.step

    def draw(self, screen):
        # label
        txt = f"{self.label}: {self.value:.2f}"
        screen.blit(self.font.render(txt, True, (230, 230, 250)), (self.rect.x, self.rect.y - 25))

        # baseline
        pygame.draw.rect(screen, (220, 220, 240), self.rect)

        # ticks
        for tval in self.ticks:
            px = self.rect.x + (tval - self.min) / (self.max - self.min) * self.rect.width
            pygame.draw.line(screen, (150, 150, 200), (px, self.rect.y - 6), (px, self.rect.y + 6), 2)

        # handle
        t = (self.value - self.min) / (self.max - self.min)
        hx = self.rect.x + int(t * self.rect.width)
        pygame.draw.circle(screen, (100, 150, 255), (hx, self.rect.y + 6), 10)

# ================================
# Checkbox + Button
# ================================
class CheckboxUI:
    def __init__(self, x, y, label, checked=True):
        self.rect = pygame.Rect(x, y, 18, 18)
        self.label = label
        self.checked = checked
        self.font = pygame.font.SysFont("arial", 16)

    def draw(self, screen):
        pygame.draw.rect(screen, (80, 85, 100), self.rect, border_radius=3)
        if self.checked:
            pygame.draw.rect(screen, (220, 220, 220), self.rect.inflate(-4, -4), border_radius=3)

        screen.blit(self.font.render(self.label, True, WHITE), (self.rect.right + 6, self.rect.y - 2))


class ButtonUI:
    def __init__(self, x, y, w, h, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.font = pygame.font.SysFont("arial", 16)

    def draw(self, screen):
        pygame.draw.rect(screen, (70, 75, 90), self.rect, border_radius=8)
        t = self.font.render(self.label, True, WHITE)
        screen.blit(t, (self.rect.centerx - t.get_width() // 2, self.rect.centery - t.get_height() // 2))


# ================================
# MAIN SIMULATOR
# ================================
class PerihelioSim:
    def __init__(self, screen):
        self.screen = screen
        self.W, self.H = screen.get_size()
        self.clock = pygame.time.Clock()

        # stars
        self.stars = gen_stars(self.W, self.H, 140)
        self.star_phase = 0

        # physics
        self.theta = 0
        self.phi_rel = 0

        # trails
        self.trail_newton = []
        self.trail_rel = []

        # sliders (GPS STYLE)
        self.slider_speed = Slider(120, self.H - 72, 420, 1, 30, 1, step=1, label="Velocidad (x)")
        self.slider_precision = Slider(560, self.H - 72, 320, 0, 1, 0.5, step=0.01, label="Precisión", ticks=[0.5])

        # toggles & button
        self.chk_newton = CheckboxUI(0, 0, "Newton (punteado)", True)
        self.chk_rel = CheckboxUI(0, 0, "Relativista (línea)", True)
        self.chk_p_new = CheckboxUI(0, 0, "Planeta Newton", True)
        self.chk_p_rel = CheckboxUI(0, 0, "Planeta Rel", True)
        self.btn_clear = ButtonUI(0, 0, 120, 36, "Limpiar Trails")

        # fonts
        self.font = pygame.font.SysFont("arial", 18)
        self.small = pygame.font.SysFont("arial", 14)

    def ellipse_point(self, f1, phi, theta, a=A, e=ECCENTRICITY):
        r = (a * (1 - e * e)) / (1 + e * math.cos(theta - phi))
        return int(f1[0] + r * math.cos(theta)), int(f1[1] + r * math.sin(theta))

    def clear_trails(self):
        self.trail_newton.clear()
        self.trail_rel.clear()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)

            # ---- EVENTS ----
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    return

                self.slider_speed.handle(ev)
                self.slider_precision.handle(ev)

                if ev.type == pygame.MOUSEBUTTONDOWN:
                    for chk in [self.chk_newton, self.chk_rel, self.chk_p_new, self.chk_p_rel]:
                        if chk.rect.collidepoint(ev.pos):
                            chk.checked = not chk.checked

                    if self.btn_clear.rect.collidepoint(ev.pos):
                        self.clear_trails()

            # ---- UPDATE ----
            self.star_phase += dt * 0.02

            speed = self.slider_speed.value
            self.theta += 0.009 * speed

            precision = self.slider_precision.value
            exaggeration = (1 - precision) * 25
            self.phi_rel += 0.0007 * exaggeration

            x_new, y_new = self.ellipse_point(SCREEN_CENTER, 0, self.theta)
            x_rel, y_rel = self.ellipse_point(SCREEN_CENTER, self.phi_rel, self.theta)

            self.trail_newton.append((x_new, y_new))
            if len(self.trail_newton) > MAX_TRAIL_POINTS:
                self.trail_newton.pop(0)

            self.trail_rel.append((x_rel, y_rel))
            if len(self.trail_rel) > MAX_TRAIL_POINTS:
                self.trail_rel.pop(0)

            # ---- DRAW ----
            draw_radial_gradient(self.screen, (self.W // 2, self.H // 2), max(self.W, self.H),
                                 (20, 24, 40), BACKGROUND)
            draw_stars(self.screen, self.stars, self.star_phase)

            draw_sun_glow(self.screen, SCREEN_CENTER[0], SCREEN_CENTER[1])

            # Trails
            if self.chk_newton.checked:
                s = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
                for i, p in enumerate(self.trail_newton):
                    if i % 3 == 0:
                        pygame.draw.circle(s, COLOR_NEWTON, p, 2)
                self.screen.blit(s, (0, 0))

            if self.chk_rel.checked and len(self.trail_rel) > 1:
                pygame.draw.lines(self.screen, COLOR_REL, False, self.trail_rel, 2)

            # planets
            if self.chk_p_new.checked:
                pygame.draw.circle(self.screen, (200, 200, 200), (x_new, y_new), 6)

            if self.chk_p_rel.checked:
                pygame.draw.circle(self.screen, COLOR_PLANET, (x_rel, y_rel), 7)

            # ---- RIGHT PANEL ----
            box_w, box_h = 340, 260
            box_x, box_y = self.W - box_w - 20, 40

            panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            pygame.draw.rect(panel, (25, 25, 40, 220), (0, 0, box_w, box_h), border_radius=12)

            panel.blit(self.font.render("Precesión del Perihelio", True, WHITE), (12, 12))

            yv = 46
            panel.blit(self.small.render(f"Velocidad anim.: {speed:.1f}×", True, WHITE), (12, yv))
            panel.blit(self.small.render(f"Precisión vis.: {precision:.2f}", True, WHITE), (12, yv + 20))

            explanation = [
                "• Newton: órbita kepleriana estable.",
                "• Relativista: el eje mayor rota lentamente.",
                "• Precisión = cuánta precesión exageramos.",
                "• 1.0 = real, 0.0 = súper exagerado.",
                "• Velocidad = rapidez de animación."
            ]
            yy = yv + 52
            for line in explanation:
                panel.blit(self.small.render(line, True, WHITE), (12, yy))
                yy += 16

            # checkboxes + button positions
            offset = 90   # ← bajarlos 50 px

            self.chk_newton.rect.topleft = (box_x + 12, box_y + yy + 6  + offset)
            self.chk_rel.rect.topleft    = (box_x + 12, box_y + yy + 32 + offset)
            self.chk_p_new.rect.topleft  = (box_x + 12, box_y + yy + 58 + offset)
            self.chk_p_rel.rect.topleft  = (box_x + 12, box_y + yy + 84 + offset)

            self.btn_clear.rect.topleft = (box_x + box_w - 140, box_y + box_h - 48)

            # draw UI
            self.screen.blit(panel, (box_x, box_y))
            self.chk_newton.draw(self.screen)
            self.chk_rel.draw(self.screen)
            self.chk_p_new.draw(self.screen)
            self.chk_p_rel.draw(self.screen)
            self.btn_clear.draw(self.screen)

            # bottom slider panel
            pygame.draw.rect(self.screen, (18, 18, 28, 220), (0, self.H - 110, self.W, 110))

            self.slider_speed.draw(self.screen)
            self.slider_precision.draw(self.screen)

            pygame.display.flip()
