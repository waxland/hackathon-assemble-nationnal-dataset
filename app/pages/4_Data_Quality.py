import streamlit as st
import json
import os
import sqlite3
import pandas as pd
from app import load_front_dataset

col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/favicon.svg", width=80)
with col_text:
    st.header("🛠️ Validation Métier & Pondération")

st.markdown("Vue dédiée à l'équipe Data pour s'assurer que le Front-End ne va pas crasher, analyser la maturité du dataset, et ajuster le score Minerve.")

# -------------------------------------------------
# 0. QUALITY REPORT & SOURCES
# -------------------------------------------------
st.subheader("0. Audit de Données & Sources")

report_path = "data/quality_report.json"
sources_path = "data/sources.json"
audit_recommendations_path = "data/audit_recommendations.json"

col_q1, col_q2 = st.columns(2)

with col_q1:
    st.markdown("**Rapport de Qualité Automatique**")
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            qr = json.load(f)
        
        st.write("Fichiers front contenant des mocks :", len(qr.get("front_files_with_mocks", [])))
        st.write("Champs critiques manquants :", sum(qr.get("missing_critical_fields", {}).values()))

        missing_fields = qr.get("missing_critical_fields", {})
        missing_urls = int(missing_fields.get("missing_any_url", 0) or 0)
        total_records = sum(int(value or 0) for value in qr.get("volumes", {}).values())
        missing_url_rate = missing_urls / total_records if total_records else 0
        st.metric("Taux de provenance URL manquante", f"{missing_url_rate:.1%}", f"{missing_urls} enregistrements")
        if missing_urls > 0:
            st.error("Des enregistrements n'ont pas encore de `sourceUrl`, `datasetUrl` ou `resourceUrl` complet.")
        else:
            st.success("Traçabilité URL complète sur les enregistrements contrôlés.")
        
        recs_non_traitees = qr.get("unresolved_audit_recommendations", 0)
        if recs_non_traitees > 0:
            st.error(f"⚠️ {recs_non_traitees} recommandation(s) Cour des Comptes non traitées !")
            if os.path.exists(audit_recommendations_path):
                with open(audit_recommendations_path, "r", encoding="utf-8") as f:
                    audit_recommendations = json.load(f)
                pending_recommendations = [
                    rec
                    for rec in audit_recommendations
                    if rec.get("status") in {"to_review", "to_validate", "open", None}
                ]
                if pending_recommendations:
                    with st.expander("Voir les recommandations Cour des comptes à traiter", expanded=True):
                        st.dataframe(
                            pd.DataFrame(pending_recommendations),
                            use_container_width=True,
                            hide_index=True,
                        )
        else:
            st.success("✅ Aucune recommandation d'audit en attente.")

        with st.expander("Voir le détail du rapport"):
            st.json(qr)
    else:
        st.warning("Aucun quality report trouvé. Lancez `make quality-report`.")

with col_q2:
    st.markdown("**Registre des Sources Actives**")
    if os.path.exists(sources_path):
        with open(sources_path, "r") as f:
            srcs = json.load(f)
        st.write("Nombre de sources interrogées :", len(srcs))
        with st.expander("Voir le registre"):
            st.dataframe(pd.DataFrame(srcs)[["name", "producer", "license"]])
    else:
        st.warning("Registre non trouvé.")

st.divider()

# -------------------------------------------------
# 1. MOCKS STATUS
# -------------------------------------------------
st.subheader("1. Statut des fichiers (Contrat Minerve)")

budget_data = load_front_dataset("budget/france-2030-budget-lines.json")
programs_data = load_front_dataset("catalog/investment-programmes.json")
parliament_data = load_front_dataset("sources/parliamentary-documents.json")
companies_data = load_front_dataset("sources/sirene-companies.json")

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

st.markdown("**Validation du schéma JSON `sirene-companies.json` :**")
if companies_data:
    try:
        sample = companies_data[0]
        assert "programmeCode" in sample, "Clé manquante: programmeCode"
        assert "companies" in sample, "Clé manquante: companies"
        st.success("Le schéma Sirene correspond au contrat !")
    except AssertionError as e:
        st.error(f"Erreur de Schéma: {e}")

st.divider()

# -------------------------------------------------
# 2. PONDÉRATION
# -------------------------------------------------
st.subheader("2. Outil de Calcul du Score d'Alignement")

weights_path = "config/scoring_weights.json"
weights = {}
if os.path.exists(weights_path):
    with open(weights_path, "r") as f:
        weights = json.load(f)

# On va utiliser le paramétrage actuel
p_fin = weights.get("financialWeight", {}).get("weight", 0.2)
p_pol = weights.get("politicalAttention", {}).get("weight", 0.3)
p_green = weights.get("greenBudget", {}).get("weight", 0.1)
p_inno = weights.get("innovationSignal", {}).get("weight", 0.2)
p_terr = weights.get("territorialDeployment", {}).get("weight", 0.2)

st.write("Modifiez les poids analytiques (la somme doit idéalement faire 1.0) :")
col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
w_fin = col_s1.number_input("Finance", value=p_fin, step=0.1)
w_pol = col_s2.number_input("Politique", value=p_pol, step=0.1)
w_green = col_s3.number_input("Green", value=p_green, step=0.1)
w_inno = col_s4.number_input("Innovation", value=p_inno, step=0.1)
w_terr = col_s5.number_input("Territoire", value=p_terr, step=0.1)

new_weights = {
  "financialWeight": {"weight": w_fin, "description": weights.get("financialWeight", {}).get("description", "")},
  "politicalAttention": {"weight": w_pol, "description": weights.get("politicalAttention", {}).get("description", "")},
  "greenBudget": {"weight": w_green, "description": weights.get("greenBudget", {}).get("description", "")},
  "innovationSignal": {"weight": w_inno, "description": weights.get("innovationSignal", {}).get("description", "")},
  "territorialDeployment": {"weight": w_terr, "description": weights.get("territorialDeployment", {}).get("description", "")}
}

if st.button("💾 Sauvegarder cette configuration"):
    with open(weights_path, "w") as f:
        json.dump(new_weights, f, indent=2)
    st.success("✅ Configuration sauvegardée ! Relancez `make export-front` pour mettre à jour les scores pour Minerve.")
