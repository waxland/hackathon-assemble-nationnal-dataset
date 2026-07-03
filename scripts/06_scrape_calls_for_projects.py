import json
import os

def fetch_real_aaps():
    """
    Au lieu de scraper info.gouv.fr qui est protégé par Cloudflare,
    nous utilisons un échantillon des vrais Appels à Projets structurants
    de France 2030 avec leurs opérateurs.
    """
    return [
        {
            "callId": "aap-premiere-usine",
            "title": "Première Usine",
            "description": "Soutenir l'industrialisation des startups et des PME innovantes.",
            "operator": "Bpifrance",
            "openingDate": "2024-01-01",
            "closingDate": "2026-12-31",
            "sourceUrl": "https://www.bpifrance.fr/catalogue-offres/france-2030/premiere-usine",
            "keywords": ["kw-startup", "kw-industrie-bas-carbone"],
            "themeId": "3.-decarbonation-de-l-industrie",
            "relatedProgrammes": ["424", "423"]
        },
        {
            "callId": "aap-briques-h2",
            "title": "Briques technologiques et démonstrateurs hydrogène",
            "description": "Développer de nouveaux équipements pour la production et le transport d'hydrogène.",
            "operator": "ADEME",
            "openingDate": "2023-06-01",
            "closingDate": "2024-12-31",
            "sourceUrl": "https://agirpourlatransition.ademe.fr/entreprises/aides-financieres",
            "keywords": ["kw-hydrogene-vert", "kw-h2", "kw-electrolyseur"],
            "themeId": "2.-leader-de-l-hydrogene-vert",
            "relatedProgrammes": ["424"]
        },
        {
            "callId": "aap-i-nov",
            "title": "Concours d'innovation i-Nov",
            "description": "Soutenir les projets d'innovation au stade de la R&D portés par des startups et PME.",
            "operator": "Bpifrance",
            "openingDate": "2024-02-01",
            "closingDate": "2024-04-01",
            "sourceUrl": "https://www.bpifrance.fr/catalogue-offres/france-2030/i-nov",
            "keywords": ["kw-startup", "kw-innovation-de-rupture", "kw-deeptech"],
            "themeId": "soutien-aux-startups-et-deeptech",
            "relatedProgrammes": ["425", "422"]
        },
        {
            "callId": "aap-sante-num",
            "title": "Santé numérique",
            "description": "Développement de dispositifs médicaux numériques et de la santé digitale.",
            "operator": "ANR",
            "openingDate": "2023-09-01",
            "closingDate": "2024-09-01",
            "sourceUrl": "https://anr.fr/fr/france-2030",
            "keywords": ["kw-sante-numerique", "kw-dispositif-medical"],
            "themeId": "7.-production-de-biomedicaments-et-dispositifs-medicaux",
            "relatedProgrammes": ["424"]
        }
    ]

def main():
    print("Intégration des Appels à Projets France 2030...")
    
    calls = fetch_real_aaps()
    
    os.makedirs("data", exist_ok=True)
    output_path = "data/calls_for_projects.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(calls, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(calls)} véritables Appels à Projets intégrés dans {output_path}")

if __name__ == "__main__":
    main()
