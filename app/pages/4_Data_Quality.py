import streamlit as st
import json
import os
import sqlite3
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from app import load_front_dataset


class ContractBase(BaseModel):
    model_config = ConfigDict(extra="allow")

    programmeCode: str
    isMock: bool
    updatedAt: str
    confidence: float | None = None


class BudgetLine(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    programmeCode: str
    programmeName: str
    expenseCategoryName: str
    amount2025: float | None = None
    isMock: bool
    sourceUrl: str | None = None
    confidence: float | None = None
    updatedAt: str


class ProgrammeCatalog(ContractBase):
    programmeName: str
    missionName: str


class CompaniesByProgramme(ContractBase):
    companies: list[dict] = Field(default_factory=list)


class ParliamentByProgramme(ContractBase):
    documents: list[dict] = Field(default_factory=list)


class TaxonomyByProgramme(ContractBase):
    themes: list[dict] = Field(default_factory=list)


class AlignmentScore(ContractBase):
    data: dict = Field(default_factory=dict)


class GenericProgrammeData(ContractBase):
    data: list | dict = Field(default_factory=list)


def validate_contract_items(name, items, model):
    errors = []
    for idx, item in enumerate(items):
        try:
            model.model_validate(item)
        except ValidationError as exc:
            errors.append({
                "file": name,
                "index": idx,
                "errors": exc.errors(),
            })
    return errors


def contract_status(filepath, model):
    items = load_front_dataset(filepath)
    if not items:
        return {
            "Fichier": filepath,
            "Statut": "Introuvable",
            "Objets": 0,
            "Mocks": 0,
            "Erreurs schema": 0,
            "errors": [],
        }

    errors = validate_contract_items(filepath, items, model)
    mock_count = sum(1 for item in items if item.get("isMock", False))
    if errors:
        status = "Schema invalide"
    elif mock_count:
        status = "Mock partiel"
    else:
        status = "Réel"

    return {
        "Fichier": filepath,
        "Statut": status,
        "Objets": len(items),
        "Mocks": mock_count,
        "Erreurs schema": len(errors),
        "errors": errors,
    }

col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/icon-minerve.png", width=80)
with col_text:
    st.header("🛠️ Validation Métier & Pondération")

st.markdown("Vue dédiée à l'équipe Data pour s'assurer que le Front-End ne va pas crasher, analyser la maturité du dataset, et ajuster le score Minerve.")

st.subheader("1. Statut des fichiers (Contrat Minerve)")

budget_data = load_front_dataset("budget/france-2030-budget-lines.json")
programs_data = load_front_dataset("catalog/investment-programmes.json")
parliament_data = load_front_dataset("sources/parliamentary-documents.json")
companies_data = load_front_dataset("sources/sirene-companies.json")

contracts = [
    ("budget/france-2030-budget-lines.json", BudgetLine),
    ("catalog/investment-programmes.json", ProgrammeCatalog),
    ("matching/programme-taxonomy.json", TaxonomyByProgramme),
    ("metrics/programme-alignment-scores.json", AlignmentScore),
    ("sources/sirene-companies.json", CompaniesByProgramme),
    ("sources/parliamentary-documents.json", ParliamentByProgramme),
    ("sources/data-gouv-datasets.json", GenericProgrammeData),
    ("sources/inpi-patent-families.json", GenericProgrammeData),
    ("sources/company-revenues.json", GenericProgrammeData),
    ("reports/investment-programme-reports.json", GenericProgrammeData),
    ("dataviz/investment-programme-dataviz.json", GenericProgrammeData),
]

contract_reports = [contract_status(path, model) for path, model in contracts]
df_contracts = pd.DataFrame([
    {k: v for k, v in report.items() if k != "errors"}
    for report in contract_reports
])
st.dataframe(df_contracts, hide_index=True, use_container_width=True)

schema_errors = [error for report in contract_reports for error in report["errors"]]
if schema_errors:
    with st.expander("Erreurs de schéma détaillées", expanded=True):
        st.json(schema_errors)
else:
    st.success("Validation Pydantic réussie sur les fichiers du contrat suivis.")

st.divider()

st.subheader("2. Outil de Calcul du Score d'Alignement")
st.markdown("""
Le Front-End Minerve a besoin d'un **Score d'Alignement (0-100)** par programme.
Ajustez les poids empiriques ci-dessous pour trouver la formule mathématique idéale.
""")

col_s1, col_s2 = st.columns(2)
with col_s1:
    poids_mentions = st.slider("Poids d'une Mention Parlementaire (Multiplicateur)", min_value=1.0, max_value=50.0, value=10.0, step=1.0)
with col_s2:
    diviseur_budget = st.slider("Diviseur du Budget (en Milliards €)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

db_path = "data/france2030.sqlite"
scores = []
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    st.markdown("### Aperçu des Scores")
    cols = st.columns(5)
    for i, prog in enumerate(["421", "422", "423", "424", "425"]):
        budg = cursor.execute("SELECT SUM(amount2025) FROM budget_lines WHERE programmeCode=?", (prog,)).fetchone()[0] or 0
        budg_mds = max(budg / 1e9, 0.1)
        mentions = cursor.execute("SELECT COUNT(*) FROM parliament_mentions WHERE relatedProgrammeCode=?", (prog,)).fetchone()[0] or 0
        
        raw_score = (mentions * poids_mentions) / (budg_mds * diviseur_budget)
        final_score = min(round(raw_score, 1), 100)
        
        scores.append({"programmeCode": prog, "score": final_score})
        cols[i % 5].metric(f"Prog {prog}", f"{final_score} / 100", delta=f"{mentions} mentions" if mentions > 0 else None)
        
    conn.close()
    
    # Bouton de sauvegarde interactif (Action: Sauvegarde interactive)
    if st.button("💾 Sauvegarder cette formule dans le contrat JSON"):
        score_files = [
            "dataset/metrics/programme-alignment-scores.json",
            "data/export_front/programme-alignment-scores.json",
        ]

        for scores_file in score_files:
            if not os.path.exists(scores_file):
                continue
            with open(scores_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for p in data.get("programmes", []):
                prog_code = p["programmeCode"]
                new_score = next((s["score"] for s in scores if s["programmeCode"] == prog_code), 0)
                if "data" not in p:
                    p["data"] = {}
                p["data"]["overallScore"] = new_score
                p["notes"] = f"Pondération Streamlit - Mentionsx{poids_mentions} / Budget(Mds)x{diviseur_budget}"

            with open(scores_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        weights = {
            "poidsMentions": poids_mentions,
            "diviseurBudgetMds": diviseur_budget,
            "formula": "(mentions * poidsMentions) / (budgetMds * diviseurBudgetMds)",
            "scores": scores,
        }
        with open("data/score_weights.json", "w", encoding="utf-8") as f:
            json.dump(weights, f, indent=2, ensure_ascii=False)

        st.success("✅ Scores et pondérations sauvegardés dans `dataset/`, `data/export_front/` et `data/score_weights.json`.")
else:
    st.error("Base de données SQLite introuvable pour calculer les scores.")
