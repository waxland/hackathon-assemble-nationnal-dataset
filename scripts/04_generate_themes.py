import json
import os
import unicodedata

def generate_theme_id(name):
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
        "confidenceScore": 1.0
    }

def main():
    print("Génération de la taxonomie depuis config/taxonomy.json...")
    
    with open("config/taxonomy.json", "r", encoding="utf-8") as f:
        taxonomy_data = json.load(f)
        
    taxonomy = taxonomy_data.get("programmes", {})
    
    themes_dict = {}
    
    for prog_code, themes_data in taxonomy.items():
        for theme_name, theme_details in themes_data.items():
            tid = generate_theme_id(theme_name)
            if tid not in themes_dict:
                themes_dict[tid] = format_theme(tid, theme_name, prog_code)
                themes_dict[tid]["confidenceScore"] = theme_details.get("mappingConfidence", 0.9)
            else:
                if prog_code not in themes_dict[tid]["relatedProgrammes"]:
                    themes_dict[tid]["relatedProgrammes"].append(prog_code)
                    
    themes = list(themes_dict.values())
    
    os.makedirs("data", exist_ok=True)
    output_path = "data/themes.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(themes, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(themes)} thématiques officielles générées dans {output_path}")

if __name__ == "__main__":
    main()
