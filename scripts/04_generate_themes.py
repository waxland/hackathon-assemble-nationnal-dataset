import json
import os
import unicodedata

# 10 Objectifs officiels + Leviers transversaux de France 2030
THEMES_MAPPING = {
    # Programme 424 - Investissements stratégiques
    "424": [
        "1. Petits réacteurs nucléaires innovants (SMR)",
        "2. Leader de l'hydrogène vert",
        "3. Décarbonation de l'industrie",
        "4. Véhicules électriques et hybrides",
        "5. Premier avion bas-carbone",
        "6. Alimentation saine, durable et traçable",
        "7. Production de biomédicaments et dispositifs médicaux",
        "8. Production de contenus culturels et créatifs",
        "9. Nouvelle aventure spatiale",
        "10. Exploration des fonds marins",
        "Levier : Composants, Cloud, IA et Quantique"
    ],
    # Programme 425 - Écosystèmes d’innovation
    "425": [
        "Soutien aux startups et DeepTech",
        "Pôles et territoires d'innovation",
        "Soutien à la French Tech"
    ],
    # Programme 422 - Valorisation de la recherche
    "422": [
        "Valorisation de la recherche publique",
        "Transfert technologique"
    ],
    # Programme 423 - Modernisation
    "423": [
        "Modernisation de l'outil de production",
        "Digitalisation des PME-ETI"
    ],
    # Programme 421 - Recherche
    "421": [
        "Soutien de la recherche fondamentale",
        "Formation aux métiers d'avenir"
    ]
}

def generate_theme_id(name):
    # Génère un ID propre, ex: "1-petits-reacteurs-nucleaires-innovants-smr"
    name = name.lower().replace("'", "-").replace(" ", "-").replace(",", "")
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    return name

def format_theme(theme_id, theme_name, prog_code):
    return {
        "themeId": theme_id,
        "themeName": theme_name,
        "relatedProgrammes": [prog_code],
        "relatedBudgetLines": [],
        "keywords": [],
        "callsForProjects": [],
        "nafCodes": [],
        "companies": [],
        "parliamentMentions": [],
        "confidenceScore": 1.0 # 1.0 car c'est la vraie taxonomie France 2030 officielle
    }

def main():
    print("Génération de la véritable taxonomie France 2030...")
    themes_dict = {}
    
    for prog, theme_list in THEMES_MAPPING.items():
        for theme_name in theme_list:
            tid = generate_theme_id(theme_name)
            if tid not in themes_dict:
                themes_dict[tid] = format_theme(tid, theme_name, prog)
            else:
                if prog not in themes_dict[tid]["relatedProgrammes"]:
                    themes_dict[tid]["relatedProgrammes"].append(prog)
                    
    themes = list(themes_dict.values())
    
    os.makedirs("data", exist_ok=True)
    output_path = "data/themes.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(themes, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(themes)} thématiques officielles générées dans {output_path}")

if __name__ == "__main__":
    main()
