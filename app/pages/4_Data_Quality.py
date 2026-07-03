import streamlit as st
from app import load_front_dataset

col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/favicon.svg", width=80)
with col_text:
    st.header("🛠️ Validation Métier (Data Quality)")

st.markdown("Vue dédiée à l'équipe Data pour s'assurer que le Front-End ne va pas crasher et analyser la maturité du dataset.")

budget_data = load_front_dataset("budget/france-2030-budget-lines.json")
programs_data = load_front_dataset("catalog/investment-programmes.json")
parliament_data = load_front_dataset("sources/parliamentary-documents.json")
companies_data = load_front_dataset("sources/sirene-companies.json")

st.subheader("Statut des fichiers (Contrat Minerve)")

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
