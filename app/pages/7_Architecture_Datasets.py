import streamlit as st
from streamlit_sidebar import render_sidebar

st.set_page_config(page_title="Architecture des Datasets", page_icon="📚", layout="wide")
render_sidebar("Architecture Datasets")

col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/favicon.svg", width=80)
with col_text:
    st.title("📚 Architecture & Explication des Datasets")

st.markdown("---")

st.header("1. Schéma Global d'Ingestion (ETL)")

# Schéma statique en texte brut si Mermaid ne s'affiche pas correctement
st.code("""
[ SOURCES EXTERNES ]
  ├─ Open Data Economie (Budget PLF)
  ├─ NosDéputés.fr (Débats Parlementaires)
  ├─ INSEE Sirene (Entreprises & NAF)
  ├─ Caisse des Dépôts / ADEME (Lauréats & AAP)
  └─ INPI (Brevets)
        │
        ▼
[ PIPELINE PYTHON ]
  └─ Base SQLite Centrale (france2030.sqlite)
        │
        ├─► [ EXPORTS MINERVE ] (JSON Contrat Front-end)
        └─► [ NEO4J ] (CSV Graphe Neo4j)
""", language="")

st.markdown("---")
st.header("2. Analyse Détaillée des Datasets")

# Dataset 1: Budget
st.subheader("💶 Open Data Économie : Budget PLF")
st.markdown("**URL / Endpoint principal** : `https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/plf25-depenses-2025-du-bg-et-des-ba-selon-nomenclatures-destination-et-nature/exports/csv`")
st.markdown("**Description** : Contient les lignes budgétaires (Autorisations d'Engagement et Crédits de Paiement) allouées aux différents programmes (ex: 421, 422, 424...). Utilisé pour le Poids Financier.")
col1, col2 = st.columns(2)
with col1:
    st.success("**Avantages (Pros)**\n- Source officielle de l'État, totalement opposable.\n- Mise à jour annuelle systématique.\n- Granularité fine (Titre, Catégorie, Nature).")
with col2:
    st.error("**Inconvénients (Cons)**\n- L'API ne contient que le PLF N et N-1, difficile d'avoir l'historique long.\n- La nomenclature peut changer d'une année sur l'autre.\n- Ne donne aucun lien vers l'utilisation finale (les entreprises).")

# Dataset 2: Sirene
st.subheader("🏢 INSEE : Base Sirene (StockUniteLegale)")
st.markdown("**URL / Endpoint principal** : `https://www.data.gouv.fr/api/1/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/`")
st.markdown("**Description** : Référentiel national des entreprises françaises. Permet d'associer un SIREN à un nom officiel, une date de création et surtout un code NAF (secteur d'activité).")
col1, col2 = st.columns(2)
with col1:
    st.success("**Avantages (Pros)**\n- Base exhaustive de toutes les entreprises en France.\n- Permet une classification robuste par secteur.\n- Fiabilité totale (INSEE).")
with col2:
    st.error("**Inconvénients (Cons)**\n- Fichier CSV extrêmement volumineux (> 1.5 Go) nécessitant un traitement en streaming pour ne pas saturer la RAM.\n- Ne contient pas de données financières (comme le chiffre d'affaires).")

# Dataset 3: NosDéputés
st.subheader("🏛️ NosDéputés.fr : Débats et Amendements")
st.markdown("**URL / Endpoint principal** : `https://www.nosdeputes.fr/16/questions/mots/[MOT-CLE]/json`")
st.markdown("**Description** : Scraping de l'API de l'association Regards Citoyens pour obtenir les mentions (Questions écrites, Amendements) de France 2030 ou de thématiques spécifiques à l'Assemblée Nationale.")
col1, col2 = st.columns(2)
with col1:
    st.success("**Avantages (Pros)**\n- API simple avec retour en JSON propre.\n- Apporte une richesse sémantique énorme (permet de relier politique et budget).\n- Inclut l'affiliation politique du député.")
with col2:
    st.error("**Inconvénients (Cons)**\n- Risque de blocage (Rate-Limit strict).\n- Limité à l'Assemblée Nationale (ignore le Sénat).\n- Moteur de recherche par mot-clé basique qui peut générer des faux positifs hors contexte.")

# Dataset 4: CDC / ADEME
st.subheader("🌍 Caisse des Dépôts / ADEME : Projets et Lauréats")
st.markdown("**URL / Endpoint principal** : `https://opendata.caissedesdepots.fr/api/explore/v2.1/catalog/datasets/liste-des-laureats/exports/csv`")
st.markdown("**Description** : Liste des projets financés par les opérateurs de l'État dans le cadre de France 2030 (ex: Démonstrateurs Ville Durable). C'est le lien concret entre l'argent et le terrain.")
col1, col2 = st.columns(2)
with col1:
    st.success("**Avantages (Pros)**\n- Identifie clairement le bénéficiaire via son SIREN.\n- Contient de vrais indicateurs d'impact écologique (ex: tonnes de CO2 économisées, m² dépollués).")
with col2:
    st.error("**Inconvénients (Cons)**\n- Très hétérogène : les formats diffèrent selon l'opérateur (ADEME vs BPI vs CDC).\n- Parfois, pour des raisons de secret industriel, les montants exacts de la subvention sont masqués.")

# Dataset 5: INPI
st.subheader("💡 INPI : Dépôts de Brevets (Innovation)")
st.markdown("**URL / Endpoint principal** : `https://data.inpi.fr/` (Mocké partiellement dans le POC)")
st.markdown("**Description** : Base de données des familles de brevets. Utilisée pour vérifier qu'une entreprise financée par France 2030 a réellement une activité de propriété intellectuelle.")
col1, col2 = st.columns(2)
with col1:
    st.success("**Avantages (Pros)**\n- Excellent proxy 'hard data' pour évaluer la capacité d'innovation technologique.\n- Informations internationales.")
with col2:
    st.error("**Inconvénients (Cons)**\n- Accès API complexe nécessitant des tokens et une pagination ardue.\n- Associer un brevet spécifique au projet précis financé par l'État est très difficile (on l'associe globalement à l'entreprise).")

st.markdown("---")
st.info("💡 **Contexte** : Ces datasets sont agrégés dans `france2030.sqlite` puis exportés sous forme de contrats JSON stricts consommés par le front-end React Minerve.")
