# perihelio.py
import pygame
import math
import sys

# ---------------------
# Parámetros visuales / físicos
# ---------------------
# Excentricidad realista (puedes ajustar aquí)
ECCENTRICITY = 0.2056      # Mercurio real (puedes cambiar si quieres)
A = 220                    # semieje mayor en pixeles (tamaño de la elipse)
SCREEN_CENTER = (450, 350) # punto donde colocamos el Sol (x,y)

# Colores RGBA
COLOR_BG = (8, 10, 20)
COLOR_SOL = (255, 180, 70)
COLOR_NEWTON = (220, 220, 220, 80)   # blanco suave con alpha baja
COLOR_REL = (60, 220, 140, 255)      # verde brillante (relativista)
COLOR_PLANET = (120, 200, 255)
COLOR_TEXT = (230, 230, 230)

# Trail settings
NEWTON_DOT_SPACING = 6  # dibuja punto cada N puntos (efecto punteado)
MAX_TRAIL_POINTS = 5000


class PerihelioSim:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # dinámica
        self.theta = 0.0            # ángulo orbital del "planeta"
        self.speed = 0.01           # incremento de theta por frame (velocidad)
        self.precision = 0.5        # de 0 a 1; 0 -> muy exagerado, 1 -> muy preciso (realista)

        # Relativista: centro de la elipse se moverá en circunferencia de radio center_radius
        # center_radius será función de (1 - precision) para exagerar cuando precision ~ 0
        self.center_orbit_angle = 0.0       # ángulo del movimiento del centro
        self.center_orbit_speed = 0.002     # velocidad angular del centro (ajustable)
        self.center_base_radius = 60        # amplitud máxima del desplazamiento del centro (px)

        # control de visualización
        self.show_newton = True
        self.show_rel = True
        self.show_planet_newton = False
        self.show_planet_rel = True

        # trails (listas de puntos)
        self.trail_newton = []
        self.trail_rel = []

        # fuentes
        self.font = pygame.font.SysFont("arial", 20)

    def clear_trails(self):
        self.trail_newton = []
        self.trail_rel = []

    def ellipse_point(self, center_x, center_y, theta, a=A, e=ECCENTRICITY):
        """
        Devuelve la (x,y) en pixeles de la elipse paramétrica con foco en un lado:
        usamos r(θ) = a(1-e^2)/(1 + e cos θ), y luego ubicamos el punto con
        respecto al centro proporcionado (center_x, center_y) asumiendo que
        ese centro es el centro geométrico de la elipse en nuestra visualización.
        """
        # Usamos la representación polar centrada en el centro geométrico:
        # Convertimos de "r(θ) con foco en uno de los focos" a una posición alrededor del centro:
        # una forma más sencilla y estable visualmente: construir la elipse paramétricamente
        # x = a * cos(t) - a*e   (shift para foco) ... pero para control visual usamos paramétrico:
        b = a * math.sqrt(1 - e ** 2)
        x = center_x + int(a * math.cos(theta))
        y = center_y + int(b * math.sin(theta))
        return x, y

    def run(self):
        running = True

        while running:
            self.screen.fill(COLOR_BG)

            # eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        return

                    # velocidad
                    if event.key == pygame.K_UP:
                        self.speed *= 1.3
                    if event.key == pygame.K_DOWN:
                        self.speed *= 0.75

                    # precision (0..1)
                    if event.key == pygame.K_RIGHT:
                        self.precision = min(1.0, self.precision + 0.05)
                    if event.key == pygame.K_LEFT:
                        self.precision = max(0.0, self.precision - 0.05)

                    # alternar visibilidad
                    if event.key == pygame.K_1:
                        self.show_newton = not self.show_newton
                    if event.key == pygame.K_2:
                        self.show_rel = not self.show_rel

                    # limpiar trails
                    if event.key == pygame.K_c:
                        self.clear_trails()

                    # planet visibility
                    if event.key == pygame.K_n:
                        self.show_planet_newton = not self.show_planet_newton
                    if event.key == pygame.K_r:
                        self.show_planet_rel = not self.show_planet_rel

            # parámetros dependientes de precision
            # center radius: cuánto se desplaza el centro de la elipse (0 si precision=1)
            center_radius = self.center_base_radius * (1.0 - self.precision)
            # velocidad del centro se escala con velocidad general
            center_speed = self.center_orbit_speed * max(0.2, self.speed * 50)

            # Avanzamos ángulos
            self.theta += self.speed
            self.center_orbit_angle += center_speed

            # --- Newton: centro fijo (centro geométrico de la elipse) ---
            # ponemos la elipse Newtoniana con su centro desplazado hacia +focus_shift en x,
            # para que el Sol (SCREEN_CENTER) quede en un foco aproximado.
            a = A
            e = ECCENTRICITY
            b = a * math.sqrt(1 - e**2)

            # posición del centro geométrico de la elipse newtoniana: lo ponemos ligeramente desplazado
            # respecto al Sol para que el Sol quede en un foco. Focus shift en x:
            focus_shift = int(a * e)  # distancia entre centro geométrico y foco
            newton_center = (SCREEN_CENTER[0] - focus_shift, SCREEN_CENTER[1])

            # punto del planeta newtoniano (usamos parámetro theta para la parametrización)
            x_new, y_new = self.ellipse_point(newton_center[0], newton_center[1], self.theta, a=a, e=e)

            # agregamos a trail newton (punteado luego)
            self.trail_newton.append((x_new, y_new))
            if len(self.trail_newton) > MAX_TRAIL_POINTS:
                self.trail_newton.pop(0)

            # --- Relativista: centro que se mueve sobre una circunferencia centrada en el Sol ---
            center_offset_x = int(center_radius * math.cos(self.center_orbit_angle))
            center_offset_y = int(center_radius * math.sin(self.center_orbit_angle))
            rel_center = (SCREEN_CENTER[0] + center_offset_x, SCREEN_CENTER[1] + center_offset_y)

            # punto del planeta relativista (usamos theta también, pero el hecho de mover el centro crea la rotación relativa)
            x_rel, y_rel = self.ellipse_point(rel_center[0], rel_center[1], self.theta, a=a, e=e)

            self.trail_rel.append((x_rel, y_rel))
            if len(self.trail_rel) > MAX_TRAIL_POINTS:
                self.trail_rel.pop(0)

            # --- Dibujar SOL ---
            pygame.draw.circle(self.screen, COLOR_SOL, SCREEN_CENTER, 20)

            # --- Dibujar Newton (fija) con opacidad y punteado ---
            if self.show_newton:
                # superficie con alpha para dibujar la elipse en baja opacidad
                surf_new = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                # dibujamos puntos punteados: sólo cada NEWTON_DOT_SPACING
                for i, (px, py) in enumerate(self.trail_newton):
                    if i % NEWTON_DOT_SPACING == 0:
                        pygame.draw.circle(surf_new, COLOR_NEWTON, (px, py), 2)
                # dibujar contorno leve de la elipse (paramétrico)
                # generar puntos de la elipse completa (opcional)
                ellipse_pts = []
                steps = 360
                for t_i in range(steps):
                    th = 2 * math.pi * (t_i / steps)
                    px, py = self.ellipse_point(newton_center[0], newton_center[1], th, a=a, e=e)
                    ellipse_pts.append((px, py))
                if len(ellipse_pts) > 2:
                    pygame.draw.aalines(surf_new, (200,200,200,60), True, ellipse_pts)
                # blit con alpha
                self.screen.blit(surf_new, (0,0))

            # --- Dibujar Relativista (centro móvil) con estela continua ---
            if self.show_rel:
                surf_rel = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                # dibujar línea continua del trail relativista
                if len(self.trail_rel) > 2:
                    pygame.draw.lines(surf_rel, COLOR_REL, False, self.trail_rel, 2)
                # dibujar contorno de la elipse actual (en su centro) para referencia
                ellipse_pts_rel = []
                steps = 360
                for t_i in range(steps):
                    th = 2 * math.pi * (t_i / steps)
                    px, py = self.ellipse_point(rel_center[0], rel_center[1], th, a=a, e=e)
                    ellipse_pts_rel.append((px, py))
                if len(ellipse_pts_rel) > 2:
                    pygame.draw.aalines(surf_rel, (60,220,140,40), True, ellipse_pts_rel)
                self.screen.blit(surf_rel, (0,0))

            # --- Dibujar planetas si se desea ---
            if self.show_planet_newton:
                pygame.draw.circle(self.screen, (150,150,150), (x_new, y_new), 6)
            if self.show_planet_rel:
                pygame.draw.circle(self.screen, COLOR_PLANET, (x_rel, y_rel), 7)

            # --- UI de texto ---
            info_lines = [
                f"Velocidad (Up/Down): {self.speed:.4f}",
                f"Precision (Izq/Dcha): {self.precision:.2f}",
                f"Center radius (auto) : {center_radius:.1f}px",
                "Teclas: 1 toggle Newton, 2 toggle Rel, N toggle Newton-planet, R toggle Rel-planet",
                "C limpia trails, ESC vuelve al menú"
            ]
            y_text = 10
            for line in info_lines:
                surf_txt = self.font.render(line, True, COLOR_TEXT)
                self.screen.blit(surf_txt, (10, y_text))
                y_text += 24

            pygame.display.flip()
            self.clock.tick(60)
