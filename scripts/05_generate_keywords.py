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
        taxonomy_data = json.load(f)
        
    taxonomy = taxonomy_data.get("programmes", {})

    keywords = []
    
    for prog_code, themes_data in taxonomy.items():
        for theme_name, theme_details in themes_data.items():
            theme_id = generate_id(theme_name)
            kw_list = theme_details.get("keywords", [])
            neg_kw_list = theme_details.get("negativeKeywords", [])
            
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
                
            for nkw in neg_kw_list:
                kw_id = f"nkw-{theme_id[:15]}-{generate_id(nkw)}"
                keywords.append({
                    "keywordId": kw_id,
                    "label": nkw,
                    "type": "exclusion",
                    "relatedThemeId": theme_id,
                    "relatedProgrammes": [prog_code],
                    "synonyms": [],
                    "confidenceScore": 1.0
                })
            

    # Déduplication
    unique_keywords = {}
    for kw in keywords:
        label = kw["label"].lower().strip()
        if label not in unique_keywords:
            unique_keywords[label] = kw
        else:
            # Fusion
            for prog in kw["relatedProgrammes"]:
                if prog not in unique_keywords[label]["relatedProgrammes"]:
                    unique_keywords[label]["relatedProgrammes"].append(prog)

    keywords = list(unique_keywords.values())

    os.makedirs("data", exist_ok=True)

    output_path = "data/keywords.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(keywords, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(keywords)} mots-clés enrichis générés dans {output_path}")

if __name__ == "__main__":
    main()
