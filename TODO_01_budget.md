# TODO 01 - Référentiel Budgétaire (Programmes & Lignes)

**Scripts concernés** : 
- `scripts/01_extract_programs.py`
- `scripts/02_extract_budget_lines.py`

## 🎯 Objectif
Extraire les vraies données chiffrées du budget de l'État (PLF 2026 ou 2025) pour la mission "Investir pour la France de 2030" (Programmes 421 à 425) afin de remplacer les données "mockées".

## 📝 Checklist d'implémentation
- [x] **Investigation des sources** : 
  - Chercher le jeu de données "PLF 2026 - données chiffrées" (ou 2025) sur `data.gouv.fr` ou `budget.gouv.fr`.
  - Trouver le fichier CSV ou Excel exact (ex: "Dépenses du BG selon nomenclatures destination et nature").
- [x] **Exploration de la donnée** :
  - Télécharger le fichier et l'ouvrir avec `pandas`.
  - Filtrer la colonne "Mission" pour isoler "Investir pour la France de 2030".
  - Vérifier la présence des programmes 421, 422, 423, 424, 425.
- [x] **Mise à jour de `01_extract_programs.py`** :
  - Extraire dynamiquement la liste des programmes depuis le CSV.
  - Conserver la structure du JSON de sortie (`data/programs.json`).
- [x] **Mise à jour de `02_extract_budget_lines.py`** :
  - Extraire les montants (exécutés 2024, votés 2025, prévus 2026).
  - Grouper par "Catégorie de dépense" (Titre 3 - Fonctionnement, Titre 6 - Intervention, etc.).
  - Sauvegarder dans `data/budget_lines.json`.

## ❓ Points d'interrogation potentiels (à creuser)
- **AE vs CP** : Les montants dans le fichier source sont-ils exprimés en Autorisations d'Engagement (AE) ou en Crédits de Paiement (CP) ? (Il faut privilégier les CP pour les dépenses réelles, ou stocker les deux).
- **Unité de valeur** : Les montants sont-ils en euros, en milliers d'euros ou en millions d'euros ?
- **Catégories manquantes** : Que faire si un programme n'a pas de Titre 3 ou Titre 6 pour une année donnée (ex: ligne à 0€) ? Doit-on l'exclure du JSON ?
- **Stabilité de l'URL** : L'URL du CSV source est-elle fixe ou change-t-elle à chaque version du PLF ? Faut-il plutôt se baser sur l'API de data.gouv.fr ?
