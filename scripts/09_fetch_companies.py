import json
import os
import zipfile
import csv
import io
import requests

DATA_GOUV_API = "https://www.data.gouv.fr/api/1/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/"
DATA_DIR = "data"
RAW_FILE = os.path.join(DATA_DIR, "raw", "StockUniteLegale.zip")

# Les 8 entreprises mock "cibles" pour le POC.
# Mais on veut aussi dynamiser la récupération à partir de nos vrais projets (issus de la Caisse des dépôts et de l'ADEME).
TARGET_COMPANIES = {
    "888047792": {"theme": "4.-vehicules-electriques-et-hybrides", "prog": "424", "source": "Sample POC"},
    "534948617": {"theme": "6.-alimentation-saine-durable-et-tracable", "prog": "424", "source": "Sample POC"},
    "952418325": {"theme": "levier-:-composants-cloud-ia-et-quantique", "prog": "424", "source": "Sample POC"},
    "849441522": {"theme": "levier-:-composants-cloud-ia-et-quantique", "prog": "424", "source": "Sample POC"},
    "850415290": {"theme": "2.-leader-de-l-hydrogene-vert", "prog": "424", "source": "Sample POC"},
    "831241179": {"theme": "9.-nouvelle-aventure-spatiale", "prog": "424", "source": "Sample POC"},
    "788658946": {"theme": "5.-premier-avion-bas-carbone", "prog": "424", "source": "Sample POC"},
    "794598813": {"theme": "7.-production-de-biomedicaments-et-dispositifs-medicaux", "prog": "424", "source": "Sample POC"}
}

def get_latest_sirene_url():
    print("Recherche de la dernière URL du StockUniteLegale sur data.gouv.fr...")
    resp = requests.get(DATA_GOUV_API)
    resp.raise_for_status()
    data = resp.json()
    for resource in data.get("resources", []):
        title = resource.get("title", "").lower()
        url = resource.get("url", "")
        if title.startswith("sirene : fichier stockunitelegale") and "historique" not in title and url.endswith(".zip"):
            return url
    raise Exception("URL StockUniteLegale non trouvée.")

def download_sirene_zip(url, dest_path):
    print(f"Téléchargement du fichier (environ 1.5 Go) : {url}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)

def main():
    print("Extraction des données depuis l'open data INSEE Base Sirene...")
    
    # 1. On récupère les SIREN depuis la base des projets (pour rendre l'extraction Sirene Dynamique)
    benef_file = os.path.join(DATA_DIR, "project_beneficiaries.json")
    if os.path.exists(benef_file):
        with open(benef_file, "r") as f:
            benefs = json.load(f)
            for b in benefs:
                if b.get("siren") and len(b.get("siren")) == 9:
                    siren = b["siren"]
                    if siren not in TARGET_COMPANIES:
                        TARGET_COMPANIES[siren] = {
                            "theme": "à_qualifier", 
                            "prog": "",
                            "source": "Project Dataset (ADEME/CDC)"
                        }

    os.makedirs(os.path.dirname(RAW_FILE), exist_ok=True)
    if not os.path.exists(RAW_FILE):
        url = get_latest_sirene_url()
        download_sirene_zip(url, RAW_FILE)
    else:
        print("Fichier Sirene ZIP déjà présent en cache.")
        
    companies = []
    naf_codes_seen = {}
    
    print(f"Parsing du CSV StockUniteLegale pour {len(TARGET_COMPANIES)} SIRENs cibles...")
    
    with zipfile.ZipFile(RAW_FILE) as z:
        csv_filename = [name for name in z.namelist() if name.endswith('.csv')][0]
        
        with z.open(csv_filename) as f:
            text_f = io.TextIOWrapper(f, encoding='utf-8')
            reader = csv.DictReader(text_f)
            
            count = 0
            for row in reader:
                count += 1
                if count % 1000000 == 0:
                    print(f"  ... {count} lignes analysées, {len(companies)} trouvées")
                
                siren = row.get("siren")
                if siren in TARGET_COMPANIES:
                    target_info = TARGET_COMPANIES[siren]
                    naf_code = row.get("activitePrincipaleUniteLegale", "Inconnu")
                    
                    themes = [target_info["theme"]] if target_info["theme"] != "à_qualifier" else []
                    progs = [target_info["prog"]] if target_info["prog"] else []
                    
                    companies.append({
                        "companyId": f"siren-{siren}",
                        "siren": siren,
                        "denominationUniteLegale": row.get("denominationUniteLegale", ""),
                        "nomUniteLegale": row.get("nomUniteLegale", ""),
                        "prenom1UniteLegale": row.get("prenom1UniteLegale", ""),
                        "categorieJuridiqueUniteLegale": row.get("categorieJuridiqueUniteLegale", ""),
                        "activitePrincipaleUniteLegale": naf_code,
                        "nomenclatureActivitePrincipaleUniteLegale": row.get("nomenclatureActivitePrincipaleUniteLegale", ""),
                        "etatAdministratifUniteLegale": row.get("etatAdministratifUniteLegale", ""),
                        "dateCreationUniteLegale": row.get("dateCreationUniteLegale", ""),
                        # Nouveautés : Adresse depuis Sirene pour la dimension Territoriale
                        "adresseSiege": "Inconnue", # Il faudrait utiliser le fichier StockEtablissement pour les adresses, le UnitéLégale n'en a pas
                        "relatedThemeIds": themes,
                        "relatedProgrammeCodes": progs,
                        "source": target_info["source"],
                        "confidenceScore": 1.0
                    })
                    
                    if naf_code not in naf_codes_seen:
                        naf_codes_seen[naf_code] = {
                            "nafCode": naf_code,
                            "nafLabel": "Inconnu (issu du flux CSV)",
                            "confidenceScore": 0.90
                        }
                            
                    if len(companies) >= len(TARGET_COMPANIES):
                        print("✅ Toutes les entreprises cibles ont été trouvées ! Fin du streaming.")
                        break

    with open(os.path.join(DATA_DIR, "companies.json"), "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)
        
    with open(os.path.join(DATA_DIR, "naf_codes.json"), "w", encoding="utf-8") as f:
        json.dump(list(naf_codes_seen.values()), f, indent=2, ensure_ascii=False)
        
    print(f"✅ Exporté dans data/companies.json")

if __name__ == "__main__":
    main()
