import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app import load_front_dataset
from streamlit_sidebar import render_sidebar

render_sidebar("Vue Macro")

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

    st.subheader("Temporalité budgétaire")
    amount_columns = [col for col in ["amount2024", "amount2025", "amount2026"] if col in df_budget.columns]
    df_years = df_budget[["programmeCode", "programmeName", *amount_columns]].copy()
    df_years = df_years.melt(
        id_vars=["programmeCode", "programmeName"],
        value_vars=amount_columns,
        var_name="year",
        value_name="amount",
    )
    df_years["year"] = df_years["year"].str.replace("amount", "", regex=False)
    df_years["amount"] = pd.to_numeric(df_years["amount"], errors="coerce")
    df_years = df_years.dropna(subset=["amount"])
    df_years = df_years.groupby(["programmeCode", "programmeName", "year"], as_index=False)["amount"].sum()

    if not df_years.empty:
        fig_yty = px.line(
            df_years,
            x="year",
            y="amount",
            color="programmeCode",
            markers=True,
            hover_name="programmeName",
            title="Évolution des crédits disponibles par programme",
        )
        fig_yty.update_yaxes(title="Montant CP (€)", tickformat=",")
        fig_yty.update_xaxes(title="Année")
        st.plotly_chart(fig_yty, use_container_width=True)

    st.subheader("Flux budgetaires par programme et categorie")
    df_sankey = df_budget.dropna(subset=["amount2025"]).copy()
    df_sankey["amount2025"] = pd.to_numeric(df_sankey["amount2025"], errors="coerce").fillna(0)
    df_sankey = df_sankey[df_sankey["amount2025"] > 0]

    if not df_sankey.empty:
        root_label = "Budget 2025 identifié"
        programme_labels = [
            f"{row.programmeCode} - {row.programmeName}"
            for row in df_sankey[["programmeCode", "programmeName"]].drop_duplicates().itertuples(index=False)
        ]
        category_labels = sorted(df_sankey["expenseCategoryName"].dropna().unique().tolist())
        labels = [root_label, *programme_labels, *category_labels]
        label_index = {label: idx for idx, label in enumerate(labels)}

        sources = []
        targets = []
        values = []

        for row in df_sankey.groupby(["programmeCode", "programmeName"], as_index=False)["amount2025"].sum().itertuples(index=False):
            programme_label = f"{row.programmeCode} - {row.programmeName}"
            sources.append(label_index[root_label])
            targets.append(label_index[programme_label])
            values.append(row.amount2025)

        for row in df_sankey.itertuples(index=False):
            programme_label = f"{row.programmeCode} - {row.programmeName}"
            sources.append(label_index[programme_label])
            targets.append(label_index[row.expenseCategoryName])
            values.append(row.amount2025)

        fig_sankey = go.Figure(
            data=[
                go.Sankey(
                    node=dict(label=labels, pad=18, thickness=18),
                    link=dict(source=sources, target=targets, value=values),
                )
            ]
        )
        fig_sankey.update_layout(title_text="Budget 2025 : Mission -> Programmes -> Categories de depense")
        st.plotly_chart(fig_sankey, use_container_width=True)

st.subheader("Implantation des entreprises identifiees")
company_rows = []
for programme in companies_data:
    for company in programme.get("companies", []):
        latitude = company.get("latitude")
        longitude = company.get("longitude")
        if latitude is None or longitude is None:
            continue
        company_rows.append({
            "programmeCode": programme.get("programmeCode"),
            "companyName": company.get("denominationUniteLegale") or company.get("nomUniteLegale") or company.get("siren"),
            "siren": company.get("siren"),
            "latitude": latitude,
            "longitude": longitude,
            "commune": company.get("communeSiege"),
            "adresse": company.get("adresseSiege"),
        })

if company_rows:
    df_map = pd.DataFrame(company_rows)
    st.map(df_map, latitude="latitude", longitude="longitude", size=80)
    st.dataframe(
        df_map[["programmeCode", "companyName", "siren", "commune", "adresse"]],
        hide_index=True,
        use_container_width=True,
    )
else:
    st.warning("Aucune coordonnée d'entreprise n'est disponible dans le contrat Sirene.")
