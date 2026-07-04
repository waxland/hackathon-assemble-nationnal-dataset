import pandas as pd
import json
import os
import requests
from io import StringIO

URL_BUDGET_VERT = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/plf-2026-budget-vert/exports/csv?use_labels=true"
DATA_DIR = "data"
RAW_FILE = os.path.join(DATA_DIR, "raw", "raw_budget_vert_2026.csv")

def download_data():
    os.makedirs(os.path.dirname(RAW_FILE), exist_ok=True)
    if not os.path.exists(RAW_FILE):
        print("Téléchargement du dataset Budget Vert PLF 2026...")
        # on télécharge le contenu pour gérer les retours chariots merdiques dans les headers
        resp = requests.get(URL_BUDGET_VERT)
        resp.raise_for_status()
        text = resp.text
        # Nettoyage des headers (les retours charriots cassent pandas)
        lines = text.split("\n")
        header = lines[0].replace("\r", " ").replace("\n", " ")
        text = header + "\n" + "\n".join(lines[1:])
        
        df = pd.read_csv(StringIO(text), sep=';', dtype=str)
        df.to_csv(RAW_FILE, index=False, sep=';')
    else:
        print("Dataset Budget Vert 2026 déjà présent en cache.")
    
    return pd.read_csv(RAW_FILE, sep=';', dtype=str)

def main():
    print("Ingestion du PLF 2026 - Budget Vert...")
    df = download_data()
    
    # Nettoyage des noms de colonnes pour enlever les \n résiduels
    df.columns = df.columns.str.replace('\n', ' ').str.replace('\r', '').str.strip()
    
    # Trouver les colonnes avec les montants, elles s'appellent souvent "LFI 2025..." ou "PLF 2026..."
    col_2026 = [c for c in df.columns if "PLF 2026" in c]
    col_2026 = col_2026[0] if col_2026 else None
    
    if not col_2026:
        print("❌ Colonne 'PLF 2026' non trouvée.")
        print("Colonnes disponibles:", df.columns.tolist())
        return
        
    df_mission = df[df["Mission"].str.contains("Investir pour la France de 2030", na=False, case=False)].copy()
    
    if df_mission.empty:
        print("❌ Aucune donnée trouvée pour France 2030 dans le Budget Vert.")
        return

    df_mission[col_2026] = pd.to_numeric(df_mission[col_2026], errors="coerce").fillna(0.0)
    
    green_budget_lines = []
    
    # Agrégation par programme et action pour le json dédié
    for _, row in df_mission.iterrows():
        if row[col_2026] == 0.0: continue
            
        prog_code = str(row["Numéro programme"]).replace(".0", "")
        action_code = str(row["Code action (si crédit budgétaire)"])
        rating = str(row["Cotation globale"])
        
        green_budget_lines.append({
            "id": f"fr2030-green-{prog_code}-{action_code}-{hash(rating)}",
            "programmeCode": prog_code,
            "actionCode": action_code,
            "actionName": row["Action (si crédit budgétaire)"],
            "globalRating": rating,
            "amount2026": float(row[col_2026]),
            "sourceUrl": "https://www.data.gouv.fr/datasets/plf-2026-budget-vert",
            "confidenceScore": 1.0
        })

    out_file = os.path.join(DATA_DIR, "green_budget_lines.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(green_budget_lines, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(green_budget_lines)} lignes de budget vert exportées dans {out_file}")
    
    # Mettre à jour budget_lines.json avec le amount2026 global par programme si possible
    budget_path = os.path.join(DATA_DIR, "budget_lines.json")
    if os.path.exists(budget_path):
        with open(budget_path, "r", encoding="utf-8") as f:
            budget_lines = json.load(f)
            
        # Groupby programme
        agg_2026 = df_mission.groupby("Numéro programme")[col_2026].sum()
        
        updated_count = 0
        for bl in budget_lines:
            prog_code = bl["programmeCode"]
            # Le budget vert n'a pas les Titres (T3, T6). 
            # On ne peut donc pas affecter la valeur exacte à la bonne "budget_line".
            # Donc on ne remplit `amount2026` QUE SI on sait à quel titre ça va (ce n'est pas le cas dans le CSV vert)
            # ou on le stocke au niveau d'un autre fichier.
            # L'énoncé dit : "Remplir amount2026 dans budget_lines.json uniquement si la jointure est fiable. Sinon, conserver amount2026: null"
            # Puisqu'on n'a pas le "Titre" dans le budget vert, la jointure n'est pas fiable.
            bl["amount2026"] = None
        
        with open(budget_path, "w", encoding="utf-8") as f:
            json.dump(budget_lines, f, indent=2, ensure_ascii=False)
            
        print("⚠️ amount2026 laissé à null dans budget_lines.json car la jointure sur 'Catégorie de dépense' (Titre) n'est pas fiable avec le fichier du Budget Vert.")

if __name__ == "__main__":
    main()
