# Retour d'Itérations

## [2026-07-04] Tâche P0.1 : Réconciliation documentation/code

- **Tâche traitée** : P0.1 Reconciliation documentation/code
- **Fichiers modifiés** : `README.md`, `TODO_ITERATION.md`
- **Résumé des changements** : Ajout d'une section clarifiant les données réelles (budget 2024/2025, API NosDéputés, API Sirene) vs les données mockées/échantillons. Vérification de la documentation.
- **Commandes lancées + résultats** : `cat README.md`, `cat DATASETS.md`.
- **Blocages / observations** : Certains fichiers mentionnés dans le TODO (`RECAP.md`, `RETOUR.md`) ont été déplacés ou supprimés auparavant, ce qui a été géré.
- **Prochaine tâche recommandée** : P0.2 Contrôle qualité automatique

## [2026-07-04] Tâche P0.2 : Contrôle qualité automatique

- **Tâche traitée** : P0.2 Controle qualite automatique
- **Fichiers modifiés** : `scripts/18_generate_quality_report.py`, `Makefile`, `TODO_ITERATION.md`
- **Résumé des changements** : Création d'un script d'analyse qualité générant `data/quality_report.json` qui détecte les IDs dupliqués, les champs critiques manquants, les relations de faible confiance, et la présence de mocks dans les fichiers front. Ajout de la commande `make quality-report`.
- **Commandes lancées + résultats** : `make quality-report`. Le rapport a révélé que `kw-satt` était dupliqué, qu'`amount2026` manquait sur 11 lignes, et que `contextAfter` manquait sur 63 mentions. 7 fichiers front ont encore des `isMock: true`.
- **Blocages / observations** : Rien de bloquant. Le rapport est fonctionnel et donne des directives claires.
- **Prochaine tâche recommandée** : P0.3 Stabilité des IDs et schéma

## [2026-07-04] Tâche P0.3 : Stabilité des IDs et schéma

- **Tâche traitée** : P0.3 Stabilité des IDs et schema
- **Fichiers modifiés** : `scripts/05_generate_keywords.py`, `scripts/19_validate_json_contracts.py`, `Makefile`, `TODO_ITERATION.md`
- **Résumé des changements** : Correction du doublon `kw-satt` en incluant un extrait du `themeId` dans le hash du mot-clé. Création du script de validation Pydantic `19_validate_json_contracts.py` avec `CompanySchema` et `MentionSchema` ajustés aux données réelles.
- **Commandes lancées + résultats** : `make validate-schema`. Tous les schémas JSON (programs, budget_lines, themes, keywords, companies, mentions, correlations) passent la validation Pydantic.
- **Blocages / observations** : Le champ `politicalGroup` peut être nul dans `parliament_mentions`, le schéma Pydantic a été assoupli avec `Optional[str]`.
- **Prochaine tâche recommandée** : P0.4 SQLite incremental et non destructif

## [2026-07-04] Tâche P0.4 : SQLite incrémental et non destructif

- **Tâche traitée** : P0.4 SQLite incremental et non destructif
- **Fichiers modifiés** : `scripts/11_export_to_sqlite.py`, `TODO_ITERATION.md`
- **Résumé des changements** : Refonte du script SQLite pour retirer la suppression aveugle de la BDD. Utilisation d'un vrai Upsert (`INSERT OR REPLACE`). Ajout de la table `ingestion_runs` pour traquer les exécutions et leurs statuts. Ajout d'une option `--reset` en CLI. Si un fichier JSON est manquant, les tables sont laissées intactes.
- **Commandes lancées + résultats** : `./venv/bin/python scripts/11_export_to_sqlite.py`. Le runID est bien généré et la base est mise à jour de manière persistante.
- **Blocages / observations** : Fonctionnement fluide. L'Upsert de SQLite assure que les mêmes IDs mettent à jour la base au lieu de faire planter le script.
- **Prochaine tâche recommandée** : P0.5 Export Neo4j réaligné

## [2026-07-04] Tâche P0.5 : Export Neo4j réaligné

- **Tâche traitée** : P0.5 Export Neo4j realigne
- **Fichiers modifiés** : `scripts/12_export_graph_neo4j.py`, `TODO_ITERATION.md`
- **Résumé des changements** : Refonte du script `12` en utilisant le module standard `csv` de Python au lieu d'une concaténation de strings, ce qui évite les bugs d'import dans Neo4j causés par les virgules et guillemets non échappés. Alignement sur les nouvelles colonnes INSEE (`denominationUniteLegale`, `activitePrincipaleUniteLegale`). Ajout de la propriété de relation `weight:float`.
- **Commandes lancées + résultats** : `make export-neo4j`. Fichiers générés avec succès et format CSV strict (rfc4180) respecté.
- **Blocages / observations** : Les nouveaux types de noeuds (`Project`, `Territory`, etc.) n'ont pas encore été créés dans les étapes précédentes de l'itération, j'ai donc laissé la structure prête à les accueillir.
- **Prochaine tâche recommandée** : La section P0 (Stabiliser le socle existant) est désormais complète. La prochaine étape logique est de passer aux tâches P1 (Ajouter les sources de forte valeur, ex: P1.1 Ingestion PLF 2026).

## [2026-07-04] Tâche P1.1 : Ingestion PLF 2026 Budget vert

- **Tâche traitée** : P1.1 Ingestion PLF 2026 Budget vert
- **Fichiers modifiés** : `scripts/14_ingest_budget_vert_2026.py`, `scripts/11_export_to_sqlite.py`, `scripts/10_generate_correlations.py`, `TODO_ITERATION.md`
- **Résumé des changements** : Création du script d'ingestion du Budget Vert. Le fichier CSV gouvernemental contenant des retours à la ligne illégaux dans les headers a été pré-traité avant d'être donné à Pandas. 56 lignes d'actions écologiques ont été extraites. La structure `green_budget_lines` a été ajoutée à SQLite et 56 nouvelles corrélations `green_finance` ont été créées.
- **Commandes lancées + résultats** : Exécution des scripts. La jointure exacte avec les "Titres" de dépenses classiques (T3/T6) de `budget_lines.json` s'est avérée impossible sans risque de doublons, donc `amount2026` est laissé à `null` conformément aux consignes.
- **Blocages / observations** : La qualité du CSV fourni par data.gouv est médiocre. Le nettoyage des headers a été obligatoire.
- **Prochaine tâche recommandée** : Passer à la suite des tâches P1, potentiellement P1.2 (Lauréats Démonstrateurs).

## [2026-07-04] Tâche P1.2 : Ingestion des lauréats Démonstrateurs ville durable

- **Tâche traitée** : P1.2 Ingestion des laureats Demonstrateurs ville durable
- **Fichiers modifiés** : `scripts/15_ingest_fr2030_laureates.py`, `scripts/11_export_to_sqlite.py`, `TODO_ITERATION.md`
- **Résumé des changements** : Création du script d'ingestion pour le fichier de la Caisse des Dépôts. Nettoyage des montants de subventions (incubation + réalisation) pour générer le `grantAmount`. Extraction des indicateurs écologiques. Décomposition en trois entités propres (Projects, Beneficiaries, Territories) qui sont liées aux thèmes et aux programmes via `correlations.json`. Ajout des trois nouvelles tables dans le schéma SQLite.
- **Commandes lancées + résultats** : Exécution du script 15. Export réussi de 39 projets, 39 bénéficiaires, 39 territoires et 156 corrélations déterministes générées. Upsert SQLite réussi sans supprimer la base.
- **Blocages / observations** : Rien de bloquant. La taxonomie d'origine pour les villes durables est rattachée empiriquement au programme 425 et au thème "Pôles et territoires d'innovation" (Score de confiance = 0.8).
- **Prochaine tâche recommandée** : P1.3 Ingestion des projets ADEME

## [2026-07-04] Tâche P1.3 : Ingestion des projets ADEME

- **Tâche traitée** : P1.3 Ingestion des projets ADEME
- **Fichiers modifiés** : `scripts/16_ingest_ademe_research_projects.py`, `TODO_ITERATION.md`
- **Résumé des changements** : Création du script d'ingestion des projets de recherche de l'ADEME. Extraction des montants financés (grant) et du coût total (budget). Mise en relation lexicale des mots-clés ADEME avec la taxonomie locale (score abaissé à 0.6 + validationStatus à "to_validate"). Extraction de plus de 600 nouveaux projets et 700 nouveaux bénéficiaires consolidés dans `projects.json`.
- **Commandes lancées + résultats** : Exécution du script 16. Le nombre de corrélations dans la base SQLite a explosé pour atteindre +2100 relations, ce qui prouve la richesse de ce jeu de données open data.
- **Blocages / observations** : Beaucoup de SIRET partiels ou manquants dans la base ADEME, le fallback a été fait sur un hash du nom du bénéficiaire.
- **Prochaine tâche recommandée** : P1.4 Ingestion brevets par SIREN

## [2026-07-04] Tâche P1.4 : Ingestion brevets par SIREN

- **Tâche traitée** : P1.4 Ingestion brevets par SIREN
- **Fichiers modifiés** : `scripts/17_ingest_patent_depositors.py`, `scripts/11_export_to_sqlite.py`, `scripts/13_export_to_front_contract.py`, `TODO_ITERATION.md`
- **Résumé des changements** : Création du script d'ingestion INPI. Le fichier CSV de 900k lignes est lu par morceaux (`chunksize=100000`) et filtré en mémoire vive grâce au set de SIREN pré-existants. Les données de propriété intellectuelle (Nb demandes et Nb de familles de brevets DOCDB) sont consolidées dans SQLite et retranscrites dans `inpi-patent-families.json`.
- **Commandes lancées + résultats** : Exécution de `17`. Le fichier cible contient désormais les brevets d'entreprises clés (Ex: Ynsect a déposé 366 demandes).
- **Blocages / observations** : Rien de bloquant. La lecture par chunks a parfaitement pallié les problèmes de RAM.
- **Prochaine tâche recommandée** : P1.5 Registre des sources
