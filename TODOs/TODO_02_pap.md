# TODO 02 - Extraction Qualitative des PAP

**Script concerné** : 
- `scripts/03_parse_pap.py`

## 🎯 Objectif
Remplacer les objectifs et actions "mockés" par les vrais textes stratégiques extraits des PDF des Projets Annuels de Performances (PAP) annexés au Projet de Loi de Finances.

## 📝 Checklist d'implémentation
- [x] **Investigation des sources** :
  - Localiser l'URL exacte des PDF des PAP pour la mission "Investir pour la France de 2030" (budget.gouv.fr).
  - *Trouvaille*: La donnée est en fait dispo en format ouvert structuré (`PLF 2025 - Performance de la dépense`) ! Pas besoin de parser de PDF.
- [x] **Test d'extraction PDF / CSV** :
  - Créer un notebook ou script de test pour télécharger un PDF (ou CSV).
  - Analyser les colonnes `Libellé Objectif` et `Libellé Action`.
- [x] **Mise à jour de `03_parse_pap.py`** :
  - Automatiser le téléchargement du CSV `raw_pap_2025.csv`.
  - Extraire spécifiquement :
    - Les "Objectifs" en filtrant le `Code Programme`
    - Les "Actions" financées en croisant avec `raw_budget.csv`.
  - Sauvegarder en fusionnant ces données dans `data/programs.json`.

## ❓ Points d'interrogation potentiels (à creuser)
- **Format du PDF** : Les PDF budgétaires sont notoirement complexes (colonnes multiples, tableaux). `pdfplumber` va-t-il casser les paragraphes ? Faut-il une étape de nettoyage (NLP / suppression des retours à la ligne intempestifs) ?
- **Disponibilité en Open Data** : Existe-t-il une version JSON/XML ou structurée des PAP sur data.gouv.fr (ex: base "PLF Performance") pour éviter le parsing de PDF ?
- **Pertinence des verbatims** : Doit-on confier l'extraction des "verbatims importants" à un LLM local ou via API, plutôt que de tout extraire bêtement en Regex ?
