# app.py
import streamlit as st
from perihelio.ui import render_perihelio_tab
from gps.ui import render_gps_tab

st.set_page_config(
    page_title="Simulador de Relatividad General",
    layout="wide",
)

st.title("Simulador Interactivo – Relatividad General")

tab1, tab2 = st.tabs(["Perihelio de Mercurio", "GPS"])

with tab1:
    render_perihelio_tab()

with tab2:
    render_gps_tab()
