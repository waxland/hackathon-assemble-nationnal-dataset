# TODO 03 - Thématiques et Mots-clés

**Scripts concernés** : 
- `scripts/04_generate_themes.py`
- `scripts/05_generate_keywords.py`

## 🎯 Objectif
Rendre la taxonomie France 2030 (les "thèmes" et les "mots-clés") robuste, officielle et exhaustive, pour que le croisement (scraping des AAP et des mentions parlementaires) ait un haut taux de succès.

## 📝 Checklist d'implémentation
- [x] **Investigation des sources** :
  - Rechercher le dossier de presse officiel France 2030 (gouvernement.fr ou sgpi.gouv.fr) pour lister les "10 objectifs" originaux (ex: Décarbonation, Santé, Espace, Fonds marins...).
- [x] **Mise à jour de `04_generate_themes.py`** :
  - Remplacer les thèmes temporaires par la vraie nomenclature officielle de France 2030.
  - Mettre en place un mapping clair : 1 Thème = X Programmes budgétaires (le plus souvent 424 ou 425).
- [x] **Mise à jour de `05_generate_keywords.py`** :
  - Pour chaque thème officiel, générer un set de mots-clés riches.
  - Ajouter les acronymes courants (ex: SMR pour Petits Réacteurs Modulaires, hydrogène, IA générative).
  - Inclure les noms des dispositifs connus (ex: "French Tech 2030", "Première Usine").

## ❓ Points d'interrogation potentiels (à creuser)
- **Extension des mots-clés** : Doit-on utiliser un LLM ou l'API conceptnet/wordnet pour étendre automatiquement le dictionnaire de synonymes, afin de ne rater aucune mention à l'Assemblée ?
- **Ambiguïté sémantique** : Comment gérer les mots-clés trop génériques (ex: "santé" ou "recherche") qui vont générer de faux positifs dans les débats parlementaires ? Faut-il forcer l'association à "France 2030" (ex: recherche AND "france 2030") ?
- **Pondération** : Certains mots-clés doivent-ils avoir un `confidenceScore` plus élevé que d'autres (ex: le mot "SMR" est très spécifique, le mot "industrie" ne l'est pas) ?
