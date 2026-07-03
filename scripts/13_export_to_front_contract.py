import json
import os
import sqlite3
from datetime import datetime, timezone

def get_current_date():
    return datetime.now(timezone.utc).isoformat() + "Z"

def format_front_json(data_list):
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
    print("🚀 Démarrage de la passerelle d'export vers le contrat Front...")
    db_path = "data/france2030.sqlite"
    if not os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    export_dir = "data/export_front"
    programs = ["421", "422", "423", "424", "425"]

    # ... (le reste du script précédent inchangé)
    print(" -> Calcul des scores d'alignement (Metrics)...")
    align_scores_front = []
    
    for prog in programs:
        item = get_base_program_skeleton(prog)
        item["confidence"] = 0.85
        
        # Logique de scoring empirique: (Nb Mentions * 10) / (Budget en Mds)
        # Ceci est un exemple métier implémenté pour le Front
        budg = cursor.execute("SELECT SUM(amount2025) FROM budget_lines WHERE programmeCode=?", (prog,)).fetchone()[0] or 0
        budg_mds = max(budg / 1e9, 0.1) # Eviter division par zéro
        
        mentions = cursor.execute("SELECT COUNT(*) FROM parliament_mentions WHERE relatedProgrammeCode=?", (prog,)).fetchone()[0] or 0
        
        score = min(round((mentions * 10) / budg_mds, 1), 100) # Score sur 100 max
        
        item["data"] = {
            "overallScore": score,
            "dimensions": {
                "politicalAttention": min(mentions * 5, 100),
                "financialWeight": min(budg_mds * 20, 100)
            }
        }
        item["isMock"] = False # Le score n'est plus mocké, il est calculé !
        item["notes"] = "Calcul dynamique : (Mentions * 10) / Budget(Mds)"
        align_scores_front.append(item)
        
    save_front_json(export_dir, "programme-alignment-scores.json", format_front_json(align_scores_front))

    conn.close()
    print(f"✅ Exportation terminée avec score calculé dans {export_dir}/")

if __name__ == "__main__":
    main()
