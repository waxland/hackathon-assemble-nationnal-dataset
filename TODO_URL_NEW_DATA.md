# TODO URL New Data - France 2030

Ce fichier cadre l'ajout des nouvelles sources transmises le 2026-07-04.
Objectif : enrichir le socle France 2030 avec les documents budgetaires, les strategies nationales d'acceleration et les sources projet-par-projet, en garantissant une tracabilite URL systematique.

---

## 0. Intention metier

Le projet doit separer clairement deux niveaux d'analyse :

- **Endogene** : ce qui est vote ou directement controle par les deputes, notamment les programmes budgetaires et les credits du PLF.
- **Exogene** : ce sur quoi les deputes veulent mesurer un impact mais n'ont pas une influence directe, notamment les strategies nationales d'acceleration, les objectifs France 2030, les enveloppes par strategie et les vecteurs de distribution.

La granularite projet-par-projet ne vient pas d'une source unique. Elle doit etre reconstruite par operateur : ADEME, Bpifrance, ANR, Caisse des Depots / Banque des Territoires, DGE / ANCT, SGPI / info.gouv.fr.

---

## 1. Regle non negociable : URL dans chaque JSON

Pour chaque nouvelle donnee ajoutee ou modifiee dans les JSON, conserver l'URL exacte de la ressource utilisee.

Champs a ajouter dans les nouveaux schemas, ou a remplir dans les schemas existants quand ils existent deja :

```json
{
  "sourceUrl": "https://example.gouv.fr/page-ou-api-utilisee",
  "datasetUrl": "https://example.gouv.fr/page-du-jeu-de-donnees",
  "resourceUrl": "https://example.gouv.fr/fichier-ou-endpoint-utilise",
  "sourceDatasetId": "dataset-id-ou-slug",
  "sourceResourceId": "resource-id-ou-slug",
  "sourceDocument": "nom-du-document-ou-null",
  "sourcePage": null,
  "sourceRow": null,
  "sourceColumn": null,
  "sourceProducer": "producteur",
  "sourceLicense": "licence-ou-null",
  "sourceRetrievedAt": "YYYY-MM-DDTHH:MM:SSZ"
}
```

Contraintes :

- [x] Garder les cles JSON en camelCase anglais.
- [x] Ne jamais inventer `sourceDatasetId` ou `sourceResourceId` : mettre `null` si la source ne fournit pas d'identifiant stable.
- [x] Pour une source PDF, renseigner `sourceDocument`, `sourcePage`, `quoteExtract` court si necessaire, et `evidenceSummary`.
- [x] Pour une source tabulaire, renseigner si possible `sourceRow` et `sourceColumn`.
- [x] Dans `data/sources.json`, creer une entree par ressource effectivement utilisee, pas seulement par dataset.
- [x] Dans les JSON metier, chaque ligne creee depuis une ressource doit conserver `datasetUrl` et `resourceUrl`.
- [x] Si plusieurs ressources d'un meme dataset sont exploitees, creer plusieurs entrees `data/sources.json` avec des `sourceId` distincts.
- [x] Ajouter un controle dans `scripts/18_generate_quality_report.py` pour lister les nouveaux enregistrements sans `sourceUrl`, `datasetUrl` ou `resourceUrl`.

Critere d'acceptation :

- [x] Aucun nouveau fichier JSON metier ne contient d'enregistrement sans URL de source exploitable.
- [x] `data/sources.json` permet de retrouver la page dataset et la ressource exacte ayant servi a produire chaque JSON.

---

## 2. Sources a integrer

### 2.1 Strategies nationales d'acceleration - exogene

Source principale :

- Page SGPI : `https://www.info.gouv.fr/organisation/secretariat-general-pour-l-investissement-sgpi/strategies-d-acceleration-pour-l-innovation`
- Type : page de cadrage strategique.
- Portee : exogene.
- Usage : decrire les strategies nationales d'acceleration, leurs themes, leurs objectifs et les liens possibles avec les programmes.

Document financier lie :

- PDF : `https://www.info.gouv.fr/upload/media/mixed/0001/17/e92490502bafcbdf2bedde2d0f6961d3f2bcf924.pdf`
- Titre observe : `Bilan financier du programme France 2030 et des Programmes d'investissement d'avenir (PIA) - 1er trimestre 2026`.
- Usage : fonds alloues aux strategies nationales d'acceleration, vecteurs de distribution, fonds par programmes, avancement financier, engagements, contractualisation, decaissements.

JSON attendus :

- [x] Creer `data/acceleration_strategies.json`.
- [x] Creer `data/strategy_funding_allocations.json`.
- [x] Creer `data/strategy_distribution_vectors.json`.
- [x] Creer ou enrichir `data/correlations.json` avec des liens `strategy -> theme`, `strategy -> programme`, uniquement si le lien est explicite ou documente.

Champs minimaux `acceleration_strategies.json` :

```json
{
  "strategyId": "sna-hydrogene-decarbone",
  "strategyName": "Hydrogene decarbone",
  "sourceScope": "exogenous",
  "sourceUrl": "https://www.info.gouv.fr/organisation/secretariat-general-pour-l-investissement-sgpi/strategies-d-acceleration-pour-l-innovation",
  "datasetUrl": "https://www.info.gouv.fr/organisation/secretariat-general-pour-l-investissement-sgpi/strategies-d-acceleration-pour-l-innovation",
  "resourceUrl": "https://www.info.gouv.fr/organisation/secretariat-general-pour-l-investissement-sgpi/strategies-d-acceleration-pour-l-innovation",
  "sourceDatasetId": null,
  "sourceResourceId": null,
  "sourceProducer": "SGPI",
  "confidenceScore": 1.0,
  "validationStatus": "validated"
}
```

Taches :

- [x] Extraire la liste des strategies depuis la page SGPI.
- [x] Normaliser les IDs de strategies avec des IDs deterministes.
- [x] Marquer toutes les strategies avec `sourceScope: "exogenous"`.
- [x] Extraire depuis le PDF uniquement les montants explicitement lisibles, avec `sourcePage`.
- [x] Ne pas convertir une phrase de cadrage strategique en montant ou indicateur quantitatif sans chiffre source.
- [x] Ajouter les sources dans `data/sources.json` avec `sourceType: "strategic_framework"` et `sourceType: "financial_report"`.

Critere d'acceptation :

- [x] Le projet peut distinguer une strategie exogene d'un programme budgetaire vote.
- [x] Chaque montant extrait du PDF a `resourceUrl`, `sourceDocument` et `sourcePage`.

---

### 2.2 Programmes budgetaires PLF 2026 - endogene

Source principale :

- Page budget.gouv : `https://www.budget.gouv.fr/documentation/documents-budgetaires-lois/exercice-2026/projet-loi-finances-les/plf-2026-donnees-chiffrees`
- Portee : endogene.
- Programme d'interet : `Investir pour la France de 2030`.

Ressources prioritaires :

- `Depenses 2026 du BG et des BA selon nomenclatures destination et nature`
  - URL page : `https://www.budget.gouv.fr/documentation/documents-budgetaires-lois/exercice-2026/projet-loi-finances-les/plf-2026-donnees-chiffrees`
  - URL ressource : `https://www.budget.gouv.fr/documentation/file-download/31618`
  - Format : XLS.
- `Depenses pluriannuelles par titre des programmes`
  - URL ressource officielle : `https://www.budget.gouv.fr/documentation/file-download/31639`
  - Lien utilisateur Google Sheet de travail : `https://docs.google.com/spreadsheets/d/1AyxTVL4296XFw-HIz0iI8RdJWjHPmWQ5c9Hk3IGHUIY/edit?usp=sharing`
  - Attention : utiliser le Google Sheet comme aide de lecture uniquement si son contenu est public et coherent avec la source budget.gouv. La source officielle reste budget.gouv.

JSON attendus :

- [x] Enrichir `data/budget_lines.json` avec les montants PLF 2026 quand la correspondance programme/action/nature est fiable.
- [x] Creer `data/programme_pluriannual_expenses.json`.
- [x] Enrichir `data/programs.json` avec les liens PLF 2026 si le schema le permet sans casse.
- [x] Ajouter les ressources PLF 2026 dans `data/sources.json`.

Champs minimaux pour toute ligne budgetaire nouvelle ou modifiee :

```json
{
  "programmeCode": "424",
  "programmeName": "Investir pour la France de 2030",
  "fiscalYear": 2026,
  "amount": null,
  "sourceScope": "endogenous",
  "sourceUrl": "https://www.budget.gouv.fr/documentation/file-download/31618",
  "datasetUrl": "https://www.budget.gouv.fr/documentation/documents-budgetaires-lois/exercice-2026/projet-loi-finances-les/plf-2026-donnees-chiffrees",
  "resourceUrl": "https://www.budget.gouv.fr/documentation/file-download/31618",
  "sourceDatasetId": "plf-2026-donnees-chiffrees",
  "sourceResourceId": "31618",
  "sourceDocument": "PLF26 - Depenses 2026 du BG et des BA selon nomenclatures destination et nature.xls",
  "sourceRow": null,
  "sourceColumn": null,
  "confidenceScore": 1.0,
  "validationStatus": "validated"
}
```

Taches :

- [x] Creer `scripts/21_ingest_plf_2026_budget_gouv.py`.
- [x] Telecharger les XLS officiels avec cache local.
- [x] Identifier les lignes relatives a `Investir pour la France de 2030`.
- [x] Verifier les codes programmes France 2030 concernes avant d'ecraser ou d'enrichir les montants existants.
- [x] Renseigner `sourceRow` et `sourceColumn` quand le parsing XLS permet de les conserver.
- [x] Conserver la distinction AE / CP si elle existe dans la ressource.
- [x] Ne pas melanger les chiffres PLF 2026 avec les chiffres d'execution France 2030 du PDF SGPI.

Critere d'acceptation :

- [x] Les montants endogenes PLF 2026 sont sourcess depuis budget.gouv, pas depuis le PDF SGPI.
- [x] Les lignes budgetaires modifiees gardent l'URL exacte de la ressource XLS.

---

### 2.3 Bilan financier France 2030 / PIA - execution et avancement

Source :

- PDF : `https://www.info.gouv.fr/upload/media/mixed/0001/17/e92490502bafcbdf2bedde2d0f6961d3f2bcf924.pdf`
- Producteur : SGPI / info.gouv.fr.
- Portee : execution / avancement, pas vote budgetaire.

JSON attendus :

- [x] Creer `data/france2030_financial_execution.json`.
- [x] Creer `data/operator_financial_execution.json`.
- [x] Creer `data/action_budget_execution.json` si les actions budgetaires sont exploitables proprement.

Champs utiles :

- `envelopeAmount`
- `engagementAmount`
- `contractualizationAmount`
- `disbursementAmount`
- `cofinancingAmount`
- `leverageRatio`
- `programmeCode`
- `operatorName`
- `actionCode`
- `sourcePage`
- `sourceUrl`
- `resourceUrl`
- `sourceDocument`

Taches :

- [x] Extraire uniquement les tableaux/chiffres lisibles du PDF.
- [x] Mettre `validationStatus: "to_validate"` sur toute extraction PDF semi-automatique.
- [x] Ajouter `extractionMethod: "pdf_table_extraction"` ou `extractionMethod: "manual_pdf_review"`.
- [x] Comparer les totaux extraits avec les chiffres cles du PDF avant export final.

Critere d'acceptation :

- [x] Chaque chiffre d'execution peut etre retrouve dans le PDF via `sourcePage`.
- [x] Les chiffres d'execution ne remplacent pas les credits votes du PLF.

---

### 2.4 ADEME - projets France 2030 et recherche

Source projet France 2030 / PIA :

- Page dataset : `https://data.ademe.fr/datasets/programmes-detat-projets-finances-par-lademe`
- API metadata : `https://data.ademe.fr/data-fair/api/v1/datasets/programmes-detat-projets-finances-par-lademe`
- Ressource raw : `https://data.ademe.fr/data-fair/api/v1/datasets/programmes-detat-projets-finances-par-lademe/raw`
- Ressource lines : `https://data.ademe.fr/data-fair/api/v1/datasets/programmes-detat-projets-finances-par-lademe/lines`
- Volume observe : 2645 enregistrements.
- Champs observes : `dossier_code`, `nom_du_projet`, `dossier_objet`, `pia_france_2030_reporting`, `axe_strategique_objet_reporting`, `aap_objet_reporting`, `date_contractualisation`, `date_engagement_juridique`, `duree_projet_en_mois`, `tiers_coordinateur`, `nombre_de_tiers_ej`, `montant_dpm`.

Sources recherche ADEME :

- Vue agregee : `https://data.ademe.fr/data-fair/api/v1/datasets/projets-de-recherche-ademe-vue-agregee-depuis-2021`
- Raw agrege : `https://data.ademe.fr/data-fair/api/v1/datasets/projets-de-recherche-ademe-vue-agregee-depuis-2021/raw`
- Vue detaillee : `https://data.ademe.fr/data-fair/api/v1/datasets/projets-de-recherche-ademe-vue-detaillee-depuis-2021`
- Raw detaille : `https://data.ademe.fr/data-fair/api/v1/datasets/projets-de-recherche-ademe-vue-detaillee-depuis-2021/raw`

JSON attendus :

- [x] Enrichir `data/projects.json`.
- [x] Enrichir `data/project_beneficiaries.json`.
- [x] Creer `data/project_funding_lines.json` si les montants par projet doivent rester separes.
- [x] Conserver les imports ADEME recherche existants et y ajouter `datasetUrl` / `resourceUrl` si absents.

Taches :

- [x] Creer ou enrichir un script ADEME dedie sans casser `scripts/16_ingest_ademe_research_projects.py`.
- [x] Filtrer explicitement France 2030 / PIA via les champs de reporting, pas seulement par mots-cles.
- [x] Rattacher les beneficiaires par SIREN uniquement quand la source donne un identifiant exploitable.
- [x] Conserver `operatorName: "ADEME"`.
- [x] Ajouter les trois ressources ADEME dans `data/sources.json`.

Critere d'acceptation :

- [x] Chaque projet ADEME a `resourceUrl` vers la ressource raw ou lines utilisee.
- [x] Les montants ADEME conservent le champ source d'origine et ne sont pas fusionnes sans preuve avec d'autres operateurs.

---

### 2.5 ANR - France 2030, PEPR, partenariats et cofinancements

Sources identifiees :

- Page generale ANR open data : `https://anr.fr/en/funded-projects-and-impact/datasets-on-funded-projects/`
- Dataset cofinancements France 2030 : `https://dataanr.opendatasoft.com/explore/dataset/public-france2030-indicateurs-cofinancements/export/?flg=en-gb`
- API cofinancements : `https://dataanr.opendatasoft.com/api/explore/v2.1/catalog/datasets/public-france2030-indicateurs-cofinancements/records`
- Dataset projets IA France 2030 : `https://data.anr.fr/explore/dataset/projetsia/`
- API projets IA : `https://dataanr.opendatasoft.com/api/explore/v2.1/catalog/datasets/projetsia/records`

JSON attendus :

- [x] Creer `data/anr_france2030_projects.json` ou enrichir `data/projects.json` avec `operatorName: "ANR"`.
- [x] Creer `data/anr_project_partners.json` si les partenaires sont disponibles.
- [x] Creer `data/anr_cofinancing_indicators.json`.

Taches :

- [x] Rechercher dans le catalogue ANR le dataset exact correspondant a `France 2030 - Partenariats` si disponible.
- [x] Prioriser l'API Opendatasoft avant le scraping HTML.
- [x] Conserver `datasetUrl`, `resourceUrl`, `sourceDatasetId` et le `recordId` si expose.
- [x] Rattacher PEPR / strategies uniquement si la source ANR expose explicitement le programme ou l'action.

Critere d'acceptation :

- [x] Les projets ANR France 2030 sont separes des projets ADEME/Bpifrance.
- [x] Les cofinancements ANR ne sont pas additionnes avec les aides ADEME sans cle projet fiable.

---

### 2.6 Caisse des Depots / Banque des Territoires

Dataset `Demontrateurs ville durable` :

- Page data.gouv : `https://www.data.gouv.fr/datasets/liste-des-laureats-demonstrateurs-ville-durable-france-2030`
- Dataset ID : `636c418c159330f20df64c85`
- CSV resource ID : `ce6c67d2-7539-4e2a-89d5-8a8df72ac1c8`
- CSV resource URL : `https://opendata.caissedesdepots.fr/api/explore/v2.1/catalog/datasets/liste-des-laureats/exports/csv?use_labels=true`
- JSON resource ID : `a691a628-a524-43ff-83b6-53e77bbbae8f`
- JSON resource URL : `https://opendata.caissedesdepots.fr/api/explore/v2.1/catalog/datasets/liste-des-laureats/exports/json`

JSON attendus :

- [x] Verifier et enrichir `data/projects.json`.
- [x] Verifier et enrichir `data/territories.json`.
- [x] Verifier et enrichir `data/project_beneficiaries.json`.

Taches :

- [x] Conserver les ressources CDC deja ingerees si elles existent, mais ajouter `datasetUrl` et `resourceUrl` partout.
- [x] Utiliser le CSV ou JSON comme ressource canonique, pas les deux pour creer des doublons.
- [x] Documenter le choix de ressource canonique dans `data/sources.json`.

Critere d'acceptation :

- [x] Chaque demonstrateur ville durable garde le lien data.gouv et le lien ressource CDC exacte.

---

### 2.7 DGE / ANCT - sites cles en main France 2030

Dataset :

- Page data.gouv : `https://www.data.gouv.fr/datasets/les-sites-cles-en-main-france-2030`
- Dataset ID : `662a4bc173fcdf4bab4ef1b6`
- CSV resource ID : `5f2e1413-552a-43fc-9669-74169cbca87d`
- CSV resource URL : `https://static.data.gouv.fr/resources/les-sites-cles-en-main-france-2030/20250924-160343/liste-sites-cles-en-main-com2025-20250919.csv`
- PDF metadata resource ID : `8459ef6c-0476-44e0-8bc7-f4cfbf891269`
- PDF metadata URL : `https://static.data.gouv.fr/resources/les-sites-cles-en-main-france-2030/20250924-160404/liste-sites-cles-en-main-metadata.pdf`

JSON attendus :

- [x] Creer ou enrichir `data/industrial_sites.json`.
- [x] Enrichir `data/territories.json`.
- [x] Ajouter des correlations `industrialSite -> territory` et, seulement si explicite, `industrialSite -> theme`.

Taches :

- [x] Garder le COG 2025 et le code commune si disponible.
- [x] Ne pas rattacher automatiquement un site a une strategie sans preuve textuelle.
- [x] Ajouter les deux ressources dans `data/sources.json`.

Critere d'acceptation :

- [x] Chaque site cle en main conserve le CSV source et la documentation metadata.

---

### 2.8 Bpifrance / Concours d'innovation / i-Nov / Premiere Usine / French Tech 2030

Sources i-Nov :

- Page data.gouv : `https://www.data.gouv.fr/datasets/laureats-du-concours-dinnovation-i-nov`
- Dataset ID : `686bade5bf26c9a85acf7a77`
- CSV resource ID : `e2ef6aac-3c7d-42d2-9097-f705187c8c76`
- CSV resource URL : `https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-laureats-concours-i-nov/exports/csv?use_labels=true`
- JSON resource ID : `56f305cc-b89f-4236-b630-e1fee17e0b02`
- JSON resource URL : `https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-laureats-concours-i-nov/exports/json`

Sources SGPI / info.gouv :

- Concours d'innovation : `https://www.info.gouv.fr/organisation/secretariat-general-pour-l-investissement-sgpi/concours-d-innovation-volet-i-nov`
- Laureats France 2030 : `https://www.info.gouv.fr/grand-dossier/france-2030/laureats?segmented-laureate=laureate-button-list`

Source Bpifrance :

- Recueil AAP France 2030 Bpifrance : `https://www.bpifrance.fr/sites/default/files/inline-files/Recueil%20AAP%20France%202030%20Bpifrance.pdf`

Sources a rechercher par AAP :

- `Premiere Usine`
- `French Tech 2030`
- `i-Nov`
- autres AAP Bpifrance France 2030 publies sur data.gouv.fr ou sites ministeriels.

JSON attendus :

- [x] Enrichir `data/projects.json`.
- [x] Enrichir `data/project_beneficiaries.json`.
- [x] Creer `data/calls_for_projects_sources.json` si les AAP doivent etre inventories separement.

Taches :

- [x] Prioriser les datasets tabulaires data.gouv / enseignementsup-recherche pour i-Nov.
- [x] Utiliser le PDF Bpifrance comme source documentaire ou descriptive, pas comme source exhaustive de montants si les montants ne sont pas tabulaires.
- [x] Pour `Premiere Usine` et `French Tech 2030`, chercher une ressource tabulaire officielle avant tout scraping de communiques.
- [x] Si seul un communique existe, mettre `dataCompleteness: "partial"` et `validationStatus: "to_validate"`.
- [x] Conserver `operatorName: "Bpifrance"` uniquement quand l'operateur est explicite.

Critere d'acceptation :

- [x] Les laureats i-Nov issus du dataset ont tous `datasetUrl` et `resourceUrl`.
- [x] Les laureats issus de pages info.gouv sont marques comme extraction partielle si aucun fichier tabulaire n'est disponible.

---

## 3. Mise a jour de `data/sources.json`

Ajouter ou verifier les entrees suivantes, une par ressource exploitee :

- [x] `src-sgpi-strategies-acceleration-page`
- [x] `src-sgpi-france2030-financial-report-2026-q1`
- [x] `src-budget-plf-2026-bg-ba-destination-nature`
- [x] `src-budget-plf-2026-pluriannual-programmes`
- [x] `src-ademe-programmes-etat-projets-finances`
- [x] `src-ademe-research-aggregated-2021`
- [x] `src-ademe-research-detailed-2021`
- [x] `src-anr-france2030-cofinancements`
- [x] `src-anr-projets-ia-france2030`
- [x] `src-cdc-demonstrateurs-ville-durable-csv`
- [x] `src-dge-anct-sites-cles-en-main-csv`
- [x] `src-dge-anct-sites-cles-en-main-metadata`
- [x] `src-esr-inov-laureates-csv`
- [x] `src-sgpi-france2030-laureates-page`
- [x] `src-bpifrance-recueil-aap-france2030`

Schema recommande pour une entree `data/sources.json` :

```json
{
  "sourceId": "src-budget-plf-2026-bg-ba-destination-nature",
  "name": "PLF 2026 - Depenses 2026 du BG et des BA selon nomenclatures destination et nature",
  "sourceType": "budget_table",
  "sourceScope": "endogenous",
  "datasetId": "plf-2026-donnees-chiffrees",
  "resourceId": "31618",
  "datasetUrl": "https://www.budget.gouv.fr/documentation/documents-budgetaires-lois/exercice-2026/projet-loi-finances-les/plf-2026-donnees-chiffrees",
  "resourceUrl": "https://www.budget.gouv.fr/documentation/file-download/31618",
  "url": "https://www.budget.gouv.fr/documentation/file-download/31618",
  "license": "Licence Ouverte / Open Licence version 2.0",
  "producer": "Direction du Budget",
  "updateFrequency": "annual",
  "lastCheckedAt": "2026-07-04T00:00:00Z",
  "ingestionScript": "scripts/21_ingest_plf_2026_budget_gouv.py"
}
```

Taches :

- [x] Mettre a jour `scripts/lib/sources.py` pour accepter `datasetUrl`, `resourceUrl`, `sourceType`, `sourceScope`.
- [x] Garder `url` pour compatibilite avec le code existant.
- [x] Ajouter un test qui verifie que toute entree `data/sources.json` possede au minimum `sourceId`, `name`, `url`, `datasetUrl`, `resourceUrl`, `sourceType`, `sourceScope`.

Critere d'acceptation :

- [x] La page dataset et la ressource exacte sont toutes deux visibles pour chaque source.

---

## 4. Priorisation des runs

### P0 - Contrat de provenance URL

- [x] Documenter le contrat `sourceUrl` / `datasetUrl` / `resourceUrl` dans `DATASETS.md`.
- [x] Ajouter la validation des URLs dans `scripts/18_generate_quality_report.py`.
- [x] Ajouter les champs manquants dans `data/sources.json` sans casser les scripts actuels.
- [x] Ajouter un test de non-regression sur les URLs de source.

### P1 - PLF 2026 endogene

- [x] Implementer `scripts/21_ingest_plf_2026_budget_gouv.py`.
- [x] Integrer la ressource `31618`.
- [x] Integrer la ressource `31639`.
- [x] Produire ou enrichir les JSON budgetaires avec URLs exactes.

### P2 - SNA exogene et bilan financier SGPI

- [x] Implementer `scripts/22_ingest_sgpi_strategies.py`.
- [x] Implementer `scripts/23_ingest_sgpi_financial_report.py`.
- [x] Produire les JSON de strategies, allocations et vecteurs de distribution.
- [x] Marquer clairement `sourceScope: "exogenous"` ou `sourceScope: "execution"`.

### P3 - Operateurs projet-par-projet

- [x] ADEME projets finances.
- [x] ADEME recherche agregee/detaillee avec URLs completees.
- [x] ANR cofinancements / partenariats / PEPR.
- [x] CDC demonstrateurs ville durable avec URLs completees.
- [x] DGE / ANCT sites cles en main.
- [x] i-Nov / Bpifrance / French Tech 2030 / Premiere Usine.

### P4 - Correlations et qualite

- [x] Ajouter `sourceScope` aux correlations nouvelles.
- [x] Ajouter des correlations `project -> operator`, `project -> strategy`, `project -> programme`, uniquement avec preuve.
- [x] Mettre `validationStatus: "to_validate"` pour toute correlation faible ou indirecte.
- [x] Faire apparaitre dans `data/quality_report.json` les enregistrements sans URL ou avec provenance incomplete.

### P5 - Export SQLite / Neo4j

- [x] Ajouter les tables necessaires si de nouveaux JSON sont crees.
- [x] Conserver les champs d'URL dans SQLite.
- [x] Conserver les champs d'URL dans l'export Neo4j quand une relation est creee depuis une source.

---

## 5. Definition of Done

- [x] Chaque nouvelle source est referencee dans `data/sources.json`.
- [x] Chaque ressource exploitee a `datasetUrl` et `resourceUrl`.
- [x] Chaque nouveau JSON metier conserve l'URL exacte de la ressource source.
- [x] Les donnees endogenes PLF 2026 ne sont pas melangees avec les donnees exogenes SNA ou execution SGPI.
- [x] Les sources projet-par-projet restent separees par operateur.
- [x] Aucun montant n'est cree par interpretation si la source ne fournit pas explicitement le chiffre.
- [x] Les scripts sont idempotents.
- [x] Les controles qualite signalent toute provenance incomplete.

### 2.7 Info.gouv - Lauréats France 2030 (API publique SGPI)

Source des lauréats :

- Page web vitrine : `https://www.info.gouv.fr/grand-dossier/france-2030/laureats?segmented-laureate=laureate-button-list`
- Type : Annuaire exhaustif des bénéficiaires et projets subventionnés France 2030 exposés par le gouvernement.
- Utilité : Il s'agit de la source principale de restitution au grand public, à croiser en priorité absolue avec les remontées opérateur.

JSON attendus :

- [x] Créer `scripts/25_ingest_infogouv_laureats.py`.
- [x] Créer `data/infogouv_laureats.json` ou enrichir directement `data/projects.json` et `data/project_beneficiaries.json` selon ce que l'API expose.
- [x] Ajouter la source `infogouv-laureats` au registre `data/sources.json`.
- [x] Mettre à jour `data/correlations.json` pour relier le projet info.gouv au programme ou thème s'il est explicitement indiqué.

Champs minimaux pour les lauréats ou les projets importés depuis info.gouv :

```json
{
  "projectId": "proj-infogouv-XXX",
  "projectName": "Nom du projet",
  "operatorName": "SGPI / info.gouv.fr",
  "sourceUrl": "https://www.info.gouv.fr/grand-dossier/france-2030/laureats",
  "datasetUrl": "https://www.info.gouv.fr/grand-dossier/france-2030/laureats",
  "resourceUrl": "URL technique (API/XHR) si trouvée",
  "sourceProducer": "SGPI",
  "confidenceScore": 1.0,
  "validationStatus": "validated"
}
```

Tâches :

- [x] Analyser le Network tab (XHR) de la page Info.gouv pour identifier l'API JSON cachée qui peuple la liste des lauréats.
- [x] Extraire les projets, montants de subvention, SIREN bénéficiaires, localisation et thématique s'ils sont disponibles.
- [x] Croiser les SIREN trouvés sur Info.gouv avec ceux déjà extraits via l'ADEME ou la Caisse des Dépôts pour dé-dupliquer les fiches entreprises.
- [x] Ne créer une nouvelle entreprise que si son SIREN est validé, et garantir un `confidenceScore: 1.0` puisqu'elle est labellisée officiellement.

Critère d'acceptation :

- [x] Les lauréats exposés sur Info.gouv se retrouvent dans `projects.json` avec la propriété `sourceUrl` pointant vers la page Info.gouv.
- [x] Les graphes Neo4j exportés montrent bien les nœuds `Project` reliés aux bénéficiaires.
