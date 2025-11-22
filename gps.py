import pygame
import math
import random
import sys
from ui_elements import BackButtonUI

# ---------- CONSTANTES ----------
RE = 6371  # Radio terrestre en km
G = 6.67430e-11
M_earth = 5.972e24


def earth_masses_to_kg(m):
    return m * M_earth


# ============================================================
# ★★★ VISUALS: ESTRELLAS + GRADIENT + GLOW (igual a perihelio)
# ============================================================
def draw_radial_gradient(surface, center, radius, inner, outer):
    cx, cy = center
    for r in range(radius, 0, -1):
        t = r / radius
        color = (
            int(inner[0] * t + outer[0] * (1 - t)),
            int(inner[1] * t + outer[1] * (1 - t)),
            int(inner[2] * t + outer[2] * (1 - t)),
        )
        pygame.draw.circle(surface, color, (cx, cy), r)


def gen_stars(w, h, n=120):
    return [(random.randint(0, w), random.randint(0, h),
             random.choice([1, 1, 2])) for _ in range(n)]


def draw_stars(surface, stars, phase):
    for x, y, s in stars:
        tw = 0.5 + 0.5 * math.sin((x * 11 + y * 5 + phase) * 0.002)
        size = max(1, int(s * tw))
        pygame.draw.circle(surface, (255, 255, 255), (x, y), size)


# ============================================================
# ★★★ SLIDER (gps-style, mismo al de perihelio)
# ============================================================
class Slider:
    def __init__(self, x, y, w, min_val, max_val, start_val,
                 step=0.1, label="", ticks=None):

        self.rect = pygame.Rect(x, y, w, 12)
        self.grab_rect = pygame.Rect(x, y - 12, w, 36)

        self.min = min_val
        self.max = max_val
        self.value = start_val
        self.label = label
        self.step = step
        self.ticks = ticks or []
        self.font = pygame.font.SysFont("arial", 18)
        self.grabbed = False

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.grab_rect.collidepoint(event.pos):
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
        screen.blit(self.font.render(txt, True, (220, 230, 255)),
                    (self.rect.x, self.rect.y - 25))

        # baseline
        pygame.draw.rect(screen, (220, 220, 240), self.rect)

        # ticks
        for tval in self.ticks:
            px = self.rect.x + (tval - self.min) / (self.max - self.min) * self.rect.width
            pygame.draw.line(screen, (140, 150, 200),
                             (px, self.rect.y - 6),
                             (px, self.rect.y + 6), 2)

        # handle
        t = (self.value - self.min) / (self.max - self.min)
        hx = self.rect.x + int(t * self.rect.width)
        pygame.draw.circle(screen, (100, 150, 255), (hx, self.rect.y + 6), 10)


# ============================================================
# ★★★ SIMULACIÓN GPS
# ============================================================
class GPSSim:
    def __init__(self, screen):
        self.screen = screen
        self.W, self.H = screen.get_size()
        self.clock = pygame.time.Clock()
        self.btn_back = BackButtonUI()

        # estrellas
        self.stars = gen_stars(self.W, self.H, 150)
        self.star_phase = 0

        # ----- sliders -----
        self.slider_radius = Slider(
            self.W - 320, 40, 260,
            0.3 * RE, 3.0 * RE, 1.0 * RE,
            step=0.05 * RE,
            label="Radio (km)",
            ticks=[0.5*RE, 1*RE, 1.5*RE, 2*RE, 2.5*RE, 3*RE]
        )

        self.slider_mass = Slider(
            self.W - 320, 120, 260,
            0.5, 3.0, 1.0,
            step=0.1,
            label="Masa (M_e)",
            ticks=[0.5, 1, 1.5, 2, 2.5, 3]
        )

        self.slider_distance = Slider(
            self.W - 320, 200, 260,
            1.1 * RE, 6.0 * RE, 4.0 * RE,
            step=0.1 * RE,
            label="Altura satélite (km)",
            ticks=[1.5*RE, 2*RE, 3*RE, 4*RE, 5*RE, 6*RE]
        )

        # imágenes
        self.planet_img = self.safe_load("earth.png", 50)
        self.sat_img = self.safe_load("sat.png", 20)

        self.font = pygame.font.SysFont("arial", 20)
        self.small = pygame.font.SysFont("arial", 16)

    def safe_load(self, path, r):
        try:
            im = pygame.image.load(path).convert_alpha()
            return im
        except:
            surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (100, 150, 255), (r, r), r)
            return surf

    # ----------------- FÍSICA RELATIVISTA -----------------
    def compute_relativistic_drift(self, mass_earths, r_km, planet_r_km):
        M = earth_masses_to_kg(mass_earths)
        r = r_km * 1000
        c = 299792458

        # velocidad orbital newtoniana
        v = math.sqrt(G * M / r)

        # dilataciones
        dt_grav = G*M/(c*c) * (1/r - 1/(planet_r_km*1000))
        dt_vel = -v*v/(2*c*c)

        total = dt_grav + dt_vel
        return total*86400*1e6, dt_grav*86400*1e6, dt_vel*86400*1e6

    # ----------------- MAIN LOOP -----------------
    def run(self):
        running = True
        angle = 0

        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    return
                if self.btn_back.handle(ev):
                    return

                self.slider_mass.handle(ev)
                self.slider_radius.handle(ev)
                self.slider_distance.handle(ev)

            # ==== fondo estrellado ====
            draw_radial_gradient(
                self.screen,
                (self.W//2, self.H//2),
                max(self.W, self.H),
                (15, 15, 30),
                (5, 5, 15)
            )

            self.star_phase += 0.35
            draw_stars(self.screen, self.stars, self.star_phase)

            # ==== valores ====
            R = self.slider_radius.value
            M = self.slider_mass.value
            D = self.slider_distance.value

            # ==== planeta ====
            cx, cy = self.W//3, self.H//2
            scale = int(R / 100)
            planet = pygame.transform.scale(self.planet_img, (scale, scale))
            self.screen.blit(planet, planet.get_rect(center=(cx, cy)))

            # ==== órbita ====
            r_px = int(D / 100)
            pygame.draw.circle(self.screen, (120, 120, 160), (cx, cy), r_px, 1)

            angle += 0.01
            sx = cx + r_px*math.cos(angle)
            sy = cy + r_px*math.sin(angle)

            sat = pygame.transform.scale(self.sat_img, (38, 38))
            self.screen.blit(sat, sat.get_rect(center=(sx, sy)))

            # ==== relatividad ====
            total, grav, vel = self.compute_relativistic_drift(M, D, R)

            # ==== panel info ====
            box_x, box_y = self.W - 360, 260
            box_w, box_h = 330, 380
            pygame.draw.rect(self.screen, (20, 20, 40, 220),
                             (box_x, box_y, box_w, box_h), border_radius=12)

            info = [
                f"Masa planeta: {M:.1f} M_e",
                f"Radio planeta: {R:,.0f} km",
                f"Altura satélite: {D-R:,.0f} km",
                "",
                "Ajuste relativista:",
                f"{total: .3f} µs/día",
                "",
                "Desglose:",
                f"  Grav.:  {grav: .3f} µs/día",
                f"  Vel.:   {vel: .3f} µs/día",
                "",
                "• Campo gravitacional acelera",
                "  el reloj del satélite.",
                "• La velocidad orbital lo retarda.",
                "• GPS corrige esta diferencia."
            ]

            y = box_y + 15
            for line in info:
                self.screen.blit(self.small.render(line, True, (230, 230, 250)),
                                 (box_x + 10, y))
                y += 22

            # ==== sliders ====
            self.slider_radius.draw(self.screen)
            self.slider_mass.draw(self.screen)
            self.slider_distance.draw(self.screen)

            self.btn_back.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)
