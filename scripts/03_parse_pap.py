import pandas as pd
import json
import os

URL_PAP_CSV = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/plf-2025-performance/exports/csv?use_labels=true"
DATA_DIR = "data"
RAW_PAP_FILE = os.path.join(DATA_DIR, "raw_pap_2025.csv")
RAW_BUDGET_FILE = os.path.join(DATA_DIR, "raw_budget.csv")

def download_data():
    if not os.path.exists(RAW_PAP_FILE):
        print("Téléchargement du dataset Performance PAP 2025...")
        df = pd.read_csv(URL_PAP_CSV, sep=';', dtype=str)
        df.to_csv(RAW_PAP_FILE, index=False, sep=';')
    else:
        print("Dataset Performance PAP 2025 déjà présent en cache.")
    
    return pd.read_csv(RAW_PAP_FILE, sep=';')

def main():
    print("Extraction des objectifs et actions réels...")
    
    input_path = os.path.join(DATA_DIR, "programs.json")
    if not os.path.exists(input_path):
        print(f"❌ Erreur: {input_path} introuvable.")
        return
        
    with open(input_path, "r", encoding="utf-8") as f:
        programs = json.load(f)

    # 1. Extraction des objectifs depuis le dataset PAP
    df_pap = download_data()
    # Nettoyage des noms de colonnes pour éviter les espaces invisibles
    df_pap.columns = df_pap.columns.str.strip()
    
    # 2. Extraction des actions depuis le raw_budget.csv (s'il existe)
    df_budget = pd.DataFrame()
    if os.path.exists(RAW_BUDGET_FILE):
        df_budget = pd.read_csv(RAW_BUDGET_FILE, sep=';', dtype=str)
    
    for p in programs:
        prog_code = p["programmeCode"]
        
        # --- Objectifs (depuis PAP) ---
        # Le format dans le CSV est ex: "P424" pour 424
        pap_filtered = df_pap[df_pap["Code Programme"] == f"P{prog_code}"]
        objectives = pap_filtered["Libellé Objectif"].dropna().unique().tolist()
        p["officialObjectives"] = [obj.strip() for obj in objectives if str(obj).strip() != ""]
        
        # --- Actions (depuis Budget) ---
        actions = []
        if not df_budget.empty:
            bud_filtered = df_budget[(df_budget["Programme"] == f"{prog_code}.0") | (df_budget["Programme"] == prog_code)]
            
            # Prendre les couples uniques "Action" - "Libellé Action"
            unique_actions = bud_filtered[["Action", "Libellé Action"]].drop_duplicates().dropna()
            for _, row in unique_actions.iterrows():
                act_code = str(row["Action"]).strip()
                act_label = str(row["Libellé Action"]).strip()
                actions.append(f"Action {act_code} - {act_label}")
                
        p["actions"] = actions
        
        # Ajouter le lien documentaire vers les données sources
        p["sourceDocuments"] = [{
            "title": "PLF 2025 - Performance de la dépense (PAP) - Open Data",
            "url": "https://www.data.gouv.fr/datasets/plf-2025-performance-de-la-depense-pap"
        }]
        
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(programs, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(programs)} programmes enrichis avec les véritables objectifs (Open Data).")

if __name__ == "__main__":
    main()
