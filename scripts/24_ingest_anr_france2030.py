import json
import os
from lib.ids import generate_id
from lib.json_io import write_json_atomic, read_json
from lib.sources import register_source
from lib.download import fetch_with_cache

DATA_DIR = "data"

def main():
    print("Ingestion des projets ANR France 2030...")
    
    dataset_url = "https://dataanr.opendatasoft.com/explore/dataset/public-france2030-indicateurs-cofinancements"
    api_url = "https://dataanr.opendatasoft.com/api/explore/v2.1/catalog/datasets/public-france2030-indicateurs-cofinancements/records"
    
    register_source("anr-france2030-cofinancement", "Indicateurs Cofinancements ANR", "ANR", dataset_url)

    params = {"limit": 10 if os.environ.get("FAST") == "1" else 100}
    try:
        data = fetch_with_cache(api_url, params=params, use_cache=True)
    except Exception as e:
        print(f"Erreur API ANR: {e}")
        data = {"results": []}

    projects = read_json(os.path.join(DATA_DIR, "projects.json"), [])
    anr_projects = []
    
    for row in data.get("results", []):
        proj_id = generate_id("proj", "anr", row.get("id_projet", row.get("numero_projet", "")))
        proj_data = {
            "projectId": proj_id,
            "projectName": row.get("titre_du_projet", "Projet ANR"),
            "operatorName": "ANR",
            "sourceUrl": api_url,
            "datasetUrl": dataset_url,
            "resourceUrl": api_url,
            "sourceDatasetId": "public-france2030-indicateurs-cofinancements",
            "sourceProducer": "ANR",
            "confidenceScore": 1.0,
            "validationStatus": "validated"
        }
        projects.append(proj_data)
        anr_projects.append(proj_data)
            
    unique_proj = {p["projectId"]: p for p in projects}.values()
    
    write_json_atomic(os.path.join(DATA_DIR, "projects.json"), list(unique_proj))
    write_json_atomic(os.path.join(DATA_DIR, "anr_france2030_projects.json"), anr_projects)
    
    print("✅ Données ANR ingérées et enrichies avec URL de source.")

if __name__ == "__main__":
    main()
