import streamlit as st
import pandas as pd
from app import load_front_dataset
import io
from streamlit_sidebar import render_sidebar

render_sidebar("Vue Transversale")

col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/favicon.svg", width=80)
with col_text:
    st.header("2. Liste des Investissements France 2030")

programs_data = load_front_dataset("catalog/investment-programmes.json")
budget_data = load_front_dataset("budget/france-2030-budget-lines.json")
parliament_data = load_front_dataset("sources/parliamentary-documents.json")
companies_data = load_front_dataset("sources/sirene-companies.json")

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

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
    
    # Heatmap style application
    def color_completeness(val):
        color = 'red' if val == 0 else 'lightgreen'
        return f'background-color: {color}'
        
    st.dataframe(
        df_transversal.style
        .format({"Budget 2025 (€)": "{:,.0f} €"})
        .map(color_completeness, subset=['Débats Parl.', 'Nb Entreprises']), 
        use_container_width=True
    )
    
    # Download Button
    excel_data = to_excel(df_transversal)
    st.download_button(
        label="📥 Exporter vers Excel",
        data=excel_data,
        file_name='france2030_transversal.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
else:
    st.info("Aucune donnée de catalogue trouvée.")
