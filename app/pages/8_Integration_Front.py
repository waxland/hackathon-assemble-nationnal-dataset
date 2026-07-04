import streamlit as st
import os

st.set_page_config(page_title="Intégration Frontend", page_icon="🎯", layout="wide")

col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/favicon.svg", width=80)
with col_text:
    st.title("🎯 TODO : Intégration Minerve & UI")

st.markdown("---")

filepath = "TODO_INTEGRATION_FRONTEND.md"

if os.path.exists(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    content = content.replace("# 🎯 TODO : Intégration des Nouvelles Données dans le Frontend (Minerve) & Streamlit\n", "")
    st.markdown(content)
else:
    st.error(f"Le fichier `{filepath}` est introuvable.")

