import pandas as pd
import json
import os
import requests
import hashlib

URL_LAUREATS = "https://opendata.caissedesdepots.fr/api/explore/v2.1/catalog/datasets/liste-des-laureats/exports/csv?use_labels=true"
DATA_DIR = "data"
RAW_FILE = os.path.join(DATA_DIR, "raw", "raw_laureats_cdd.csv")

def get_hash_id(prefix, *args):
    s = "_".join(str(a) for a in args).encode('utf-8')
    return prefix + "-" + hashlib.md5(s).hexdigest()[:8]

def download_data():
    os.makedirs(os.path.dirname(RAW_FILE), exist_ok=True)
    if not os.path.exists(RAW_FILE):
        print("Téléchargement du dataset Lauréats Démonstrateurs Ville Durable...")
        resp = requests.get(URL_LAUREATS)
        resp.raise_for_status()
        with open(RAW_FILE, "wb") as f:
            f.write(resp.content)
    return pd.read_csv(RAW_FILE, sep=';', dtype=str)

def main():
    print("Ingestion des projets Lauréats (Caisse des Dépôts)...")
    try:
        df = download_data()
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement : {e}")
        return
        
    projects = []
    beneficiaries = []
    territories = []
    correlations = []
    
    # On nettoie un peu le df
    df.fillna("", inplace=True)
    
    # Thème France 2030 déduit pour "Ville Durable"
    # D'après la taxo P425: "Pôles et territoires d'innovation"
    theme_id = "poles-et-territoires-d-innovation"
    prog_code = "425"
    
    seen_terrs = set()
    seen_benefs = set()
    
    for idx, row in df.iterrows():
        nom_projet = row.get("Nom projet", "").strip()
        if not nom_projet: continue
            
        proj_id = get_hash_id("proj", nom_projet, row.get("Code com Insee", ""))
        
        # --- Montants ---
        inc_str = row.get("Montant engagé subvention incubation", "").replace(" ", "").replace(",", ".")
        rea_str = row.get("Montant engagé subvention réalisation", "").replace(" ", "").replace(",", ".")
        inc_amount = float(inc_str) if inc_str else 0.0
        rea_amount = float(rea_str) if rea_str else 0.0
        total_grant = inc_amount + rea_amount
        
        # --- Projets ---
        projects.append({
            "projectId": proj_id,
            "projectName": nom_projet,
            "description": row.get("Descriptif du projet", ""),
            "operator": "Caisse des Dépôts",
            "grantAmount": total_grant,
            "impactIndicators": {
                "co2SavedPerYear": row.get("Tonnes de CO2 équivalent évitées/an", ""),
                "kwhSavedPerYear": row.get("Gains en kWh évités/an sur la consommation énergétique globale", ""),
                "renaturedSurfaceHa": row.get("Surfaces renaturées (HA)", ""),
                "depollutedSurfaceHa": row.get("Surfaces dépolluées (HA)", "")
            },
            "sourceUrl": "https://www.data.gouv.fr/datasets/liste-des-laureats-demonstrateurs-ville-durable-france-2030",
            "confidenceScore": 1.0
        })
        
        # --- Bénéficiaires ---
        benef_name = row.get("Bénéficiaire", "").strip()
        if benef_name:
            benef_id = get_hash_id("benef", benef_name)
            if benef_id not in seen_benefs:
                beneficiaries.append({
                    "beneficiaryId": benef_id,
                    "name": benef_name,
                    "type": row.get("Porteur projet", ""),
                    "confidenceScore": 1.0
                })
                seen_benefs.add(benef_id)
            
            # Corr: Project -> Beneficiary
            correlations.append({
                "correlationId": get_hash_id("corr", proj_id, benef_id, "project_beneficiary"),
                "sourceEntityType": "project",
                "sourceEntityId": proj_id,
                "targetEntityType": "beneficiary",
                "targetEntityId": benef_id,
                "correlationType": "project_beneficiary",
                "confidenceScore": 1.0,
                "evidenceSource": "raw_laureats_cdd.csv",
                "validationStatus": "validated"
            })
            
        # --- Territoires ---
        com_code = row.get("Code com Insee", "").strip()
        com_name = row.get("Libellé de la Commune", "").strip()
        if com_code and com_name:
            terr_id = get_hash_id("terr", com_code)
            if terr_id not in seen_terrs:
                territories.append({
                    "territoryId": terr_id,
                    "communeCode": com_code,
                    "communeName": com_name,
                    "departement": row.get("Département", ""),
                    "region": row.get("Région", ""),
                    "confidenceScore": 1.0
                })
                seen_terrs.add(terr_id)
                
            # Corr: Project -> Territory
            correlations.append({
                "correlationId": get_hash_id("corr", proj_id, terr_id, "project_territory"),
                "sourceEntityType": "project",
                "sourceEntityId": proj_id,
                "targetEntityType": "territory",
                "targetEntityId": terr_id,
                "correlationType": "project_territory",
                "confidenceScore": 1.0,
                "evidenceSource": "raw_laureats_cdd.csv",
                "validationStatus": "validated"
            })
            
        # Corr: Project -> Theme (Ville durable)
        correlations.append({
            "correlationId": get_hash_id("corr", proj_id, theme_id, "project_theme"),
            "sourceEntityType": "project",
            "sourceEntityId": proj_id,
            "targetEntityType": "theme",
            "targetEntityId": theme_id,
            "correlationType": "project_theme",
            "confidenceScore": 0.9, # Déduction lexicale
            "evidenceSource": "raw_laureats_cdd.csv",
            "validationStatus": "to_validate"
        })
        
        # Corr: Project -> Programme (425)
        correlations.append({
            "correlationId": get_hash_id("corr", proj_id, prog_code, "project_programme"),
            "sourceEntityType": "project",
            "sourceEntityId": proj_id,
            "targetEntityType": "programme",
            "targetEntityId": prog_code,
            "correlationType": "project_programme",
            "confidenceScore": 0.8,
            "evidenceSource": "raw_laureats_cdd.csv",
            "validationStatus": "to_validate"
        })

    with open(os.path.join(DATA_DIR, "projects.json"), "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)
    with open(os.path.join(DATA_DIR, "project_beneficiaries.json"), "w", encoding="utf-8") as f:
        json.dump(beneficiaries, f, indent=2, ensure_ascii=False)
    with open(os.path.join(DATA_DIR, "territories.json"), "w", encoding="utf-8") as f:
        json.dump(territories, f, indent=2, ensure_ascii=False)
        
    # Append correlations
    corr_file = os.path.join(DATA_DIR, "correlations.json")
    existing_corrs = []
    if os.path.exists(corr_file):
        with open(corr_file, "r", encoding="utf-8") as f:
            existing_corrs = json.load(f)
            
    # Combine and deduplicate
    all_corrs = existing_corrs + correlations
    unique_corrs = {c["correlationId"]: c for c in all_corrs}.values()
    
    with open(corr_file, "w", encoding="utf-8") as f:
        json.dump(list(unique_corrs), f, indent=2, ensure_ascii=False)
        
    print(f"✅ Export: {len(projects)} projets, {len(beneficiaries)} bénéficiaires, {len(territories)} territoires.")
    print(f"✅ {len(correlations)} nouvelles corrélations ajoutées.")

if __name__ == "__main__":
    main()
