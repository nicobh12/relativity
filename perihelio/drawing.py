# perihelio/drawing.py

import pygame
from pygame import gfxdraw

# Colores
COLOR_BG = (5, 5, 15)
COLOR_NEWTON = (255, 255, 255)
COLOR_REL = (60, 255, 150)

def draw_background(surface):
    surface.fill(COLOR_BG)


def draw_orbit_paths(surface, state, show_newton, show_rel):
    if show_newton:
        for (x, y) in state["orbit_points_newton"]:
            gfxdraw.pixel(surface, x, y, COLOR_NEWTON)

    if show_rel:
        if len(state["orbit_points_rel"]) > 2:
            pygame.draw.lines(surface, COLOR_REL, False, state["orbit_points_rel"], 2)


def draw_radial_gradient(surface, x, y, radius, inner_color, outer_color):
    """Dibuja un circulito degradado."""
    for r in range(radius, 0, -1):
        t = r / radius
        color = (
            int(inner_color[0] * t + outer_color[0] * (1 - t)),
            int(inner_color[1] * t + outer_color[1] * (1 - t)),
            int(inner_color[2] * t + outer_color[2] * (1 - t)),
        )
        gfxdraw.filled_circle(surface, x, y, r, color)


def draw_mercury_planets(surface, pos_new, pos_rel, show_newton, show_rel):
    # ----------------------
    # Newtoniano (más apagado)
    # ----------------------
    if show_newton:
        draw_radial_gradient(
            surface,
            pos_new[0], pos_new[1],
            radius=6,
            inner_color=(180, 180, 180),
            outer_color=(80, 80, 80)
        )

    # ----------------------
    # Relativista (más brillante)
    # ----------------------
    if show_rel:
        draw_radial_gradient(
            surface,
            pos_rel[0], pos_rel[1],
            radius=8,
            inner_color=(255, 200, 120),
            outer_color=(200, 100, 50)
        )
