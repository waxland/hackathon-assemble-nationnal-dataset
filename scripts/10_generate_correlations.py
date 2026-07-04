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
    print("Génération de la table plate des corrélations (P3.2: Enrichissement du Graphe)...")
    
    budget_lines = load_json("data/budget_lines.json")
    green_budget_lines = load_json("data/green_budget_lines.json")
    themes = load_json("data/themes.json")
    calls = load_json("data/calls_for_projects.json")
    mentions = load_json("data/parliament_mentions.json")
    companies = load_json("data/companies.json")
    keywords = load_json("data/keywords.json")
    projects = load_json("data/projects.json")
    territories = load_json("data/territories.json")
    beneficiaries = load_json("data/project_beneficiaries.json")
    
    # On ajoute aussi les corrélations externes qui pourraient déjà exister (ex: générées par ADEME / CDC / INPI)
    existing_correlations = load_json("data/correlations.json")
    
    correlations = []
    
    # programme -> budgetLine
    for bl in budget_lines:
        cid = get_hash_id(bl.get("programmeCode"), bl.get("id"), "programme_budgetLine")
        correlations.append({
            "correlationId": cid,
            "sourceEntityType": "programme",
            "sourceEntityId": bl.get("programmeCode"),
            "targetEntityType": "budgetLine",
            "targetEntityId": bl.get("id"),
            "correlationType": "programme_budgetLine",
            "confidenceScore": 1.0,
            "evidenceSource": "budget_lines.json",
            "evidence": {"sourceUrl": bl.get("sourceUrl", ""), "matchMethod": "exact_programme_code", "matchedValue": bl.get("programmeCode")},
            "validationStatus": get_validation_status(1.0)
        })
        
    # programme -> greenBudgetLine
    for gbl in green_budget_lines:
        cid = get_hash_id(gbl.get("programmeCode"), gbl.get("id"), "programme_greenBudgetLine")
        correlations.append({
            "correlationId": cid,
            "sourceEntityType": "programme",
            "sourceEntityId": gbl.get("programmeCode"),
            "targetEntityType": "greenBudgetLine",
            "targetEntityId": gbl.get("id"),
            "correlationType": "programme_greenBudgetLine",
            "confidenceScore": 1.0,
            "evidenceSource": "green_budget_lines.json",
            "evidence": {"sourceUrl": gbl.get("sourceUrl", ""), "matchMethod": "exact_programme_code", "matchedValue": gbl.get("programmeCode")},
            "validationStatus": get_validation_status(1.0)
        })
        
    # programme -> theme
    for t in themes:
        for prog in t.get("relatedProgrammes", []):
            conf = t.get("confidenceScore", 0.8)
            cid = get_hash_id(prog, t.get("themeId"), "programme_theme")
            correlations.append({
                "correlationId": cid,
                "sourceEntityType": "programme",
                "sourceEntityId": prog,
                "targetEntityType": "theme",
                "targetEntityId": t.get("themeId"),
                "correlationType": "programme_theme",
                "confidenceScore": conf,
                "evidenceSource": "themes.json",
                "evidence": {"sourceUrl": "config/taxonomy.json", "matchMethod": "manual_expert_mapping", "matchedValue": t.get("themeId")},
                "validationStatus": get_validation_status(conf)
            })
            
    # theme -> keyword
    for k in keywords:
        tid = k.get("relatedThemeId")
        if tid:
            conf = k.get("confidenceScore", 0.9)
            cid = get_hash_id(tid, k.get("keywordId"), "theme_keyword")
            correlations.append({
                "correlationId": cid,
                "sourceEntityType": "theme",
                "sourceEntityId": tid,
                "targetEntityType": "keyword",
                "targetEntityId": k.get("keywordId"),
                "correlationType": "theme_keyword",
                "confidenceScore": conf,
                "evidenceSource": "keywords.json",
                "evidence": {"sourceUrl": "config/taxonomy.json", "matchMethod": "manual_expert_mapping", "matchedValue": k.get("label")},
                "validationStatus": get_validation_status(conf)
            })
            
    # callForProject -> theme
    for call in calls:
        if call.get("themeId"):
            conf = 0.9 if call.get("dataCompleteness") == "sample" else 1.0
            cid = get_hash_id(call.get("callId"), call.get("themeId"), "callForProject_theme")
            correlations.append({
                "correlationId": cid,
                "sourceEntityType": "callForProject",
                "sourceEntityId": call.get("callId"),
                "targetEntityType": "theme",
                "targetEntityId": call.get("themeId"),
                "correlationType": "callForProject_theme",
                "confidenceScore": conf,
                "evidenceSource": "calls_for_projects.json",
                "evidence": {"sourceUrl": call.get("sourceUrl", ""), "matchMethod": "keyword_matching", "matchedValue": call.get("themeId")},
                "validationStatus": get_validation_status(conf)
            })
            
    # parliamentMention -> theme & parliamentMention -> programme
    for m in mentions:
        if m.get("relatedThemeId"):
            conf = m.get("confidenceScore", 0.8)
            cid = get_hash_id(m.get("mentionId"), m.get("relatedThemeId"), "parliamentMention_theme")
            correlations.append({
                "correlationId": cid,
                "sourceEntityType": "parliamentMention",
                "sourceEntityId": m.get("mentionId"),
                "targetEntityType": "theme",
                "targetEntityId": m.get("relatedThemeId"),
                "correlationType": "parliamentMention_theme",
                "confidenceScore": conf,
                "evidenceSource": "parliament_mentions.json",
                "evidence": {"sourceUrl": m.get("sourceUrl", ""), "matchMethod": m.get("matchMethod", "keyword_with_context"), "matchedValue": m.get("matchedKeyword", "")},
                "validationStatus": get_validation_status(conf)
            })
        if m.get("relatedProgrammeCode"):
            cid2 = get_hash_id(m.get("mentionId"), m.get("relatedProgrammeCode"), "parliamentMention_programme")
            correlations.append({
                "correlationId": cid2,
                "sourceEntityType": "parliamentMention",
                "sourceEntityId": m.get("mentionId"),
                "targetEntityType": "programme",
                "targetEntityId": m.get("relatedProgrammeCode"),
                "correlationType": "parliamentMention_programme",
                "confidenceScore": conf,
                "evidenceSource": "parliament_mentions.json",
                "evidence": {"sourceUrl": m.get("sourceUrl", ""), "matchMethod": m.get("matchMethod", "keyword_with_context"), "matchedValue": m.get("matchedKeyword", "")},
                "validationStatus": get_validation_status(conf)
            })
            
    # company -> theme & company -> nafCode
    for c in companies:
        for tid in c.get("relatedThemeIds", []):
            conf = c.get("confidenceScore", 0.8)
            cid = get_hash_id(c.get("companyId"), tid, "company_theme")
            correlations.append({
                "correlationId": cid,
                "sourceEntityType": "company",
                "sourceEntityId": c.get("companyId"),
                "targetEntityType": "theme",
                "targetEntityId": tid,
                "correlationType": "company_theme",
                "confidenceScore": conf,
                "evidenceSource": "companies.json",
                "evidence": {"sourceUrl": "https://recherche-entreprises.api.gouv.fr/", "matchMethod": "inherited_from_project_or_laureate", "matchedValue": c.get("source", "")},
                "validationStatus": get_validation_status(conf)
            })
        if c.get("activitePrincipaleUniteLegale"):
            cid2 = get_hash_id(c.get("companyId"), c.get("activitePrincipaleUniteLegale"), "company_nafCode")
            correlations.append({
                "correlationId": cid2,
                "sourceEntityType": "company",
                "sourceEntityId": c.get("companyId"),
                "targetEntityType": "nafCode",
                "targetEntityId": c.get("activitePrincipaleUniteLegale"),
                "correlationType": "company_nafCode",
                "confidenceScore": 1.0,
                "evidenceSource": "companies.json",
                "evidence": {"sourceUrl": "https://recherche-entreprises.api.gouv.fr/", "matchMethod": "exact_sirene_extract", "matchedValue": c.get("activitePrincipaleUniteLegale")},
                "validationStatus": "validated"
            })
            
    # beneficiary -> company (Reconciliation SIREN)
    for b in beneficiaries:
        if b.get("siren"):
            comp_id = f"siren-{b['siren']}"
            # On vérifie si l'entreprise existe bien dans la table (elle devrait)
            if any(c.get("companyId") == comp_id for c in companies):
                cid = get_hash_id(b.get("beneficiaryId"), comp_id, "beneficiary_company")
                correlations.append({
                    "correlationId": cid,
                    "sourceEntityType": "beneficiary",
                    "sourceEntityId": b.get("beneficiaryId"),
                    "targetEntityType": "company",
                    "targetEntityId": comp_id,
                    "correlationType": "beneficiary_company",
                    "confidenceScore": 0.95,
                    "evidenceSource": "project_beneficiaries.json",
                    "evidence": {"sourceUrl": "", "matchMethod": "exact_siren_match", "matchedValue": b['siren']},
                    "validationStatus": "validated"
                })

    # On charge d'abord les anciennes (elles seront écrasées par les nouvelles si même ID)
    unique_correlations = {}
    
    for ec in existing_correlations:
        if "evidence" not in ec:
            ec["evidence"] = {
                "sourceUrl": "",
                "matchMethod": "legacy",
                "matchedValue": ""
            }
            ec["validationStatus"] = get_validation_status(ec.get("confidenceScore", 0.5))
        unique_correlations[ec["correlationId"]] = ec
        
    for c in correlations:
        unique_correlations[c["correlationId"]] = c
        
    output_path = "data/correlations.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(list(unique_correlations.values()), f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(unique_correlations)} corrélations générées ou consolidées dans {output_path}")

if __name__ == "__main__":
    main()
