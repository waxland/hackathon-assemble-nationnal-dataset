import json
import os
import requests
from lib.ids import generate_id
from lib.json_io import write_json_atomic, read_json
from lib.sources import register_source
from lib.download import fetch_with_cache

DATA_DIR = "data"

def main():
    print("Ingestion des projets ADEME France 2030...")
    
    dataset_url = "https://data.ademe.fr/datasets/programmes-detat-projets-finances-par-lademe"
    resource_url = "https://data.ademe.fr/data-fair/api/v1/datasets/programmes-detat-projets-finances-par-lademe/lines"
    
    register_source("ademe-france2030", "Projets financés ADEME (France 2030)", "ADEME", dataset_url)

    # Récupération via l'API (utilisation du cache si FAST=1)
    params = {"q": "france 2030", "size": 10 if os.environ.get("FAST") == "1" else 100}
    try:
        data = fetch_with_cache(resource_url, params=params, use_cache=True)
    except Exception as e:
        print(f"Erreur API ADEME: {e}")
        data = {"results": []}

    projects = read_json(os.path.join(DATA_DIR, "projects.json"), [])
    beneficiaries = read_json(os.path.join(DATA_DIR, "project_beneficiaries.json"), [])
    
    for row in data.get("results", []):
        # Filtrer via pia_france_2030_reporting
        if "2030" not in str(row.get("pia_france_2030_reporting", "")).lower():
            continue
            
        proj_id = generate_id("proj", "ademe", row.get("dossier_code", ""))
        projects.append({
            "projectId": proj_id,
            "projectName": row.get("nom_du_projet", "Projet ADEME"),
            "operatorName": "ADEME",
            "sourceUrl": resource_url,
            "datasetUrl": dataset_url,
            "resourceUrl": resource_url,
            "sourceDatasetId": "programmes-detat-projets-finances-par-lademe",
            "sourceProducer": "ADEME",
            "confidenceScore": 1.0,
            "validationStatus": "validated"
        })
        
        # Ajout du bénéficiaire si SIREN dispo
        siren = row.get("siren_du_beneficiaire")
        if siren:
            benef_id = generate_id("benef", "ademe", siren)
            beneficiaries.append({
                "beneficiaryId": benef_id,
                "projectId": proj_id,
                "siren": siren,
                "operatorName": "ADEME",
                "sourceUrl": resource_url,
                "datasetUrl": dataset_url,
                "resourceUrl": resource_url,
                "confidenceScore": 1.0,
                "validationStatus": "validated"
            })
            
    # Déduplication
    unique_proj = {p["projectId"]: p for p in projects}.values()
    unique_benef = {b["beneficiaryId"]: b for b in beneficiaries}.values()
    
    write_json_atomic(os.path.join(DATA_DIR, "projects.json"), list(unique_proj))
    write_json_atomic(os.path.join(DATA_DIR, "project_beneficiaries.json"), list(unique_benef))
    
    print("✅ Données ADEME ingérées et enrichies avec URL de source.")

if __name__ == "__main__":
    main()
