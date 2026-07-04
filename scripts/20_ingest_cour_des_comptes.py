from lib.json_io import write_json_atomic


OUTPUT_FILE = "data/audit_documents.json"


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
    documents = sorted(AUDIT_DOCUMENTS, key=lambda item: item["auditDocumentId"])
    write_json_atomic(OUTPUT_FILE, documents)
    print(f"{len(documents)} documents Cour des comptes exportes dans {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
