import json
import os
import requests
import time

# Liste de startups emblématiques soutenues par France 2030 (French Tech 2030 / AAP)
# Associées à nos mots-clés enrichis.
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

def search_company(name):
    url = f"https://recherche-entreprises.api.gouv.fr/search?q={name}&per_page=1"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                return data["results"][0]
    except Exception as e:
        print(f"Erreur API pour {name}: {e}")
    return None

def main():
    print("Recherche des entreprises (API Sirene) et extraction de leurs codes NAF...")
    
    companies = []
    naf_codes_seen = {}
    
    for l in KNOWN_LAUREATES:
        print(f" -> Interrogation pour {l['name']}...")
        result = search_company(l["name"])
        
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
            
            # Stockage des NAF codes pour le référentiel
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
                    
        time.sleep(0.5) # respect du rate limiting
        
    os.makedirs("data", exist_ok=True)
    
    out_companies = "data/companies.json"
    with open(out_companies, "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)
        
    out_naf = "data/naf_codes.json"
    with open(out_naf, "w", encoding="utf-8") as f:
        json.dump(list(naf_codes_seen.values()), f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(companies)} entreprises fiabilisées sauvegardées dans {out_companies}")
    print(f"✅ {len(naf_codes_seen)} codes NAF uniques sauvegardés dans {out_naf}")

if __name__ == "__main__":
    main()
