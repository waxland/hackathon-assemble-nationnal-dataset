# 📊 Bilan du Développement Dashboard Streamlit (Outil Interne)

Ce document récapitule l'ensemble du travail de conception et d'implémentation de notre interface interne Python/Streamlit (`app/`). Il a été construit comme un outil d'exploration Data pour l'équipe, et surtout comme un miroir fidèle du contrat JSON attendu par le Front-End (`Minerve`).

---

## 🏛️ Architecture et Pages du Dashboard

L'application a été restructurée avec un Routeur multi-pages natif. Voici l'analyse de chaque module.

### `app.py` & `home_intro.md` (Accueil)
*Point d'entrée du routeur, gérant la configuration globale et l'explication métier.*
* **✅ PROS** :
  - Centralisation du logo (`favicon.svg`) et de la configuration des onglets.
  - Implémente le design system de l'État (couleurs Bleues/Rouges via `.streamlit/config.toml`).
  - Cache natif `@st.cache_data` pour charger les JSON sans latence.
* **⚠️ CONS** :
  - Le texte d'intro est statique. Si la mission du hackathon pivote, il faudra éditer le `.md` manuellement.
* **💡 Améliorations possibles** :
  - [ ] Rendre l'URL du repository GitHub et du projet Vercel dynamiques via un `.env` pour les afficher sur l'accueil.
  - [ ] Afficher un log des derniers commits ou de la dernière date d'exécution de `make export-front` pour s'assurer que les données lues sont fraîches.

### `1_Vue_Macro.py`
*Vue d'agrégation affichant les grands totaux du budget et de l'écho parlementaire.*
* **✅ PROS** :
  - Utilise `plotly.express` pour un Camembert interactif et responsive (nettement supérieur au `st.bar_chart` par défaut).
  - Fournit en 1 coup d'œil les 3 "Kpis" majeurs du projet.
* **⚠️ CONS** :
  - L'agrégation est calculée en mémoire avec Pandas `sum()` sur des dataframes. Si le volume JSON explose (ex: des années de budget), la RAM en pâtira.
* **💡 Améliorations possibles** :
  - [ ] Ajouter une comparaison "Année sur Année" (YtY) via des graphiques en courbes (ex: Budget 2024 vs 2025).
  - [ ] Ajouter un Sankey Diagram (Diagramme de flux) complexe montrant l'argent allant des Catégories de Dépense vers les Thématiques.

### `2_Vue_Transversale.py`
*Tableau de bord croisant la complétude de la donnée pour chaque programme France 2030.*
* **✅ PROS** :
  - Permet de voir instantanément quel programme est riche en données, et quel programme est un "trou noir" (ex: 0 entreprise, 0 mention).
* **⚠️ CONS** :
  - Le tableau `st.dataframe` est basique et ne permet pas d'export immédiat (CSV/Excel) côté utilisateur.
* **💡 Améliorations possibles** :
  - [ ] Ajouter des filtres dynamiques (ex: "Afficher uniquement les programmes avec des mentions > 10").
  - [ ] Permettre un export des résultats transverses en Excel directement depuis le Dashboard.

### `3_Rapport_Programme.py`
*Vue "Slide" filtrée dynamiquement via un Selectbox (Le cœur du miroir Front-End).*
* **✅ PROS** :
  - UX en double colonne ultra dense (Budget à gauche, Parlement à droite, Startups en bas).
  - Les verbatims des discours sont gérés via des `st.expander` pour ne pas polluer l'écran.
  - Chronologie des interventions via Histogramme Plotly triée par Groupe Politique.
* **⚠️ CONS** :
  - Si un programme compte 15 000 mentions (ex: le nucléaire), le rendu des `st.expander` fera crasher le navigateur du client.
* **💡 Améliorations possibles** :
  - [ ] Implémenter une vraie pagination (10 par 10) pour l'affichage des verbatims dans Streamlit.
  - [ ] Lier la temporalité des discours à celle du budget (Superposer le budget 2024/2025 avec les pics de discours de ces mêmes années).
  - [ ] Brancher un appel API LLM pour afficher un "Résumé de sentiment" (Les députés sont-ils "Pour" ou "Contre" ce programme ?)

### `4_Data_Quality.py`
*Outil exclusif de l'équipe Data pour auditer les JSON et pondérer les scores empiriques.*
* **✅ PROS** :
  - Track impitoyablement les fichiers ayant conservé l'attribut `"isMock": true`.
  - Propose un outil de simulation interactive (`st.slider`) pour ajuster le "Score d'Alignement". Cela permet aux PMs de jouer avec les maths sans toucher au code Python.
* **⚠️ CONS** :
  - Le score d'alignement simulé ici n'est pas réécrit dynamiquement dans la base. Le Data Engineer doit encore lire le résultat à l'écran et aller modifier `13_export_to_front_contract.py` à la main.
* **💡 Améliorations possibles** :
  - [ ] Permettre au Dashboard d'écraser directement le fichier `programme-alignment-scores.json` lorsque l'utilisateur clique sur un bouton "Sauvegarder cette formule".
  - [ ] Ajouter un validateur de Schéma JSON (Pydantic / JSONSchema) qui affiche des erreurs en rouge si les clés des JSON ne correspondent plus au contrat exact de `TODO_DATASET_JSON.md`.
