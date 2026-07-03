import pandas as pd
import json
import os

URL_CSV = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/plf25-depenses-2025-du-bg-et-des-ba-selon-nomenclatures-destination-et-nature/exports/csv?use_labels=true"
DATA_DIR = "data"
RAW_FILE = os.path.join(DATA_DIR, "raw_budget.csv")

def download_data():
    if not os.path.exists(RAW_FILE):
        print("Téléchargement du dataset PLF 2025...")
        df = pd.read_csv(URL_CSV, sep=';', dtype=str)
        df.to_csv(RAW_FILE, index=False, sep=';')
    else:
        print("Dataset PLF 2025 déjà présent en cache.")
    
    return pd.read_csv(RAW_FILE, sep=';')

def format_program(prog_code, prog_name, mission_name):
    return {
        "programmeCode": str(prog_code).replace(".0", ""),
        "programmeName": str(prog_name).strip(),
        "missionName": str(mission_name).strip(),
        "budgetLines": [],
        "officialObjectives": [],
        "actions": [],
        "themes": [],
        "keywords": [],
        "callsForProjects": [],
        "parliamentMentions": [],
        "sourceDocuments": []
    }

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    df = download_data()
    
    # Filtrage sur la mission
    df_mission = df[df["Mission"].str.contains("Investir pour la France de 2030", na=False, case=False)]
    
    if df_mission.empty:
        print("❌ Aucune donnée trouvée pour la mission 'Investir pour la France de 2030'.")
        return
        
    programs_dict = {}
    
    for _, row in df_mission.iterrows():
        prog_code = row["Programme"]
        prog_name = row["Libellé Programme"]
        mission_name = row["Mission"]
        
        clean_code = str(prog_code).replace(".0", "")
        
        if clean_code not in programs_dict:
            programs_dict[clean_code] = format_program(prog_code, prog_name, mission_name)
            
    programs_list = list(programs_dict.values())
    programs_list = sorted(programs_list, key=lambda x: x["programmeCode"])
    
    output_path = os.path.join(DATA_DIR, "programs.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(programs_list, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(programs_list)} programmes extraits depuis la source officielle dans {output_path}")

if __name__ == "__main__":
    main()
