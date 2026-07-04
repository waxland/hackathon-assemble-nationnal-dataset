import streamlit as st
import os
from streamlit_sidebar import render_sidebar

st.set_page_config(page_title="Questions Ouvertes", page_icon="❓", layout="wide")
render_sidebar("Questions Ouvertes")

col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/favicon.svg", width=80)
with col_text:
    st.title("❓ Questions Ouvertes & Choix Techniques")

st.markdown("---")

filepath = "QUESTIONS_OUVERTES.md"

if os.path.exists(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # On affiche le contenu markdown directement dans Streamlit
    st.markdown(content)
else:
    st.error(f"Le fichier `{filepath}` est introuvable.")
