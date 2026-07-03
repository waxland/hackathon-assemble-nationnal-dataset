# Hackathon Assemblée Nationale - POC France 2030 (Terminé)

## 🏁 Bilan des travaux accomplis

Le POC a été intégralement exécuté avec succès. L'objectif initial qui était de **"construire une base de corrélation propre"** entre le budget France 2030, les thématiques d'innovation, les entreprises lauréates et les débats parlementaires a été validé.

Nous sommes passés d'une feuille blanche à un **pipeline d'acquisition de données Open Data fonctionnel, scripté en Python et packagé en SQLite.**

---

## 🏗️ Architecture et Pipeline mis en place

Le dépôt Github contient désormais l'ensemble de l'outillage :

1. **`TODO.md` & `TODO_XX.md`** : Le cahier des charges a été entièrement dépilé. Les 7 phases du projet ont été explorées, codées et validées.
2. **`DATASETS.md`** : La documentation de l'architecture relationnelle (schéma Entité-Association généré en Mermaid) est disponible.
3. **Dossier `scripts/`** : 11 scripts Python séquentiels qui s'occupent d'aller récupérer la vraie donnée, de la parser et de la nettoyer.
4. **Dossier `data/`** : Le cœur du réacteur. Les données extraites au format brut (`.csv`), nettoyé (`.json`) et compilé (`.sqlite`).

---

## 🔍 Provenance de la donnée (Open Data fiabilisé)

Au lieu de faire du parsing hasardeux (PDF) ou de laisser l'IA halluciner, nous avons branché le POC sur des flux de données souverains :

- **Budget & Projets Annuels de Performances (PAP)** :
  - **Source** : `data.economie.gouv.fr`
  - **Résultat** : Récupération des montants votés exacts (CP) pour 2025 sur les programmes 421 à 425 de la mission France 2030 (ex: 4,3 Mds€ pour le Prog 424). Récupération des objectifs et actions officiels sans parsing PDF hasardeux.
- **Entreprises & Codes NAF** :
  - **Source** : API Sirene (`recherche-entreprises.api.gouv.fr`)
  - **Résultat** : Un échantillon de licornes/DeepTechs (Verkor, Mistral AI, Pasqal, etc.) a été interrogé pour récupérer leur Code NAF officiel.
- **Mentions Parlementaires (Le cœur du Hackathon)** :
  - **Source** : API de l'association *Regards Citoyens* (`NosDéputés.fr`)
  - **Résultat** : Croisement automatisé des mots-clés technologiques de France 2030 (SMR, Hydrogène, Quantique) avec les archives des amendements et questions écrites de l'Assemblée nationale.

---

## 📈 La Base de Données Finale (`france2030.sqlite`)

Le point d'orgue du projet est le script `11_export_to_sqlite.py`. 
Il ingère les milliers de lignes JSON pour construire une base relationnelle ultra-rapide comprenant **9 tables** (Programmes, Thèmes, Mots-clés, Mentions, Entreprises, etc.) et **73 corrélations explicites**.

La base est structurée pour répondre immédiatement, via de simples requêtes SQL, aux problématiques de Data-Visualisation du Hackathon :
* *"Quels sont les thèmes industriels les plus débattus dans l'hémicycle ?"*
* *"Où va précisément l'argent du programme 425 ?"*

---

## 🚀 Prochaines étapes suggérées (Pour l'équipe Data-Viz / Front-End minerve.gouv.fr)

Maintenant que le socle de données est robuste et prêt, l'équipe technique peut se concentrer sur l'interface :

1. **Dashboard Interactif** : Brancher `Metabase`, `Superset` ou un script `Streamlit` directement sur le fichier `data/france2030.sqlite`.
2. **Visualisation de Graphe** : Utiliser les données de la table `correlations` avec une librairie comme `D3.js` ou `Cytoscape.js` pour afficher la toile d'araignée liant un Député -> à un Mot Clé -> à une Entreprise -> à un Budget.
3. **Mise à l'échelle** : Relancer les scripts Python (qui sont idempotents) en retirant les limites de "POC" (ex: la limite de 15 mots-clés ou de 3 mentions max par mot-clé) pour ingérer l'intégralité des données disponibles sur l'année écoulée.
