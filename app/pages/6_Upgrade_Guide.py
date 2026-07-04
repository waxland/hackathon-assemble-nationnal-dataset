import streamlit as st
import os
from streamlit_sidebar import render_sidebar

st.set_page_config(page_title="Upgrade POC", page_icon="🚀", layout="wide")
render_sidebar("Upgrade Guide")

col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/favicon.svg", width=80)
with col_text:
    st.title("🚀 Comment passer du POC à la Production (Upgrade Guide)")

st.markdown("---")

filepath = "HOW_TO_UPGRADE_POC.md"

if os.path.exists(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # On affiche le contenu markdown directement dans Streamlit, on retire le titre 1 car on l'a déjà mis
    content = content.replace("# 🚀 Comment passer du POC à la Production (Upgrade Guide)\n", "")
    st.markdown(content)
else:
    st.error(f"Le fichier `{filepath}` est introuvable.")
