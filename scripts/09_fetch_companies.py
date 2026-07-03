import json
import os
import requests
import time

KNOWN_LAUREATES = [
    {"name": "VERKOR", "theme": "4.-vehicules-electriques-et-hybrides", "prog": "424"},
    {"name": "YNSECT", "theme": "6.-alimentation-saine-durable-et-tracable", "prog": "424"},
    {"name": "MISTRAL AI", "theme": "levier-:-composants-cloud-ia-et-quantique", "prog": "424"},
    {"name": "PASQAL", "theme": "levier-:-composants-cloud-ia-et-quantique", "prog": "424"},
    {"name": "LHYFE", "theme": "2.-leader-de-l-hydrogene-vert", "prog": "424"},
    {"name": "EXOTRAIL", "theme": "9.-nouvelle-aventure-spatiale", "prog": "424"},
    {"name": "FLYING WHALES", "theme": "5.-premier-avion-bas-carbone", "prog": "424"},
    {"name": "DOCTOLIB", "theme": "7.-production-de-biomedicaments-et-dispositifs-medicaux", "prog": "424"}
]

def search_company_with_retry(name, max_retries=3):
    url = f"https://recherche-entreprises.api.gouv.fr/search?q={name}&per_page=1"
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("results"):
                    return data["results"][0]
                return None
            elif response.status_code == 429: # Too Many Requests
                print(f"    ⚠️ Rate limit atteint. Attente avant retry {attempt+1}/{max_retries}...")
                time.sleep(2 ** attempt) # Exponential backoff
            else:
                break
        except Exception as e:
            print(f"    ⚠️ Erreur réseau: {e}")
            time.sleep(1)
    return None

def main():
    print("Recherche des entreprises avec mécanisme de Retry (API Sirene)...")
    companies = []
    naf_codes_seen = {}
    
    for l in KNOWN_LAUREATES:
        print(f" -> Interrogation pour {l['name']}...")
        result = search_company_with_retry(l["name"])
        
        if result:
            naf_code = result.get("activite_principale", "Inconnu")
            companies.append({
                "companyId": f"siren-{result['siren']}",
                "companyName": result["nom_complet"],
                "siren": result["siren"],
                "nafCode": naf_code,
                "relatedThemeIds": [l["theme"]],
                "relatedProgrammeCodes": [l["prog"]],
                "source": "French Tech 2030 / France 2030 Lauréat",
                "confidenceScore": 0.95
            })
            if naf_code not in naf_codes_seen:
                naf_codes_seen[naf_code] = {
                    "nafCode": naf_code,
                    "nafLabel": result.get("libelle_activite_principale", "Inconnu"),
                    "relatedThemeIds": [l["theme"]],
                    "confidenceScore": 0.90
                }
            else:
                if l["theme"] not in naf_codes_seen[naf_code]["relatedThemeIds"]:
                    naf_codes_seen[naf_code]["relatedThemeIds"].append(l["theme"])
        time.sleep(0.5) 
        
    os.makedirs("data", exist_ok=True)
    with open("data/companies.json", "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)
    with open("data/naf_codes.json", "w", encoding="utf-8") as f:
        json.dump(list(naf_codes_seen.values()), f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(companies)} entreprises fiabilisées sauvegardées.")

if __name__ == "__main__":
    main()
