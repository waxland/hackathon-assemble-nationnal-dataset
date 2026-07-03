import streamlit as st
import pandas as pd
from app import load_front_dataset

col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/favicon.svg", width=80)
with col_text:
    st.header("2. Liste des Investissements France 2030")

programs_data = load_front_dataset("catalog/investment-programmes.json")
budget_data = load_front_dataset("budget/france-2030-budget-lines.json")
parliament_data = load_front_dataset("sources/parliamentary-documents.json")
companies_data = load_front_dataset("sources/sirene-companies.json")

if programs_data:
    df_budget = pd.DataFrame(budget_data)
    data_table = []
    
    for p in programs_data:
        code = p.get("programmeCode")
        budg = df_budget[df_budget["programmeCode"] == code]["amount2025"].sum() if not df_budget.empty else 0
        mentions_count = len(next((x.get("documents", []) for x in parliament_data if x.get("programmeCode") == code), []))
        comps_count = len(next((x.get("companies", []) for x in companies_data if x.get("programmeCode") == code), []))
        
        data_table.append({
            "Code": code,
            "Nom": p.get("programmeName"),
            "Budget 2025 (€)": budg,
            "Débats Parl.": mentions_count,
            "Nb Entreprises": comps_count,
            "Donnée Simulée ?": "🔴 Oui" if p.get("isMock") else "🟢 Non"
        })
        
    df_transversal = pd.DataFrame(data_table)
    st.dataframe(df_transversal.style.format({"Budget 2025 (€)": "{:,.0f} €"}), use_container_width=True)
else:
    st.info("Aucune donnée de catalogue trouvée.")
