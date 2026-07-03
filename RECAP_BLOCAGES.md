# Bilan Final - Points de Blocages Résiduels

La majorité des actions critiques listées dans la roadmap (`BILAN_TODO.md`) ont été traitées, permettant d'obtenir une architecture robuste (UUIDs déterministes, base SQLite en Upsert, retry sur les APIs, déploiement Docker).

Cependant, il reste des **points de blocages profonds** nécessitant soit un arbitrage métier, soit une refonte technique majeure que nous ne pouvions pas adresser dans le temps imparti.

Voici les checkboxes des chantiers ouverts (blocages identifiés) pour l'équipe qui reprendra le code :

## 1. 🌐 Blocages Réseaux (Scraping & Ingestion)

- [ ] **L'Anti-Bot Cloudflare sur Info.gouv.fr (`06_scrape_calls_for_projects.py`)** :
  - **Le problème** : Impossible de scraper la liste des Appels à Candidatures via de simples requêtes `requests` ou `curl`, le portail du gouvernement bloque les requêtes non-humaines avec un challenge Cloudflare.
  - **La solution** : Il faudra mettre en place `Playwright` ou `Puppeteer` avec des configurations anti-détection (ex: `playwright-stealth`) pour simuler un vrai navigateur.
- [ ] **L'absence d'historique budgétaire unifié (`02_extract_budget_lines.py`)** :
  - **Le problème** : Les montants de 2024 (Exécuté) et 2026 (Prévu) ne figurent pas dans le même export CSV Open Data que le budget PLF 2025. Le format des CSV de data.economie.gouv.fr change souvent d'une année sur l'autre.
  - **La solution** : Télécharger manuellement les CSV de chaque année, harmoniser les noms de colonnes et faire une jointure externe complexe dans Pandas.

## 2. 🤖 Blocages Métiers (NLP)

- [ ] **Les "Faux Positifs" à l'Assemblée Nationale (`07_fetch_parliament_mentions.py`)** :
  - **Le problème** : La recherche "Full Text" est trop basique. Un député peut parler d'une "Startup" ou de "l'Université" sans que cela n'ait aucun rapport avec le programme *France 2030* (créant du bruit dans le Front-End).
  - **La solution** : Introduire une solution de Natural Language Processing (NLP). Soit un filtre NLTK de proximité (le mot "France 2030" doit être proche du mot "Startup"), soit confier la phrase à un LLM (Ollama) pour qu'il retourne un booléen (`is_related_to_france_2030: true`).

## 3. 🎨 Blocages Front-End (Outils de Dataviz)

- [ ] **Le Calcul du Score d'Alignement (`13_export_to_front_contract.py`)** :
  - **Le problème** : Le Front-End (Minerve.fr) s'attend à recevoir un score d'alignement pour chaque programme dans `programme-alignment-scores.json`. Mais ce score n'a pas encore de formule mathématique validée par le métier (Faut-il compter le nombre d'entreprises financées ? Le volume financier divisé par le nombre de discours parlementaires ?).
  - **La solution** : Développer l'outil de pondération interactif via les `st.slider` de Streamlit pour que les Product Owners définissent empiriquement la bonne formule avant de l'injecter en dur dans le code Python.
