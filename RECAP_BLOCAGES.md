# Bilan Final - Points de Blocages Résiduels

La majorité des actions critiques listées dans la roadmap (`BILAN_TODO.md`) ont été traitées, permettant d'obtenir une architecture robuste (UUIDs déterministes, base SQLite en Upsert, retry sur les APIs, taxonomie externalisée, filtrage NLP basique, scores dynamiques et export Neo4j pondéré).

Cependant, il reste des **points de blocages profonds** nécessitant soit un arbitrage métier, soit une refonte technique majeure que nous ne pouvions pas adresser dans le temps imparti.

Voici les checkboxes des chantiers ouverts (blocages identifiés) pour l'équipe qui reprendra le code :

## 1. 🌐 Blocages Réseaux (Scraping & Ingestion)

- [ ] **L'Anti-Bot Cloudflare sur Info.gouv.fr (`06_scrape_calls_for_projects.py`)** :
  - **Le problème** : Impossible de scraper la liste des Appels à Candidatures via de simples requêtes HTTP sur la source ciblée (`https://www.info.gouv.fr/grand-dossier/france-2030/appels-a-candidatures`). Le portail du gouvernement bloque les requêtes non-humaines avec un challenge Cloudflare. Les alternatives API (ex: `https://aides-territoires.beta.gouv.fr/api/aides/`) testées ne retournaient aucun résultat pertinent pour les mots-clés "France 2030". Les données actuelles sont donc un mock partiel réaliste.
  - **La solution** : Il faudra mettre en place `Playwright` ou `Puppeteer` avec des configurations anti-détection (ex: `playwright-stealth`) pour simuler un vrai navigateur et valider le challenge JS, ou trouver un jeu de données brut Bpifrance/ADEME.
  
- [x] **L'absence d'historique budgétaire unifié (`02_extract_budget_lines.py`)** :
  - **Le problème** : Les montants de 2024 (Exécuté) et 2026 (Prévu) ne figurent pas dans le même export CSV Open Data que le budget PLF 2025 (`https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/plf25-depenses-2025-du-bg-et-des-ba-selon-nomenclatures-destination-et-nature`). Le format des CSV de `data.economie.gouv.fr` change souvent d'une année sur l'autre, empêchant un script générique.
  - **La solution** : Le script Python a été complexifié pour télécharger deux datasets (PLF 2024 et PLF 2025), mapper les noms de colonnes variables ("Mission" vs "Libellé Mission") et réaliser une jointure en mémoire pour regrouper les montants sur la même ligne (la colonne `amount2024` n'est plus `null`).

## 2. 🤖 Blocages Métiers (NLP & Croisement)

- [ ] **Faux Positifs résiduels à l'Assemblée Nationale (`07_fetch_parliament_mentions.py`)** :
  - **Le problème** : Bien qu'un filtre de proximité ait été implémenté (vérifiant la présence des mots "France 2030", "milliard" etc. dans la même phrase), certains discours fleuves peuvent passer au travers du filet.
  - **La solution** : Confier la phrase à un LLM local (Ollama) pour qu'il retourne un booléen (`is_related_to_france_2030: true`) ou utiliser un modèle de classification pré-entraîné.

- [ ] **Enrichissement croisé (Sirene x AAP) manquant** :
  - **Le problème** : Actuellement, les entreprises sont liées à un thème (ex: "Hydrogène"), mais il est très difficile de les lier à l'Appel à Projet exact (ex: "Briques technologiques H2") de manière automatisée sans un identifiant commun dans l'Open Data.
  - **La solution** : Récupérer les identifiants de subvention (numéro de convention) pour créer une table de correspondance stricte.

## 3. 🎨 Blocages Front-End (Dashboard & Dataviz)

- [ ] **Outil de Pondération dans Streamlit absent (`dashboard.py`)** :
  - **Le problème** : Bien que le score soit désormais calculé dynamiquement en Python (Mentions * 10 / Budget), le Dashboard Streamlit n'offre pas encore de *sliders* interactifs pour permettre aux Product Owners d'ajuster ce ratio et de voir l'impact en direct.
  - **La solution** : Ajouter `st.slider` dans l'onglet "Data Quality" du `dashboard.py` et sauvegarder la configuration choisie par l'utilisateur pour l'export JSON.
