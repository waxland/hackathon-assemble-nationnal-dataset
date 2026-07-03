import json
import os
import sqlite3
from datetime import datetime

# --- UTILITAIRES ---
def get_current_date():
    return datetime.utcnow().isoformat() + "Z"

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


def main():
    print("🚀 Démarrage de la passerelle d'export vers le contrat Front (Minerve.fr)...")
    
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
    
    # On récupère toutes les lignes de budget avec le nom du programme associé
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
            # Récupérer les "officialObjectives"
            # Note: dans notre BDD SQL actuelle on n'a pas stocké la liste brute d'objectifs, 
            # on va lire data/programs.json pour faciliter.
            import json as j
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
        
        # Trouver les entreprises liées à ce programme
        query_comp = """
        SELECT c.companyName, c.siren, c.nafCode, c.source, c.confidenceScore
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
                    "name": c_row["companyName"],
                    "siren": siren,
                    "nafCode": c_row["nafCode"],
                    "source": c_row["source"]
                })
                seen_sirens.add(siren)
                
        # Si on n'a pas d'entreprise, on marque isMock = True pour ce tableau vide
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
            # Chercher les mots-clés de ce thème
            query_kw = "SELECT label FROM keywords WHERE relatedThemeId = ?"
            for k_row in cursor.execute(query_kw, (t_row["themeId"],)).fetchall():
                theme_obj["keywords"].append(k_row["label"])
                
            item["themes"].append(theme_obj)
            
        taxonomy_front.append(item)
        
    save_front_json(export_dir, "programme-taxonomy.json", format_front_json(taxonomy_front))


    # =========================================================================
    # 6. Fichiers restants (Mocks Vides pour ne pas faire crasher le front)
    # =========================================================================
    print(" -> Création des mocks vides (INPI, revenues, etc.)...")
    empty_mocks = [
        "investment-programme-reports.json",
        "investment-programme-dataviz.json",
        "data-gouv-datasets.json",
        "inpi-patent-families.json",
        "company-revenues.json",
        "programme-alignment-scores.json"
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
