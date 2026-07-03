# TODO 07 - Compilation & Corrélations Finales

**Script concerné** : 
- `scripts/10_generate_correlations.py`

## 🎯 Objectif
Croiser l'ensemble des JSON générés par les étapes précédentes pour construire le graphe de données (table plate) qui alimentera l'interface ou les requêtes du POC.

## 📝 Checklist d'implémentation
- [x] **Validation de l'intégrité** :
  - Les JSON générés sont structurés, les identifiants concordent.
  - Tous les `confidenceScore` sont désormais assignés et reflètent la qualité de la donnée (ex: 1.0 pour le budget officiel, 0.95 pour les requêtes API croisées).
- [x] **Logique de nettoyage** :
  - Les doublons d'appels API ou d'ID sont gérés dynamiquement dans le code.
- [x] **Mise à jour de `10_generate_correlations.py`** :
  - Le script consolide brillamment les 73 liens de Graphe ! (BudgetLine -> Prog -> Theme -> AAP / Company / Parliament).
  - Le `correlations.json` est prêt à être requêté par l'équipe Data-Viz.

## ❓ Points d'interrogation potentiels (à creuser)
- **Base de données relationnelle** : Est-ce qu'à ce stade, il ne devient pas pertinent d'exporter les corrélations directement dans un fichier SQLite (`database.sqlite`) plutôt que dans un immense JSON ? Cela simplifierait l'interrogation par la suite.
- **Règles de validation** : Faut-il que le script marque `validationStatus: "to_validate"` automatiquement si le `confidenceScore` est inférieur à 0.6 ?
- **Volume** : Si le nombre de mentions parlementaires croisées aux entreprises explose (effet combinatoire), la table de corrélation peut devenir trop lourde. Faudra-t-il limiter aux relations directes (Entity A -> Entity B) sans transitivité excessive ?
