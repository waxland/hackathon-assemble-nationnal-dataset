import streamlit as st
import json
import os
import sqlite3
from app import load_front_dataset

# Couleurs et Header
col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/favicon.svg", width=80)
with col_text:
    st.header("🛠️ Validation Métier & Pondération")

st.markdown("Vue dédiée à l'équipe Data pour s'assurer que le Front-End ne va pas crasher, analyser la maturité du dataset, et ajuster le score France 2030.")

# -----------------------------------------
# 1. QUALITÉ DE LA DONNÉE (MOCKS)
# -----------------------------------------
st.subheader("1. Statut des fichiers (Contrat Minerve)")

budget_data = load_front_dataset("budget/france-2030-budget-lines.json")
programs_data = load_front_dataset("catalog/investment-programmes.json")
parliament_data = load_front_dataset("sources/parliamentary-documents.json")
companies_data = load_front_dataset("sources/sirene-companies.json")

def check_mock(data_array):
    if not data_array: return "🔴 Introuvable"
    return "🔴 MOCK" if any(p.get("isMock", False) for p in data_array) else "🟢 REAL"

budget_mock_status = "🔴 MOCK" if any(b.get("isMock", False) for b in budget_data) else "🟢 REAL"

st.code(f"""
- dataset/budget/france-2030-budget-lines.json    -> {budget_mock_status}
- dataset/catalog/investment-programmes.json      -> {check_mock(programs_data)}
- dataset/sources/sirene-companies.json           -> {check_mock(companies_data)}
- dataset/sources/parliamentary-documents.json    -> {check_mock(parliament_data)}
""")

st.info("Pour faire passer un fichier de 🔴 MOCK à 🟢 REAL, sourcez les données dans les scripts d'extraction puis lancez `make export-front`.")
st.divider()

# -----------------------------------------
# 2. OUTIL DE PONDÉRATION (SCORE D'ALIGNEMENT)
# -----------------------------------------
st.subheader("2. Outil de Calcul du Score d'Alignement")
st.markdown("""
Le Front-End Minerve a besoin d'un **Score d'Alignement (0-100)** par programme.
Ajustez les poids empiriques ci-dessous pour trouver la formule mathématique idéale avant de modifier le code de `13_export_to_front_contract.py`.
""")

col_s1, col_s2 = st.columns(2)
with col_s1:
    poids_mentions = st.slider("Poids d'une Mention Parlementaire (Multiplicateur)", min_value=1.0, max_value=50.0, value=10.0, step=1.0)
with col_s2:
    diviseur_budget = st.slider("Diviseur du Budget (en Milliards €)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

# Calcul dynamique pour preview
db_path = "data/france2030.sqlite"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    st.markdown("### Aperçu des Scores")
    cols = st.columns(5)
    for i, prog in enumerate(["421", "422", "423", "424", "425"]):
        budg = cursor.execute("SELECT SUM(amount2025) FROM budget_lines WHERE programmeCode=?", (prog,)).fetchone()[0] or 0
        budg_mds = max(budg / 1e9, 0.1)
        mentions = cursor.execute("SELECT COUNT(*) FROM parliament_mentions WHERE relatedProgrammeCode=?", (prog,)).fetchone()[0] or 0
        
        # Formule interactive
        raw_score = (mentions * poids_mentions) / (budg_mds * diviseur_budget)
        final_score = min(round(raw_score, 1), 100)
        
        cols[i % 5].metric(f"Prog {prog}", f"{final_score} / 100", delta=f"{mentions} mentions" if mentions > 0 else None)
        
    conn.close()
    
    st.warning("⚠️ Une fois la bonne formule trouvée, vous devez l'appliquer en dur dans `scripts/13_export_to_front_contract.py` et relancer `make export-front`.")
else:
    st.error("Base de données SQLite introuvable pour calculer les scores.")
