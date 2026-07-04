import json
import os
import sqlite3
from datetime import datetime, timezone

# --- UTILITAIRES ---
def get_current_date():
    return datetime.now(timezone.utc).isoformat() + "Z"

def format_front_json(data_list):
    """Encapsule une liste de data dans la structure requise par le front (objet avec clé 'programmes')."""
    return {"programmes": data_list}

def save_front_json(output_dir, filename, data):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_base_program_skeleton(prog_code):
    return {
        "programmeCode": prog_code,
        "isMock": False,
        "sourceUrl": None,
        "confidence": None,
        "updatedAt": get_current_date(),
        "notes": ""
    }

# --- CALCUL ANALYTIQUE (P3.3) ---
def calculate_dimensions(prog, cursor, weights):
    # 1. financialWeight (Budget CP 2025 normalisé sur max 5 Milliards)
    budg = cursor.execute("SELECT SUM(amount2025) FROM budget_lines WHERE programmeCode=?", (prog,)).fetchone()[0] or 0
    budg_mds = max(budg / 1e9, 0.1)
    financial_score = min((budg_mds / 5.0) * 100, 100)
    
    # 2. politicalAttention (Mentions / Milliard, normalisé sur max 20)
    mentions = cursor.execute("SELECT COUNT(*) FROM parliament_mentions WHERE relatedProgrammeCode=?", (prog,)).fetchone()[0] or 0
    political_score = min(((mentions / budg_mds) / 20.0) * 100, 100)
    
    # 3. greenBudget (Green Budget vs Total, normalisé sur 100%)
    green_budg = cursor.execute("SELECT SUM(amount2026) FROM green_budget_lines WHERE programmeCode=?", (prog,)).fetchone()[0] or 0
    green_score = min(((green_budg / 1e9) / budg_mds) * 100, 100)
    
    # 4. innovationSignal (Nb Brevets, normalisé sur max 50)
    brevets = cursor.execute("""
        SELECT COUNT(*) FROM patent_depositors pd
        JOIN correlations c ON pd.patentFamilyId = c.targetEntityId AND c.correlationType = 'company_patent'
        JOIN correlations c2 ON c.sourceEntityId = c2.sourceEntityId AND c2.correlationType = 'company_theme'
        JOIN correlations c3 ON c2.targetEntityId = c3.targetEntityId AND c3.correlationType = 'programme_theme'
        WHERE c3.sourceEntityId = ?
    """, (prog,)).fetchone()[0] or 0
    innovation_score = min((brevets / 50.0) * 100, 100)
    
    # 5. territorialDeployment (Nb de projets ADEME/CDC, normalisé sur max 100)
    projets = cursor.execute("""
        SELECT COUNT(DISTINCT targetEntityId) FROM correlations 
        WHERE correlationType = 'project_programme' AND targetEntityId = ?
    """, (prog,)).fetchone()[0] or 0
    territorial_score = min((projets / 100.0) * 100, 100)
    
    dims = {
        "financialWeight": round(financial_score, 1),
        "politicalAttention": round(political_score, 1),
        "greenBudget": round(green_score, 1),
        "innovationSignal": round(innovation_score, 1),
        "territorialDeployment": round(territorial_score, 1)
    }
    
    overall = sum(dims[k] * w.get("weight", 0.2) for k, w in weights.items())
    
    return round(overall, 1), dims

def main():
    print("🚀 Démarrage de la passerelle d'export vers le contrat Front (Minerve)...")
    
    db_path = "data/france2030.sqlite"
    if not os.path.exists(db_path):
        print("❌ Erreur: Base SQLite introuvable. Lancez le script 11 d'abord.")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    export_dir = "data/export_front"
    os.makedirs(export_dir, exist_ok=True)
    
    programs = ["421", "422", "423", "424", "425"]

    # =========================================================================
    # 1. dataset/budget/france-2030-budget-lines.json
    # =========================================================================
    print(" -> Exportation de france-2030-budget-lines.json...")
    budget_lines_front = []
    
    query_budget = """
    SELECT b.id, b.programmeCode, p.programmeName, b.expenseCategoryName, 
           b.amount2024, b.amount2025, b.amount2026, b.sourceUrl, b.qualityStatus
    FROM budget_lines b
    JOIN programs p ON b.programmeCode = p.programmeCode
    """
    for row in cursor.execute(query_budget).fetchall():
        amount_2024 = int(row["amount2024"]) if row["amount2024"] else None
        amount_2025 = int(row["amount2025"]) if row["amount2025"] else None
        amount_2026 = int(row["amount2026"]) if row["amount2026"] else None
        
        item = {
            "id": row["id"],
            "programmeCode": row["programmeCode"],
            "programmeName": row["programmeName"],
            "expenseCategoryName": row["expenseCategoryName"],
            "amount2024": amount_2024,
            "amount2025": amount_2025,
            "amount2026": amount_2026,
            "isMock": False,
            "sourceUrl": row["sourceUrl"],
            "confidence": 1.0 if row["qualityStatus"] == "verified" else 0.8,
            "updatedAt": get_current_date(),
            "notes": ""
        }
        budget_lines_front.append(item)
    
    save_front_json(export_dir, "france-2030-budget-lines.json", budget_lines_front)

    # =========================================================================
    # 2. dataset/catalog/investment-programmes.json
    # =========================================================================
    print(" -> Exportation de investment-programmes.json...")
    catalog_front = []
    
    for prog in programs:
        row = cursor.execute("SELECT * FROM programs WHERE programmeCode = ?", (prog,)).fetchone()
        if row:
            item = get_base_program_skeleton(prog)
            item["programmeName"] = row["programmeName"]
            item["missionName"] = row["missionName"]
            
            import json as j
            if os.path.exists("data/programs.json"):
                with open("data/programs.json") as f:
                    progs_json = j.load(f)
                    p_data = next((p for p in progs_json if p["programmeCode"] == prog), None)
                    if p_data:
                        item["objectives"] = p_data.get("officialObjectives", [])
                        item["actions"] = p_data.get("actions", [])
                        if p_data.get("sourceDocuments"):
                            item["sourceUrl"] = p_data["sourceDocuments"][0].get("url")
            
            item["confidence"] = 1.0
            catalog_front.append(item)
            
    save_front_json(export_dir, "investment-programmes.json", format_front_json(catalog_front))

    # =========================================================================
    # 3. dataset/sources/sirene-companies.json
    # =========================================================================
    print(" -> Exportation de sirene-companies.json...")
    companies_front = []
    
    for prog in programs:
        item = get_base_program_skeleton(prog)
        item["companies"] = []
        item["confidence"] = 0.9
        
        query_comp = """
        SELECT c.siren, c.denominationUniteLegale, c.nomUniteLegale, c.prenom1UniteLegale,
               c.categorieJuridiqueUniteLegale, c.activitePrincipaleUniteLegale,
               c.nomenclatureActivitePrincipaleUniteLegale, c.etatAdministratifUniteLegale,
               c.dateCreationUniteLegale, c.source
        FROM companies c
        JOIN correlations cor ON c.companyId = cor.sourceEntityId
        WHERE cor.targetEntityType = 'theme'
          AND cor.targetEntityId IN (
              SELECT targetEntityId FROM correlations WHERE sourceEntityId = ? AND sourceEntityType = 'programme'
          )
        """
        seen_sirens = set()
        for c_row in cursor.execute(query_comp, (prog,)).fetchall():
            siren = c_row["siren"]
            if siren not in seen_sirens:
                item["companies"].append({
                    "siren": siren,
                    "denominationUniteLegale": c_row["denominationUniteLegale"],
                    "nomUniteLegale": c_row["nomUniteLegale"],
                    "prenom1UniteLegale": c_row["prenom1UniteLegale"],
                    "categorieJuridiqueUniteLegale": c_row["categorieJuridiqueUniteLegale"],
                    "activitePrincipaleUniteLegale": c_row["activitePrincipaleUniteLegale"],
                    "nomenclatureActivitePrincipaleUniteLegale": c_row["nomenclatureActivitePrincipaleUniteLegale"],
                    "etatAdministratifUniteLegale": c_row["etatAdministratifUniteLegale"],
                    "dateCreationUniteLegale": c_row["dateCreationUniteLegale"],
                    "source": c_row["source"]
                })
                seen_sirens.add(siren)
                
        if not item["companies"]:
            item["isMock"] = True
            
        companies_front.append(item)
        
    save_front_json(export_dir, "sirene-companies.json", format_front_json(companies_front))

    # =========================================================================
    # 4. dataset/sources/parliamentary-documents.json
    # =========================================================================
    print(" -> Exportation de parliamentary-documents.json...")
    parliament_front = []
    
    for prog in programs:
        item = get_base_program_skeleton(prog)
        item["documents"] = []
        item["confidence"] = 0.9
        
        query_parl = "SELECT * FROM parliament_mentions WHERE relatedProgrammeCode = ?"
        for m_row in cursor.execute(query_parl, (prog,)).fetchall():
            item["documents"].append({
                "id": m_row["mentionId"],
                "date": m_row["date"],
                "chamber": m_row["chamber"],
                "speakerName": m_row["speakerName"],
                "politicalGroup": m_row["politicalGroup"],
                "matchedKeyword": m_row["matchedKeyword"],
                "text": m_row["interventionText"],
                "url": m_row["sourceUrl"]
            })
            if not item["sourceUrl"]:
                item["sourceUrl"] = m_row["sourceUrl"]
                
        if not item["documents"]:
            item["isMock"] = True
            
        parliament_front.append(item)
        
    save_front_json(export_dir, "parliamentary-documents.json", format_front_json(parliament_front))

    # =========================================================================
    # 5. dataset/matching/programme-taxonomy.json
    # =========================================================================
    print(" -> Exportation de programme-taxonomy.json...")
    taxonomy_front = []
    
    for prog in programs:
        item = get_base_program_skeleton(prog)
        item["themes"] = []
        item["confidence"] = 1.0
        
        query_themes = """
        SELECT t.themeId, t.themeName
        FROM themes t
        JOIN correlations c ON t.themeId = c.targetEntityId
        WHERE c.sourceEntityId = ? AND c.correlationType = 'thematic_mapping'
        """
        for t_row in cursor.execute(query_themes, (prog,)).fetchall():
            theme_obj = {
                "themeId": t_row["themeId"],
                "themeName": t_row["themeName"],
                "keywords": []
            }
            query_kw = "SELECT label FROM keywords WHERE relatedThemeId = ?"
            for k_row in cursor.execute(query_kw, (t_row["themeId"],)).fetchall():
                theme_obj["keywords"].append(k_row["label"])
                
            item["themes"].append(theme_obj)
            
        taxonomy_front.append(item)
        
    save_front_json(export_dir, "programme-taxonomy.json", format_front_json(taxonomy_front))

    # =========================================================================
    # 6. dataset/metrics/programme-alignment-scores.json
    # =========================================================================
    print(" -> Calcul des scores d'alignement (Metrics Multi-Dimensionnelles)...")
    
    with open("config/scoring_weights.json", "r") as f:
        weights = json.load(f)
        
    align_scores_front = []
    
    for prog in programs:
        item = get_base_program_skeleton(prog)
        item["confidence"] = 0.90
        
        overall, dimensions = calculate_dimensions(prog, cursor, weights)
        
        item["data"] = {
            "overallScore": overall,
            "dimensions": dimensions
        }
        item["isMock"] = False 
        item["notes"] = f"Calcul basé sur 5 dimensions pondérées. Configuration: {json.dumps({k: v['weight'] for k,v in weights.items()})}"
        align_scores_front.append(item)
        
    save_front_json(export_dir, "programme-alignment-scores.json", format_front_json(align_scores_front))

    # =========================================================================
    # 7. dataset/sources/inpi-patent-families.json
    # =========================================================================
    print(" -> Exportation de inpi-patent-families.json...")
    inpi_front = []
    
    for prog in programs:
        item = get_base_program_skeleton(prog)
        item["data"] = []
        item["confidence"] = 1.0
        
        # Trouver les brevets liés à ce programme
        query_inpi = """
        SELECT pd.siren, pd.companyName, pd.nbDemandes, pd.nbFamilles, pd.sourceUrl
        FROM patent_depositors pd
        JOIN correlations cor ON pd.patentFamilyId = cor.targetEntityId
        WHERE cor.correlationType = 'company_patent'
          AND cor.sourceEntityId IN (
              SELECT c.companyId FROM companies c
              JOIN correlations cor2 ON c.companyId = cor2.sourceEntityId
              WHERE cor2.targetEntityType = 'theme'
                AND cor2.targetEntityId IN (
                    SELECT targetEntityId FROM correlations WHERE sourceEntityId = ? AND sourceEntityType = 'programme'
                )
          )
        """
        for i_row in cursor.execute(query_inpi, (prog,)).fetchall():
            item["data"].append({
                "siren": i_row["siren"],
                "companyName": i_row["companyName"],
                "nbDemandes": i_row["nbDemandes"],
                "nbFamilles": i_row["nbFamilles"],
                "sourceUrl": i_row["sourceUrl"]
            })
                
        if not item["data"]:
            item["isMock"] = True
            
        inpi_front.append(item)
        
    save_front_json(export_dir, "inpi-patent-families.json", format_front_json(inpi_front))

    # =========================================================================
    # 8. dataset/sources/data-gouv-datasets.json
    # =========================================================================
    print(" -> Exportation de data-gouv-datasets.json...")
    sources_front = []
    
    # On lit la table source_registry
    all_sources = cursor.execute("SELECT * FROM source_registry").fetchall()
    sources_dict = [dict(s) for s in all_sources]
    
    for prog in programs:
        item = get_base_program_skeleton(prog)
        item["data"] = sources_dict
        item["confidence"] = 1.0
        item["isMock"] = False
        item["notes"] = "Sources consolidées depuis data/sources.json via SQLite"
        sources_front.append(item)
        
    save_front_json(export_dir, "data-gouv-datasets.json", format_front_json(sources_front))

    # =========================================================================
    # 9. dataset/dataviz/investment-programme-dataviz.json
    # =========================================================================
    print(" -> Exportation de investment-programme-dataviz.json (Agrégats)...")
    dataviz_front = []
    
    for prog in programs:
        item = get_base_program_skeleton(prog)
        item["confidence"] = 0.9
        
        # Agrégation budgétaire
        budg_rows = cursor.execute("SELECT expenseCategoryName, SUM(amount2025) as val FROM budget_lines WHERE programmeCode=? GROUP BY expenseCategoryName", (prog,)).fetchall()
        budget_breakdown = [{"label": r["expenseCategoryName"], "value": r["val"] or 0} for r in budg_rows]
        
        # Agrégation parlementaire (Mentions par mois/année)
        parl_rows = cursor.execute("SELECT SUBSTR(date, 1, 7) as month, COUNT(*) as val FROM parliament_mentions WHERE relatedProgrammeCode=? GROUP BY month ORDER BY month", (prog,)).fetchall()
        mentions_timeline = [{"date": r["month"], "value": r["val"]} for r in parl_rows]
        
        # Agrégation projets (Projets par région)
        proj_rows = cursor.execute("""
            SELECT t.region, COUNT(DISTINCT p.projectId) as val 
            FROM projects p
            JOIN correlations c ON p.projectId = c.sourceEntityId AND c.correlationType = 'project_territory'
            JOIN territories t ON c.targetEntityId = t.territoryId
            JOIN correlations c2 ON p.projectId = c2.sourceEntityId AND c2.correlationType = 'project_programme'
            WHERE c2.targetEntityId = ?
            GROUP BY t.region
        """, (prog,)).fetchall()
        projects_geography = [{"region": r["region"], "value": r["val"]} for r in proj_rows]
        
        item["data"] = {
            "budgetBreakdown": budget_breakdown,
            "mentionsTimeline": mentions_timeline,
            "projectsGeography": projects_geography
        }
        item["isMock"] = False
        item["notes"] = "Agrégats calculés dynamiquement depuis SQLite pour la dataviz."
        dataviz_front.append(item)
        
    save_front_json(export_dir, "investment-programme-dataviz.json", format_front_json(dataviz_front))

    # =========================================================================
    # 10. Fichiers restants (Mocks Vides pour ne pas faire crasher le front)
    # =========================================================================
    print(" -> Création des mocks vides restants...")
    empty_mocks = [
        "investment-programme-reports.json",
        "company-revenues.json"
    ]
    
    for mock_file in empty_mocks:
        mock_data = []
        for prog in programs:
            item = get_base_program_skeleton(prog)
            item["isMock"] = True
            item["data"] = []
            mock_data.append(item)
        save_front_json(export_dir, mock_file, format_front_json(mock_data))

    conn.close()
    print(f"✅ Exportation terminée ! Les 11 fichiers du contrat Front sont dans {export_dir}/")

if __name__ == "__main__":
    main()
