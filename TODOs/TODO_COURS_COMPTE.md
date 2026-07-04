Oui — la Cour des comptes a des rapports exploitables, mais plutôt sous forme de rapports PDF / notes d’analyse, pas vraiment sous forme de base de données brute comme data.gouv.

Pour ton POC, la source la plus utile est la note d’exécution budgétaire “Investir pour la France de 2030”. Elle couvre précisément la mission budgétaire qui t’intéresse, avec les programmes 421, 422, 423, 424 et 425. La Cour y indique que la mission regroupe le PIA 3 et France 2030, avec le PIA 3 retracé dans les programmes 421, 422, 423, et France 2030 principalement dans les programmes 424 et 425.  

Ce qui est intéressant pour toi :

Source Cour des comptes	Intérêt pour ta BDD / JSON
NEB — Investir pour la France de 2030	Données budgétaires, exécution, gouvernance, programmes 421-425, opérateurs
Rapports sur les Investissements d’avenir / France 2030	Vision critique, suivi parlementaire, dispersion des indicateurs, pilotage
Rapports thématiques France 2030	Données par secteur : IA, semi-conducteurs, décarbonation, agences de programmes, etc.
Rapport sur la stratégie nationale IA	Exemple de rapport directement relié à une stratégie d’accélération France 2030
Rapports sur décarbonation / semi-conducteurs	Très utile pour relier une thématique à des financements, objectifs, opérateurs, limites

La Cour des comptes parle bien des stratégies nationales d’accélération : dans la note “Investir pour la France de 2030”, elle décrit la gouvernance avec le COMEX, le SGPI, les comités de pilotage ministériels, et le fait que ces comités pilotent les moyens financiers des stratégies d’accélération.  

Pour ton usage, je créerais une source dédiée :

Source : Cour des comptes
Type : rapport d’évaluation / note d’exécution budgétaire
Usage : enrichissement critique, exécution budgétaire, gouvernance, indicateurs, limites, recommandations
Niveau de confiance : élevé
Format : PDF / HTML, à transformer en données structurées

À ajouter dans ta TODO :

## Source complémentaire — Cour des comptes
- [ ] Rechercher les rapports Cour des comptes liés à “Investir pour la France de 2030”.
- [ ] Récupérer la note d’exécution budgétaire “Investir pour la France de 2030”.
- [ ] Extraire les passages sur les programmes 421, 422, 423, 424, 425.
- [ ] Extraire les montants globaux mentionnés pour France 2030.
- [ ] Extraire les opérateurs mentionnés :
  - [ ] ADEME
  - [ ] ANR
  - [ ] Bpifrance
  - [ ] Caisse des Dépôts
  - [ ] SGPI
- [ ] Extraire les éléments de gouvernance :
  - [ ] C2I
  - [ ] COMEX
  - [ ] comités de pilotage ministériels
  - [ ] stratégies nationales d’accélération
- [ ] Extraire les critiques / limites :
  - [ ] dispersion des indicateurs
  - [ ] difficulté de suivi parlementaire
  - [ ] pilotage complexe
  - [ ] lisibilité budgétaire
  - [ ] suivi des retours financiers
  - [ ] évaluation des impacts
- [ ] Extraire les recommandations de la Cour.
- [ ] Relier chaque recommandation à :
  - [ ] un programme budgétaire
  - [ ] une thématique France 2030
  - [ ] un opérateur
  - [ ] un problème de donnée
  - [ ] un risque de gouvernance
- [ ] Créer une table `court_of_auditors_reports`.
- [ ] Créer une table `court_of_auditors_findings`.
- [ ] Créer une table `court_of_auditors_recommendations`.

Structure JSON utile :

{
  "reportId": "cour-comptes-neb-france-2030-2026",
  "sourceName": "Cour des comptes",
  "reportTitle": "Investir pour la France de 2030",
  "reportType": "note_execution_budgetaire",
  "year": 2026,
  "relatedMission": "Investir pour la France de 2030",
  "relatedProgrammes": ["421", "422", "423", "424", "425"],
  "relatedThemes": [],
  "operatorsMentioned": ["ADEME", "ANR", "Bpifrance", "Caisse des Dépôts", "SGPI"],
  "findings": [],
  "recommendations": [],
  "sourceUrl": ""
}

Et pour les constats :

{
  "findingId": "finding-suivi-parlementaire",
  "reportId": "cour-comptes-neb-france-2030-2026",
  "findingType": "governance",
  "summary": "Difficulté de suivi parlementaire et dispersion des indicateurs.",
  "relatedProgrammes": ["421", "422", "423", "424", "425"],
  "relatedThemes": ["gouvernance", "performance", "suivi budgétaire"],
  "evidenceText": "",
  "sourcePage": null,
  "confidenceScore": 0.9
}

Donc oui : ce n’est pas une base de données exploitable directement, mais c’est une source très forte pour ajouter une couche “contrôle / audit / qualité de pilotage” à ta BDD.

Pour ton POC, je la classerais comme ça :

Niveau 1 — Données sources officielles :
budget.gouv.fr, data.economie.gouv.fr, data.assemblee-nationale.fr
Niveau 2 — Données de débat / visibilité politique :
comptes rendus Assemblée nationale, Sénat, amendements, questions
Niveau 3 — Données d’évaluation critique :
Cour des comptes
Niveau 4 — Données économiques :
Sirene, NAF, lauréats, entreprises, opérateurs

Et la vraie corrélation intéressante devient :

Budget prévu
→ Budget exécuté
→ Programme 421-425
→ Thématique France 2030 / SNA
→ Opérateur
→ Appels à projets
→ Mentions parlementaires
→ Critiques Cour des comptes
→ Niveau de lisibilité / pilotage / impact