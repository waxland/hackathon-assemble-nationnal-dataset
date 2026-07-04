import json
import os
import hashlib

def get_hash_id(source_id, target_id, ctype):
    """Génère un UUID MD5 déterministe pour éviter les doublons instables."""
    s = f"{source_id}_{target_id}_{ctype}".encode('utf-8')
    return "corr-" + hashlib.md5(s).hexdigest()[:8]

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def main():
    print("Génération de la table plate des corrélations (IDs déterministes)...")
    
    budget_lines = load_json("data/budget_lines.json")
    green_budget_lines = load_json("data/green_budget_lines.json")
    themes = load_json("data/themes.json")
    calls = load_json("data/calls_for_projects.json")
    mentions = load_json("data/parliament_mentions.json")
    companies = load_json("data/companies.json")
    
    correlations = []
    
    for bl in budget_lines:
        cid = get_hash_id(bl.get("programmeCode"), bl.get("id"), "finance")
        correlations.append({
            "correlationId": cid,
            "sourceEntityType": "programme",
            "sourceEntityId": bl.get("programmeCode"),
            "targetEntityType": "budgetLine",
            "targetEntityId": bl.get("id"),
            "correlationType": "finance",
            "confidenceScore": 1.0,
            "evidenceSource": "budget_lines.json",
            "validationStatus": "validated"
        })
        
    for gbl in green_budget_lines:
        cid = get_hash_id(gbl.get("programmeCode"), gbl.get("id"), "green_finance")
        correlations.append({
            "correlationId": cid,
            "sourceEntityType": "programme",
            "sourceEntityId": gbl.get("programmeCode"),
            "targetEntityType": "greenBudgetLine",
            "targetEntityId": gbl.get("id"),
            "correlationType": "green_finance",
            "confidenceScore": 1.0,
            "evidenceSource": "green_budget_lines.json",
            "validationStatus": "validated"
        })
        
    for t in themes:
        for prog in t.get("relatedProgrammes", []):
            cid = get_hash_id(prog, t.get("themeId"), "thematic_mapping")
            correlations.append({
                "correlationId": cid,
                "sourceEntityType": "programme",
                "sourceEntityId": prog,
                "targetEntityType": "theme",
                "targetEntityId": t.get("themeId"),
                "correlationType": "thematic_mapping",
                "confidenceScore": t.get("confidenceScore", 0.8),
                "evidenceSource": "themes.json",
                "validationStatus": "validated"
            })
            
    for call in calls:
        if call.get("themeId"):
            cid = get_hash_id(call.get("callId"), call.get("themeId"), "call_classification")
            correlations.append({
                "correlationId": cid,
                "sourceEntityType": "callForProject",
                "sourceEntityId": call.get("callId"),
                "targetEntityType": "theme",
                "targetEntityId": call.get("themeId"),
                "correlationType": "call_classification",
                "confidenceScore": 0.9,
                "evidenceSource": "calls_for_projects.json",
                "validationStatus": "validated"
            })
            
    for m in mentions:
        if m.get("relatedThemeId"):
            cid = get_hash_id(m.get("mentionId"), m.get("relatedThemeId"), "parliamentary_debate")
            correlations.append({
                "correlationId": cid,
                "sourceEntityType": "parliamentMention",
                "sourceEntityId": m.get("mentionId"),
                "targetEntityType": "theme",
                "targetEntityId": m.get("relatedThemeId"),
                "correlationType": "parliamentary_debate",
                "confidenceScore": m.get("confidenceScore", 0.8),
                "evidenceSource": "parliament_mentions.json",
                "validationStatus": "validated"
            })
            
    for c in companies:
        for tid in c.get("relatedThemeIds", []):
            cid = get_hash_id(c.get("companyId"), tid, "company_activity")
            correlations.append({
                "correlationId": cid,
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
    
    # Éliminer d'éventuels doublons
    unique_correlations = {c["correlationId"]: c for c in correlations}.values()
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(list(unique_correlations), f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(unique_correlations)} corrélations générées dans {output_path}")

if __name__ == "__main__":
    main()
