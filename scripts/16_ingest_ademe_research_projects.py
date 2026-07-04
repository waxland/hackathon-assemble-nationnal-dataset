import pandas as pd
import json
import os
import requests
import hashlib

URL_ADEME = "https://data.ademe.fr/data-fair/api/v1/datasets/projets-de-recherche-ademe-vue-detaillee-depuis-2021/convert?format=csv"
DATA_DIR = "data"
RAW_FILE = os.path.join(DATA_DIR, "raw", "raw_ademe.csv")

def get_hash_id(prefix, *args):
    s = "_".join(str(a) for a in args).encode('utf-8')
    return prefix + "-" + hashlib.md5(s).hexdigest()[:8]

def download_data():
    os.makedirs(os.path.dirname(RAW_FILE), exist_ok=True)
    if not os.path.exists(RAW_FILE):
        print("Téléchargement du dataset ADEME Projets de recherche...")
        resp = requests.get(URL_ADEME)
        resp.raise_for_status()
        with open(RAW_FILE, "wb") as f:
            f.write(resp.content)
    return pd.read_csv(RAW_FILE, sep=',', dtype=str)

def get_theme_mapping(keywords, keywords_db):
    """Mappe un mot-clé ADEME vers un theme France 2030 (naïf)."""
    if not keywords: return None
    kw_lower = keywords.lower()
    for kw in keywords_db:
        if kw["label"].lower() in kw_lower:
            return kw["relatedThemeId"]
    return None

def main():
    print("Ingestion des projets de recherche ADEME...")
    try:
        df = download_data()
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement : {e}")
        return
        
    df.fillna("", inplace=True)
    
    # Load keywords for mapping
    keywords_db = []
    kw_path = os.path.join(DATA_DIR, "keywords.json")
    if os.path.exists(kw_path):
        with open(kw_path, "r", encoding="utf-8") as f:
            keywords_db = json.load(f)

    projects = []
    beneficiaries = []
    correlations = []
    
    seen_projs = set()
    seen_benefs = set()
    
    for idx, row in df.iterrows():
        # L'identifiant ADEME
        identifier = row.get("identifier", "").strip()
        if not identifier: continue
            
        proj_id = f"ademe-{identifier}"
        
        # --- Montants ---
        grant_amount = float(row.get("budget.grant") or 0.0)
        budget_amount = float(row.get("budget.amount") or 0.0)
        
        if proj_id not in seen_projs:
            projects.append({
                "projectId": proj_id,
                "projectName": row.get("title", ""),
                "description": row.get("description", ""),
                "operator": "ADEME",
                "grantAmount": grant_amount,
                "budgetAmount": budget_amount,
                "startDate": row.get("start_date", ""),
                "endDate": row.get("end_date", ""),
                "status": row.get("status", ""),
                "keywords": row.get("keywords", ""),
                "sourceUrl": "https://www.data.gouv.fr/datasets/projets-de-recherche-ademe-vue-detaillee-depuis-2021",
                "confidenceScore": 1.0
            })
            seen_projs.add(proj_id)
            
            # Mapping Thématique
            theme_id = get_theme_mapping(row.get("keywords", "") + " " + row.get("title", ""), keywords_db)
            if theme_id:
                correlations.append({
                    "correlationId": get_hash_id("corr", proj_id, theme_id, "project_theme"),
                    "sourceEntityType": "project",
                    "sourceEntityId": proj_id,
                    "targetEntityType": "theme",
                    "targetEntityId": theme_id,
                    "correlationType": "project_theme",
                    "confidenceScore": 0.6, # Seulement lexical
                    "evidenceSource": "raw_ademe.csv",
                    "validationStatus": "to_validate"
                })
        
        # --- Bénéficiaires ---
        siret = row.get("grantee.SIRET", "").strip()
        name = row.get("grantee.name", "").strip()
        if siret or name:
            siren = siret[:9] if len(siret) >= 9 else ""
            benef_id = f"siren-{siren}" if siren else get_hash_id("benef", name)
            
            if benef_id not in seen_benefs:
                beneficiaries.append({
                    "beneficiaryId": benef_id,
                    "name": name,
                    "siren": siren,
                    "type": "Company/Research",
                    "confidenceScore": 0.8 if siren else 0.4
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
                "evidenceSource": "raw_ademe.csv",
                "validationStatus": "validated"
            })

    # Append to existing projects
    existing_projs = []
    if os.path.exists(os.path.join(DATA_DIR, "projects.json")):
        with open(os.path.join(DATA_DIR, "projects.json"), "r") as f:
            existing_projs = json.load(f)
            
    existing_benefs = []
    if os.path.exists(os.path.join(DATA_DIR, "project_beneficiaries.json")):
        with open(os.path.join(DATA_DIR, "project_beneficiaries.json"), "r") as f:
            existing_benefs = json.load(f)
            
    existing_corrs = []
    if os.path.exists(os.path.join(DATA_DIR, "correlations.json")):
        with open(os.path.join(DATA_DIR, "correlations.json"), "r") as f:
            existing_corrs = json.load(f)

    all_projs = existing_projs + projects
    all_benefs = existing_benefs + beneficiaries
    all_corrs = existing_corrs + correlations
    
    # Deduplicate
    unique_projs = {p["projectId"]: p for p in all_projs}.values()
    unique_benefs = {b["beneficiaryId"]: b for b in all_benefs}.values()
    unique_corrs = {c["correlationId"]: c for c in all_corrs}.values()

    with open(os.path.join(DATA_DIR, "projects.json"), "w", encoding="utf-8") as f:
        json.dump(list(unique_projs), f, indent=2, ensure_ascii=False)
    with open(os.path.join(DATA_DIR, "project_beneficiaries.json"), "w", encoding="utf-8") as f:
        json.dump(list(unique_benefs), f, indent=2, ensure_ascii=False)
    with open(os.path.join(DATA_DIR, "correlations.json"), "w", encoding="utf-8") as f:
        json.dump(list(unique_corrs), f, indent=2, ensure_ascii=False)
        
    print(f"✅ Export ADEME: {len(unique_projs)} projets au total, {len(unique_benefs)} bénéficiaires au total.")
    print(f"✅ Table des corrélations contient désormais {len(unique_corrs)} relations.")

if __name__ == "__main__":
    main()
