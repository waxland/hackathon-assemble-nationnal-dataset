import json
import os
import requests
import zipfile
import csv
import io

DATA_GOUV_API = "https://www.data.gouv.fr/api/1/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/"

TARGET_COMPANIES = {
    "888047792": {"theme": "4.-vehicules-electriques-et-hybrides", "prog": "424", "source": "French Tech 2030 / France 2030 Lauréat"},
    "534948617": {"theme": "6.-alimentation-saine-durable-et-tracable", "prog": "424", "source": "French Tech 2030 / France 2030 Lauréat"},
    "952418325": {"theme": "levier-:-composants-cloud-ia-et-quantique", "prog": "424", "source": "French Tech 2030 / France 2030 Lauréat"},
    "849441522": {"theme": "levier-:-composants-cloud-ia-et-quantique", "prog": "424", "source": "French Tech 2030 / France 2030 Lauréat"},
    "850415290": {"theme": "2.-leader-de-l-hydrogene-vert", "prog": "424", "source": "French Tech 2030 / France 2030 Lauréat"},
    "831241179": {"theme": "9.-nouvelle-aventure-spatiale", "prog": "424", "source": "French Tech 2030 / France 2030 Lauréat"},
    "788658946": {"theme": "5.-premier-avion-bas-carbone", "prog": "424", "source": "French Tech 2030 / France 2030 Lauréat"},
    "794598813": {"theme": "7.-production-de-biomedicaments-et-dispositifs-medicaux", "prog": "424", "source": "French Tech 2030 / France 2030 Lauréat"}
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
    print("Téléchargement terminé.")

def main():
    print("Extraction des données depuis l'open data INSEE Base Sirene...")
    os.makedirs("data/raw", exist_ok=True)
    zip_path = "data/raw/StockUniteLegale.zip"
    
    if not os.path.exists(zip_path):
        url = get_latest_sirene_url()
        download_sirene_zip(url, zip_path)
    else:
        print("Fichier Sirene ZIP déjà présent en cache.")
        
    companies = []
    naf_codes_seen = {}
    
    print("Parsing du CSV StockUniteLegale...")
    with zipfile.ZipFile(zip_path) as z:
        csv_filename = [name for name in z.namelist() if name.endswith('.csv')][0]
        
        with z.open(csv_filename) as f:
            text_f = io.TextIOWrapper(f, encoding='utf-8')
            reader = csv.DictReader(text_f)
            
            count = 0
            for row in reader:
                count += 1
                if count % 1000000 == 0:
                    print(f"  ... {count} lignes analysées")
                
                siren = row.get("siren")
                if siren in TARGET_COMPANIES:
                    target_info = TARGET_COMPANIES[siren]
                    naf_code = row.get("activitePrincipaleUniteLegale", "Inconnu")
                    
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
                        "relatedThemeIds": [target_info["theme"]],
                        "relatedProgrammeCodes": [target_info["prog"]],
                        "source": target_info["source"],
                        "confidenceScore": 1.0
                    })
                    
                    if naf_code not in naf_codes_seen:
                        naf_codes_seen[naf_code] = {
                            "nafCode": naf_code,
                            "nafLabel": "Inconnu (issu du flux CSV)",
                            "relatedThemeIds": [target_info["theme"]],
                            "confidenceScore": 0.90
                        }
                    else:
                        if target_info["theme"] not in naf_codes_seen[naf_code]["relatedThemeIds"]:
                            naf_codes_seen[naf_code]["relatedThemeIds"].append(target_info["theme"])
                            
                    if len(companies) == len(TARGET_COMPANIES):
                        print("✅ Toutes les entreprises cibles trouvées ! Fin du streaming.")
                        break

    with open("data/companies.json", "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)
    with open("data/naf_codes.json", "w", encoding="utf-8") as f:
        json.dump(list(naf_codes_seen.values()), f, indent=2, ensure_ascii=False)
        
    print(f"✅ Exporté dans data/companies.json")

if __name__ == "__main__":
    main()
