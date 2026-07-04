# TODO Iteration - Reprise du socle France 2030

Ce document consolide les constats de `BILAN.md`, `RECAP_BLOCAGES.md`, `RECAP_STREAMLIT.md` et `RETOUR.md`. Il sert de feuille de route concrete pour la prochaine iteration du projet **France 2030 - Scraping & Data Correlation**.

L'objectif est de passer d'un POC deja fonctionnel a un socle de donnees plus fiable, plus source, plus explicable et plus simple a maintenir.

---

## 0. Contexte projet a garder en tete

Le projet cherche a construire une base de donnees locale qui relie :

- les programmes budgetaires France 2030 `421`, `422`, `423`, `424`, `425` ;
- les lignes budgetaires par programme, annee et categorie de depense ;
- les objectifs et actions issus des donnees PAP ;
- une taxonomie thematique France 2030 ;
- les mots-cles permettant de detecter des sujets dans les sources externes ;
- les appels a projets, dispositifs et projets laureats ;
- les entreprises, SIREN, codes NAF et signaux d'innovation ;
- les mentions parlementaires et leur contexte ;
- les correlations explicites entre toutes ces entites.

Le depot contient deja :

- un pipeline Python sequentiel dans `scripts/` ;
- des fichiers JSON metier dans `data/` ;
- une base SQLite `data/france2030.sqlite` ;
- un export graphe dans `data/neo4j_export/` ;
- un contrat JSON front dans `data/export_front/` puis `dataset/` ;
- un Streamlit interne dans `app/` pour explorer et controler les donnees.

Le perimetre prioritaire reste **data engineering / scraping / structuration / correlation**. Le Streamlit est un outil de controle interne, pas le produit principal.

---

## 1. Contraintes non negociables

- [ ] Respecter les schemas JSON existants ou documenter explicitement toute evolution.
- [ ] Garder les noms de cles JSON en `camelCase` et en anglais.
- [ ] Ne jamais inventer une donnee manquante : utiliser `null`, `[]`, ou `isMock: true`.
- [ ] Ajouter `sourceUrl`, `sourceDocument`, `sourceDatasetId` ou `sourceResourceId` des qu'une donnee provient d'une source externe.
- [ ] Ajouter un `confidenceScore` pour toute correlation non strictement identifiee par une cle exacte.
- [ ] Mettre `validationStatus: "to_validate"` pour toute relation avec `confidenceScore < 0.7`.
- [ ] Conserver le contexte parlementaire avec `contextBefore` et `contextAfter`.
- [ ] Rendre les scripts idempotents : relancer le pipeline ne doit pas dupliquer les donnees ni changer les IDs stables.
- [ ] Privilegier les API et exports open data officiels avant le scraping HTML ou PDF.
- [ ] Garder les fichiers de sortie separes et lisibles : budget, themes, projets, entreprises, mentions, correlations.

---

## 2. Etat connu au demarrage de l'iteration

Etat observe dans le depot au moment du bilan :

- `programs.json` : 5 programmes.
- `budget_lines.json` : 11 lignes budgetaires, avec `amount2024` et `amount2025`, mais `amount2026` encore `null`.
- `themes.json` : 20 themes.
- `keywords.json` : 107 mots-cles, avec un doublon d'ID `kw-satt`.
- `calls_for_projects.json` : 4 AAP statiques, utiles comme echantillon mais non exhaustifs.
- `parliament_mentions.json` : 63 mentions, toutes rattachees au programme `424`.
- `companies.json` : 8 entreprises, issues d'une liste de SIREN hardcodee.
- `correlations.json` : 43 correlations, IDs deterministes.
- Plusieurs exports front sont encore des mocks vides : `data-gouv-datasets.json`, `inpi-patent-families.json`, `company-revenues.json`, `investment-programme-reports.json`, `investment-programme-dataviz.json`.

Ecarts techniques verifies :

- `scripts/11_export_to_sqlite.py` supprime encore la base avec `os.remove(db_path)`.
- `scripts/12_export_graph_neo4j.py` attend `companyName` et `nafCode`, alors que SQLite expose `denominationUniteLegale` et `activitePrincipaleUniteLegale`.
- `scripts/07_fetch_parliament_mentions.py` definit `is_relevant_mention()` mais ne l'applique pas dans le flux courant.
- Les textes parlementaires contiennent encore du HTML.
- Le projet parle parfois de PLF 2026, mais l'extraction principale exploite surtout PLF 2024/2025.

---

## 3. Sources ouvertes a exploiter en priorite

### 3.1 PLF 2026 - Budget vert

- URL : `https://www.data.gouv.fr/datasets/plf-2026-budget-vert/`
- Dataset ID : `6916717fd1613a14a77b95df`
- Ressource CSV : `https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/plf-2026-budget-vert/exports/csv?use_labels=true`
- Valeur attendue :
  - remplir `amount2026` quand la correspondance programme/action/titre est fiable ;
  - produire `green_budget_lines.json` ;
  - ajouter des parts `Favorable`, `Neutre`, `NC` par programme ;
  - creer un signal d'impact environnemental.

### 3.2 Liste des laureats "Demonstrateurs ville durable" - France 2030

- URL : `https://www.data.gouv.fr/datasets/liste-des-laureats-demonstrateurs-ville-durable-france-2030/`
- Dataset ID : `636c418c159330f20df64c85`
- Organisation : Caisse des Depots
- Valeur attendue :
  - remplacer une partie des AAP statiques par de vrais projets ;
  - recuperer beneficiaires, porteurs, partenaires, communes, regions ;
  - recuperer montants engages et indicateurs d'impact ;
  - creer des relations projet -> territoire -> theme -> programme.

### 3.3 Les sites cles en main - France 2030

- URL : `https://www.data.gouv.fr/datasets/les-sites-cles-en-main-france-2030/`
- Dataset ID : `662a4bc173fcdf4bab4ef1b6`
- Valeur attendue :
  - ajouter une dimension territoriale industrielle ;
  - produire des liens commune/site/maturite.

### 3.4 Projets de recherche ADEME depuis 2021

- Vue agregee : `https://www.data.gouv.fr/datasets/projets-de-recherche-ademe-vue-agregee-depuis-2021/`
- Dataset ID : `675989349d0cd0356d9ddcde`
- Vue detaillee : `https://www.data.gouv.fr/datasets/projets-de-recherche-ademe-vue-detaillee-depuis-2021/`
- Dataset ID : `67597783fd21598e5b511399`
- Valeur attendue :
  - recuperer `identifier`, `title`, `keywords`, `budget.amount`, `budget.grant`, `grantee.name` ;
  - relier projets, beneficiaires et themes avec une preuve plus forte que le matching lexical.

### 3.5 Deposants des brevets

- URL : `https://www.data.gouv.fr/datasets/deposants-des-brevets-1/`
- Dataset ID : `63b4ebd006676a13059dde9a`
- Valeur attendue :
  - exploiter `siren`, `nom_demandeur`, `key_appln_nr`, `nr_famille_docdb` ;
  - alimenter `inpi-patent-families.json` ;
  - produire un signal d'innovation par entreprise.

### 3.6 API Aides Territoires

- URL catalogue : `https://www.data.gouv.fr/dataservices/672cf9b850f5422ee3ea8775/`
- Base API : `https://aides-territoires.beta.gouv.fr/api`
- Valeur attendue :
  - identifier des dispositifs proches des themes France 2030 ;
  - ne pas utiliser comme preuve de financement si aucun laureat/montant n'est present.

---

## 4. Definition of Done globale

L'iteration est consideree reussie si :

- [ ] `make run-scraping` termine sans erreur sur une machine propre apres installation des dependances.
- [ ] `make export-front` regenere les fichiers `dataset/**` sans casse de schema.
- [ ] `amount2026` est renseigne ou explicitement justifie comme indisponible.
- [ ] Au moins un fichier front actuellement mocke est remplace par une vraie source.
- [ ] `data/quality_report.json` liste les mocks, trous, doublons, scores faibles et champs manquants.
- [ ] Les correlations nouvelles ont `sourceUrl`, `confidenceScore`, `validationStatus` et IDs deterministes.
- [ ] Les textes parlementaires sont nettoyes du HTML et conservent un contexte exploitable.
- [ ] L'export Neo4j fonctionne avec le schema SQLite courant.
- [ ] Le Streamlit lit les nouvelles donnees sans `SELECT *` massif ni rendu de milliers de composants.

---

## 5. Plan d'action priorise

### P0 - Stabiliser le socle existant avant d'ajouter de la donnee

#### P0.1 Reconciliation documentation/code

- [x] Relire `README.md`, `RECAP.md`, `BILAN.md`, `RECAP_BLOCAGES.md`, `RETOUR.md` et aligner les affirmations contradictoires.
- [x] Indiquer clairement que le pipeline budget courant est base sur PLF 2024/2025, avec un chantier PLF 2026 a ajouter.
- [x] Remplacer les mentions "termine" ou "entierement valide" par un statut plus precis : POC fonctionnel, industrialisation en cours.
- [x] Ajouter une section "donnees reelles vs echantillons vs mocks" dans `README.md`.
- [x] Mettre a jour `DATASETS.md` si le schema ajoute `projects`, `project_beneficiaries`, `green_budget_lines`, `source_registry`.

Critere d'acceptation :

- [x] Un lecteur externe peut comprendre ce qui est reel, partiel, mocke et a faire sans lire tout le code.

#### P0.2 Controle qualite automatique

- [x] Creer `scripts/18_generate_quality_report.py`.
- [x] Mesurer les volumes de chaque fichier JSON.
- [x] Detecter les IDs dupliques (`kw-satt`, correlations, companies, mentions, budget lines).
- [x] Detecter les champs critiques manquants : `sourceUrl`, `confidenceScore`, `validationStatus`, `amount2026`, `contextAfter`.
- [x] Detecter les fichiers front contenant `isMock: true`.
- [x] Detecter les relations avec `confidenceScore < 0.7`.
- [x] Sortir `data/quality_report.json`.
- [x] Ajouter une cible `make quality-report`.

Critere d'acceptation :

- [x] Le rapport qualite peut etre genere sans relancer tout le scraping.
- [x] Le rapport donne une liste actionnable de problemes, pas seulement des compteurs.

#### P0.3 Stabilite des IDs et schema

- [x] Corriger le doublon `kw-satt` dans `scripts/05_generate_keywords.py`.
- [x] Decider de la strategie d'ID keyword : `kw-{themeId}-{keywordSlug}` ou `kw-{keywordSlug}-{hash(themeId)}`.
- [x] Verifier que `correlations.json` conserve des IDs deterministes apres regeneration.
- [x] Ajouter un script de validation schema minimal dans `scripts/19_validate_json_contracts.py`.
- [x] Valider au minimum `programs`, `budget_lines`, `themes`, `keywords`, `companies`, `mentions`, `correlations`.

Critere d'acceptation :

- [x] Deux executions consecutives du pipeline produisent les memes IDs pour les memes entites.
- [x] Les duplications d'IDs sont signalees avant l'export SQLite.

#### P0.4 SQLite incremental et non destructif

- [x] Supprimer le `os.remove(db_path)` de `scripts/11_export_to_sqlite.py`.
- [x] Garder `CREATE TABLE IF NOT EXISTS`.
- [x] Utiliser `INSERT OR REPLACE` sur toutes les tables.
- [x] Ajouter une option explicite `--reset` si une reconstruction totale est necessaire.
- [x] Ajouter une table `ingestion_runs` avec `runId`, `startedAt`, `completedAt`, `status`, `sourceFiles`.
- [x] Ne pas perdre l'historique si un JSON intermediaire est temporairement absent.

Critere d'acceptation :

- [x] Relancer `scripts/11_export_to_sqlite.py` deux fois ne supprime pas les tables ni les donnees valides.
- [x] Une reconstruction destructive n'est possible que via une option explicite.

#### P0.5 Export Neo4j realigne

- [x] Modifier `scripts/12_export_graph_neo4j.py` pour utiliser `denominationUniteLegale` comme nom entreprise.
- [x] Modifier `scripts/12_export_graph_neo4j.py` pour utiliser `activitePrincipaleUniteLegale` comme code NAF.
- [x] Echaper proprement les virgules, guillemets et retours ligne via `csv.writer`.
- [x] Conserver `weight:float` depuis `confidenceScore`.
- [x] Ajouter les nouveaux types de noeuds si crees : `Project`, `Territory`, `PatentFamily`, `SourceDataset`.

Critere d'acceptation :

- [x] `make export-neo4j` fonctionne avec le schema SQLite courant.
- [x] Les CSV produits sont importables dans Neo4j ou Gephi sans correction manuelle.

---

### P1 - Ajouter les sources qui augmentent vraiment la valeur

#### P1.1 Ingestion PLF 2026 Budget vert

- [x] Creer `scripts/14_ingest_budget_vert_2026.py`.
- [x] Telecharger la ressource CSV Budget vert avec retry et cache local.
- [x] Filtrer sur `Mission == "Investir pour la France de 2030"`.
- [x] Normaliser les colonnes dont les noms contiennent des retours ligne.
- [x] Produire `data/green_budget_lines.json`.
- [x] Agreger les montants par `programmeCode`, `actionCode`, `globalRating`.
- [x] Remplir `amount2026` dans `budget_lines.json` uniquement si la jointure est fiable.
- [x] Sinon, conserver `amount2026: null` et ajouter une note dans `quality_report.json`.
- [x] Ajouter les lignes correspondantes en SQLite.
- [x] Ajouter les correlations `programme -> greenBudgetLine`.

Critere d'acceptation :

- [x] Les programmes 421 a 425 ont un resume Budget vert 2026.
- [x] Les montants agreges sont sources et tracables.
- [x] Le front peut afficher une metrique environnementale sans mock.

#### P1.2 Ingestion des laureats Demonstrateurs ville durable

- [x] Creer `scripts/15_ingest_fr2030_laureates.py`.
- [x] Telecharger CSV ou JSON depuis la Caisse des Depots.
- [x] Produire `data/projects.json`.
- [x] Produire `data/project_beneficiaries.json`.
- [x] Produire `data/territories.json`.
- [x] Normaliser `region`, `departement`, `communeCode`, `communeName`.
- [x] Extraire `grantAmount` depuis montants incubation/realisation.
- [x] Extraire les indicateurs d'impact : CO2 evite, kWh evites, EnR, surfaces renaturees, surfaces depolluees.
- [x] Mapper les thematiques source vers `themeId` avec un `confidenceScore`.
- [x] Mettre `validationStatus: "to_validate"` si le mapping thematique est seulement lexical.
- [x] Ajouter les correlations `project -> theme`, `project -> territory`, `project -> beneficiary`, `project -> programme`.

Critere d'acceptation :

- [x] Au moins un fichier front mocke peut etre remplace par de vraies donnees territoriales/projets.
- [x] Chaque projet a une source et un ID deterministe.

#### P1.3 Ingestion des projets ADEME

- [x] Creer `scripts/16_ingest_ademe_research_projects.py`.
- [x] Recuperer la vue agregee ADEME depuis 2021.
- [x] Produire `data/research_projects.json` (On utilise directement la table unifiée `projects.json`).
- [x] Conserver `identifier`, `title`, `keywords`, `budgetAmount`, `grantAmount`, `startDate`, `endDate`, `status`, `granteeName`.
- [x] Tenter une reconciliation `granteeName -> SIREN` seulement si le score est suffisant.
- [x] Eviter l'homonymie : ne jamais valider automatiquement un SIREN trouve par nom seul si plusieurs candidats existent.
- [x] Mapper `keywords` vers `themeId`.
- [x] Ajouter `sourceDatasetId`, `sourceResourceId`, `sourceUrl`.
- [x] Ajouter les correlations `researchProject -> theme`, `researchProject -> beneficiary`.

Critere d'acceptation :

- [x] Les projets ADEME enrichissent les themes avec des montants reels de subvention.
- [x] Les beneficiaires incertains sont marques `to_validate`.

#### P1.4 Ingestion brevets par SIREN

- [x] Creer `scripts/17_ingest_patent_depositors.py`.
- [x] Lire le dataset `deposants-des-brevets`.
- [x] Filtrer d'abord sur les SIREN deja presents dans `companies.json` pour eviter de charger inutilement 900k+ lignes en memoire.
- [x] Produire `data/patent_depositors.json`.
- [x] Agreger par `siren` : nombre de demandes, nombre de familles `nr_famille_docdb`, liste d'exemples.
- [x] Exporter vers `data/export_front/inpi-patent-families.json`.
- [x] Mettre `isMock: false` pour les programmes qui ont des entreprises avec brevets.
- [x] Ajouter les correlations `company -> patentFamily`.

Critere d'acceptation :

- [x] `dataset/sources/inpi-patent-families.json` n'est plus un mock vide pour les entreprises ayant des brevets.
- [x] La jointure se fait par `siren`, pas par nom.

#### P1.5 Registre des sources

- [x] Creer `data/sources.json`.
- [x] Ajouter une entree par source : Budget PLF 2024, Budget PLF 2025, PAP 2025, Budget vert 2026, Sirene, NosDeputes, Demonstrateurs ville durable, ADEME, Brevets.
- [x] Pour chaque source, renseigner `sourceId`, `name`, `datasetId`, `resourceId`, `url`, `license`, `producer`, `updateFrequency`, `lastCheckedAt`, `ingestionScript`.
- [x] Faire reference a `sourceId` dans les nouveaux JSON quand c'est pertinent.

Critere d'acceptation :

- [x] Une personne peut auditer toutes les sources sans ouvrir les scripts Python.

---

### P2 - Fiabiliser les extractions existantes

#### P2.1 Mentions parlementaires

- [x] Appliquer reellement `is_relevant_mention()` dans `scripts/07_fetch_parliament_mentions.py`.
- [x] Remplacer le filtre actuel par un filtre de proximite plus strict : `France 2030`, `PIA`, `investissement`, `subvention`, `budget`, `milliard`, ou nom de dispositif dans une fenetre de mots.
- [x] Nettoyer le HTML avec BeautifulSoup ou un helper de nettoyage texte.
- [x] Extraire `contextBefore` et `contextAfter` a partir de phrases voisines, pas seulement du sujet.
- [x] Ajouter `matchedSentence` (nommé `interventionText` en base de données pour ce hackathon).
- [x] Ajouter `matchMethod`: `exact_keyword`, `keyword_with_context`, `manual_source`, `llm_classifier`.
- [x] Ajouter `validationStatus`.
- [x] Gerer la pagination NosDeputes si l'API l'expose (Remplacé par la gestion en `asyncio` sur les résultats initiaux).
- [x] Limiter le debit pour respecter la source.
- [ ] Prevoir une alternative LesTricoteuses ou Open Data Assemblee si NosDeputes devient limitant.

Critere d'acceptation :

- [x] Les mentions hors sujet sont reduites.
- [x] Les programmes autres que `424` peuvent recevoir des mentions si leurs themes sont detectes.
- [x] Les verbatims sont lisibles sans balises HTML.

#### P2.2 AAP et dispositifs

- [x] Conserver les 4 AAP statiques comme `seed` ou `sample`, pas comme source exhaustive.
- [x] Ajouter un champ `dataCompleteness: "sample"` dans `calls_for_projects.json` si la source reste statique.
- [x] Tester d'abord les datasets data.gouv.fr et Bpifrance/ADEME avant de mettre en place Playwright.
- [x] Si scraping `info.gouv.fr` reste necessaire, isoler le scraper dans un script dedie et documenter le blocage Cloudflare.
- [x] Ne pas contourner Cloudflare sans justification claire : preferer une source open data brute.

Critere d'acceptation :

- [x] Le statut des AAP ne laisse pas croire a une couverture exhaustive.
- [x] Les AAP nouveaux ont une source exploitable et stable.

#### P2.3 Entreprises et SIREN

- [x] Remplacer progressivement la liste hardcodee de SIREN dans `09_fetch_companies.py` par des SIREN issus des sources laureats/projets.
- [x] Conserver les 8 entreprises actuelles comme echantillon de reference.
- [x] Ajouter une table `company_aliases.json` si les sources utilisent des noms differents (Non nécessaire : on filtre purement sur les SIREN officiels).
- [x] Ajouter une reconciliation prudente nom -> SIREN avec score et statut de validation.
- [x] Ajouter l'adresse siege ou commune si disponible dans Sirene pour enrichir la dimension territoriale.
- [x] Ajouter `nafLabel` depuis une source officielle NAF si possible.

Critere d'acceptation :

- [x] Une entreprise reliee a un projet a une preuve de provenance autre qu'une liste hardcodee.
- [x] Les reconciliations incertaines ne sont pas marquees `validated`.

#### P2.4 Taxonomie et mapping metier

- [x] Garder `config/taxonomy.json` comme source principale editable.
- [x] Ajouter `description`, `officialObjective`, `programmeCode`, `keywords`, `negativeKeywords` si necessaire.
- [x] Ajouter des mots-cles d'exclusion pour reduire les faux positifs parlementaires.
- [x] Documenter les mappings theme -> programme.
- [x] Ajouter un champ `taxonomyVersion`.

Critere d'acceptation :

- [x] Un changement de taxonomie est versionne et explique.
- [x] Les mappings ambigus sont identifies.

---

### P3 - Rendre les correlations plus explicables

#### P3.1 Nouveau modele de preuve

- [x] Ajouter un bloc `evidence` aux nouvelles correlations.
- [x] Inclure `sourceUrl`, `sourceDatasetId`, `sourceResourceId`, `matchedField`, `matchedValue`, `matchMethod`.
- [x] Documenter les niveaux de `confidenceScore`.
- [x] Mettre `validationStatus` selon le score.
- [x] Garder les anciennes correlations compatibles avec le schema existant.

Critere d'acceptation :

- [x] On peut expliquer pourquoi deux entites sont reliees sans relire tout le code.

#### P3.2 Relations a plus forte valeur

- [ ] Produire `programme -> budgetLine`.
- [ ] Produire `programme -> greenBudgetLine`.
- [ ] Produire `programme -> theme`.
- [ ] Produire `theme -> keyword`.
- [ ] Produire `project -> theme`.
- [ ] Produire `project -> beneficiary`.
- [ ] Produire `beneficiary -> company` quand SIREN est confirme.
- [ ] Produire `company -> nafCode`.
- [ ] Produire `company -> patentFamily`.
- [ ] Produire `parliamentMention -> theme`.
- [ ] Produire `parliamentMention -> programme`.
- [ ] Produire `territory -> project`.

Critere d'acceptation :

- [ ] Les graphes ne sont plus seulement "programme -> theme -> entreprise", mais aussi "source -> projet -> beneficiaire -> preuve".

#### P3.3 Scores analytiques

- [x] Recalculer `programme-alignment-scores.json` avec plusieurs dimensions.
- [x] Dimension `financialWeight`: poids budgetaire.
- [x] Dimension `politicalAttention`: mentions parlementaires qualifiees par milliard d'euros.
- [x] Dimension `greenBudget`: part favorable Budget vert.
- [x] Dimension `innovationSignal`: brevets et projets R&D.
- [x] Dimension `territorialDeployment`: nombre de projets/territoires relies.
- [x] Documenter la formule dans `notes`.
- [x] Sauvegarder les poids dans un fichier de configuration, pas en dur dans le script.

Critere d'acceptation :

- [x] Le score d'alignement devient explicable et rejouable.
- [x] Le Streamlit peut simuler les poids et exporter la configuration retenue.

---

### P4 - Contrat front et Streamlit de controle

#### P4.1 Exports front a democker en priorite

- [x] `dataset/sources/inpi-patent-families.json` via le dataset brevets.
- [x] `dataset/sources/data-gouv-datasets.json` via `data/sources.json`.
- [x] `dataset/dataviz/investment-programme-dataviz.json` via agregats budget, budget vert, mentions, projets.
- [ ] `dataset/reports/investment-programme-reports.json` via synthese par programme.
- [ ] `dataset/sources/company-revenues.json` seulement si une source fiable est identifiee ; sinon rester mock avec justification.

Critere d'acceptation :

- [x] Chaque fichier exporte indique clairement `isMock`, `sourceUrl`, `confidence`, `updatedAt`, `notes`.

#### P4.2 Streamlit - robustesse et audit

- [x] Eviter les `SELECT *` massifs dans les pages Streamlit (Fait, requêtes optimisées ou datasets JSON).
- [x] Garder la pagination des verbatims.
- [x] Ajouter un bouton de telechargement CSV/Excel dans la vue transversale.
- [x] Ajouter une heatmap simple de completude par programme.
- [x] Afficher `data/quality_report.json` dans la page Data Quality.
- [x] Afficher les sources actives depuis `data/sources.json`.
- [x] Permettre d'exporter la configuration de ponderation du score.
- [x] Ne pas faire du Streamlit une dependance obligatoire du pipeline data.

Critere d'acceptation :

- [x] Le Streamlit reste utilisable meme si le volume de mentions augmente fortement.
- [x] La page Data Quality permet d'identifier les prochains trous de donnees.

---

### P5 - Industrialisation minimale

#### P5.1 Helpers communs

- [x] Creer `scripts/lib/`.
- [x] Ajouter `download.py` pour requetes HTTP avec retry, timeout, cache et user-agent.
- [x] Ajouter `json_io.py` pour lecture/ecriture atomique JSON.
- [x] Ajouter `text.py` pour nettoyage HTML, espaces invisibles et normalisation.
- [x] Ajouter `ids.py` pour generation d'IDs deterministes.
- [x] Ajouter `sources.py` pour lire/ecrire `data/sources.json`.

Critere d'acceptation :

- [x] Les nouveaux scripts n'ont pas chacun leur logique de download, nettoyage et hash.

#### P5.2 Makefile et execution

- [ ] Ajouter `make quality-report`.
- [ ] Ajouter `make validate-data`.
- [ ] Ajouter `make export-all` qui lance scraping, SQLite, front, Neo4j, quality report.
- [ ] Ajouter un mode `FAST=1` ou `--sample` pour eviter les gros downloads lors des tests.
- [ ] Documenter les commandes dans `README.md`.

Critere d'acceptation :

- [ ] Un repreneur peut lancer une iteration complete avec des commandes simples.

#### P5.3 Tests pragmatiques

- [ ] Ajouter des tests unitaires sur `generate_id`, nettoyage texte, hash correlation.
- [ ] Ajouter un test de non-regression sur le doublon `kw-satt`.
- [ ] Ajouter un test de schema sur les JSON critiques.
- [ ] Ajouter un test de generation SQLite sur un petit jeu de fixtures.
- [ ] Ajouter un test de l'export Neo4j avec le schema courant.

Critere d'acceptation :

- [ ] Les regressions de schema et d'IDs sont detectees avant de regenerer tous les exports.

---

## 6. Ordre conseille d'execution

1. [ ] Corriger les contradictions et creer `quality_report`.
2. [ ] Corriger `kw-satt`, SQLite non destructif et export Neo4j.
3. [ ] Integrer Budget vert 2026.
4. [ ] Integrer brevets par SIREN pour democker `inpi-patent-families.json`.
5. [ ] Integrer laureats Demonstrateurs ville durable.
6. [ ] Integrer projets ADEME.
7. [ ] Recalculer correlations et scores.
8. [ ] Regenerer SQLite, front, Neo4j et quality report.
9. [ ] Mettre a jour documentation et README.

---

## 7. Livrable cible de cette iteration

Livrable minimum :

- [ ] `data/quality_report.json`
- [ ] `data/sources.json`
- [ ] `data/green_budget_lines.json`
- [ ] `data/patent_depositors.json`
- [ ] `dataset/sources/inpi-patent-families.json` avec `isMock: false` pour les programmes concernes
- [ ] `scripts/14_ingest_budget_vert_2026.py`
- [ ] `scripts/17_ingest_patent_depositors.py`
- [ ] `scripts/18_generate_quality_report.py`
- [ ] `scripts/19_validate_json_contracts.py`
- [ ] `scripts/11_export_to_sqlite.py` non destructif par defaut
- [ ] `scripts/12_export_graph_neo4j.py` compatible avec le schema actuel

Livrable enrichi si temps disponible :

- [ ] `data/projects.json`
- [ ] `data/project_beneficiaries.json`
- [ ] `data/territories.json`
- [ ] `data/research_projects.json`
- [ ] `scripts/15_ingest_fr2030_laureates.py`
- [ ] `scripts/16_ingest_ademe_research_projects.py`
- [ ] nouveaux exports front demockes pour `data-gouv-datasets`, `investment-programme-dataviz`, `investment-programme-reports`

---

## 8. Points d'attention avant implementation

- [ ] Ne pas presenter les 4 AAP actuels comme exhaustifs.
- [ ] Ne pas valider une entreprise par nom seul si plusieurs SIREN candidats existent.
- [ ] Ne pas remplir `amount2026` par approximation si la jointure budgetaire est ambigue.
- [ ] Ne pas melanger les donnees de controle Streamlit avec les donnees canoniques.
- [ ] Ne pas augmenter les volumes parlementaires sans pagination et nettoyage.
- [ ] Ne pas casser le contrat `dataset/**` utilise par le front.
- [ ] Ne pas supprimer les changements utilisateur deja presents dans le depot.

---

## 9. Questions metier a trancher

- [ ] Quel niveau de preuve est requis pour dire qu'une entreprise est beneficiaire France 2030 ?
- [ ] Faut-il privilegier les projets laureats territoriaux ou les aides R&D ADEME pour la prochaine demo ?
- [ ] Le score d'alignement doit-il favoriser le poids budgetaire, l'attention parlementaire, l'impact environnemental ou le signal d'innovation ?
- [ ] Les mentions parlementaires doivent-elles couvrir uniquement l'Assemblee nationale ou aussi le Senat ?
- [ ] Les AAP doivent-ils representer des dispositifs ouverts ou des projets laureats finances ?
- [ ] Est-ce que les fichiers front doivent rester strictement par programme ou accepter des objets transversaux `projects`, `territories`, `sources` ?

---

## 10. Synthese de priorite

La prochaine iteration doit viser la valeur suivante :

1. rendre la qualite observable ;
2. corriger les incoherences qui peuvent casser la confiance ;
3. ajouter le Budget vert 2026 ;
4. democker une source front avec les brevets ;
5. relier de vrais projets/laureats a des montants, territoires et beneficiaires ;
6. produire des correlations mieux preuvees.

Ce chemin apporte plus de valeur que de simplement augmenter le volume de scraping : il rend le socle plus comprehensible, plus audit-able et plus defensible.
