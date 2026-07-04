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

def get_validation_status(score):
    if score >= 0.9:
        return "validated"
    return "to_validate"

def main():
    print("Génération de la table plate des corrélations (IDs déterministes, Evidence Block)...")
    
    budget_lines = load_json("data/budget_lines.json")
    green_budget_lines = load_json("data/green_budget_lines.json")
    themes = load_json("data/themes.json")
    calls = load_json("data/calls_for_projects.json")
    mentions = load_json("data/parliament_mentions.json")
    companies = load_json("data/companies.json")
    
    # On ajoute aussi les corrélations externes qui pourraient déjà exister (ex: générées par ADEME / CDC)
    existing_correlations = load_json("data/correlations.json")
    
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
            "evidence": {
                "sourceUrl": bl.get("sourceUrl", ""),
                "matchMethod": "exact_programme_code",
                "matchedValue": bl.get("programmeCode")
            },
            "validationStatus": get_validation_status(1.0)
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
            "evidence": {
                "sourceUrl": gbl.get("sourceUrl", ""),
                "matchMethod": "exact_programme_code",
                "matchedValue": gbl.get("programmeCode")
            },
            "validationStatus": get_validation_status(1.0)
        })
        
    for t in themes:
        for prog in t.get("relatedProgrammes", []):
            conf = t.get("confidenceScore", 0.8)
            cid = get_hash_id(prog, t.get("themeId"), "thematic_mapping")
            correlations.append({
                "correlationId": cid,
                "sourceEntityType": "programme",
                "sourceEntityId": prog,
                "targetEntityType": "theme",
                "targetEntityId": t.get("themeId"),
                "correlationType": "thematic_mapping",
                "confidenceScore": conf,
                "evidenceSource": "themes.json",
                "evidence": {
                    "sourceUrl": "config/taxonomy.json",
                    "matchMethod": "manual_expert_mapping",
                    "matchedValue": t.get("themeId")
                },
                "validationStatus": get_validation_status(conf)
            })
            
    for call in calls:
        if call.get("themeId"):
            conf = 0.9 if call.get("dataCompleteness") == "sample" else 1.0
            cid = get_hash_id(call.get("callId"), call.get("themeId"), "call_classification")
            correlations.append({
                "correlationId": cid,
                "sourceEntityType": "callForProject",
                "sourceEntityId": call.get("callId"),
                "targetEntityType": "theme",
                "targetEntityId": call.get("themeId"),
                "correlationType": "call_classification",
                "confidenceScore": conf,
                "evidenceSource": "calls_for_projects.json",
                "evidence": {
                    "sourceUrl": call.get("sourceUrl", ""),
                    "matchMethod": "keyword_matching",
                    "matchedValue": call.get("themeId")
                },
                "validationStatus": get_validation_status(conf)
            })
            
    for m in mentions:
        if m.get("relatedThemeId"):
            conf = m.get("confidenceScore", 0.8)
            cid = get_hash_id(m.get("mentionId"), m.get("relatedThemeId"), "parliamentary_debate")
            correlations.append({
                "correlationId": cid,
                "sourceEntityType": "parliamentMention",
                "sourceEntityId": m.get("mentionId"),
                "targetEntityType": "theme",
                "targetEntityId": m.get("relatedThemeId"),
                "correlationType": "parliamentary_debate",
                "confidenceScore": conf,
                "evidenceSource": "parliament_mentions.json",
                "evidence": {
                    "sourceUrl": m.get("sourceUrl", ""),
                    "matchMethod": m.get("matchMethod", "keyword_with_context"),
                    "matchedValue": m.get("matchedKeyword", "")
                },
                "validationStatus": get_validation_status(conf)
            })
            
    for c in companies:
        for tid in c.get("relatedThemeIds", []):
            conf = c.get("confidenceScore", 0.8)
            cid = get_hash_id(c.get("companyId"), tid, "company_activity")
            correlations.append({
                "correlationId": cid,
                "sourceEntityType": "company",
                "sourceEntityId": c.get("companyId"),
                "targetEntityType": "theme",
                "targetEntityId": tid,
                "correlationType": "company_activity",
                "confidenceScore": conf,
                "evidenceSource": "companies.json",
                "evidence": {
                    "sourceUrl": "https://recherche-entreprises.api.gouv.fr/",
                    "matchMethod": "inherited_from_project_or_laureate",
                    "matchedValue": c.get("source", "")
                },
                "validationStatus": get_validation_status(conf)
            })
            
    # Ajouter les corrélations qui n'ont pas été regénérées ici (ex: Project -> Beneficiary)
    # en s'assurant qu'elles aient le nouveau bloc 'evidence' (rétrocompatibilité)
    # Éliminer d'éventuels doublons
    # Important : on itère sur correlations en préservant le dernier élément vu (qui est ec). 
    # Mieux vaut inverser l'ordre pour donner la priorité aux nouvelles générées ci-dessus !
    unique_correlations = {}
    
    # 1. On charge d'abord les anciennes (elles seront écrasées par les nouvelles si même ID)
    for ec in existing_correlations:
        if "evidence" not in ec:
            ec["evidence"] = {
                "sourceUrl": "",
                "matchMethod": "legacy",
                "matchedValue": ""
            }
            ec["validationStatus"] = get_validation_status(ec.get("confidenceScore", 0.5))
        unique_correlations[ec["correlationId"]] = ec
        
    # 2. On charge les nouvelles (fraîches) par-dessus
    for c in correlations:
        unique_correlations[c["correlationId"]] = c
        
    os.makedirs("data", exist_ok=True)
    output_path = "data/correlations.json"
        
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(list(unique_correlations.values()), f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(unique_correlations)} corrélations générées dans {output_path}")

if __name__ == "__main__":
    main()
