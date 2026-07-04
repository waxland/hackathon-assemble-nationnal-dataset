from lib.ids import generate_id
from lib.json_io import write_json_atomic, read_json

OUTPUT_FILE = "data/audit_documents.json"
OUTPUT_REC = "data/audit_recommendations.json"
OUTPUT_FINDINGS = "data/audit_findings.json"

RECOMMENDATIONS = [
    {
        "recommendationId": generate_id("rec", "ccomptes-neb-2026-france-2030", "1"),
        "auditDocumentId": "ccomptes-neb-2026-france-2030",
        "recommendationText": "Mettre en place un outil de suivi centralisé des décaissements réels par les opérateurs.",
        "issuer": "Cour des comptes",
        "targetOrganization": "SGPI",
        "sourcePage": 14,
        "status": "to_review"
    },
    {
        "recommendationId": generate_id("rec", "ccomptes-decarbonation-industrie-2026", "1"),
        "auditDocumentId": "ccomptes-decarbonation-industrie-2026",
        "recommendationText": "Conditionner les aides à la décarbonation à la publication d'un bilan GES audité.",
        "issuer": "Cour des comptes",
        "targetOrganization": "ADEME",
        "sourcePage": 45,
        "status": "to_review"
    }
]

FINDINGS = [
    {
        "findingId": generate_id("finding", "ccomptes-agences-programmes-2025", "1"),
        "auditDocumentId": "ccomptes-agences-programmes-2025",
        "findingType": "risk",
        "findingText": "Risque de chevauchement de compétences entre l'ANR et les nouvelles agences de programme thématiques.",
        "riskLevel": "high",
        "relatedProgrammeCodes": ["424"],
        "relatedThemeIds": ["soutien-de-la-recherche-fondamentale"],
        "sourcePage": 23,
        "evidenceSummary": "La Cour note une complexité administrative accrue.",
        "confidenceScore": 1.0
    }
]



AUDIT_DOCUMENTS = [
    {
        "auditDocumentId": "ccomptes-neb-2024-france-2030",
        "title": "Note d'execution budgetaire 2024 - Investir pour la France de 2030",
        "publisher": "Cour des comptes",
        "publicationDate": "2025-04",
        "documentType": "budget_execution_note",
        "sourceUrl": "https://www.ccomptes.fr/sites/default/files/2025-04/NEB-2024-Investir-pour-France-2030.pdf",
        "pdfUrl": "https://www.ccomptes.fr/sites/default/files/2025-04/NEB-2024-Investir-pour-France-2030.pdf",
        "publicationUrl": None,
        "relatedProgrammeCodes": ["421", "422", "423", "424", "425"],
        "relatedThemeIds": [],
        "sourcePages": [],
        "confidenceScore": 1.0,
        "validationStatus": "validated",
    },
    {
        "auditDocumentId": "ccomptes-neb-2026-france-2030",
        "title": "Note d'execution budgetaire 2025 - Investir pour la France de 2030",
        "publisher": "Cour des comptes",
        "publicationDate": "2026-04",
        "documentType": "budget_execution_note",
        "sourceUrl": "https://www.ccomptes.fr/sites/default/files/2026-04/NEB-2026-Investir-pour-France-2030.pdf",
        "pdfUrl": "https://www.ccomptes.fr/sites/default/files/2026-04/NEB-2026-Investir-pour-France-2030.pdf",
        "publicationUrl": None,
        "relatedProgrammeCodes": ["421", "422", "423", "424", "425"],
        "relatedThemeIds": [],
        "sourcePages": [],
        "confidenceScore": 1.0,
        "validationStatus": "validated",
    },
    {
        "auditDocumentId": "ccomptes-decarbonation-industrie-2026",
        "title": "Les aides a la decarbonation de l'industrie du plan de relance et de France 2030",
        "publisher": "Cour des comptes",
        "publicationDate": "2026-03-11",
        "documentType": "policy_evaluation_report",
        "sourceUrl": "https://www.ccomptes.fr/fr/publications/les-aides-la-decarbonation-de-lindustrie-du-plan-de-relance-et-de-france-2030",
        "pdfUrl": "https://www.ccomptes.fr/sites/default/files/2026-03/20260311-Aides-a-decarbonation-de-l-industrie-du-plan-de-relance-et-de-France-2030.pdf",
        "publicationUrl": "https://www.ccomptes.fr/fr/publications/les-aides-la-decarbonation-de-lindustrie-du-plan-de-relance-et-de-france-2030",
        "relatedProgrammeCodes": [],
        "relatedThemeIds": ["3.-decarbonation-de-l-industrie"],
        "sourcePages": [],
        "confidenceScore": 1.0,
        "validationStatus": "validated",
    },
    {
        "auditDocumentId": "ccomptes-aap-pia4-culture-2025",
        "title": "Les appels a projets du 4e programme d'investissement d'avenir (PIA4) sur l'experience augmentee du spectacle vivant et la numerisation du patrimoine",
        "publisher": "Cour des comptes",
        "publicationDate": "2025-10-21",
        "documentType": "final_observations",
        "sourceUrl": "https://www.ccomptes.fr/fr/publications/les-appels-projets-du-4e-programme-dinvestissement-davenir-pia4-sur-lexperience",
        "pdfUrl": "https://www.ccomptes.fr/sites/default/files/2025-10/20251015-S2025-1409-Appels-a-projets-4e-programme-investissement-avenir-PIA4.pdf",
        "publicationUrl": "https://www.ccomptes.fr/fr/publications/les-appels-projets-du-4e-programme-dinvestissement-davenir-pia4-sur-lexperience",
        "relatedProgrammeCodes": [],
        "relatedThemeIds": ["8.-production-de-contenus-culturels-et-creatifs"],
        "sourcePages": [],
        "confidenceScore": 1.0,
        "validationStatus": "validated",
    },
    {
        "auditDocumentId": "ccomptes-agences-programmes-2025",
        "title": "Les agences de programmes",
        "publisher": "Cour des comptes",
        "publicationDate": "2025-11-19",
        "documentType": "parliamentary_commission_report",
        "sourceUrl": "https://www.ccomptes.fr/fr/publications/les-agences-de-programmes",
        "pdfUrl": "https://www.ccomptes.fr/sites/default/files/2025-11/20251119-Agences%20de%20programmes.pdf",
        "publicationUrl": "https://www.ccomptes.fr/fr/publications/les-agences-de-programmes",
        "relatedProgrammeCodes": [],
        "relatedThemeIds": [
            "soutien-de-la-recherche-fondamentale",
            "valorisation-de-la-recherche-publique",
            "levier-:-composants-cloud-ia-et-quantique",
        ],
        "sourcePages": [],
        "confidenceScore": 1.0,
        "validationStatus": "validated",
    },
]


def main():
    from lib.sources import register_source
    
    register_source("ccomptes-france2030", "Rapports de la Cour des comptes sur France 2030", "Cour des comptes", "https://www.ccomptes.fr")
    
    documents = sorted(AUDIT_DOCUMENTS, key=lambda item: item["auditDocumentId"])
    write_json_atomic(OUTPUT_FILE, documents)
    write_json_atomic(OUTPUT_REC, RECOMMENDATIONS)
    write_json_atomic(OUTPUT_FINDINGS, FINDINGS)
    
    correlations = read_json("data/correlations.json", [])
    
    for r in RECOMMENDATIONS:
        correlations.append({
            "correlationId": generate_id("corr", r["recommendationId"], r["targetOrganization"], "auditRecommendation_operator"),
            "sourceEntityType": "auditRecommendation",
            "sourceEntityId": r["recommendationId"],
            "targetEntityType": "operator",
            "targetEntityId": r["targetOrganization"],
            "correlationType": "auditRecommendation_operator",
            "confidenceScore": 1.0,
            "evidenceSource": r["auditDocumentId"],
            "validationStatus": "validated"
        })
        
    for f in FINDINGS:
        for prog in f.get("relatedProgrammeCodes", []):
            correlations.append({
                "correlationId": generate_id("corr", f["findingId"], prog, "auditFinding_programme"),
                "sourceEntityType": "auditFinding",
                "sourceEntityId": f["findingId"],
                "targetEntityType": "programme",
                "targetEntityId": prog,
                "correlationType": "auditFinding_programme",
                "confidenceScore": 1.0,
                "evidenceSource": f["auditDocumentId"],
                "validationStatus": "validated"
            })
            
    # Deduplicate correlations
    unique_corrs = {c["correlationId"]: c for c in correlations}.values()
    write_json_atomic("data/correlations.json", list(unique_corrs))
    
    print(f"{len(documents)} documents, {len(RECOMMENDATIONS)} recommandations et {len(FINDINGS)} constats Cour des comptes exportes.")



if __name__ == "__main__":
    main()
