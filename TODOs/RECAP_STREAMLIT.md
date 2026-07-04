# 📊 Bilan du Développement Dashboard Streamlit (Outil Interne)

Ce document récapitule l'ensemble du travail de conception et d'implémentation de notre interface interne Python/Streamlit (`app/`). Il a été construit comme un outil d'exploration Data pour l'équipe, et surtout comme un miroir fidèle du contrat JSON attendu par le Front-End (`Minerve`).

---

## 🏛️ Architecture et Pages du Dashboard

L'application a été restructurée avec un Routeur multi-pages natif. Voici l'analyse de chaque module.

### `1_Vue_Macro.py`
*Vue d'agrégation affichant les grands totaux du budget et de l'écho parlementaire.*
* **✅ PROS** :
  - Utilise `plotly.express` pour un Camembert interactif et responsive (nettement supérieur au `st.bar_chart` par défaut).
  - Fournit en 1 coup d'œil les 3 "Kpis" majeurs du projet.
* **💡 Améliorations possibles** :
  - [x] **Temporalité (YtY)** : Ajouter une comparaison "Année sur Année" via des graphiques en courbes (ex: Budget 2024 vs 2025).
  - [x] **Sankey Diagram** : Ajouter un diagramme de flux complexe montrant l'argent allant des Catégories de Dépense vers les Programmes.
  - [x] **Cartographie** : Intégrer une carte de France (`st.map`) pointant la localisation géographique des entreprises financées quand les coordonnées Sirene sont disponibles.

### `2_Vue_Transversale.py`
*Tableau de bord croisant la complétude de la donnée pour chaque programme France 2030.*
* **✅ PROS** :
  - Permet de voir instantanément quel programme est riche en données, et quel programme est un "trou noir" (ex: 0 entreprise, 0 mention).
* **⚠️ CONS** :
  - Le tableau `st.dataframe` est basique et ne permet pas d'export immédiat (CSV/Excel) côté utilisateur pour l'instant.
* **💡 Améliorations possibles** :
  - [x] **Filtres Avancés** : Ajouter des filtres dynamiques (ex: "Afficher uniquement les programmes avec des mentions > 10").
  - [x] **Export Data** : Permettre un export des résultats transverses en Excel/CSV via un bouton `st.download_button` directement depuis le Dashboard.
  - [x] **Tri conditionnel** : Ajouter un code couleur (Heatmap) dans le tableau pour mettre en surbrillance les lignes où la donnée manque (en rouge).

### `3_Rapport_Programme.py`
*Vue "Slide" filtrée dynamiquement via un Selectbox (Le cœur du miroir Front-End).*
* **✅ PROS** :
  - UX en double colonne ultra dense (Budget à gauche, Parlement à droite, Startups en bas).
  - Les verbatims des discours sont gérés via des `st.expander` pour ne pas polluer l'écran.
  - Chronologie des interventions via Histogramme Plotly triée par Groupe Politique.
* **⚠️ CONS** :
  - Si un programme compte 15 000 mentions (ex: le nucléaire), le rendu de milliers de `st.expander` fera crasher le navigateur du client.
* **💡 Améliorations possibles** :
  - [x] **Pagination des Verbatims** : Implémenter une vraie pagination (10 par 10) pour l'affichage des verbatims dans Streamlit.
  - [x] **Superposition Temporelle** : Lier la temporalité des discours à celle du budget (Superposer le budget 2024/2025 avec les pics de discours de ces mêmes années sur le même graphe Plotly).
  - [x] **Analyse de Sentiment locale** : Ajouter un résumé de tonalité heuristique sans dépendance API externe.
  - [x] **Nuage de mots (Wordcloud)** : Générer un nuage de mots des thématiques les plus abordées par les parlementaires pour un programme donné.

### `4_Data_Quality.py`
*Outil exclusif de l'équipe Data pour auditer les JSON et pondérer les scores empiriques.*
* **✅ PROS** :
  - Track impitoyablement les fichiers ayant conservé l'attribut `"isMock": true`.
  - Propose un outil de simulation interactive (`st.slider`) pour ajuster le "Score d'Alignement". Cela permet aux PMs de jouer avec les maths sans toucher au code Python.
* **⚠️ CONS** :
  - Le score d'alignement simulé ici n'est pas réécrit dynamiquement dans la base. Le Data Engineer doit encore lire le résultat à l'écran et aller modifier `13_export_to_front_contract.py` à la main.
* **💡 Améliorations possibles** :
  - [x] **Validation de Schéma stricte** : Ajouter un validateur de Schéma JSON (Pydantic / JSONSchema) qui affiche des erreurs en rouge si les clés des JSON ne correspondent plus au contrat exact de `TODO_DATASET_JSON.md`.
  - [x] **Sauvegarde des pondérations** : Écrire les scores ajustés dans `dataset/`, `data/export_front/` et sauvegarder les poids dans `data/score_weights.json`.
