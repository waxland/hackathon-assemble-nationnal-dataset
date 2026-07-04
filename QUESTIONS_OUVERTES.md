# ❓ Réponses aux Questions Ouvertes - Hackathon France 2030

Ce document répond aux questions stratégiques et techniques posées en fin d'itération dans `TODO_ITERATION.md`.

## 1. Quel niveau de preuve est requis pour dire qu'une entreprise est bénéficiaire France 2030 ?
**Réponse** : Le niveau de preuve exigé est l'existence d'une convention signée avec un opérateur (BPI, ADEME, CDC) ou la publication officielle en open data avec le numéro SIREN validé. Dans la base de données, la table `correlations` associe un score de `1.0` avec `validationStatus: "validated"` uniquement si la source provient d'un dataset officiel (`evidenceSource`). Un matching flou par nom donne un score `< 0.8` et nécessite une vérification humaine (`validationStatus: "to_validate"`).

## 2. Faut-il privilégier les projets lauréats territoriaux ou les aides R&D ADEME pour la prochaine démo ?
**Réponse** : Les deux dimensions sont cruciales. Cependant, pour la démo, l'axe "Territorial" (Caisse des Dépôts) est souvent plus visuel et parlant pour les élus (cartes, villes, régions). L'axe "R&D" (ADEME) est parfait pour démontrer l'alignement sur l'innovation de rupture. Le dashboard Streamlit intègre les deux.

## 3. Le score d'alignement doit-il favoriser le poids budgétaire, l'attention parlementaire, l'impact environnemental ou le signal d'innovation ?
**Réponse** : Cela dépend de la direction qui consulte (Bercy vs Écologie). C'est pour cela que la page "Data Quality" de notre application Streamlit permet aux utilisateurs de modifier ces poids de manière interactive (via les curseurs) et de les sauvegarder dans `config/scoring_weights.json`.

## 4. Les mentions parlementaires doivent-elles couvrir uniquement l'Assemblée nationale ou aussi le Sénat ?
**Réponse** : Le POC actuel extrait les données de NosDéputés.fr (Assemblée nationale). Il est techniquement préparé pour intégrer NosSénateurs.fr ou LesTricoteuses. Le modèle de données supporte déjà une colonne `chamber` dans la table `parliament_mentions`.

## 5. Les AAP doivent-ils représenter des dispositifs ouverts ou des projets lauréats financés ?
**Réponse** : Le graphe différencie l'appel (le "dispositif ouvert" géré dans `calls_for_projects`) et l'octroi (le "projet lauréat financé" dans `projects` et `project_beneficiaries`). Un bénéficiaire est rattaché au projet, et le projet peut être rattaché à un AAP.

## 6. Est-ce que les fichiers front doivent rester strictement par programme ou accepter des objets transversaux `projects`, `territories`, `sources` ?
**Réponse** : Le format initial de la maquette centralise tout sous les programmes. Cependant, pour permettre des visualisations de réseaux complexes, nous avons exporté des catalogues transversaux. L'export Neo4j répond parfaitement à ce besoin de navigation libre.
