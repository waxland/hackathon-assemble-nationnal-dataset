# Retour d'Expérience et Points de Friction (RETOUR.md) - V2 (Analyse Profonde)

Suite à une relecture exhaustive de la base de code et de l'architecture du projet, ce document dresse un bilan critique complet des **points de friction potentiels** et de la **dette technique** qui devront être adressés pour passer de ce Proof of Concept (POC) à un produit en production.

---

## 🌐 1. Extraction, Scraping & APIs (Risques d'Ingestion)

- [ ] **Friction - Blocage Cloudflare sur les Appels à Projets (AAP) (`script 06`)** : Le site `info.gouv.fr` bloque les requêtes automatisées. Le script actuel utilise un mock de 4 AAP. 
  - *Action* : Utiliser un scraper headless (Playwright/Puppeteer) ou trouver un jeu de données officiel des AAP sur `data.gouv.fr` (ex: API Aides-Territoires, si elle intègre France 2030).
- [ ] **Friction - Instabilité des URLs sources (`scripts 01, 02, 03`)** : Les URLs des fichiers CSV de `data.economie.gouv.fr` sont hardcodées. Si le jeu de données change d'ID pour le PLF 2027, les scripts casseront.
  - *Action* : Utiliser l'API de recherche du catalogue (par mot-clé) pour résoudre dynamiquement l'URL du dernier millésime avant de le télécharger.
- [ ] **Friction - Rate Limiting API Sirene (`script 09`)** : L'API `recherche-entreprises` est limitée à 7 requêtes/seconde. Le script utilise un fragile `time.sleep(0.5)`. 
  - *Action* : Implémenter un vrai mécanisme de `Retry-After` (via la librairie `tenacity` ou `urllib3.util.Retry`).
- [ ] **Friction - Lenteur & Pagination NosDéputés.fr (`script 07`)** : Le script est bridé volontairement (15 mots-clés, 3 résultats max) pour éviter de bloquer l'API.
  - *Action* : Passer sur une ingestion asynchrone (`asyncio` + `aiohttp`) et gérer la pagination (attribut `next_page` de l'API) pour rapatrier tout l'historique d'une législature en tâche de fond.

---

## 🧹 2. Qualité et Fiabilisation de la Donnée (Risques Métier)

- [ ] **Friction - Homonymie sur l'API Sirene (`script 09`)** : Rechercher une entreprise par son "Nom complet" est dangereux (chercher "Alan" ou "GreenTech" peut retourner 50 entreprises). 
  - *Action* : Obtenir le SIREN exact depuis le jeu de données source des lauréats Bpifrance/ADEME, plutôt que d'utiliser l'endpoint `/search`.
- [ ] **Friction - Faux Positifs dans les Débats Parlementaires (`script 07`)** : La recherche textuelle est littérale. Si un député prononce le mot "Hydrogène" dans un débat sur l'énergie, ce n'est pas forcément lié aux financements *France 2030*.
  - *Action* : Ajouter un filtre de proximité (ex: "France 2030" doit être prononcé dans les 50 mots précédents) ou utiliser un LLM (via API ou modèle local) pour classifier la pertinence de la mention.
- [ ] **Friction - Dictionnaire statique et hardcodé (`scripts 04, 05`)** : Les taxonomies (`THEMES_MAPPING` et `KEYWORDS_RICH_MAPPING`) sont définies en dur dans le code Python.
  - *Action* : Déporter ces configurations dans des fichiers YAML ou un Back-Office (CMS) pour que les experts métiers puissent ajouter des mots-clés sans toucher au code.

---

## 🏗️ 3. Architecture et Scripts Python (Dette Technique)

- [ ] **Friction - Scripts Synchrones et Séquentiels** : Si un script plante à 99% (ex: timeout API), toutes les données en RAM sont perdues car l'écriture JSON se fait à la fin du process.
  - *Action* : Sauvegarder les données de manière incrémentale (mode `append` JSONL) ou écrire dans SQLite au fil de l'eau.
- [ ] **Friction - Destruction systématique de la base SQLite (`script 11`)** : Le script fait un `os.remove(db_path)` à chaque exécution. C'est parfait pour un POC, mais inacceptable en production.
  - *Action* : Utiliser la commande `INSERT OR REPLACE` (Upsert) sur les clés primaires sans `DROP TABLE` pour permettre des mises à jour incrémentales.
- [ ] **Friction - Couplage fort et instabilité des IDs (`script 10`)** : Les identifiants de corrélation sont générés avec `uuid.uuid4()`. À chaque exécution, les IDs changent, rendant impossible la synchronisation avec des systèmes tiers (ex: Neo4j).
  - *Action* : Générer des hash déterministes basés sur le contenu : `hash(sourceEntityId + targetEntityId + correlationType)`.

---

## 🚢 4. Déploiement & Interface (Limites Front-End)

- [ ] **Friction - Dépendance de montage sous Docker (`docker-compose.yml`)** : Si on lance `docker-compose up` sur une machine vierge avant d'avoir exécuté les scripts Python, le `dashboard.py` plantera car `france2030.sqlite` n'existera pas.
  - *Action* : Créer un fichier `entrypoint.sh` pour le conteneur Docker qui vérifie la présence de la BDD et lance le pipeline d'ingestion automatiquement si elle est absente.
- [ ] **Friction - Scalabilité du Dashboard Streamlit** : L'interface charge les DataFrames en mémoire vive via `pd.read_sql`. Si la table `parliament_mentions` grandit massivement, l'application crashera (OOM).
  - *Action* : Paginer les requêtes SQL côté backend (utilisation de `LIMIT` et `OFFSET`) et éviter les `SELECT *` massifs.

---

## 🎯 Conclusion pour l'équipe technique

Ce POC valide magistralement l'approche d'agrégation de multiples sources Open Data (Budget, Assemblée, Sirene). Néanmoins, le passage à un outil industriel ("Scale-up") nécessitera l'introduction d'un orchestrateur de tâches (comme **Apache Airflow** ou **Prefect**) pour remplacer l'exécution manuelle des 11 scripts, gérer les retries d'API, et consolider les données dans une vraie base PostgreSQL ou Neo4j.
