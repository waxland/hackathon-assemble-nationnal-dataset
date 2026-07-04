import os

import streamlit as st


NAV_ITEMS = [
    ("Accueil", "/"),
    ("Vue Macro", "/Vue_Macro"),
    ("Vue Transversale", "/Vue_Transversale"),
    ("Rapport Programme", "/Rapport_Programme"),
    ("Data Quality", "/Data_Quality"),
    ("Questions Ouvertes", "/Questions_Ouvertes"),
    ("Upgrade Guide", "/Upgrade_Guide"),
    ("Architecture Datasets", "/Architecture_Datasets"),
    ("Docs Data Usage", "/Docs_Data_Usage"),
    ("SNA Mots Cles Parlement", "/SNA_Mots_Cles_Parlement"),
]


def render_sidebar(active_page):
    icon_path = "app/content/icon-minerve.png"
    if os.path.exists(icon_path):
        st.sidebar.image(icon_path, width=96)

    st.sidebar.title("Hackathon 2026")
    st.sidebar.caption("Exploration du dataset France 2030")
    st.sidebar.divider()
    st.sidebar.markdown("### Navigation")

    for label, url in NAV_ITEMS:
        if label == active_page:
            st.sidebar.markdown(f"**{label}**")
        else:
            st.sidebar.markdown(f"[{label}]({url})")

    st.sidebar.divider()
    st.sidebar.caption("Data engineering, sources publiques et correlation.")
