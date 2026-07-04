# Bilan projet - France 2030 Scraping & Data Correlation

Ce document resume l'etat reel du depot apres relecture du code, des exports et des donnees generees. Il sert de point de reprise pour ajouter de la valeur au socle data sans complexifier inutilement le projet.

## 1. Ce que le projet cherche a faire

Le projet construit un socle de donnees local autour de la mission budgetaire **Investir pour la France de 2030**. L'objectif n'est pas de produire un dashboard, mais de relier des donnees publiques heterogenes :

- programmes budgetaires 421 a 425 ;
- lignes de credits budgetaires par programme et titre de depense ;
- objectifs et actions issus des donnees PAP ;
- taxonomie France 2030 et mots-cles ;
- mentions parlementaires detectees par mots-cles ;
- appels a projets ou dispositifs France 2030 ;
- entreprises / SIREN / codes NAF ;
- correlations entre ces entites, exportees en JSON, SQLite, CSV Neo4j et contrat JSON front.

Le depot a donc deja une vraie ossature d'acquisition, de structuration et d'export.

## 2. Etat actuel verifie

Volumes actuellement presents dans `data/` et `data/france2030.sqlite` :

| Entite | Volume | Commentaire |
| --- | ---: | --- |
| Programmes | 5 | Programmes 421, 422, 423, 424, 425 extraits depuis le PLF 2025. |
| Lignes budgetaires | 11 | Montants 2024/2025 presents, `amount2026` encore vide partout. |
| Themes | 20 | Generes depuis `config/taxonomy.json`. |
| Mots-cles | 107 JSON / 106 SQLite | Un doublon d'identifiant existe : `kw-satt`. |
| Appels a projets | 4 | Echantillon statique realiste, pas une ingestion exhaustive. |
| Mentions parlementaires | 63 | Toutes rattachees au programme 424 dans l'etat courant. |
| Entreprises | 8 | SIREN cibles hardcodes, enrichis via le stock Sirene. |
| Codes NAF | 6 | Generes depuis les entreprises trouvees. |
| Correlations | 43 | IDs deterministes par hash MD5. |

Budgets CP actuellement agreges dans SQLite :

| Programme | CP 2024 | CP 2025 | CP 2026 |
| --- | ---: | ---: | ---: |
| 421 | 0,255 Md EUR | 0,219 Md EUR | null |
| 422 | 0,088 Md EUR | 0,243 Md EUR | null |
| 423 | 0,014 Md EUR | 0,186 Md EUR | null |
| 424 | 5,692 Md EUR | 4,373 Md EUR | null |
| 425 | 1,653 Md EUR | 0,779 Md EUR | null |

Exports deja presents :

- `data/*.json` : fichiers metier intermediaires ;
- `data/france2030.sqlite` : base relationnelle locale ;
- `data/neo4j_export/*.csv` : export graphe ;
- `data/export_front/*.json` puis `dataset/**` : contrat JSON pour consommation front ;
- `app/` : Streamlit de controle interne, utile pour explorer le contrat JSON.

## 3. Ce qui est solide

Le projet a deja plusieurs points forts :

- la structure des donnees est comprehensible et modulaire ;
- le pipeline est scriptable via `Makefile` ;
- les budgets et les objectifs PAP proviennent de sources publiques officielles ;
- la taxonomie est sortie du code et centralisee dans `config/taxonomy.json` ;
- les correlations ont maintenant des identifiants deterministes ;
- le contrat front est genere automatiquement depuis SQLite ;
- le Streamlit expose deja un controle de maturite `isMock` et un simulateur de score.

## 4. Limites importantes a traiter

Ces points sont les principaux risques de qualite de donnee.

1. **Le projet parle parfois de PLF 2026, mais le pipeline budget principal utilise surtout PLF 2024 et PLF 2025.**  
   `amount2026` est encore `null` dans toutes les lignes budgetaires. Le dataset `PLF 2026 - Budget vert` permet de combler une partie de ce manque.

2. **Les AAP ne sont pas encore scrapés dynamiquement.**  
   `scripts/06_scrape_calls_for_projects.py` contient 4 appels a projets statiques. C'est acceptable pour un POC, mais il faut les marquer comme echantillon et les remplacer par des sources ouvertes exploitables.

3. **Les mentions parlementaires restent trop partielles.**  
   Le script est asynchrone, mais il ne traite qu'un sous-ensemble de mots-cles et de resultats. La fonction `is_relevant_mention()` existe mais n'est pas appliquee. Les textes contiennent encore du HTML et `contextAfter` est souvent vide.

4. **Les entreprises ne viennent pas d'une source de laureats exhaustive.**  
   Les 8 SIREN sont hardcodes dans `09_fetch_companies.py`. La relation entreprise -> theme est donc fiable pour l'echantillon, mais pas exhaustive et pas strictement reliee a un `callId`.

5. **SQLite n'est pas encore un vrai upsert incremental.**  
   `scripts/11_export_to_sqlite.py` supprime encore `data/france2030.sqlite` avec `os.remove(db_path)`. La documentation dit parfois l'inverse.

6. **Le contrat Neo4j est a realigner.**  
   `scripts/12_export_graph_neo4j.py` attend `companyName` et `nafCode`, mais la table SQLite actuelle contient `denominationUniteLegale` et `activitePrincipaleUniteLegale`. L'export CSV present semble donc issu d'un ancien schema.

7. **Plusieurs fichiers front restent des mocks vides.**  
   `data-gouv-datasets.json`, `inpi-patent-families.json`, `company-revenues.json`, `investment-programme-reports.json` et `investment-programme-dataviz.json` sont generes pour eviter les crashs, mais ne portent pas encore de valeur data.

## 5. Sources data.gouv.fr pertinentes a ajouter

Recherche effectuee dans le catalogue data.gouv.fr. Les sources ci-dessous sont les meilleures candidates pour remplacer les mocks et enrichir les correlations.

### 5.1 PLF 2026 - Budget vert

- URL : https://www.data.gouv.fr/datasets/plf-2026-budget-vert/
- Dataset ID : `6916717fd1613a14a77b95df`
- Ressource CSV : `https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/plf-2026-budget-vert/exports/csv?use_labels=true`
- Interet :
  - contient la mission `Investir pour la France de 2030` ;
  - apporte des montants CP 2026 ;
  - ajoute une cotation environnementale : favorable, neutre, non cote ;
  - permet un score supplementaire `greenBudgetShare`.

Extraction rapide observee sur la mission France 2030 : 71 lignes. Exemples d'agregats PLF 2026 par cotation :

| Programme | Cotation | Montant PLF 2026 |
| --- | --- | ---: |
| 424 | Favorable | 1,675 Md EUR |
| 424 | Neutre | 1,569 Md EUR |
| 424 | NC | 0,510 Md EUR |
| 425 | Favorable | 0,238 Md EUR |
| 425 | Neutre | 1,092 Md EUR |

Priorite : tres haute. C'est la meilleure source pour combler `amount2026` et enrichir les lignes budgetaires.

### 5.2 Liste des laureats "Demonstrateurs ville durable" - France 2030

- URL : https://www.data.gouv.fr/datasets/liste-des-laureats-demonstrateurs-ville-durable-france-2030/
- Dataset ID : `636c418c159330f20df64c85`
- Organisation : Caisse des Depots
- Derniere mise a jour observee : 2026-05-05
- Ressources : CSV, JSON, GeoJSON, SHP
- Interet :
  - vrais projets laureats France 2030 ;
  - beneficiaire, porteur projet, partenaires, commune, region ;
  - montants engages incubation / realisation ;
  - indicateurs d'impact : CO2 evite, kWh evites, surfaces renaturees, surfaces depolluees ;
  - thematiques et innovations ville durable.

Priorite : tres haute. Cette source peut remplacer une partie des AAP statiques par de vrais projets finances et geolocalises.

### 5.3 Les sites cles en main - France 2030

- URL : https://www.data.gouv.fr/datasets/les-sites-cles-en-main-france-2030/
- Dataset ID : `662a4bc173fcdf4bab4ef1b6`
- Organisation : ANCT
- Ressource CSV : 55 communes observees via l'API tabulaire
- Colonnes utiles : `id_site`, `insee_com`, `lib_com`, `maturite_site`
- Interet :
  - ajoute une dimension territoriale et industrielle ;
  - utile pour relier France 2030 a des communes et a des sites industriels.

Priorite : moyenne. Simple a integrer et utile pour l'analyse territoriale.

### 5.4 Projets de recherche ADEME - depuis 2021

- Vue agregée : https://www.data.gouv.fr/datasets/projets-de-recherche-ademe-vue-agregee-depuis-2021/
- Dataset ID agrege : `675989349d0cd0356d9ddcde`
- Vue detaillee : https://www.data.gouv.fr/datasets/projets-de-recherche-ademe-vue-detaillee-depuis-2021/
- Dataset ID detaille : `67597783fd21598e5b511399`
- Organisation : ADEME
- Derniere mise a jour observee : 2026-06-27 pour la vue detaillee
- Volume tabulaire observe sur la vue agregee : 651 lignes
- Colonnes utiles :
  - `identifier`
  - `title`
  - `keywords`
  - `budget.amount`
  - `budget.grant`
  - `start_date`
  - `status`
  - `grantee.name`

Priorite : haute. Cette source donne des montants de subvention et des beneficiaires, donc une correlation plus forte que les simples mots-cles.

### 5.5 Deposants des brevets

- URL : https://www.data.gouv.fr/datasets/deposants-des-brevets-1/
- Dataset ID : `63b4ebd006676a13059dde9a`
- Organisation : Ministere de l'Enseignement superieur, de la Recherche et de l'Espace
- Volume observe via API tabulaire : 949 226 lignes
- Colonnes utiles :
  - `key_appln_nr`
  - `nr_famille_docdb`
  - `nom_demandeur`
  - `siren`

Priorite : haute. Le champ `siren` permet une jointure directe avec `companies.json` et peut alimenter le fichier front encore mocke `inpi-patent-families.json`.

### 5.6 API Aides Territoires

- URL catalogue : https://www.data.gouv.fr/dataservices/672cf9b850f5422ee3ea8775/
- Base API : `https://aides-territoires.beta.gouv.fr/api`
- Interet :
  - catalogue de dispositifs d'aides publiques ;
  - utile pour trouver des dispositifs proches France 2030, meme si ce n'est pas une source stricte de laureats.

Priorite : moyenne. A utiliser comme source de dispositifs, pas comme preuve de financement.

## 6. Analyses et correlations a forte valeur

Les enrichissements les plus utiles ne sont pas seulement de nouveaux fichiers. Il faut produire des relations plus explicables.

1. **Budget x attention parlementaire**  
   Mesurer les mentions par milliard d'euros et par theme, pas seulement le nombre brut de mentions. Aujourd'hui, le score est fortement biaise car toutes les mentions collectees sont rattachees au programme 424.

2. **Budget vert x taxonomie**  
   Ajouter pour chaque programme et theme une part favorable / neutre / non cotee. Exemple : `greenBudgetShare`, `neutralBudgetShare`, `unratedBudgetShare`.

3. **Projet finance x beneficiaire x SIREN**  
   Creer une table stricte `project_beneficiaries.json` avec `projectId`, `beneficiaryName`, `siren`, `grantAmount`, `sourceUrl`, `confidenceScore`. Cette table doit devenir le pivot entre AAP, entreprises et themes.

4. **Entreprise x brevets x France 2030**  
   Pour chaque SIREN laureat, compter les familles de brevets et deposants associes. Cela donne un signal d'intensite d'innovation plus solide que le seul code NAF.

5. **Territoire x programme x impact**  
   A partir des laureats ville durable et des sites cles en main : region, departement, commune, montants engages, CO2 evite, kWh evites, surfaces renaturees.

6. **Qualite des mentions parlementaires**  
   Nettoyer HTML, extraire de vraies fenetres `contextBefore` / `contextAfter`, puis classifier la pertinence :
   - `validated` si France 2030 ou un dispositif source est cite ;
   - `to_validate` si le lien est purement lexical ;
   - `rejected` si le mot-cle est hors sujet.

## 7. Roadmap pragmatique

### Priorite 0 - Rendre le socle coherent

- Corriger les contradictions de documentation : PLF 2025/2024 vs PLF 2026.
- Ajouter un controle schema simple pour verifier les cles attendues.
- Supprimer le doublon `kw-satt` ou rendre les IDs de mots-cles uniques par theme.
- Faire appliquer `is_relevant_mention()` ou supprimer la fonction si elle n'est pas utilisee.
- Nettoyer le HTML des mentions parlementaires.
- Corriger `11_export_to_sqlite.py` pour ne plus supprimer la base si l'objectif est bien l'upsert.
- Corriger `12_export_graph_neo4j.py` avec les colonnes reelles du schema courant.

### Priorite 1 - Combler les vrais trous data

Scripts proposes :

- `scripts/14_ingest_budget_vert_2026.py`
  - source : PLF 2026 Budget vert ;
  - sortie : enrichissement de `budget_lines.json` ou creation de `green_budget_lines.json`.

- `scripts/15_ingest_fr2030_laureates.py`
  - source : laureats Demonstrateurs ville durable ;
  - sorties : `projects.json`, `project_beneficiaries.json`, `territories.json`.

- `scripts/16_ingest_ademe_research_projects.py`
  - source : projets ADEME depuis 2021 ;
  - sorties : `research_projects.json`, correlations projet -> theme -> beneficiaire.

- `scripts/17_ingest_patent_depositors.py`
  - source : deposants des brevets ;
  - sortie : `patent_depositors.json`, puis export front `inpi-patent-families.json`.

- `scripts/18_generate_quality_report.py`
  - sortie : `data/quality_report.json` avec volumes, mocks, doublons, champs manquants, scores faibles.

### Priorite 2 - Rendre les correlations plus profondes

- Remplacer les relations faibles `company -> theme` par des relations sourcees `company -> project -> programme/theme`.
- Ajouter des `evidence` structurées dans `correlations.json` :
  - `sourceUrl`
  - `sourceDatasetId`
  - `sourceResourceId`
  - `matchedField`
  - `matchMethod`
- Differencier les scores :
  - `1.0` : identifiant exact, SIREN ou code programme ;
  - `0.8-0.9` : matching source + libelle coherent ;
  - `0.6-0.7` : heuristique lexicale ;
  - `<0.7` : `validationStatus = "to_validate"`.

### Priorite 3 - Simplifier la maintenance

- Ajouter `data/sources.json` comme registre unique des sources :
  - `sourceId`
  - `datasetId`
  - `resourceId`
  - `url`
  - `license`
  - `lastCheckedAt`
  - `updateFrequency`
  - `ingestionScript`
- Factoriser les helpers communs dans `scripts/lib/` :
  - telechargement avec retry ;
  - ecriture JSON atomique ;
  - nettoyage texte ;
  - generation d'ID deterministe ;
  - normalisation SIREN / code commune / montant.
- Faire de SQLite le pivot canonique, puis generer tous les JSON finaux depuis SQLite.

## 8. Proposition de modele de donnees additionnel

Nouveaux fichiers JSON utiles :

### `data/projects.json`

```json
[
  {
    "projectId": "fr2030-dvd-auxerre-ambitieuse",
    "projectName": "Auxerre ambitieuse",
    "programmeCode": "424",
    "themeIds": ["ville-durable", "energie"],
    "operator": "Caisse des Depots",
    "grantAmount": 500000,
    "sourceUrl": "https://www.data.gouv.fr/datasets/liste-des-laureats-demonstrateurs-ville-durable-france-2030/",
    "sourceDatasetId": "636c418c159330f20df64c85",
    "confidenceScore": 1.0,
    "validationStatus": "validated"
  }
]
```

### `data/project_beneficiaries.json`

```json
[
  {
    "projectId": "fr2030-dvd-auxerre-ambitieuse",
    "beneficiaryName": "AUXERRE",
    "siren": null,
    "communeCode": "89024",
    "role": "beneficiary",
    "sourceUrl": "https://www.data.gouv.fr/datasets/liste-des-laureats-demonstrateurs-ville-durable-france-2030/",
    "confidenceScore": 0.9,
    "validationStatus": "validated"
  }
]
```

### `data/green_budget_lines.json`

```json
[
  {
    "id": "green-424-424-01-anr-favorable",
    "programmeCode": "424",
    "actionCode": "424-01",
    "label": "Programmes et equipements prioritaires de recherche ANR favorable",
    "globalRating": "Favorable",
    "amount2024": 22204336.13,
    "amount2025": 4523105.51,
    "amount2026": 97535599.79,
    "sourceUrl": "https://www.data.gouv.fr/datasets/plf-2026-budget-vert/",
    "confidenceScore": 1.0
  }
]
```

## 9. Definition simple de la prochaine valeur livrable

La prochaine valeur claire serait :

1. **remplir `amount2026` et ajouter la cotation Budget vert** ;
2. **remplacer au moins un mock front par une vraie source** : `inpi-patent-families.json` ou `data-gouv-datasets.json` ;
3. **creer un rapport qualite automatique** qui dit ce qui est reel, mocke, incomplet ou a valider ;
4. **lier au moins une vraie source de laureats/projets a des montants, territoires et beneficiaires**.

Cela augmenterait fortement la credibilite du POC tout en restant dans le perimetre data : extraction, structuration, tracabilite et correlation.
