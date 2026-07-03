# Bilan et Roadmap des TODOs (BILAN_TODO.md)

Ce document centralise, ordonne et priorise les actions restantes à accomplir sur le socle Data (Python / SQLite / JSON) et son intégration avec le Frontend. Il est construit à la lumière des limites identifiées dans le `RETOUR.md` et de la vision globale de `DATASETS.md`.

---

## 🏗️ 1. Amélioration de l'Ingestion (Scraping & APIs)
*Ces étapes visent à passer des données mockées/partielles à une véritable industrialisation de la collecte.*

- [ ] **Étape 1.1 : Industrialiser l'API Sirene** 
  - *Action* : Dans `09_fetch_companies.py`, remplacer le `time.sleep()` par une librairie de retry robuste (ex: `tenacity`).
  - *Critère de succès* : Pouvoir ingérer une liste de 500 entreprises lauréates sans erreur HTTP 429.
- [ ] **Étape 1.2 : Compléter l'historique budgétaire**
  - *Action* : Dans `02_extract_budget_lines.py`, croiser le CSV du PLF 2025 avec ceux des PLF 2024 et PLF 2023 pour avoir une série temporelle complète sur les 3 ans.
  - *Critère de succès* : Les clés `amount2024` et `amount2026` ne sont plus `null`.
- [ ] **Étape 1.3 : Scraping dynamique des AAP**
  - *Action* : Dans `06_scrape_calls_for_projects.py`, remplacer les 4 Mocks par un scraping Playwright ou BeautifulSoup sur `info.gouv.fr` ou par l'appel à une API tierce centralisée.
  - *Critère de succès* : Récupération automatique des nouveaux Appels à Projets chaque semaine.
- [ ] **Étape 1.4 : Pagination et asynchronisme sur NosDéputés.fr**
  - *Action* : Dans `07_fetch_parliament_mentions.py`, implémenter `asyncio` pour requêter les centaines de pages de l'API sans bloquer le script pendant des heures.
  - *Critère de succès* : Extraction de >1000 mentions parlementaires en moins de 2 minutes.

---

## 🧹 2. Affinage Métier (NLP & Taxonomie)
*Ces étapes visent à réduire les faux positifs et à améliorer la "Confidence" des données extraites.*

- [ ] **Étape 2.1 : Externaliser la Taxonomie**
  - *Action* : Sortir les dictionnaires codés en dur dans `04_generate_themes.py` et `05_generate_keywords.py` pour les placer dans un fichier `config/taxonomy.yaml`.
  - *Critère de succès* : Un chef de projet peut ajouter des mots-clés sans savoir coder en Python.
- [ ] **Étape 2.2 : Filtre de pertinence (NLP basique)**
  - *Action* : Modifier la logique de croisement dans `07_fetch_parliament_mentions.py` pour rejeter les mentions qui ne contiennent pas le mot "France 2030" ou "Milliard" dans les 100 mots autour du mot-clé détecté.
  - *Critère de succès* : Hausse drastique du score de pertinence des verbatims extraits.
- [ ] **Étape 2.3 : Enrichissement croisé (Sirene x AAP)**
  - *Action* : Lier formellement les identifiants `companyId` aux `callId` (si l'info est dans la source) plutôt que de les lier uniquement au `themeId`.

---

## 🗄️ 3. Robustesse de la Base de Données (SQLite & Neo4j)
*Ces étapes préparent la base de données à des mises à jour quotidiennes (CRON) sans perte de données.*

- [ ] **Étape 3.1 : Déterminisme des UUIDs**
  - *Action* : Dans `10_generate_correlations.py`, remplacer `uuid4()` par un hash MD5 déterministe (ex: `md5(sourceId + targetId + type)`).
  - *Critère de succès* : Relancer le script ne modifie pas les IDs existants dans `correlations.json`.
- [ ] **Étape 3.2 : Upsert SQLite**
  - *Action* : Modifier `11_export_to_sqlite.py` pour arrêter de faire `os.remove(db_path)`. Utiliser exclusivement `INSERT OR REPLACE`.
  - *Critère de succès* : La BDD conserve son historique même si le script JSON plante.
- [ ] **Étape 3.3 : Améliorer l'export Neo4j**
  - *Action* : Dans `12_export_graph_neo4j.py`, inclure les propriétés de poids (`confidenceScore`) dans les fichiers CSV des "Relationships" pour permettre des requêtes de graphe pondérées.

---

## 🎨 4. Finalisation du Contrat Front (Streamlit & JSON)
*Ces étapes garantissent que le travail de l'équipe Data est parfaitement aligné avec l'intégration React/Vue.*

- [ ] **Étape 4.1 : Implémenter le Score d'Alignement**
  - *Action* : Coder dans `13_export_to_front_contract.py` un calcul réel pour le fichier `programme-alignment-scores.json` (ratio Mentions / Budget).
  - *Critère de succès* : Le fichier n'est plus un "mock vide" (`isMock: false`).
- [ ] **Étape 4.2 : Sécuriser le lancement Docker**
  - *Action* : Créer un `entrypoint.sh` pour le conteneur Streamlit qui exécute `make run-scraping` et `make export-front` si la BDD est absente au démarrage.
  - *Critère de succès* : `docker-compose up` fonctionne "Out-of-the-box" sur une machine vierge.
- [ ] **Étape 4.3 : Outil de Pondération dans Streamlit**
  - *Action* : Ajouter des *sliders* interactifs dans le dashboard Streamlit pour permettre d'ajuster le poids des variables (ex: Importance des Brevets vs Mentions) dans le calcul du score final.
