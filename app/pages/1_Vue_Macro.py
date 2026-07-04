import streamlit as st
import pandas as pd
import plotly.express as px
from app import load_front_dataset

col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/icon-minerve.png", width=80)
with col_text:
    st.header("1. Vue Macro France 2030")

budget_data = load_front_dataset("budget/france-2030-budget-lines.json")
parliament_data = load_front_dataset("sources/parliamentary-documents.json")
companies_data = load_front_dataset("sources/sirene-companies.json")

df_budget = pd.DataFrame(budget_data)
total_2025 = df_budget["amount2025"].sum() if not df_budget.empty and "amount2025" in df_budget else 0
total_mentions = sum(len(p.get("documents", [])) for p in parliament_data)
total_companies = sum(len(p.get("companies", [])) for p in companies_data)

col1, col2, col3 = st.columns(3)
col1.metric("Budget 2025 Identifié", f"{total_2025 / 1e9:.2f} Mds €" if total_2025 else "N/A")
col2.metric("Mentions Parlementaires (POC)", total_mentions)
col3.metric("Startups/Entreprises Lauréates", total_companies)

st.divider()
if not df_budget.empty:
    st.subheader("Répartition budgétaire 2025 par Programme")
    df_grouped = df_budget.groupby("programmeName")["amount2025"].sum().reset_index()
    
    # Création d'une étiquette personnalisée pour afficher le montant en texte
    df_grouped["label"] = df_grouped.apply(lambda row: f"{row['programmeName']} ({row['amount2025'] / 1e9:.2f} Mds €)", axis=1)
    
    fig = px.pie(df_grouped, values='amount2025', names='label', 
                 title="Ventilation du budget (2025)",
                 color_discrete_sequence=px.colors.sequential.RdBu)
    
    # Configuration pour afficher le Pourcentage ET la Valeur absolue au survol, et personnaliser la légende
    fig.update_traces(
        textposition='inside', 
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Budget: %{value:,.0f} €<br>Part: %{percent}<extra></extra>"
    )
    
    # Amélioration de la légende
    fig.update_layout(
        legend_title="Programmes (et Budget)",
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True)
