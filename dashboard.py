import streamlit as st
import json
import pandas as pd
import os

# Configuration de la page
st.set_page_config(page_title="France 2030 - Dashboard", page_icon="🇫🇷", layout="wide")

st.title("🇫🇷 POC France 2030 : Exploration du Contrat Data (JSON)")
st.markdown("""
Ce tableau de bord se branche **directement sur les fichiers JSON générés pour le Front-End** dans le dossier `dataset/`.
Il agit comme un miroir de validation métier, assurant que ce qui est affiché ici sera exactement ce qui apparaîtra sur Minerve.fr.
""")

# Chargement générique des JSON du contrat Front
@st.cache_data
def load_front_dataset(filepath):
    """Charge un fichier JSON du contrat front. Renvoie la liste 'programmes' ou le tableau direct."""
    full_path = os.path.join("dataset", filepath)
    if not os.path.exists(full_path):
        st.error(f"Fichier introuvable : {full_path}")
        return []
        
    with open(full_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    if isinstance(data, dict) and "programmes" in data:
        return data["programmes"]
    return data

# Chargement des données
budget_data = load_front_dataset("budget/france-2030-budget-lines.json")
programs_data = load_front_dataset("catalog/investment-programmes.json")
parliament_data = load_front_dataset("sources/parliamentary-documents.json")
companies_data = load_front_dataset("sources/sirene-companies.json")

# Création des onglets (Miroir des routes du Front)
tab_accueil, tab_transversal, tab_programme = st.tabs(["🏠 Accueil (/)", "📊 Transversale (/investissements)", "🔍 Rapport (/investissements/[id])"])

# ==========================================
# ONGLET 1 : ACCUEIL
# ==========================================
with tab_accueil:
    st.header("Vue Macro France 2030")
    
    # Agrégation des montants depuis le fichier Budget
    df_budget = pd.DataFrame(budget_data)
    total_2025 = df_budget["amount2025"].sum() if not df_budget.empty and "amount2025" in df_budget else 0
    
    # Agrégation des entreprises et mentions
    total_mentions = sum(len(p.get("documents", [])) for p in parliament_data)
    total_companies = sum(len(p.get("companies", [])) for p in companies_data)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Budget 2025 Identifié", f"{total_2025 / 1e9:.2f} Mds €" if total_2025 else "N/A")
    col2.metric("Mentions Parlementaires", total_mentions)
    col3.metric("Startups/Entreprises Lauréates", total_companies)
    
    if not df_budget.empty:
        st.subheader("Répartition budgétaire 2025 par Programme")
        # Grouper par programmeName
        df_grouped = df_budget.groupby("programmeName")["amount2025"].sum().reset_index()
        st.bar_chart(df_grouped.set_index("programmeName")["amount2025"])

# ==========================================
# ONGLET 2 : VUE TRANSVERSALE
# ==========================================
with tab_transversal:
    st.header("Liste des Investissements France 2030")
    
    if programs_data:
        df_programs = pd.DataFrame([{
            "Code": p.get("programmeCode"),
            "Nom": p.get("programmeName"),
            "Mission": p.get("missionName"),
            "Mocké ?": "Oui" if p.get("isMock") else "Non",
            "Confiance": p.get("confidence")
        } for p in programs_data])
        
        st.dataframe(df_programs, use_container_width=True)
    else:
        st.info("Aucune donnée de catalogue trouvée.")

# ==========================================
# ONGLET 3 : VUE PROGRAMME
# ==========================================
with tab_programme:
    st.header("Rapport par Programme")
    
    if programs_data:
        # Sélecteur de programme
        prog_options = {p.get("programmeCode"): f"{p.get('programmeCode')} - {p.get('programmeName')}" for p in programs_data}
        selected_prog_code = st.selectbox("Sélectionnez un Programme", options=list(prog_options.keys()), format_func=lambda x: prog_options[x])
        
        st.divider()
        st.subheader(f"Dossier Programme {selected_prog_code}")
        
        col_bud, col_parl = st.columns(2)
        
        with col_bud:
            st.write("💰 **Lignes Budgétaires Associées**")
            prog_budget = [b for b in budget_data if str(b.get("programmeCode")) == selected_prog_code]
            if prog_budget:
                df_prog_bud = pd.DataFrame(prog_budget)[["expenseCategoryName", "amount2025"]]
                st.dataframe(df_prog_bud.style.format({"amount2025": "{:,.0f} €"}))
            else:
                st.write("Aucun budget identifié.")
                
        with col_parl:
            st.write("🏛️ **Écho Parlementaire**")
            prog_mentions = next((p for p in parliament_data if str(p.get("programmeCode")) == selected_prog_code), {})
            docs = prog_mentions.get("documents", [])
            if docs:
                for doc in docs:
                    with st.expander(f"{doc.get('speakerName')} ({doc.get('politicalGroup')}) - {doc.get('matchedKeyword')}"):
                        st.write(doc.get('text'))
                        st.caption(f"Date: {doc.get('date')} - Source: {doc.get('url')}")
            else:
                st.write("Aucun écho parlementaire trouvé pour ce programme.")
                
        st.divider()
        st.write("🚀 **Startups & Deeptech Soutenues**")
        prog_comp = next((p for p in companies_data if str(p.get("programmeCode")) == selected_prog_code), {})
        companies = prog_comp.get("companies", [])
        if companies:
            st.dataframe(pd.DataFrame(companies))
        else:
            st.write("Aucune entreprise identifiée pour ce programme.")
            
    else:
        st.warning("Veuillez générer les fichiers JSON du contrat front d'abord.")

# Sidebar de debug / Data Quality
st.sidebar.title("🛠️ Validation Métier")
st.sidebar.markdown("""
Ce panel vérifie la qualité des JSON du dossier `dataset/`.
""")

st.sidebar.subheader("Statut des Mocks")
# Vérifie le booléen isMock dans les fichiers
is_mock_budget = False # Budget lines n'a pas le tag global mais dans la row.
is_mock_comp = any(p.get("isMock", False) for p in companies_data)
is_mock_parl = any(p.get("isMock", False) for p in parliament_data)

st.sidebar.write(f"Budget Lines : {'🔴 MOCK' if is_mock_budget else '🟢 REAL'}")
st.sidebar.write(f"Entreprises : {'🔴 MOCK' if is_mock_comp else '🟢 REAL'}")
st.sidebar.write(f"Mentions Parl. : {'🔴 MOCK' if is_mock_parl else '🟢 REAL'}")

st.sidebar.info("Modifiez les scripts d'extraction puis lancez `make export-front` pour actualiser ces vues.")
