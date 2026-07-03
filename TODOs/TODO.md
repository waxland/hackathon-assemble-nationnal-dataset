# Checklist Projet - France 2030 (Data & Scraping)

Ce document liste l'ensemble des étapes et des scripts à développer pour construire le socle de données du projet France 2030. L'objectif final est de disposer d'une base de données relationnelle sous forme de fichiers JSON, propre et exploitable.

## 🗄️ Étape 1 : Référentiel Budgétaire (Programmes et Lignes)

- [x] **TODO 1.1 : Script d'extraction des programmes (`scripts/01_extract_programs.py`)**
  - **Comment faire** : Créer un script Python pour initialiser les 5 programmes majeurs (421, 422, 423, 424, 425). Ces données de base peuvent être définies statiquement ou extraites d'un CSV initial, en respectant les dénominations officielles de la mission "Investir pour la France de 2030".
  - **Attendu final (`data/programs.json`)** : 
    ```json
    [
      {
        "programmeCode": "424",
        "programmeName": "Financement des investissements stratégiques",
        "missionName": "Investir pour la France de 2030",
        "budgetLines": [],
        "officialObjectives": [],
        "actions": [],
        "themes": [],
        "keywords": [],
        "callsForProjects": [],
        "parliamentMentions": [],
        "sourceDocuments": []
      }
    ]
    ```

- [x] **TODO 1.2 : Script d'extraction des lignes budgétaires (`scripts/02_extract_budget_lines.py`)**
  - **Comment faire** : Scrapper ou télécharger le document de données chiffrées PLF 2026 depuis `budget.gouv.fr` (fichier Dépenses 2026 du BG). Filtrer sur les programmes 421 à 425 et extraire les montants budgétaires des années 2024, 2025 et 2026 par catégorie de dépense. 
  - **Attendu final (`data/budget_lines.json`)** :
    ```json
    [
      {
        "id": "fr2030-424-6",
        "programmeCode": "424",
        "expenseCategoryCode": "6",
        "expenseCategoryName": "Dépenses d’intervention",
        "amount2024": 3318311564,
        "amount2025": 4052897364,
        "amount2026": 3364301779,
        "sourceUrl": "...",
        "sourceDocument": "Dépenses 2026 du BG...",
        "qualityStatus": "verified"
      }
    ]
    ```

## 📄 Étape 2 : Extraction Qualitative des Projets Annuels de Performances (PAP)

- [x] **TODO 2.1 : Script de parsing des documents PAP (`scripts/03_parse_pap.py`)**
  - **Comment faire** : Télécharger les documents PDF des PAP des programmes 421 à 425 sur `budget.gouv.fr`. Utiliser une librairie comme `pdfplumber` ou `PyMuPDF` pour extraire le texte des sections "Présentation stratégique", "Objectifs", "Dispositifs" et "Indicateurs". Isoler les verbatims pertinents.
  - **Attendu final (Mise à jour de `data/programs.json`)** : Enrichir le JSON existant des programmes en remplissant les tableaux `"officialObjectives"`, `"actions"`, et `"sourceDocuments"` (avec le numéro de page précis).

## 🏷️ Étape 3 : Taxonomie des Thématiques et Mots-Clés

- [x] **TODO 3.1 : Script de génération des thématiques (`scripts/04_generate_themes.py`)**
  - **Comment faire** : Sur la base des textes extraits du PAP et des grandes lignes définies dans le `RECAP.md`, générer un dictionnaire (statique ou via une extraction LLM sur les textes) identifiant les thématiques majeures (ex: Hydrogène, Semi-conducteurs, Écosystèmes d'innovation). Relier manuellement ou sémantiquement chaque thématique au programme correspondant.
  - **Attendu final (`data/themes.json`)** :
    ```json
    [
      {
        "themeId": "hydrogene",
        "themeName": "Hydrogène",
        "relatedProgrammes": ["424"],
        "relatedBudgetLines": [],
        "keywords": ["kw-hydrogene"],
        "confidenceScore": 0.8
      }
    ]
    ```

- [x] **TODO 3.2 : Script de génération du dictionnaire de mots-clés (`scripts/05_generate_keywords.py`)**
  - **Comment faire** : Pour chaque thématique identifiée, définir une liste de mots-clés (technologies, dispositifs, synonymes). Assigner un identifiant unique à chaque mot-clé et le lier au `themeId`.
  - **Attendu final (`data/keywords.json`)** :
    ```json
    [
      {
        "keywordId": "kw-hydrogene",
        "label": "hydrogène",
        "type": "technology",
        "relatedThemeId": "hydrogene",
        "relatedProgrammes": ["424"],
        "synonyms": ["hydrogène décarboné", "H2", "hydrogène vert"],
        "confidenceScore": 0.9
      }
    ]
    ```

## 📢 Étape 4 : Appels à Projets (AAP)

- [x] **TODO 4.1 : Script de scrapping des AAP (`scripts/06_scrape_calls_for_projects.py`)**
  - **Comment faire** : Scrapper la page `info.gouv.fr/grand-dossier/france-2030/appels-a-candidatures`. Extraire le titre, la description courte, les dates (ouverture/clôture), et l'opérateur. Utiliser la description et le titre pour faire un matching avec le dictionnaire de `keywords.json` afin d'affecter automatiquement l'AAP à un `themeId` (et par extension à un `programmeCode`).
  - **Attendu final (`data/calls_for_projects.json`)** :
    ```json
    [
      {
        "callId": "fr2030-call-123",
        "title": "Soutien aux briques technologiques hydrogène",
        "description": "Appel à projet visant à soutenir la filière hydrogène...",
        "themeId": "hydrogene",
        "relatedProgrammes": ["424"],
        "operator": "ADEME",
        "openingDate": "2024-02-01",
        "closingDate": "2024-06-30",
        "sourceUrl": "...",
        "keywords": ["kw-hydrogene"]
      }
    ]
    ```

## 🏛️ Étape 5 : Mentions Parlementaires

- [x] **TODO 5.1 : Script de recherche dans les débats de l'Assemblée nationale (`scripts/07_fetch_parliament_mentions.py`)**
  - **Comment faire** : Interroger l'API Open Data de l'Assemblée nationale ou parser les fichiers JSON/XML massifs de `data.assemblee-nationale.fr`. Rechercher les occurrences exactes (ou lemmatisées) des mots-clés du fichier `keywords.json` dans les interventions (`intervention_text`). Extraire les métadonnées de l'intervention et une fenêtre de texte de contexte.
  - **Attendu final (`data/parliament_mentions.json`)** :
    ```json
    [
      {
        "mentionId": "an-mention-987",
        "date": "2024-10-15",
        "chamber": "Assemblée nationale",
        "speakerName": "Jean Dupont",
        "politicalGroup": "Ecolo",
        "matchedKeyword": "hydrogène vert",
        "relatedThemeId": "hydrogene",
        "relatedProgrammeCode": "424",
        "interventionText": "L'investissement dans l'hydrogène vert est crucial...",
        "contextBefore": "Concernant la souveraineté industrielle, ",
        "contextAfter": " Nous devons accélérer.",
        "sourceUrl": "...",
        "confidenceScore": 1.0
      }
    ]
    ```

## 🏢 Étape 6 : Codes NAF et Entreprises (Étape Avancée)

- [x] **TODO 6.1 : Script de mapping des Codes NAF (`scripts/08_map_naf_codes.py`)**
  - **Comment faire** : Associer de manière heuristique ou via une liste prédéfinie les `themeId` du projet avec les codes NAF officiels de l'INSEE. Ajouter un score de confiance et flagguer les relations ambiguës.
  - **Attendu final (`data/naf_codes.json`)** :
    ```json
    [
      {
        "nafCode": "20.11Z",
        "nafLabel": "Fabrication de gaz industriels",
        "relatedThemeIds": ["hydrogene"],
        "confidenceScore": 0.8
      }
    ]
    ```

- [x] **TODO 6.2 : Script d'extraction des entreprises bénéficiaires (`scripts/09_fetch_companies.py`)**
  - **Comment faire** : Extraire les noms d'entreprises citées dans les résultats d'appels à projets, les communiqués de presse ou les débats. Interroger l'API Sirene pour obtenir leur code NAF exact et leur numéro SIREN. Lier l'entreprise au `themeId` et au `programmeCode` correspondant.
  - **Attendu final (`data/companies.json`)** :
    ```json
    [
      {
        "companyId": "siren-123456789",
        "companyName": "HydroTech France",
        "siren": "123456789",
        "nafCode": "20.11Z",
        "relatedThemeIds": ["hydrogene"],
        "relatedProgrammeCodes": ["424"],
        "source": "Lauréat AAP fr2030-call-123",
        "confidenceScore": 0.9
      }
    ]
    ```

## 🔗 Étape 7 : Table des Corrélations

- [x] **TODO 7.1 : Script de compilation des corrélations (`scripts/10_generate_correlations.py`)**
  - **Comment faire** : Écrire un script consolidant tous les fichiers JSON précédents. Le but est de créer une table plate (ou un tableau d'objets de liaison) qui matérialise chaque relation (ex: Programme 424 -> Thème Hydrogène). Ce fichier est la "base de données de graph" qui permettra au POC de répondre aux questions transversales.
  - **Attendu final (`data/correlations.json`)** :
    ```json
    [
      {
        "correlationId": "corr-1",
        "sourceEntityType": "programme",
        "sourceEntityId": "424",
        "targetEntityType": "theme",
        "targetEntityId": "hydrogene",
        "correlationType": "finances",
        "confidenceScore": 0.9,
        "evidenceSource": "budget_lines.json",
        "validationStatus": "validated"
      }
    ]
    ```

---

## 🚀 Phase 2 : Implémentation Réelle, Scraping et Fiabilisation des Données

Cette phase vise à remplacer les données "mockées" (générées dans la Phase 1) par de **vraies données** extraites d'Internet. Pour vous guider dans l'investigation, l'itération et la récupération de ces jeux de données de manière très poussée, référez-vous aux fichiers TODO détaillés ci-dessous :

- [ ] 🔗 **[TODO 01 - Référentiel Budgétaire (Programmes & Lignes)](TODO_01_budget.md)** : Extraire les vraies données PLF 2026/2025 (CSV/Excel).
- [ ] 🔗 **[TODO 02 - Extraction Qualitative des PAP](TODO_02_pap.md)** : Téléchargement et parsing des PDF officiels de la performance.
- [ ] 🔗 **[TODO 03 - Thématiques et Mots-clés](TODO_03_themes_keywords.md)** : Élaboration de la taxonomie officielle et de ses synonymes.
- [ ] 🔗 **[TODO 04 - Appels à Projets (AAP)](TODO_04_aap.md)** : Web scraping ou API pour l'inventaire des candidatures.
- [ ] 🔗 **[TODO 05 - Mentions Parlementaires](TODO_05_parlement.md)** : Requêtage massif de l'Open Data de l'Assemblée nationale.
- [ ] 🔗 **[TODO 06 - Entreprises & Codes NAF](TODO_06_entreprises_naf.md)** : Réconciliation avec Sirene et identification des lauréats.
- [ ] 🔗 **[TODO 07 - Compilation & Corrélations Finales](TODO_07_correlations.md)** : Jointure experte de l'ensemble du graphe (JSON / SQLite).
