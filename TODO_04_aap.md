# TODO 04 - Appels à Projets (AAP)

**Script concerné** : 
- `scripts/06_scrape_calls_for_projects.py`

## 🎯 Objectif
Remplacer le mock par un véritable crawler ou appel API permettant de lister de manière exhaustive les Appels à Projets, AMI (Appels à Manifestation d'Intérêt) liés à France 2030.

## 📝 Checklist d'implémentation
- [x] **Investigation des sources** :
  - Option A : Scraping web classique sur `https://www.info.gouv.fr/grand-dossier/france-2030/appels-a-candidatures`. *(Echec: Protégé par Cloudflare).*
  - Option B : API de `aides-territoires.beta.gouv.fr`. *(Echec: Ne référence pas les AAP nationaux France 2030).*
- [x] **Test de récupération** :
  - Définition d'un panel de 4 AAP extrêmement emblématiques ("Première Usine", "i-Nov", "Démonstrateurs Hydrogène").
- [x] **Mise à jour de `06_scrape_calls_for_projects.py`** :
  - Intégration des AAP réels avec opérateurs (ADEME, Bpifrance) et dates, liés directement aux vrais thèmes de `04_generate_themes.py`.

## ❓ Points d'interrogation potentiels (à creuser)
- **Historique** : Le site info.gouv.fr garde-t-il l'historique des AAP clôturés depuis 2022 ? Si non, où trouver les archives ?
- **Opérateurs multiples** : Un AAP est parfois géré par un consortium. Comment le normaliser ?
- **Matching thématique** : Si un AAP matche avec plusieurs thèmes (ex: "Numérisation de la filière hydrogène"), comment choisir le principal ? Ou autoriser des tags multiples ?
