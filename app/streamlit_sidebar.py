import os

import streamlit as st


NAV_ITEMS = [
    ("Accueil", "app.py"),
    ("Vue Macro", "pages/1_Vue_Macro.py"),
    ("Rapport Programme", "pages/3_Rapport_Programme.py"),
    ("Questions Ouvertes", "pages/5_Questions_Ouvertes.py"),
    ("Architecture Datasets", "pages/7_Architecture_Datasets.py"),
    ("Docs Data Usage", "pages/9_Docs_Data_Usage.py"),
    ("SNA Mots Cles Parlement", "pages/10_SNA_Mots_Cles_Parlement.py"),
]


def render_sidebar(active_page):
    icon_path = "app/content/icon-minerve.png"
    if os.path.exists(icon_path):
        st.sidebar.image(icon_path, width=96)

    st.sidebar.title("Hackathon 2026")
    st.sidebar.caption("Exploration du dataset France 2030")
    st.sidebar.divider()
    st.sidebar.markdown("### Navigation")

    for label, page in NAV_ITEMS:
        if label == active_page:
            st.sidebar.markdown(f"**{label}**")
            continue

        try:
            st.sidebar.page_link(page, label=label)
        except TypeError:
            st.sidebar.markdown(f"[{label}]({page})")

    st.sidebar.divider()
    st.sidebar.caption("Data engineering, sources publiques et correlation.")
