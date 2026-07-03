# TODO 06 - Entreprises & Codes NAF

**Scripts concernés** : 
- `scripts/08_map_naf_codes.py`
- `scripts/09_fetch_companies.py`

## 🎯 Objectif
Identifier les entreprises qui bénéficient de France 2030 et les relier à leurs secteurs macro-économiques (Codes NAF) pour pouvoir, à terme, mesurer l'impact sur l'économie réelle.

## 📝 Checklist d'implémentation
- [x] **Investigation des sources (Lauréats)** :
  - Constitution d'une liste de Lauréats ultra-connus (Verkor, Ynsect, Mistral AI, Pasqal, Lhyfe).
- [x] **Investigation API Sirene** :
  - Étude réussie de `recherche-entreprises.api.gouv.fr` (API ouverte).
  - Validation du retour (Code NAF, SIREN).
- [x] **Mise à jour de `08_map_naf_codes.py`** :
  - *(Fusionné dans le script 09)* : Les codes NAF sont déduits et stockés dynamiquement à la volée.
- [x] **Mise à jour de `09_fetch_companies.py`** :
  - Pour chaque entreprise, appel de l'API Sirene.
  - Extraction du code NAF exact (ex: `27.20Z` pour Verkor), association au Thème de l'entreprise.
  - Gestion d'un `time.sleep(0.5)` pour contourner le rate limiting de l'API.

## ❓ Points d'interrogation potentiels (à creuser)
- **Rate limiting** : L'API `recherche-entreprises` est limitée (ex: 7 requêtes/seconde). Le script doit impérativement intégrer un système de `time.sleep()` ou de `Retry`.
- **Qualité des données Bpifrance** : Parfois, les aides sont versées à des filiales ou des SPV (Special Purpose Vehicles). Le code NAF sera alors "Fonds de placement" ou "Holding" au lieu du vrai code industriel. Comment gérer cette perte de sens ?
- **SIREN manquant** : Si le CSV des lauréats n'a que des noms (ex: "GreenTech SAS"), l'API Sirene peut retourner 10 entreprises homonymes. Faut-il prendre le premier résultat ? Filtrer par région ? (Le `confidenceScore` sera très utile ici).
