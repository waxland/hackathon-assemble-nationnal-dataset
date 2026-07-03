import streamlit as st
import pandas as pd
import plotly.express as px
from app import load_front_dataset

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
    fig = px.pie(df_grouped, values='amount2025', names='programmeName', 
                 title="Ventilation du budget (2025)",
                 color_discrete_sequence=px.colors.sequential.RdBu)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
