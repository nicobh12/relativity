# perihelio/ui.py
import streamlit as st
from .simulation import run_simulation

def render_perihelio_tab():
    st.header("Simulador de Precesión del Perihelio de Mercurio")

    st.markdown(
        """
        Aquí puedes comparar visualmente la órbita **newtoniana** vs. la **relativista**.
        Usa los controles para activar o desactivar elementos de la animación.
        """
    )

    # Sidebar con controles
    st.sidebar.subheader("Controles – Perihelio")

    speed = st.sidebar.slider("Velocidad de animación", 0.1, 3.0, 1.0, 0.1)
    show_newton = st.sidebar.checkbox("Mostrar órbita Newtoniana", True)
    show_newton_planet = st.sidebar.checkbox("Mostrar planeta Newtoniano", True)
    show_relativity = st.sidebar.checkbox("Mostrar órbita Relativista", True)
    show_rel_planet = st.sidebar.checkbox("Mostrar planeta Relativista", True)

    btn_start = st.sidebar.button("▶ Iniciar")
    btn_stop = st.sidebar.button("⏸ Pausar")
    btn_reset = st.sidebar.button("🔄 Resetear")

    # Run simulation
    frame = run_simulation(
        speed=speed,
        show_newton=show_newton,
        show_newton_planet=show_newton_planet,
        show_rel=show_relativity,
        show_rel_planet=show_rel_planet,
        btn_start=btn_start,
        btn_stop=btn_stop,
        btn_reset=btn_reset,
    )

    # Mostrar frame
    if frame is not None:
        st.image(frame, caption="Animación del perihelio", use_container_width=True)
    else:
        st.info("Pulsa ▶ Iniciar para comenzar la simulación.")
