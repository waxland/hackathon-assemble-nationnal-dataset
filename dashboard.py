import streamlit as st
import sqlite3
import pandas as pd
import json

# Configuration de la page
st.set_page_config(page_title="France 2030 - Dashboard", page_icon="🇫🇷", layout="wide")

st.title("🇫🇷 POC France 2030 : Du Budget aux Débats Parlementaires")
st.markdown("""
Ce tableau de bord interactif permet de naviguer dans les données du plan **France 2030**.
Il connecte la base de données relationnelle locale (`france2030.sqlite`) générée par nos scripts.
""")

# Connexion à SQLite
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect("data/france2030.sqlite", check_same_thread=False)
    return conn

conn = get_db_connection()

# Onglets
tab1, tab2, tab3 = st.tabs(["💰 Budget & Programmes", "🏛️ Débats Parlementaires", "🚀 Entreprises & Startups"])

with tab1:
    st.header("Analyse du Budget France 2030 (PLF 2025)")
    
    query_budget = """
    SELECT p.programmeCode, p.programmeName, SUM(b.amount2025) as budget_2025 
    FROM programs p 
    JOIN budget_lines b ON p.programmeCode = b.programmeCode 
    GROUP BY p.programmeName 
    ORDER BY budget_2025 DESC;
    """
    df_budget = pd.read_sql(query_budget, conn)
    
    # Affichage des métriques clés
    col1, col2 = st.columns(2)
    col1.metric("Budget Total 2025 (France 2030)", f"{df_budget['budget_2025'].sum() / 1e9:.2f} Milliards €")
    col2.metric("Programme le mieux doté", df_budget.iloc[0]['programmeName'])
    
    st.subheader("Répartition du budget par programme")
    st.bar_chart(df_budget.set_index("programmeName")["budget_2025"])
    
    st.dataframe(df_budget.style.format({"budget_2025": "{:,.0f} €"}))

with tab2:
    st.header("L'écho de France 2030 à l'Assemblée Nationale")
    
    query_mentions = """
    SELECT t.themeName as 'Thématique', COUNT(pm.mentionId) as 'Nombre de mentions'
    FROM themes t
    LEFT JOIN parliament_mentions pm ON t.themeId = pm.relatedThemeId
    GROUP BY t.themeName
    ORDER BY 'Nombre de mentions' DESC
    LIMIT 10;
    """
    df_mentions = pd.read_sql(query_mentions, conn)
    
    st.subheader("Thématiques technologiques les plus discutées")
    st.bar_chart(df_mentions.set_index("Thématique")["Nombre de mentions"])
    
    st.subheader("Derniers Amendements / Questions Écrites")
    query_details = "SELECT date, speakerName, politicalGroup, matchedKeyword, interventionText FROM parliament_mentions LIMIT 10;"
    df_details = pd.read_sql(query_details, conn)
    for _, row in df_details.iterrows():
        with st.expander(f"🗣️ {row['speakerName']} ({row['politicalGroup']}) - {row['date']} - Mot-clé : {row['matchedKeyword']}"):
            st.write(row['interventionText'])

with tab3:
    st.header("Les Acteurs de l'Innovation (Entreprises & DeepTech)")
    
    query_companies = """
    SELECT c.companyName as 'Nom', c.siren as 'SIREN', c.nafCode as 'Code NAF', t.themeName as 'Thématique liée'
    FROM companies c
    JOIN themes t ON c.companyId IN (
        SELECT sourceEntityId FROM correlations 
        WHERE targetEntityId = t.themeId AND sourceEntityType = 'company'
    )
    """
    try:
        df_comp = pd.read_sql(query_companies, conn)
        st.dataframe(df_comp)
    except Exception as e:
        # Fallback query if correlation join is too complex for SQLite string array
        st.info("Aperçu brut des lauréats France 2030 intégrés en base :")
        query_simple = "SELECT companyName, siren, nafCode, source FROM companies"
        st.dataframe(pd.read_sql(query_simple, conn))

st.sidebar.title("Informations")
st.sidebar.info("Données générées via Open Data (data.gouv.fr, API Sirene, NosDéputés.fr).")
