# Retour d'Expérience et Points de Friction (RETOUR.md)

Ce document dresse un bilan critique de l'architecture et du code générés pour le POC France 2030. Il met en lumière les **points de friction potentiels** (limites techniques, dette technique, qualité de la donnée) qui devront être adressés pour passer de ce Proof of Concept (POC) à un produit en production.

---

## 🌐 1. Extraction, Scraping & API (Limites Réseau)

- [ ] **Friction - Blocage Cloudflare sur les Appels à Projets (AAP)** : Le site `info.gouv.fr` bloque les requêtes automatisées. *Solution de contournement actuelle : Données mockées.*
  - *Action* : Trouver le jeu de données officiel des AAP sur `data.gouv.fr` ou utiliser un scraper avec navigateur headless (ex: Playwright/Selenium) pour contourner la protection.
- [ ] **Friction - Rate Limiting API Sirene** : L'API `recherche-entreprises` est limitée à 7 requêtes/seconde. Le script `09_fetch_companies.py` utilise un simple `time.sleep(0.5)`. 
  - *Action* : Implémenter un vrai mécanisme de `Retry-After` avec `Tenacity` ou `requests.adapters.Retry` pour gérer les montées en charge sur des milliers d'entreprises.
- [ ] **Friction - Lenteur & Pagination NosDéputés.fr** : Le script `07_fetch_parliament_mentions.py` est bridé volontairement (15 mots-clés, 3 résultats max) pour éviter de surcharger l'API ou de prendre des heures.
  - *Action* : Passer sur une ingestion asynchrone (ex: `asyncio` + `aiohttp`) et gérer la pagination complète pour rapatrier tout l'historique d'une législature.

---

## 🧹 2. Qualité et Fiabilisation de la Donnée

- [ ] **Friction - Homonymie sur l'API Sirene** : Rechercher une entreprise par son "Nom" est dangereux (ex: chercher "GreenTech" peut retourner 50 entreprises). 
  - *Action* : Obtenir obligatoirement le SIREN exact depuis le jeu de données source des lauréats, plutôt que de deviner par le nom.
- [ ] **Friction - Faux Positifs dans les Débats Parlementaires** : La recherche textuelle est "bête". Si un député dit le mot "Nucléaire" ou "Hydrogène", ce n'est pas forcément lié au plan *France 2030*.
  - *Action* : Ajouter un filtre strict (ex: n'accepter la mention que si "France 2030" ou "Milliard" est aussi présent dans un rayon de 50 mots) ou utiliser un LLM (Ollama/OpenAI) pour valider le contexte.
- [ ] **Friction - Historique Budgétaire (2024 / 2026)** : Le fichier actuel "PLF 2025" donne les Crédits de Paiement (CP) de 2025. Les colonnes 2024 et 2026 sont vides dans notre BDD.
  - *Action* : Télécharger, parser et faire une jointure avec les fichiers PLF 2024 (Exécuté) et la programmation pluriannuelle pour combler les trous.

---

## 🏗️ 3. Architecture et Scripts Python

- [ ] **Friction - Scripts Synchrones et Séquentiels** : Si un script plante à 99%, toutes les données de la session en cours sont perdues car l'écriture du JSON se fait tout à la fin.
  - *Action* : Sauvegarder les données de manière incrémentale (ex: mode `append` sur un fichier JSONL - JSON Lines) ou écrire directement dans SQLite au fil de l'eau.
- [ ] **Friction - Destruction de la base SQLite (`11_export_to_sqlite.py`)** : Le script fait un `os.remove(db_path)` à chaque exécution. C'est idéal pour un POC, mais catastrophique en production.
  - *Action* : Utiliser des `INSERT OR REPLACE` (Upsert) basés sur les clés primaires sans supprimer les tables pour permettre des mises à jour incrémentales.
- [ ] **Friction - Couplage fort des ID générés** : Les identifiants (ex: `corr-af2591db`) sont regénérés aléatoirement (`uuid4()`) à chaque exécution.
  - *Action* : Générer des hash déterministes (ex: `md5(source_id + target_id)`) pour que les ID des corrélations soient stables entre deux exécutions des scripts.

---

## 🚢 4. Déploiement & Interface (Streamlit / Docker)

- [ ] **Friction - Dépendance à l'ordre d'exécution sous Docker** : Le `docker-compose.yml` monte le dossier `./data`. Si on lance Docker *avant* d'avoir exécuté les scripts Python locaux, Streamlit plantera car `france2030.sqlite` n'existera pas.
  - *Action* : Ajouter une logique dans `dashboard.py` (ou via un `entrypoint.sh`) qui vérifie la présence de la base SQLite, affiche un message convivial si elle manque, ou lance la génération de base (mock) automatiquement.
- [ ] **Friction - Scalabilité du Dashboard** : Streamlit charge le `pd.read_sql` en mémoire (`RAM`). Si la base contient 2 millions d'amendements, l'app plantera.
  - *Action* : Ne jamais faire de `SELECT *`. Toujours paginer les résultats affichés dans Streamlit ou utiliser des requêtes SQL d'agrégation.

---

## 🎯 Conclusion pour l'équipe technique

Ce POC démontre la **faisabilité technique** du croisement de données entre Budget, Parlement et Entreprises. Cependant, le passage à l'échelle nécessitera de robustifier l'ingestion (asynchronisme, gestion d'erreurs API) et d'affiner l'intelligence métier (NLP) pour nettoyer les faux-positifs.
