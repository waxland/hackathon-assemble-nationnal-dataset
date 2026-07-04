import streamlit as st
import pandas as pd
from io import BytesIO
from app import load_front_dataset

col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/icon-minerve.png", width=80)
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
        is_mock = bool(p.get("isMock"))
        completeness_score = 0
        completeness_score += 25 if budg > 0 else 0
        completeness_score += 25 if mentions_count > 0 else 0
        completeness_score += 25 if comps_count > 0 else 0
        completeness_score += 25 if not is_mock else 0
        
        data_table.append({
            "Code": code,
            "Nom": p.get("programmeName"),
            "Budget 2025 (€)": budg,
            "Débats Parl.": mentions_count,
            "Nb Entreprises": comps_count,
            "Score complétude": completeness_score,
            "Donnée Simulée ?": "🔴 Oui" if is_mock else "🟢 Non"
        })
        
    df_transversal = pd.DataFrame(data_table)

    col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1, 1, 1])
    with col_f1:
        selected_codes = st.multiselect(
            "Programmes",
            options=df_transversal["Code"].tolist(),
            default=df_transversal["Code"].tolist(),
        )
    with col_f2:
        min_mentions = st.number_input("Mentions min.", min_value=0, value=0, step=1)
    with col_f3:
        min_companies = st.number_input("Entreprises min.", min_value=0, value=0, step=1)
    with col_f4:
        hide_mock = st.checkbox("Masquer mocks", value=False)

    df_filtered = df_transversal[
        df_transversal["Code"].isin(selected_codes)
        & (df_transversal["Débats Parl."] >= min_mentions)
        & (df_transversal["Nb Entreprises"] >= min_companies)
    ].copy()
    if hide_mock:
        df_filtered = df_filtered[df_filtered["Donnée Simulée ?"] == "🟢 Non"]

    if df_filtered.empty:
        st.info("Aucun programme ne correspond aux filtres sélectionnés.")
    else:
        styled = (
            df_filtered.style
            .format({"Budget 2025 (€)": "{:,.0f} €", "Score complétude": "{:.0f} / 100"})
            .background_gradient(
                subset=["Budget 2025 (€)", "Débats Parl.", "Nb Entreprises", "Score complétude"],
                cmap="RdYlGn",
            )
        )
        st.dataframe(styled, use_container_width=True)

    csv_data = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Télécharger la vue filtrée (CSV)",
        data=csv_data,
        file_name="france2030_vue_transversale.csv",
        mime="text/csv",
    )

    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df_filtered.to_excel(writer, index=False, sheet_name="Vue transversale")
    st.download_button(
        "Télécharger la vue filtrée (Excel)",
        data=excel_buffer.getvalue(),
        file_name="france2030_vue_transversale.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("Aucune donnée de catalogue trouvée.")
