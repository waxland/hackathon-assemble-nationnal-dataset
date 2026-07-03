import streamlit as st
import pandas as pd
import plotly.express as px
from app import load_front_dataset

# Couleurs DSFR
COLOR_BLEU_FRANCE = "#000091"
COLOR_ROUGE_MARIANNE = "#e1000f"

st.header("3. Rapport par Programme")

programs_data = load_front_dataset("catalog/investment-programmes.json")
budget_data = load_front_dataset("budget/france-2030-budget-lines.json")
parliament_data = load_front_dataset("sources/parliamentary-documents.json")
companies_data = load_front_dataset("sources/sirene-companies.json")

if programs_data:
    prog_options = {p.get("programmeCode"): f"Programme {p.get('programmeCode')} - {p.get('programmeName')}" for p in programs_data}
    selected_prog_code = st.selectbox("Sélectionnez un Programme :", options=list(prog_options.keys()), format_func=lambda x: prog_options[x])
    
    st.divider()
    st.subheader(f"Dossier Programme {selected_prog_code}")
    
    col_g, col_d = st.columns([1, 1])
    
    with col_g:
        st.markdown("### 💰 Budget & Subventions")
        prog_budget = [b for b in budget_data if str(b.get("programmeCode")) == selected_prog_code]
        if prog_budget:
            df_prog_bud = pd.DataFrame(prog_budget)
            fig_bar = px.bar(df_prog_bud, x="expenseCategoryName", y="amount2025", 
                             title="Répartition par type de dépense",
                             color="expenseCategoryName",
                             color_discrete_sequence=[COLOR_BLEU_FRANCE, COLOR_ROUGE_MARIANNE])
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.write("Aucun budget identifié.")
            
        st.markdown("### 🚀 Écosystème & Entreprises")
        prog_comp = next((p for p in companies_data if str(p.get("programmeCode")) == selected_prog_code), {})
        companies = prog_comp.get("companies", [])
        if companies:
            st.dataframe(pd.DataFrame(companies), hide_index=True)
        else:
            st.write("Aucune entreprise identifiée.")

    with col_d:
        st.markdown("### 🏛️ Écho Parlementaire (Assemblée)")
        prog_mentions = next((p for p in parliament_data if str(p.get("programmeCode")) == selected_prog_code), {})
        docs = prog_mentions.get("documents", [])
        if docs:
            df_docs = pd.DataFrame(docs)
            fig_time = px.histogram(df_docs, x="date", color="politicalGroup", 
                                    title="Chronologie des interventions", nbins=10)
            st.plotly_chart(fig_time, use_container_width=True)
            
            st.markdown("**Derniers verbatims extraits :**")
            for doc in docs[:5]:
                with st.expander(f"🗣️ {doc.get('speakerName')} ({doc.get('politicalGroup')}) - {doc.get('date')}"):
                    st.markdown(f"**Mot-clé détecté :** `{doc.get('matchedKeyword')}`")
                    st.info(doc.get('text'))
        else:
            st.write("Aucun écho parlementaire trouvé.")
else:
    st.warning("Veuillez générer les fichiers JSON du contrat front d'abord.")
