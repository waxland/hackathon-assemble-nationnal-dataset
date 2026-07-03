import pandas as pd
import json
import os

RAW_FILE = os.path.join("data", "raw_budget.csv")

TITRE_LABELS = {
    "2": "Dépenses de personnel",
    "3": "Dépenses de fonctionnement",
    "5": "Dépenses d'investissement",
    "6": "Dépenses d'intervention",
    "7": "Dépenses d'opérations financières"
}

def main():
    if not os.path.exists(RAW_FILE):
        print(f"❌ {RAW_FILE} introuvable. Lancez le script 01 d'abord.")
        return
        
    df = pd.read_csv(RAW_FILE, sep=';', dtype=str)
    
    # Filtrage sur la mission
    df_mission = df[df["Mission"].str.contains("Investir pour la France de 2030", na=False, case=False)]
    
    # Convertir CP PLF en float
    df_mission["CP PLF"] = pd.to_numeric(df_mission["CP PLF"], errors="coerce").fillna(0.0)
    
    # Group by Programme et Code Titre
    grouped = df_mission.groupby(["Programme", "Code Titre"])["CP PLF"].sum().reset_index()
    
    budget_lines = []
    
    for _, row in grouped.iterrows():
        prog_code = str(row["Programme"]).replace(".0", "")
        code_titre = str(row["Code Titre"]).replace(".0", "")
        amount_2025 = float(row["CP PLF"])
        
        # Ignorer les lignes à zéro si pertinent (pour le POC on garde tout pour voir)
        if amount_2025 == 0.0:
            continue
            
        budget_lines.append({
            "id": f"fr2030-{prog_code}-{code_titre}",
            "programmeCode": prog_code,
            "expenseCategoryCode": code_titre,
            "expenseCategoryName": TITRE_LABELS.get(code_titre, f"Titre {code_titre}"),
            "amount2024": None, # Non dispo dans ce CSV
            "amount2025": amount_2025,
            "amount2026": None,
            "sourceUrl": "https://www.data.gouv.fr/datasets/plf-2025-depenses-2025-du-bg-et-des-ba-selon-nomenclatures-destination-et-nature",
            "sourceDocument": "PLF 2025 - Dépenses du BG",
            "sourcePage": "",
            "qualityStatus": "verified"
        })
        
    budget_lines = sorted(budget_lines, key=lambda x: (x["programmeCode"], x["expenseCategoryCode"]))
    
    output_path = os.path.join("data", "budget_lines.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(budget_lines, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(budget_lines)} lignes budgétaires extraites depuis la source officielle dans {output_path}")

if __name__ == "__main__":
    main()
