# perihelio/simulation.py
import numpy as np
from PIL import Image

# Estado global simple (lo reemplazaremos luego por pygame)
simulation_running = False

def run_simulation(
    speed,
    show_newton,
    show_newton_planet,
    show_rel,
    show_rel_planet,
    btn_start,
    btn_stop,
    btn_reset
):
    global simulation_running

    # Control de estado
    if btn_start:
        simulation_running = True
    if btn_stop:
        simulation_running = False
    if btn_reset:
        simulation_running = False
        return black_frame()

    if not simulation_running:
        return None

    # TEMPORAL: devolvemos un frame negro
    return black_frame()


def black_frame():
    """Devuelve un frame negro de 800x800."""
    arr = np.zeros((800, 800, 3), dtype=np.uint8)
    return Image.fromarray(arr)
