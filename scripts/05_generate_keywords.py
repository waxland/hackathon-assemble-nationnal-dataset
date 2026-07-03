import json
import os
import unicodedata

# Dictionnaire riche de mots-clés par Thématique ID (basé sur le script 04)
KEYWORDS_RICH_MAPPING = {
    "1.-petits-reacteurs-nucleaires-innovants-(smr)": ["SMR", "petits réacteurs modulaires", "nucléaire", "EPR", "réacteur nucléaire", "gestion des déchets radioactifs"],
    "2.-leader-de-l-hydrogene-vert": ["hydrogène vert", "hydrogène décarboné", "électrolyseur", "pile à combustible", "gigafactory hydrogène", "H2"],
    "3.-decarbonation-de-l-industrie": ["décarbonation", "industrie bas-carbone", "capture carbone", "efficacité énergétique industrielle", "chaleur bas-carbone", "CCUS"],
    "4.-vehicules-electriques-et-hybrides": ["véhicule électrique", "batteries", "gigafactory de batteries", "borne de recharge", "véhicule hybride", "mobilité durable"],
    "5.-premier-avion-bas-carbone": ["avion bas-carbone", "aéronautique décarbonée", "carburant d'aviation durable", "SAF", "moteur à hydrogène"],
    "6.-alimentation-saine-durable-et-tracable": ["alimentation durable", "agriculture de précision", "agroécologie", "foodtech", "agritech", "protéines alternatives", "traçabilité alimentaire"],
    "7.-production-de-biomedicaments-et-dispositifs-medicaux": ["biomédicament", "biothérapie", "santé numérique", "dispositif médical", "thérapie génique", "healthtech"],
    "8.-production-de-contenus-culturels-et-creatifs": ["industries culturelles et créatives", "ICC", "métavers", "studios de tournage", "effets visuels", "jeux vidéo", "billetterie"],
    "9.-nouvelle-aventure-spatiale": ["spatial", "micro-lanceurs", "constellation de satellites", "new space", "orbite", "CNES"],
    "10.-exploration-des-fonds-marins": ["fonds marins", "grands fonds marins", "exploration océanique", "robotique sous-marine", "AUV", "ROV"],
    "levier-:-composants-cloud-ia-et-quantique": ["intelligence artificielle", "IA", "quantique", "ordinateur quantique", "cloud souverain", "semi-conducteurs", "composants électroniques", "puces électroniques"],
    "soutien-aux-startups-et-deeptech": ["startup", "deeptech", "licorne", "innovation de rupture", "levée de fonds"],
    "poles-et-territoires-d-innovation": ["pôles de compétitivité", "territoires d'innovation", "incubateur", "SATT", "écosystème d'innovation"],
    "soutien-a-la-french-tech": ["French Tech", "mission French Tech", "French Tech 2030", "Next40", "FT120"]
}

def generate_id(name):
    name = name.lower().replace("'", "-").replace(" ", "-")
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    return name

def main():
    print("Génération du référentiel des mots-clés enrichis...")
    
    themes_path = "data/themes.json"
    if not os.path.exists(themes_path):
        print("❌ themes.json manquant.")
        return
        
    with open(themes_path, "r", encoding="utf-8") as f:
        themes = json.load(f)
    theme_programs = {t["themeId"]: t["relatedProgrammes"] for t in themes}

    keywords = []
    
    for theme_id, kw_list in KEYWORDS_RICH_MAPPING.items():
        progs = theme_programs.get(theme_id, [])
        if not progs:
            print(f"⚠️ Attention : le thème '{theme_id}' n'a pas été trouvé dans themes.json")
            
        for kw in kw_list:
            kw_id = f"kw-{generate_id(kw)}"
            keywords.append({
                "keywordId": kw_id,
                "label": kw,
                "type": "technology" if "tech" in kw.lower() else "concept",
                "relatedThemeId": theme_id,
                "relatedProgrammes": progs,
                "synonyms": [],
                "confidenceScore": 0.95
            })
            
    output_path = "data/keywords.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(keywords, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(keywords)} mots-clés enrichis générés dans {output_path}")

if __name__ == "__main__":
    main()
