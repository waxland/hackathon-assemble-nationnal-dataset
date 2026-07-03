# TODO - Dashboard Streamlit (Miroir du Front "minerve.gouv.fr")

Ce document dresse la feuille de route pour aligner l'outil d'exploration Data interne (`dashboard.py` sous Streamlit) avec la vision Produit officielle du frontend `minerve.gouv.fr` (telle que définie dans le projet principal React/Next.js).

L'objectif est que le Streamlit ne soit pas juste un "dump de la BDD", mais une véritable interface miroir du front-end, avec la même philosophie de navigation et d'UX, afin de servir de bac à sable pour l'équipe Data.

## 🎯 Vision Globale & Design System

- [x] **Cohérence visuelle (UI/UX)** :
  - Appliquer un thème sobre inspiré du standard de l'État (`sites.beta.gouv.fr` / DSFR).
  - Configurer `st.set_page_config` avec les bonnes couleurs (Bleu France) via un fichier `.streamlit/config.toml`.
  - Intégrer le logo ou l'icône `icon-minerve.png` dans la barre latérale.

## 🗺️ Architecture des Routes (Onglets ou Sidebar)

Le Streamlit doit refléter l'arborescence à 3 niveaux du Frontend Minerve :

- [x] **1. Route `/` -> "Accueil / Vue Macro"** :
  - Créer une page d'accueil d'atterrissage (Landing page de présentation du POC).
  - Afficher les macro-métriques (Budget global France 2030, nombre total de mentions à l'Assemblée, nombre d'entreprises).
  - Inclure le **Camembert de répartition des investissements 2026** (comme requis sur le Front).

- [x] **2. Route `/investissements` -> "Vue Transversale"** :
  - Créer un onglet listant les grands programmes (421 à 425) sous forme de tableau ou de "Cards".
  - Afficher un tableau croisé dynamique comparant les programmes sur différentes dimensions : Budget vs Appels à projets vs Startups financées.

- [x] **3. Routes `/investissements/[programmeCode]` -> "Rapports par Programme"** :
  - Implémenter un sélecteur dans la sidebar : *"Sélectionnez un Programme (421, 422, 423, 424, 425)"*.
  - Créer une vue "Rapport façon slide" pour le programme sélectionné.
  - La vue doit agréger, pour UN programme donné :
    - [x] Son budget précis (CP 2024, 2025, 2026).
    - [x] Sa taxonomie / ses mots-clés associés.
    - [x] L'écho parlementaire ciblé (ex: les débats liés au 424 uniquement).
    - [x] Les entreprises / startups de la French Tech financées (avec leur code NAF).

## 📊 Dataviz & Intégration Data (SQLite / JSON)

- [x] **Remplacement des requêtes "brutes"** :
  - Actuellement, le `dashboard.py` fait des requêtes SQL très génériques. Il faut créer des fonctions Python (ex: `get_program_metrics(prog_id)`) qui interrogent `france2030.sqlite` pour calculer les scores d'alignement attendus par le Front (ex: score de couverture Parlementaire vs Budget).
  - *Fait : Branché en lecture directe sur le contrat JSON (dossier dataset/).*
- [x] **Composants Dataviz "Miroir"** :
  - Re-créer les graphiques attendus sur le Front en utilisant `plotly` ou `altair` dans Streamlit (plus esthétique et interactif que `st.bar_chart`).
  - Graphiques attendus :
    - Répartition des lignes budgétaires (Titre 3 vs Titre 6).
    - Histogramme des interventions parlementaires dans le temps par groupe politique.

## 🛠️ Outils "Data" exclusifs au Streamlit

Puisque Streamlit est d'abord un outil d'exploration Data pour préparer le Front, il doit apporter des fonctionnalités de validation métier :

- [x] **Onglet "Qualité de la donnée"** :
  - Afficher les pourcentages de `isMock: true` vs `isMock: false` dans la BDD.
  - Lister les entreprises pour lesquelles le SIREN n'a pas été trouvé.
  - Afficher les "trous" (ex: "Aucune mention parlementaire trouvée pour le programme 421").
- [ ] **Onglet "Calcul de Score d'Alignement"** :
  - Créer une interface permettant à un Data Scientist de jouer avec des pondérations (ex: poids des débats vs poids des subventions) pour observer le "Score France 2030" changer en temps réel avant de le figer en JSON pour le Front.

---
*Ce TODO garantit que l'outil Streamlit n'avance pas à l'aveugle, mais reste le brouillon Data parfait pour le rendu final sur minerve.gouv.fr.*
