import json
import os
from lib.ids import generate_id
from lib.json_io import write_json_atomic, read_json
from lib.sources import register_source

DATA_DIR = "data"

def main():
    print("Ingestion des Stratégies Nationales d'Accélération (SGPI)...")
    
    # Enregistrement des sources
    register_source(
        "sgpi-sna", 
        "Stratégies d'accélération pour l'innovation", 
        "SGPI", 
        "https://www.info.gouv.fr/organisation/secretariat-general-pour-l-investissement-sgpi/strategies-d-acceleration-pour-l-innovation"
    )
    register_source(
        "sgpi-bilan-fin", 
        "Bilan financier France 2030 (PDF)", 
        "SGPI", 
        "https://www.info.gouv.fr/upload/media/mixed/0001/17/e92490502bafcbdf2bedde2d0f6961d3f2bcf924.pdf"
    )

    strategies = [
        {
            "strategyId": "sna-hydrogene-decarbone",
            "strategyName": "Hydrogène décarboné",
            "sourceScope": "exogenous",
            "sourceUrl": "https://www.info.gouv.fr/organisation/secretariat-general-pour-l-investissement-sgpi/strategies-d-acceleration-pour-l-innovation",
            "datasetUrl": "https://www.info.gouv.fr/organisation/secretariat-general-pour-l-investissement-sgpi/strategies-d-acceleration-pour-l-innovation",
            "resourceUrl": "https://www.info.gouv.fr/organisation/secretariat-general-pour-l-investissement-sgpi/strategies-d-acceleration-pour-l-innovation",
            "sourceDatasetId": None,
            "sourceResourceId": None,
            "sourceProducer": "SGPI",
            "confidenceScore": 1.0,
            "validationStatus": "validated"
        },
        {
            "strategyId": "sna-sante-numerique",
            "strategyName": "Santé numérique",
            "sourceScope": "exogenous",
            "sourceUrl": "https://www.info.gouv.fr/organisation/secretariat-general-pour-l-investissement-sgpi/strategies-d-acceleration-pour-l-innovation",
            "datasetUrl": "https://www.info.gouv.fr/organisation/secretariat-general-pour-l-investissement-sgpi/strategies-d-acceleration-pour-l-innovation",
            "resourceUrl": "https://www.info.gouv.fr/organisation/secretariat-general-pour-l-investissement-sgpi/strategies-d-acceleration-pour-l-innovation",
            "sourceProducer": "SGPI",
            "confidenceScore": 1.0,
            "validationStatus": "validated"
        }
    ]
    
    financial_execution = [
        {
            "id": generate_id("exec", "424", "2026-Q1"),
            "programmeCode": "424",
            "operatorName": "Global",
            "envelopeAmount": 54000000000.0,
            "engagementAmount": 25000000000.0,
            "disbursementAmount": 8000000000.0,
            "sourcePage": 12,
            "sourceUrl": "https://www.info.gouv.fr/upload/media/mixed/0001/17/e92490502bafcbdf2bedde2d0f6961d3f2bcf924.pdf",
            "resourceUrl": "https://www.info.gouv.fr/upload/media/mixed/0001/17/e92490502bafcbdf2bedde2d0f6961d3f2bcf924.pdf",
            "sourceDocument": "Bilan financier du programme France 2030",
            "extractionMethod": "manual_pdf_review",
            "validationStatus": "to_validate"
        }
    ]
    
    write_json_atomic(os.path.join(DATA_DIR, "acceleration_strategies.json"), strategies)
    write_json_atomic(os.path.join(DATA_DIR, "strategy_funding_allocations.json"), [])
    write_json_atomic(os.path.join(DATA_DIR, "strategy_distribution_vectors.json"), [])
    write_json_atomic(os.path.join(DATA_DIR, "france2030_financial_execution.json"), financial_execution)
    
    print("✅ Données SGPI (Stratégies et Exécution) générées.")

if __name__ == "__main__":
    main()
