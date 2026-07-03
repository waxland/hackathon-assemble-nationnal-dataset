import json
import os

def mock_naf_mapping():
    """
    Simule une table de correspondance heuristique entre Thèmes France 2030 et Codes NAF.
    """
    return [
        {
            "nafCode": "20.11Z",
            "nafLabel": "Fabrication de gaz industriels",
            "relatedThemeIds": ["investissements-strategiques"], # par ex. pour l'hydrogène
            "confidenceScore": 0.8
        },
        {
            "nafCode": "62.01Z",
            "nafLabel": "Programmation informatique",
            "relatedThemeIds": ["ecosystemes-d-innovation", "modernisation-des-entreprises"],
            "confidenceScore": 0.7
        },
        {
            "nafCode": "72.19Z",
            "nafLabel": "Recherche-développement en autres sciences physiques et naturelles",
            "relatedThemeIds": ["recherche", "valorisation-de-la-recherche"],
            "confidenceScore": 0.9
        }
    ]

def main():
    print("Mapping des codes NAF...")
    
    naf_codes = mock_naf_mapping()
    
    os.makedirs("data", exist_ok=True)
    output_path = "data/naf_codes.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(naf_codes, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(naf_codes)} codes NAF mappés dans {output_path}")

if __name__ == "__main__":
    main()
