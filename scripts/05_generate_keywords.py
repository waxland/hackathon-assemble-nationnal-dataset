import json
import os
import unicodedata

def generate_id(name):
    name = name.lower().replace("'", "-").replace(" ", "-").replace(",", "")
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    return name

def main():
    print("Génération des mots-clés depuis config/taxonomy.json...")
    
    with open("config/taxonomy.json", "r", encoding="utf-8") as f:
        taxonomy = json.load(f)

    keywords = []
    
    for prog_code, themes_data in taxonomy.items():
        for theme_name, kw_list in themes_data.items():
            theme_id = generate_id(theme_name)
            
            for kw in kw_list:
                kw_id = f"kw-{theme_id[:15]}-{generate_id(kw)}"
                keywords.append({
                    "keywordId": kw_id,
                    "label": kw,
                    "type": "technology" if "tech" in kw.lower() else "concept",
                    "relatedThemeId": theme_id,
                    "relatedProgrammes": [prog_code],
                    "synonyms": [],
                    "confidenceScore": 0.95
                })
            
    os.makedirs("data", exist_ok=True)
    output_path = "data/keywords.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(keywords, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(keywords)} mots-clés enrichis générés dans {output_path}")

if __name__ == "__main__":
    main()
