import json
import os
import uuid

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def main():
    print("Génération de la table plate des corrélations...")
    
    # Charger les référentiels
    budget_lines = load_json("data/budget_lines.json")
    themes = load_json("data/themes.json")
    calls = load_json("data/calls_for_projects.json")
    mentions = load_json("data/parliament_mentions.json")
    companies = load_json("data/companies.json")
    
    correlations = []
    
    # Corrélation: Programme -> Budget Line
    for bl in budget_lines:
        correlations.append({
            "correlationId": f"corr-{uuid.uuid4().hex[:8]}",
            "sourceEntityType": "programme",
            "sourceEntityId": bl.get("programmeCode"),
            "targetEntityType": "budgetLine",
            "targetEntityId": bl.get("id"),
            "correlationType": "finance",
            "confidenceScore": 1.0,
            "evidenceSource": "budget_lines.json",
            "validationStatus": "validated"
        })
        
    # Corrélation: Programme -> Theme
    for t in themes:
        for prog in t.get("relatedProgrammes", []):
            correlations.append({
                "correlationId": f"corr-{uuid.uuid4().hex[:8]}",
                "sourceEntityType": "programme",
                "sourceEntityId": prog,
                "targetEntityType": "theme",
                "targetEntityId": t.get("themeId"),
                "correlationType": "thematic_mapping",
                "confidenceScore": t.get("confidenceScore", 0.8),
                "evidenceSource": "themes.json",
                "validationStatus": "validated"
            })
            
    # Corrélation: Call -> Theme & Programme
    for call in calls:
        if call.get("themeId"):
            correlations.append({
                "correlationId": f"corr-{uuid.uuid4().hex[:8]}",
                "sourceEntityType": "callForProject",
                "sourceEntityId": call.get("callId"),
                "targetEntityType": "theme",
                "targetEntityId": call.get("themeId"),
                "correlationType": "call_classification",
                "confidenceScore": 0.9,
                "evidenceSource": "calls_for_projects.json",
                "validationStatus": "validated"
            })
        for prog in call.get("relatedProgrammes", []):
            correlations.append({
                "correlationId": f"corr-{uuid.uuid4().hex[:8]}",
                "sourceEntityType": "callForProject",
                "sourceEntityId": call.get("callId"),
                "targetEntityType": "programme",
                "targetEntityId": prog,
                "correlationType": "call_funding",
                "confidenceScore": 0.8,
                "evidenceSource": "calls_for_projects.json",
                "validationStatus": "to_validate"
            })
            
    # Corrélation: Mention -> Theme & Programme
    for m in mentions:
        if m.get("relatedThemeId"):
            correlations.append({
                "correlationId": f"corr-{uuid.uuid4().hex[:8]}",
                "sourceEntityType": "parliamentMention",
                "sourceEntityId": m.get("mentionId"),
                "targetEntityType": "theme",
                "targetEntityId": m.get("relatedThemeId"),
                "correlationType": "parliamentary_debate",
                "confidenceScore": m.get("confidenceScore", 0.8),
                "evidenceSource": "parliament_mentions.json",
                "validationStatus": "validated"
            })
            
    # Corrélation: Company -> Theme & Programme
    for c in companies:
        for tid in c.get("relatedThemeIds", []):
            correlations.append({
                "correlationId": f"corr-{uuid.uuid4().hex[:8]}",
                "sourceEntityType": "company",
                "sourceEntityId": c.get("companyId"),
                "targetEntityType": "theme",
                "targetEntityId": tid,
                "correlationType": "company_activity",
                "confidenceScore": c.get("confidenceScore", 0.8),
                "evidenceSource": "companies.json",
                "validationStatus": "validated"
            })
            
    os.makedirs("data", exist_ok=True)
    output_path = "data/correlations.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(correlations, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(correlations)} corrélations générées dans {output_path}")

if __name__ == "__main__":
    main()
