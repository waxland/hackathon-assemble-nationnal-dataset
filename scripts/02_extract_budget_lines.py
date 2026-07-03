import pandas as pd
import json
import os
import ssl
import urllib.request

# Désactivation de la vérification SSL pour contourner le bug des certificats MacOS
ssl._create_default_https_context = ssl._create_unverified_context

RAW_FILE_2025 = os.path.join("data", "raw_budget_2025.csv")
RAW_FILE_2024 = os.path.join("data", "raw_budget_2024.csv")

URL_2025 = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/plf25-depenses-2025-du-bg-et-des-ba-selon-nomenclatures-destination-et-nature/exports/csv?use_labels=true"
URL_2024 = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/plf-2024-depenses-2024-selon-nomenclatures-destination-et-nature/exports/csv?use_labels=true"

TITRE_LABELS = {
    "2": "Dépenses de personnel",
    "3": "Dépenses de fonctionnement",
    "5": "Dépenses d'investissement",
    "6": "Dépenses d'intervention",
    "7": "Dépenses d'opérations financières"
}

def download_data(url, filepath):
    if not os.path.exists(filepath):
        print(f"Téléchargement du dataset : {filepath}...")
        df = pd.read_csv(url, sep=';', dtype=str)
        df.to_csv(filepath, index=False, sep=';')
    return pd.read_csv(filepath, sep=';', dtype=str)

def main():
    print("Extraction et consolidation des lignes budgétaires (2024/2025)...")
    os.makedirs("data", exist_ok=True)
    
    # --- Traitement 2025 ---
    df_2025 = download_data(URL_2025, RAW_FILE_2025)
    df_mission_25 = df_2025[df_2025["Mission"].str.contains("Investir pour la France de 2030", na=False, case=False)].copy()
    df_mission_25["CP PLF"] = pd.to_numeric(df_mission_25["CP PLF"], errors="coerce").fillna(0.0)
    grouped_25 = df_mission_25.groupby(["Programme", "Code Titre"])["CP PLF"].sum().reset_index()
    
    # --- Traitement 2024 ---
    df_2024 = download_data(URL_2024, RAW_FILE_2024)
    mission_col = "Mission" if "Mission" in df_2024.columns else "Libellé Mission"
    if mission_col not in df_2024.columns:
        for col in df_2024.columns:
            if "mission" in col.lower(): mission_col = col; break
            
    df_mission_24 = df_2024[df_2024[mission_col].str.contains("Investir pour la France de 2030", na=False, case=False)].copy()
    df_mission_24["CP PLF"] = pd.to_numeric(df_mission_24["CP PLF"], errors="coerce").fillna(0.0)
    grouped_24 = df_mission_24.groupby(["Programme", "Code Titre"])["CP PLF"].sum().reset_index()

    # --- Consolidation ---
    budget_lines_dict = {}
    
    for _, row in grouped_25.iterrows():
        prog_code = str(row["Programme"]).replace(".0", "")
        code_titre = str(row["Code Titre"]).replace(".0", "")
        amount_2025 = float(row["CP PLF"])
        
        b_id = f"fr2030-{prog_code}-{code_titre}"
        budget_lines_dict[b_id] = {
            "id": b_id,
            "programmeCode": prog_code,
            "expenseCategoryCode": code_titre,
            "expenseCategoryName": TITRE_LABELS.get(code_titre, f"Titre {code_titre}"),
            "amount2024": None,
            "amount2025": amount_2025,
            "amount2026": None,
            "sourceUrl": URL_2025,
            "sourceDocument": "PLF 2025 et PLF 2024 - Dépenses du BG",
            "sourcePage": "",
            "qualityStatus": "verified"
        }
        
    for _, row in grouped_24.iterrows():
        prog_code = str(row["Programme"]).replace(".0", "")
        code_titre = str(row["Code Titre"]).replace(".0", "")
        amount_2024 = float(row["CP PLF"])
        
        b_id = f"fr2030-{prog_code}-{code_titre}"
        if b_id in budget_lines_dict:
            budget_lines_dict[b_id]["amount2024"] = amount_2024
        else:
            budget_lines_dict[b_id] = {
                "id": b_id,
                "programmeCode": prog_code,
                "expenseCategoryCode": code_titre,
                "expenseCategoryName": TITRE_LABELS.get(code_titre, f"Titre {code_titre}"),
                "amount2024": amount_2024,
                "amount2025": None,
                "amount2026": None,
                "sourceUrl": URL_2024,
                "sourceDocument": "PLF 2024 - Dépenses du BG",
                "sourcePage": "",
                "qualityStatus": "verified"
            }
            
    budget_lines = list(budget_lines_dict.values())
    budget_lines = sorted(budget_lines, key=lambda x: (x["programmeCode"], x["expenseCategoryCode"]))
    
    output_path = os.path.join("data", "budget_lines.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(budget_lines, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(budget_lines)} lignes budgétaires (2024-2025) extraites dans {output_path}")

if __name__ == "__main__":
    main()
