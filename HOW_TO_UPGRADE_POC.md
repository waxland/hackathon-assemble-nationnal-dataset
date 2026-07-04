# 🚀 Comment passer du POC à la Production (Upgrade Guide)

Ce document liste l'ensemble des chantiers techniques, architecturaux et fonctionnels recommandés pour transformer ce Proof of Concept (réalisé lors du Hackathon) en un produit de niveau "Production" (Robuste, Scalable, Automatisé et Intelligent).

---

## 1. ☁️ Architecture & Infrastructure (DevOps)
Actuellement, le pipeline tourne en local via un `Makefile` et génère un fichier SQLite.
- [ ] **Conteneurisation (Docker)** : Créer un `Dockerfile` et un `docker-compose.yml` pour encapsuler l'environnement Python et ses dépendances.
- [ ] **Base de données managée** : Remplacer `france2030.sqlite` par une instance **PostgreSQL** managée (ex: Scalingo, CleverCloud ou GCP Cloud SQL) pour permettre des accès concurrents et des requêtes analytiques plus lourdes.
- [ ] **Orchestration (Airflow / Kestra / Dagster)** : Remplacer l'orchestration linéaire séquentielle (`make run-scraping`) par des DAGs (Directed Acyclic Graphs) pour paralléliser les requêtes réseau, gérer les retries complexes et isoler les étapes d'Extraction, Transformation et Chargement (ETL).
- [ ] **Neo4j en tant que Service** : Remplacer l'export de fichiers CSV (`data/neo4j_export`) par une ingestion directe vers une base de graphe hébergée (ex: Neo4j AuraDB).
- [ ] **Stockage S3** : Stocker les gros fichiers bruts téléchargés (ex: le ZIP Sirene de 1.5 Go) sur un bucket S3/MinIO plutôt que dans le dossier local `data/raw/` pour préserver le stockage des workers.

## 2. 🔌 Fiabilisation des Sources de Données
Le POC s'appuie sur des échantillons et des APIs de contournement pour des raisons de temps.
- [ ] **Passage à l'Open Data Assemblée Nationale** : Remplacer le scraping de `NosDéputés.fr` (qui peut être instable ou avoir un rate-limit strict) par l'utilisation des dumps officiels de l'Assemblée Nationale ou l'API `LesTricoteuses`.
- [ ] **Intégration du Sénat** : Actuellement, seules les mentions de l'Assemblée sont traquées. Intégrer les données du Sénat (`NosSénateurs.fr` ou Open Data Sénat) pour avoir la vision bicamérale complète.
- [ ] **Automatisation du PLF (Projet de Loi de Finances)** : Automatiser la récupération du millésime de l'année en cours (ex: PLF 2026, 2027) sans avoir à coder en dur les URLs vers `data.economie.gouv.fr`.
- [ ] **Traitement Big Data pour SIRENE** : Le fichier StockUniteLegale de l'INSEE est massif. Utiliser **DuckDB**, **Polars** ou **Dask** dans `scripts/09_fetch_companies.py` pour parser et filtrer ce CSV de plusieurs Go en streaming avec une empreinte mémoire très faible.
- [ ] **Démockage des derniers JSON** : Trouver une API fiable pour les "Revenus des entreprises" (`company-revenues.json`), qui sont actuellement mockés.

## 3. 🧠 Intelligence Artificielle & Amélioration de la Qualité (Data Science)
Les corrélations reposent actuellement sur des mots-clés (`scripts/05_generate_keywords.py`) et des regex.
- [ ] **Matching Sémantique (NLP)** : Remplacer la recherche par mot-clé stricte des textes parlementaires par du clustering sémantique (Embeddings). Utiliser des modèles comme `CamemBERT`, `SentenceTransformers` ou une API LLM pour calculer une distance cosinus entre le texte d'un amendement et la description d'un thème France 2030.
- [ ] **Entity Resolution (Record Linkage)** : Pour lier une entreprise à son code SIREN quand ce dernier n'est pas fourni (ex: texte brut), implémenter un algorithme de corrélation floue (Fuzzy Matching, Levenshtein, ou modèles ML) pour retrouver l'entreprise dans la base INSEE avec un score de confiance.
- [ ] **Classification LLM des Sentiments** : Utiliser un LLM pour analyser si une mention parlementaire est "Favorable", "Défavorable", ou "Neutre" vis-à-vis d'un programme d'investissement.
- [ ] **Extraction d'Entités Nommées (NER)** : Extraire automatiquement de nouveaux mots-clés, montants ou acteurs depuis le texte brut des débats grâce à un modèle NLP (ex: SpaCy).

## 4. 🛠️ Backend & API (Exposition des Données)
Actuellement, le script `13_export_to_front_contract.py` génère des fichiers JSON statiques.
- [ ] **Création d'une API REST / GraphQL** : Remplacer les JSON statiques par une API dynamique (ex: **FastAPI**). Cela permettra au Front-End Minerve de faire des requêtes filtrées, de gérer la pagination (indispensable quand on aura des milliers de mentions), et d'avoir des temps de chargement instantanés.
- [ ] **Mise en cache (Redis)** : Implémenter un cache en mémoire pour les requêtes les plus fréquentes de l'API (ex: les agrégats de la vue macro).
- [ ] **Sécurisation (Authentification)** : Si des données budgétaires non encore publiques venaient à être intégrées, sécuriser l'API et le dashboard via un SSO (ex: AgentConnect / ProConnect).

## 5. 🛡️ Monitoring & CI/CD (DevX)
Le pipeline dispose déjà d'un rapport de qualité (`make quality-report`) et de tests de schémas.
- [ ] **Intégration Continue (GitHub Actions)** : Déplacer l'exécution des tests (`pytest tests/`) et la validation de schéma dans une GitHub Action exécutée à chaque Pull Request.
- [ ] **Déploiement Continu du Streamlit** : Déployer l'application de contrôle (DQA) sur un service cloud comme *Streamlit Community Cloud*, *HuggingFace Spaces* ou *CleverCloud*.
- [ ] **Alerting (Slack / Mattermost)** : Brancher le `quality_report.json` à un webhook. Si lors d'une mise à jour quotidienne (cron), le `confidenceScore` moyen s'effondre ou qu'un champ critique disparaît, envoyer une notification à l'équipe Data.
- [ ] **Monitoring de l'API** : Mettre en place un outil d'APM (Application Performance Monitoring) comme Sentry ou Datadog pour traquer les erreurs HTTP lors du scraping (ex: API INSEE down).

## 6. 🎨 Front-End & Dataviz (Minerve)
Côté restitution finale au commanditaire.
- [ ] **Intégration d'un Graphe Interactif** : Profiter de l'export Neo4j pour afficher un graphe interactif (via `Vis.js` ou `Cytoscape.js`) dans l'interface, permettant de naviguer visuellement d'un Député ➡️ Amendement ➡️ Objectif de développement ➡️ Appels à projets ➡️ Entreprise.
- [ ] **Explorateur de Code NAF** : Créer un "Sunburst" ou un diagramme arborescent pour naviguer dans les secteurs d'activité financés.
