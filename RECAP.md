Oui — à mon avis, pour un POC, il faut éviter de viser tout de suite une visualisation complexe ou une analyse trop ambitieuse. Le plus faisable et le plus utile, c’est de construire une base de corrélation propre entre :

Budget France 2030
→ Programmes 421-425
→ Actions / dispositifs
→ Thématiques
→ Mots-clés
→ Appels à projets
→ Entreprises / secteurs / codes NAF
→ Mentions parlementaires
→ Verbatims sourcés

Le cœur du POC, ce n’est pas “faire un dashboard”, c’est réussir à produire un JSON / une BDD propre qui permet ensuite de dire :

Cette thématique est financée par tel programme, citée X fois au Parlement, liée à tels mots-clés, tels appels à projets, tels secteurs NAF et potentiellement telles entreprises.

Voici la version reformattée en checklist projet.

TODO — Construction d’une base de données France 2030 centrée sur les programmes 421 à 425

Objectif du POC

- Construire une base de données ou un JSON structuré permettant de relier les financements France 2030 aux thématiques d’innovation.
- Se concentrer uniquement sur la récupération, la structuration et la corrélation des données.
- Ne pas traiter dans cette phase les propositions visuelles, les camemberts, les slides ou les interfaces.
- Produire un socle de données suffisamment propre pour alimenter ensuite un POC de visualisation.
- Permettre une lecture croisée entre :
  - programmes budgétaires ;
  - montants financiers ;
  - actions / dispositifs ;
  - thématiques France 2030 ;
  - mots-clés ;
  - appels à projets ;
  - secteurs économiques ;
  - codes NAF ;
  - entreprises ;
  - mentions parlementaires ;
  - verbatims sourcés.

⸻

1. Périmètre prioritaire

Programmes à traiter

- Programme 421 — Soutien des progrès de l’enseignement et de la recherche.
- Programme 422 — Valorisation de la recherche.
- Programme 423 — Accélération de la modernisation des entreprises.
- Programme 424 — Financement des investissements stratégiques.
- Programme 425 — Financement structurel des écosystèmes d’innovation.

Priorité POC

- Priorité 1 : programme 424.
- Priorité 2 : programme 425.
- Priorité 3 : programme 423.
- Priorité 4 : programme 422.
- Priorité 5 : programme 421 comme contexte complémentaire.

Codes d’action / programmes à rechercher en priorité

- 422.
- 423.
- 424.
- 425.

Lignes budgétaires déjà identifiées

- 421 — catégorie 6 — Dépenses d’intervention.
- 422 — catégorie 3 — Dépenses de fonctionnement.
- 422 — catégorie 6 — Dépenses d’intervention.
- 423 — catégorie 3 — Dépenses de fonctionnement.
- 423 — catégorie 6 — Dépenses d’intervention.
- 423 — catégorie 7 — Dépenses d’opérations financières.
- 424 — catégorie 3 — Dépenses de fonctionnement.
- 424 — catégorie 6 — Dépenses d’intervention.
- 425 — catégorie 3 — Dépenses de fonctionnement.
- 425 — catégorie 6 — Dépenses d’intervention.

⸻

2. Ce qui est faisable pour un POC

Faisable à court terme

- Récupérer les montants budgétaires 2024, 2025, 2026 par programme.
- Récupérer les montants par catégorie de dépense.
- Récupérer les documents PAP liés aux programmes 421 à 425.
- Extraire les objectifs, actions, dispositifs et verbatims depuis les PAP.
- Construire une première taxonomie de thématiques France 2030.
- Récupérer les appels à projets / appels à candidatures France 2030.
- Associer chaque appel à une ou plusieurs thématiques.
- Associer chaque thématique à des mots-clés.
- Rechercher ces mots-clés dans les comptes rendus des débats de l’Assemblée nationale.
- Compter les occurrences par mot-clé, date, député, groupe politique et thématique.
- Produire une table de corrélation entre programme, thématique, mots-clés et mentions parlementaires.
- Produire un premier JSON propre par thématique.
- Produire un premier JSON propre par programme.

Faisable mais plus long

- Identifier précisément les bénéficiaires / lauréats France 2030.
- Relier les bénéficiaires aux appels à projets.
- Relier les bénéficiaires aux entreprises Sirene.
- Associer automatiquement les entreprises à des codes NAF.
- Agréger des indicateurs économiques par code NAF.
- Identifier les startups associées à chaque thématique.
- Relier les entreprises citées dans les débats parlementaires aux thématiques.
- Ajouter les données du Sénat.
- Ajouter les questions écrites et orales.
- Ajouter les amendements budgétaires.

À éviter pour un premier POC

- Ne pas chercher à reconstruire toute la chaîne financière complète de France 2030.
- Ne pas chercher à obtenir immédiatement tous les bénéficiaires finaux.
- Ne pas chercher à calculer précisément l’impact économique réel.
- Ne pas chercher à produire une analyse causale.
- Ne pas mélanger trop tôt brevets, startups, CA, employés, débats, budgets et appels à projets sans table de correspondance claire.
- Ne pas commencer par la visualisation.
- Ne pas commencer par les slides.
- Ne pas commencer par les graphiques.
- D’abord construire les données et leurs relations.

⸻

3. Sources à exploiter

Source 1 — Données budgétaires PLF 2026

- Utiliser la source suivante :
  - https://www.budget.gouv.fr/documentation/documents-budgetaires-lois/exercice-2026/projet-loi-finances-les/plf-2026-donnees-chiffrees
- Récupérer le document :
  - “Dépenses 2026 du BG et des BA selon nomenclatures destination et nature”.
- Filtrer sur :
  - budget général ;
  - mission “Investir pour la France de 2030” ;
  - programmes 421, 422, 423, 424, 425.
- Extraire :
  - code mission ;
  - nom mission ;
  - code programme ;
  - nom programme ;
  - code catégorie de dépense ;
  - nom catégorie de dépense ;
  - montant 2024 ;
  - montant 2025 ;
  - montant 2026 ;
  - ministère ;
  - source ;
  - année source.

Source 2 — Documents PAP 2025

- Utiliser la source suivante :
  - https://www.budget.gouv.fr/documentation/documents-budgetaires/exercice-2025/projet-loi-finances-les/budget-general-plf-2025-6
- Récupérer les documents liés à :
  - programme 421 ;
  - programme 422 ;
  - programme 423 ;
  - programme 424 ;
  - programme 425.
- Extraire pour chaque programme :
  - présentation stratégique ;
  - objectifs ;
  - actions ;
  - dispositifs ;
  - opérateurs ;
  - indicateurs ;
  - justification des crédits ;
  - bénéficiaires types ;
  - mots-clés ;
  - verbatims importants ;
  - pages de référence.

Source 3 — RAP / rapports annuels de performance

- Chercher les RAP disponibles sur budget.gouv.fr.
- Identifier les RAP liés à la mission “Investir pour la France de 2030”.
- Chercher les programmes :
  - 421 ;
  - 422 ;
  - 423 ;
  - 424 ;
  - 425.
- Extraire :
  - crédits prévus ;
  - crédits exécutés ;
  - écarts entre prévision et exécution ;
  - commentaires sur les écarts ;
  - indicateurs réalisés ;
  - résultats atteints ;
  - verbatims explicatifs.

Source 4 — Data économie / PLF Performance

- Utiliser la source suivante :
  - https://data.economie.gouv.fr/explore/assets/plf-2025-performance/view/
- Rechercher les programmes 421 à 425.
- Extraire :
  - objectifs de performance ;
  - indicateurs ;
  - valeurs ;
  - cibles ;
  - années ;
  - commentaires éventuels.

Source 5 — France 2030 / appels à candidatures

- Utiliser la source suivante :
  - https://www.info.gouv.fr/grand-dossier/france-2030/appels-a-candidatures
- Récupérer les appels à projets / appels à candidatures.
- Pour chaque appel, extraire :
  - titre ;
  - description ;
  - thématique ;
  - date d’ouverture ;
  - date de clôture ;
  - opérateur ;
  - type de bénéficiaire ;
  - lien source ;
  - mots-clés.
- Relier chaque appel à une ou plusieurs thématiques.
- Relier chaque appel à un programme probable si le lien est identifiable.

Source 6 — Comptes rendus des débats de l’Assemblée nationale

- Utiliser la source suivante :
  - https://www.data.gouv.fr/datasets/comptes-rendus-des-debats-de-l-assemblee-nationale
- Récupérer les comptes rendus.
- Extraire les interventions.
- Pour chaque intervention, structurer :
  - date ;
  - séance ;
  - orateur ;
  - fonction ;
  - groupe politique si disponible ;
  - texte de l’intervention ;
  - texte examiné si disponible ;
  - source ;
  - fichier source.
- Rechercher les mots-clés issus des programmes, thématiques et appels à projets.
- Créer une table des mentions parlementaires.

Source 7 — Assemblée nationale Open Data

- Utiliser la source suivante :
  - https://data.assemblee-nationale.fr/
- Récupérer les données complémentaires :
  - députés ;
  - groupes politiques ;
  - organes ;
  - amendements ;
  - dossiers législatifs ;
  - questions écrites ;
  - questions orales ;
  - scrutins.
- Relier les interventions aux députés.
- Relier les interventions aux textes budgétaires.
- Relier les amendements aux programmes 421 à 425 quand possible.

Source 8 — Les Tricoteuses

- Utiliser comme source complémentaire :
  - https://www.tricoteuses.fr/
  - https://www.tricoteuses.fr/assemblee
- Vérifier si Les Tricoteuses permettent d’accéder plus facilement :
  - aux débats ;
  - aux amendements ;
  - aux textes ;
  - aux dossiers ;
  - aux parlementaires ;
  - aux scrutins.
- Utiliser cette source comme source d’enrichissement, pas comme source primaire.
- Comparer les résultats avec les sources officielles.

Source 9 — Sénat

- Utiliser la source suivante :
  - https://data.senat.fr/
- Rechercher les mentions :
  - France 2030 ;
  - Investir pour la France de 2030 ;
  - programme 421 ;
  - programme 422 ;
  - programme 423 ;
  - programme 424 ;
  - programme 425.
- Récupérer si possible :
  - débats ;
  - questions ;
  - amendements ;
  - rapports ;
  - auteurs ;
  - groupes politiques.
- Ajouter une colonne “chambre” pour distinguer :
  - Assemblée nationale ;
  - Sénat.

Source 10 — Données entreprises et codes NAF

- Identifier les sources pour les données Sirene / INSEE.
- Identifier les sources pour les lauréats France 2030.
- Identifier les sources Bpifrance si disponibles.
- Identifier les sources sur les startups et entreprises innovantes.
- Récupérer pour chaque entreprise :
  - nom ;
  - SIREN ;
  - SIRET si disponible ;
  - code NAF ;
  - libellé NAF ;
  - secteur ;
  - région ;
  - effectif ;
  - chiffre d’affaires si disponible ;
  - lien avec une thématique ;
  - lien avec un appel à projet ;
  - lien avec un programme ;
  - source.

⸻

4. Structure de corrélation cible

Relation 1 — Programme → ligne budgétaire

- Relier chaque programme à ses lignes budgétaires.
- Exemple :
  - programme 424 ;
  - catégorie 3 ;
  - catégorie 6 ;
  - montants 2024, 2025, 2026.

Relation 2 — Programme → objectifs PAP

- Relier chaque programme à ses objectifs stratégiques.
- Relier chaque programme à ses indicateurs de performance.
- Relier chaque programme à ses verbatims officiels.
- Relier chaque programme à ses actions ou dispositifs.

Relation 3 — Programme → thématique

- Identifier les thématiques associées à chaque programme.
- Créer une relation directe :
  - programme 422 → recherche / valorisation / transfert technologique ;
  - programme 423 → modernisation des entreprises / industrie / transformation ;
  - programme 424 → investissements stratégiques / souveraineté / technologies critiques ;
  - programme 425 → écosystèmes d’innovation / startups / territoires / structures d’accompagnement.
- Ajouter un score de confiance pour chaque lien programme → thématique.

Relation 4 — Thématique → mots-clés

- Créer une liste de mots-clés par thématique.
- Distinguer :
  - mots-clés exacts ;
  - synonymes ;
  - acronymes ;
  - noms de dispositifs ;
  - noms d’opérateurs ;
  - noms d’entreprises ;
  - noms de technologies.
- Ajouter un score de pertinence à chaque mot-clé.

Relation 5 — Thématique → appels à projets

- Relier chaque appel France 2030 à une thématique.
- Relier chaque appel à un ou plusieurs mots-clés.
- Relier chaque appel à un programme si possible.
- Ajouter un score de confiance au lien.

Relation 6 — Thématique → codes NAF

- Associer chaque thématique à des codes NAF pertinents.
- Justifier le lien entre la thématique et le code NAF.
- Ajouter un score de confiance.
- Prévoir une validation manuelle sur les premiers codes NAF.

Relation 7 — Code NAF → entreprises

- Récupérer les entreprises associées aux codes NAF.
- Relier les entreprises aux thématiques via leur code NAF.
- Relier les entreprises aux appels à projets si elles sont identifiées comme bénéficiaires ou candidates.
- Relier les entreprises aux mentions parlementaires si elles sont citées.

Relation 8 — Mots-clés → débats parlementaires

- Rechercher les mots-clés dans les débats parlementaires.
- Compter les occurrences.
- Stocker le contexte de chaque occurrence.
- Relier chaque occurrence :
  - au mot-clé ;
  - à la thématique ;
  - au programme ;
  - à l’orateur ;
  - à la date ;
  - à la chambre ;
  - au texte débattu si disponible.

Relation 9 — Entreprise → débats parlementaires

- Rechercher les noms d’entreprises dans les débats parlementaires.
- Stocker les citations.
- Relier les entreprises citées à leurs thématiques.
- Relier les entreprises citées à leurs codes NAF.
- Relier les entreprises citées aux programmes associés.

Relation 10 — Budget → débat parlementaire

- Relier les montants budgétaires aux mentions parlementaires par programme.
- Calculer le nombre de mentions par programme.
- Calculer le nombre de mentions par thématique.
- Identifier les programmes très financés mais peu cités.
- Identifier les thématiques très citées mais peu financées.
- Produire un indicateur simple :
  - montant budgétaire ;
  - nombre de mentions ;
  - ratio mentions / montant ;
  - évolution dans le temps.

⸻

5. Modèle JSON cible

Objet “program”

- Créer un objet par programme.

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

Objet “budgetLine”

- Créer un objet par ligne budgétaire.

{
"id": "fr2030-424-6",
"programmeCode": "424",
"expenseCategoryCode": "6",
"expenseCategoryName": "Dépenses d’intervention",
"amount2024": 3318311564,
"amount2025": 4052897364,
"amount2026": 3364301779,
"sourceUrl": "",
"sourceDocument": "",
"sourcePage": "",
"qualityStatus": "verified"
}

Objet “theme”

- Créer un objet par thématique.

{
"themeId": "hydrogene",
"themeName": "Hydrogène",
"relatedProgrammes": ["424"],
"relatedBudgetLines": [],
"keywords": [],
"callsForProjects": [],
"nafCodes": [],
"companies": [],
"parliamentMentions": [],
"confidenceScore": 0.8
}

Objet “keyword”

- Créer un objet par mot-clé.

{
"keywordId": "kw-hydrogene",
"label": "hydrogène",
"type": "technology",
"relatedThemeId": "hydrogene",
"relatedProgrammes": ["424"],
"synonyms": ["hydrogène décarboné", "H2", "hydrogène vert"],
"confidenceScore": 0.9
}

Objet “callForProject”

- Créer un objet par appel à projet.

{
"callId": "fr2030-call-example",
"title": "",
"description": "",
"themeId": "",
"relatedProgrammes": [],
"operator": "",
"beneficiaryType": "",
"openingDate": "",
"closingDate": "",
"sourceUrl": "",
"keywords": []
}

Objet “parliamentMention”

- Créer un objet par mention parlementaire.

{
"mentionId": "",
"date": "",
"chamber": "Assemblée nationale",
"speakerName": "",
"politicalGroup": "",
"matchedKeyword": "",
"relatedThemeId": "",
"relatedProgrammeCode": "",
"interventionText": "",
"contextBefore": "",
"contextAfter": "",
"sourceUrl": "",
"confidenceScore": 0.8
}

Objet “company”

- Créer un objet par entreprise.

{
"companyId": "",
"companyName": "",
"siren": "",
"nafCode": "",
"nafLabel": "",
"relatedThemeIds": [],
"relatedProgrammeCodes": [],
"relatedCalls": [],
"parliamentMentions": [],
"revenue": null,
"employees": null,
"region": "",
"source": "",
"confidenceScore": 0.7
}

⸻

6. Tables de travail à produire

Table 1 — budget_lines

- id
- budget_type
- mission_code
- mission_name
- programme_code
- programme_name
- expense_category_code
- expense_category_name
- amount_2024
- amount_2025
- amount_2026
- ministry_code
- ministry_name
- source_url
- source_document
- source_page
- quality_status

Table 2 — programs

- programme_code
- programme_name
- mission_name
- strategic_summary
- objectives
- actions
- operators
- beneficiaries
- indicators
- source_pap_url
- source_rap_url
- key_verbatims

Table 3 — themes

- theme_id
- theme_name
- theme_description
- parent_theme
- related_programmes
- related_keywords
- confidence_score
- source

Table 4 — keywords

- keyword_id
- label
- type
- synonyms
- related_theme_id
- related_programmes
- confidence_score

Table 5 — calls_for_projects

- call_id
- title
- description
- theme_id
- related_programmes
- operator
- beneficiary_type
- opening_date
- closing_date
- source_url
- keywords

Table 6 — naf_codes

- naf_code
- naf_label
- related_theme_ids
- related_programmes
- confidence_score
- source

Table 7 — companies

- company_id
- company_name
- siren
- siret
- naf_code
- naf_label
- sector
- region
- employees
- revenue
- related_theme_ids
- related_programme_codes
- related_calls
- source
- confidence_score

Table 8 — parliament_mentions

- mention_id
- chamber
- date
- session_id
- speaker_name
- speaker_role
- political_group
- intervention_text
- matched_keyword
- keyword_type
- related_theme_id
- related_programme_code
- related_company_id
- source_url
- context_before
- context_after
- confidence_score

Table 9 — correlations

- correlation_id
- source_entity_type
- source_entity_id
- target_entity_type
- target_entity_id
- correlation_type
- confidence_score
- evidence_source
- evidence_text
- validation_status

⸻

7. Premières corrélations à créer

Corrélation programme → budget

- 421 → ligne fr2030-421-6.
- 422 → lignes fr2030-422-3 et fr2030-422-6.
- 423 → lignes fr2030-423-3, fr2030-423-6 et fr2030-423-7.
- 424 → lignes fr2030-424-3 et fr2030-424-6.
- 425 → lignes fr2030-425-3 et fr2030-425-6.

Corrélation programme → thématique initiale

- 421 → enseignement supérieur.
- 421 → recherche.
- 421 → formation.
- 422 → valorisation de la recherche.
- 422 → transfert technologique.
- 422 → innovation issue de la recherche.
- 423 → modernisation des entreprises.
- 423 → transformation industrielle.
- 423 → compétitivité.
- 423 → transition numérique.
- 424 → investissements stratégiques.
- 424 → souveraineté industrielle.
- 424 → technologies critiques.
- 424 → filières industrielles.
- 425 → écosystèmes d’innovation.
- 425 → startups.
- 425 → pôles d’innovation.
- 425 → territoires d’innovation.
- 425 → accompagnement des entreprises innovantes.

Corrélation thématique → mots-clés initiaux

- Recherche :
  - recherche ;
  - enseignement supérieur ;
  - laboratoire ;
  - doctorat ;
  - université ;
  - ANR.
- Valorisation :
  - valorisation de la recherche ;
  - transfert technologique ;
  - propriété intellectuelle ;
  - brevet ;
  - innovation de rupture.
- Modernisation :
  - modernisation des entreprises ;
  - industrie 4.0 ;
  - robotisation ;
  - automatisation ;
  - numérique ;
  - PME ;
  - ETI.
- Investissements stratégiques :
  - investissements stratégiques ;
  - souveraineté ;
  - filière stratégique ;
  - décarbonation ;
  - semi-conducteurs ;
  - hydrogène ;
  - batteries ;
  - nucléaire ;
  - quantique ;
  - intelligence artificielle.
- Écosystèmes d’innovation :
  - startup ;
  - French Tech ;
  - incubateur ;
  - accélérateur ;
  - pôle de compétitivité ;
  - écosystème d’innovation ;
  - financement de l’innovation.

⸻

8. Ordre d’exécution recommandé pour le POC

Étape 1 — Stabiliser le référentiel budgétaire

- Créer la table / JSON des programmes 421 à 425.
- Créer la table / JSON des lignes budgétaires.
- Vérifier les montants 2024, 2025, 2026.
- Associer chaque ligne budgétaire au bon programme.
- Associer chaque ligne budgétaire à sa catégorie de dépense.
- Ajouter les sources officielles.

Étape 2 — Extraire la matière qualitative des PAP

- Récupérer les PAP 421 à 425.
- Extraire les objectifs.
- Extraire les actions.
- Extraire les dispositifs.
- Extraire les opérateurs.
- Extraire les indicateurs.
- Extraire les verbatims.
- Associer chaque élément au bon programme.
- Créer une première liste de mots-clés par programme.

Étape 3 — Créer la taxonomie des thématiques

- Lister les thématiques France 2030 depuis les appels à candidatures.
- Regrouper les thématiques similaires.
- Associer chaque thématique à un ou plusieurs programmes.
- Associer chaque thématique à des mots-clés.
- Ajouter un score de confiance.
- Identifier les thématiques qui nécessitent une validation manuelle.

Étape 4 — Récupérer les appels à projets

- Récupérer les appels France 2030.
- Extraire titre, description, dates, opérateur, bénéficiaire, lien source.
- Associer chaque appel à une thématique.
- Associer chaque appel à des mots-clés.
- Associer chaque appel à un programme si possible.
- Créer les relations appel → thématique → programme.

Étape 5 — Rechercher les mentions parlementaires

- Récupérer les comptes rendus de l’Assemblée nationale.
- Rechercher les mots-clés par programme.
- Rechercher les mots-clés par thématique.
- Rechercher les noms d’opérateurs.
- Rechercher les noms de dispositifs.
- Stocker les mentions.
- Relier les mentions aux thématiques.
- Relier les mentions aux programmes.
- Stocker le contexte de citation.
- Extraire les verbatims les plus exploitables.

Étape 6 — Ajouter les codes NAF

- Pour chaque thématique, proposer une première liste de codes NAF.
- Justifier chaque code NAF par rapport à la thématique.
- Relier les codes NAF aux thématiques.
- Relier les codes NAF aux programmes via les thématiques.
- Ajouter un score de confiance.
- Prévoir une validation humaine.

Étape 7 — Ajouter les entreprises

- Identifier les entreprises depuis les appels à projets.
- Identifier les entreprises depuis les débats parlementaires.
- Identifier les entreprises depuis les documents budgétaires si présentes.
- Récupérer les informations Sirene.
- Ajouter le code NAF.
- Relier chaque entreprise à une thématique.
- Relier chaque entreprise à un programme.
- Relier chaque entreprise à une mention parlementaire si elle est citée.
- Ajouter un score de confiance.

Étape 8 — Produire le JSON final du POC

- Créer un JSON par programme.
- Créer un JSON par thématique.
- Créer un JSON global de corrélation.
- Vérifier que chaque relation dispose d’une source.
- Vérifier que chaque relation dispose d’un score de confiance.
- Vérifier que chaque donnée importante est reliée à son document source.
- Identifier les données manquantes.
- Identifier les relations faibles.
- Identifier les relations à valider manuellement.

⸻

9. Indicateurs minimum à produire dans le POC

Par programme

- Montant 2024.
- Montant 2025.
- Montant 2026.
- Évolution 2024 → 2025.
- Évolution 2025 → 2026.
- Nombre de thématiques associées.
- Nombre de mots-clés associés.
- Nombre d’appels à projets associés.
- Nombre de mentions parlementaires.
- Nombre de verbatims exploitables.

Par thématique

- Programmes associés.
- Montant budgétaire estimé ou directement associé.
- Nombre d’appels à projets.
- Nombre de mots-clés.
- Nombre de mentions parlementaires.
- Nombre d’entreprises identifiées.
- Nombre de codes NAF associés.
- Nombre de verbatims parlementaires.
- Score de confiance global.

Par mot-clé

- Thématique associée.
- Programme associé.
- Nombre d’occurrences dans les débats.
- Nombre d’occurrences dans les PAP / RAP.
- Nombre d’appels à projets où le mot-clé apparaît.
- Verbatims associés.

Par entreprise

- Nom.
- SIREN.
- Code NAF.
- Thématique associée.
- Programme associé.
- Appel à projet associé.
- Nombre de mentions parlementaires.
- Source d’identification.
- Score de confiance.

⸻

10. Règles de qualité de la donnée

- Chaque donnée budgétaire doit avoir une source officielle.
- Chaque montant doit être relié à une année.
- Chaque montant doit être relié à un programme.
- Chaque programme doit être relié à au moins une source PAP.
- Chaque thématique doit être reliée à au moins un mot-clé.
- Chaque mot-clé doit être relié à une thématique.
- Chaque mention parlementaire doit conserver son contexte.
- Chaque mention parlementaire doit conserver sa source.
- Chaque entreprise doit conserver sa source d’identification.
- Chaque relation automatique doit avoir un score de confiance.
- Les relations faibles doivent être marquées comme “à valider”.
- Les données manquantes doivent être explicitement listées.
- Les données contradictoires doivent être marquées comme “conflit”.
- Les données non sourcées ne doivent pas être utilisées pour le POC final.

⸻

11. Format de sortie attendu

Sortie 1 — Référentiel programmes

- Fournir un JSON ou tableau des programmes 421 à 425.
- Inclure les noms, montants, catégories de dépenses et sources.

Sortie 2 — Référentiel thématiques

- Fournir un JSON ou tableau des thématiques France 2030.
- Inclure les programmes associés, mots-clés et sources.

Sortie 3 — Référentiel mots-clés

- Fournir un JSON ou tableau des mots-clés.
- Inclure les synonymes, thématiques, programmes et types.

Sortie 4 — Référentiel appels à projets

- Fournir un JSON ou tableau des appels à projets.
- Inclure les thématiques, opérateurs, dates, bénéficiaires et sources.

Sortie 5 — Mentions parlementaires

- Fournir un JSON ou tableau des mentions parlementaires.
- Inclure date, orateur, texte, mot-clé, programme, thématique et source.

Sortie 6 — Corrélations

- Fournir un JSON ou tableau de toutes les relations créées.
- Inclure type de relation, source, cible, score de confiance et preuve.

⸻

12. Structure finale minimale du POC

- Un fichier programs.json.
- Un fichier budget_lines.json.
- Un fichier themes.json.
- Un fichier keywords.json.
- Un fichier calls_for_projects.json.
- Un fichier parliament_mentions.json.
- Un fichier naf_codes.json.
- Un fichier companies.json.
- Un fichier correlations.json.
- Un fichier sources.json.

⸻

13. Priorité finale

À faire absolument

- Programmes.
- Lignes budgétaires.
- Sources PAP.
- Thématiques.
- Mots-clés.
- Appels à projets.
- Mentions parlementaires.
- Corrélations.

À faire si le temps le permet

- Codes NAF.
- Entreprises.
- Sénat.
- Questions écrites.
- Amendements.
- Données économiques.
- Données brevets.

À garder pour une version 2

- Analyse économique complète.
- Analyse scientifique complète.
- Données brevets détaillées.
- CA et effectifs consolidés par secteur.
- Dashboard avancé.
- Rapport visuel page par page.
- Visualisations interactives.

⸻

14. Critère de réussite du POC

Le POC est réussi si l’on peut répondre avec les données structurées aux questions suivantes :

- Quel programme finance quelle thématique ?
- Quelle thématique est reliée à quels mots-clés ?
- Quels appels à projets sont liés à quelle thématique ?
- Quels mots-clés apparaissent dans les débats parlementaires ?
- Combien de fois une thématique est-elle citée au Parlement ?
- Quels programmes sont les plus financés ?
- Quels programmes sont les plus discutés ?
- Quelles thématiques sont très financées mais peu discutées ?
- Quelles thématiques sont très discutées mais peu financées ?
- Quelles entreprises ou secteurs ressortent des données ?
- Quels codes NAF peuvent être associés aux thématiques ?
- Quelles données restent faibles, incertaines ou à valider ?

⸻

15. Résumé de la logique de corrélation

- Le budget donne les programmes et les montants.
- Les PAP donnent le sens politique et opérationnel des programmes.
- Les appels à projets donnent les thématiques concrètes.
- Les mots-clés permettent de relier les thématiques aux débats.
- Les débats parlementaires donnent la visibilité politique des sujets.
- Les codes NAF donnent une correspondance économique.
- Les entreprises donnent une matérialisation terrain.
- Les corrélations permettent de relier tout cela dans une base exploitable.
- Le POC doit donc d’abord produire une base relationnelle claire avant toute restitution visuelle.
