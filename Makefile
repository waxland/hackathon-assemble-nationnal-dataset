# 🇫🇷 Makefile - Hackathon Assemblée Nationale - France 2030

.PHONY: help install run-scraping export-front export-neo4j clean run-dashboard quality-report validate-schema validate-data export-all

EXPORT_DIR=dataset

help: ## Affiche l'aide
	@echo "🛠️ Commandes disponibles :"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installe l'environnement virtuel et les dépendances
	@echo "📦 Installation de l'environnement virtuel..."
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo "✅ Installation terminée. N'oubliez pas d'activer l'environnement avec 'source venv/bin/activate'."

run-scraping: ## Lance la pipeline complète d'extraction des données et génère la base SQLite (FAST=1 pour bypasser gros downloads)
	@echo "🚀 Démarrage de la pipeline d'extraction des données (FAST=$(FAST))..."
	FAST=$(FAST) ./venv/bin/python scripts/01_extract_programs.py
	FAST=$(FAST) ./venv/bin/python scripts/02_extract_budget_lines.py
	FAST=$(FAST) ./venv/bin/python scripts/03_parse_pap.py
	FAST=$(FAST) ./venv/bin/python scripts/04_generate_themes.py
	FAST=$(FAST) ./venv/bin/python scripts/05_generate_keywords.py
	FAST=$(FAST) ./venv/bin/python scripts/06_scrape_calls_for_projects.py
	FAST=$(FAST) ./venv/bin/python scripts/07_fetch_parliament_mentions.py
	FAST=$(FAST) ./venv/bin/python scripts/08_map_naf_codes.py
	FAST=$(FAST) ./venv/bin/python scripts/09_fetch_companies.py
	FAST=$(FAST) ./venv/bin/python scripts/10_generate_correlations.py
	FAST=$(FAST) ./venv/bin/python scripts/20_ingest_sgpi_strategies.py
	FAST=$(FAST) ./venv/bin/python scripts/21_ingest_plf_2026_budget_gouv.py
	FAST=$(FAST) ./venv/bin/python scripts/23_ingest_ademe_france2030.py
	FAST=$(FAST) ./venv/bin/python scripts/24_ingest_anr_france2030.py
	FAST=$(FAST) ./venv/bin/python scripts/25_ingest_infogouv_laureats.py
	FAST=$(FAST) ./venv/bin/python scripts/11_export_to_sqlite.py
	@echo "✅ Base de données france2030.sqlite générée avec succès."

export-front: ## Traduit la BDD au format du Front et l'exporte dans le dossier 'dataset'
	@echo "📤 Export des données pour le Front-End..."
	./venv/bin/python scripts/13_export_to_front_contract.py
	@echo "📁 Déplacement des fichiers vers le dossier final '$(EXPORT_DIR)'..."
	mkdir -p $(EXPORT_DIR)/budget $(EXPORT_DIR)/catalog $(EXPORT_DIR)/matching $(EXPORT_DIR)/metrics $(EXPORT_DIR)/reports $(EXPORT_DIR)/sources $(EXPORT_DIR)/dataviz
	cp data/export_front/france-2030-budget-lines.json $(EXPORT_DIR)/budget/
	cp data/export_front/investment-programmes.json $(EXPORT_DIR)/catalog/
	cp data/export_front/programme-taxonomy.json $(EXPORT_DIR)/matching/
	cp data/export_front/programme-alignment-scores.json $(EXPORT_DIR)/metrics/
	cp data/export_front/investment-programme-reports.json $(EXPORT_DIR)/reports/
	cp data/export_front/investment-programme-dataviz.json $(EXPORT_DIR)/dataviz/
	cp data/export_front/data-gouv-datasets.json $(EXPORT_DIR)/sources/
	cp data/export_front/inpi-patent-families.json $(EXPORT_DIR)/sources/
	cp data/export_front/sirene-companies.json $(EXPORT_DIR)/sources/
	cp data/export_front/company-revenues.json $(EXPORT_DIR)/sources/
	cp data/export_front/parliamentary-documents.json $(EXPORT_DIR)/sources/
	@echo "✅ Dossier '$(EXPORT_DIR)' prêt à être copié dans le repo Front."

export-neo4j: ## Génère les fichiers CSV structurés pour un import Neo4j / Gephi
	@echo "🕸️ Exportation des Noeuds et Relations pour analyse de Graphe..."
	./venv/bin/python scripts/12_export_graph_neo4j.py

run-dashboard: ## Lance le dashboard interactif Streamlit en local
	@echo "📊 Lancement du Dashboard Streamlit..."
	./venv/bin/streamlit run app/app.py

quality-report: ## Génère un rapport de qualité des données
	@echo "📊 Génération du rapport de qualité..."
	./venv/bin/python scripts/18_generate_quality_report.py

validate-schema: ## Valide les schémas JSON internes via Pydantic
	@echo "🛡️ Validation des schémas JSON..."
	./venv/bin/python scripts/19_validate_json_contracts.py

validate-data: validate-schema quality-report ## Alias pour exécuter la validation de schéma et le rapport de qualité
	@echo "✅ Validation des données terminée."

export-all: run-scraping export-front export-neo4j validate-data ## Lance l'itération complète : extraction, SQLite, front, Neo4j, quality report
	@echo "🚀 Itération complète terminée !"

clean: ## Supprime l'environnement virtuel, les caches et le dossier data/
	@echo "🧹 Nettoyage du projet..."
	rm -rf venv/
	rm -rf __pycache__/
	rm -rf data/
	rm -rf $(EXPORT_DIR)/
	@echo "✅ Projet nettoyé."
