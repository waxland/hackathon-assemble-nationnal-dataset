import streamlit as st
import json
import os
from streamlit_sidebar import render_sidebar

# Paramétrage global de la page
st.set_page_config(
    page_title="France 2030 - Dashboard Data",
    page_icon="app/content/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction de chargement de dataset commune
@st.cache_data
def load_front_dataset(filepath):
    """Charge un fichier JSON du contrat front."""
    full_path = os.path.join("dataset", filepath)
    if not os.path.exists(full_path):
        return []
    with open(full_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "programmes" in data:
        return data["programmes"]
    return data

# Charger un fichier markdown
def load_markdown(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

render_sidebar("Accueil")

# --- Page d'accueil par défaut ---
st.title("🇫🇷 POC France 2030 : Contrat Data (JSON)")

content_intro = load_markdown("app/content/home_intro.md")
st.markdown(content_intro)

st.info("Veuillez sélectionner une vue dans le menu latéral à gauche pour commencer l'exploration de la base.")
