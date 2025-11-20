# perihelio/simulation.py

import numpy as np
import pygame
from pygame import gfxdraw
from PIL import Image
import io

from .drawing import (
    draw_background,
    draw_orbit_paths,
    draw_mercury_planets
)

# -------------------------
# Estado global de la simulación
# -------------------------
state = {
    "running": False,
    "theta": 0.0,               # ángulo de la órbita (acumulativo)
    "rel_advance": np.radians(3),  # precesión artificial por revolución
    "orbit_points_newton": [],
    "orbit_points_rel": [],
}

# Configuración de pantalla
WIDTH = 800
HEIGHT = 800
CENTER = (WIDTH // 2, HEIGHT // 2)

# Inicializamos pygame en modo "headless"
pygame.init()
surface = pygame.Surface((WIDTH, HEIGHT))


def run_simulation(
    speed,
    show_newton,
    show_newton_planet,
    show_rel,
    show_rel_planet,
    btn_start,
    btn_stop,
    btn_reset,
):
    global state

    # -------------------------
    # Comandos de control
    # -------------------------
    if btn_start:
        state["running"] = True

    if btn_stop:
        state["running"] = False

    if btn_reset:
        state["running"] = False
        state["theta"] = 0.0
        state["orbit_points_newton"] = []
        state["orbit_points_rel"] = []
        return black_frame()

    if not state["running"]:
        return None

    # -------------------------
    # Avance temporal
    # -------------------------
    dt = 0.02 * speed
    state["theta"] += dt

    # -------------------------
    # Parámetros de órbita
    # -------------------------
    a = 250            # semieje mayor de la elipse visual
    e = 0.20           # excentricidad exagerada para hacerlo visible
    dtheta = state["rel_advance"]

    theta = state["theta"]

    # -------------------------
    # Newtoniana
    # -------------------------
    r_new = (a * (1 - e**2)) / (1 + e * np.cos(theta))

    x_new = CENTER[0] + int(r_new * np.cos(theta))
    y_new = CENTER[1] + int(r_new * np.sin(theta))

    if show_newton:
        state["orbit_points_newton"].append((x_new, y_new))
        if len(state["orbit_points_newton"]) > 1500:
            state["orbit_points_newton"].pop(0)

    # -------------------------
    # Relativista (visual)
    # -------------------------
    # el ángulo se "dobla" por precesión
    theta_eff = theta - dtheta * (theta / (2 * np.pi))

    r_rel = (a * (1 - e**2)) / (1 + e * np.cos(theta_eff))

    x_rel = CENTER[0] + int(r_rel * np.cos(theta_eff))
    y_rel = CENTER[1] + int(r_rel * np.sin(theta_eff))

    if show_rel:
        state["orbit_points_rel"].append((x_rel, y_rel))
        if len(state["orbit_points_rel"]) > 1500:
            state["orbit_points_rel"].pop(0)

    # -------------------------
    # DIBUJAR FRAME
    # -------------------------
    draw_background(surface)
    draw_orbit_paths(surface, state, show_newton, show_rel)
    draw_mercury_planets(
        surface,
        (x_new, y_new),
        (x_rel, y_rel),
        show_newton_planet,
        show_rel_planet
    )

    # -------------------------
    # Convertir pygame → PNG → Streamlit
    # -------------------------
    return surface_to_image(surface)


def black_frame():
    return Image.fromarray(np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8))


def surface_to_image(surface):
    """Convierte surface pygame → PNG → PIL."""
    data = pygame.image.tostring(surface, "RGB")
    img = Image.frombytes("RGB", (WIDTH, HEIGHT), data)
    return img
