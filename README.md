# Hackathon Assemblée Nationale - Dataset France 2030

Ce dépôt contient les scripts et les données générées pour le Hackathon de l'Assemblée Nationale (POC). L'objectif est de relier le budget de l'État (Mission France 2030) aux débats parlementaires, en passant par les thématiques d'innovation et les entreprises lauréates.

## 🗂️ Architecture des données

L'ensemble des scripts génère une base de données relationnelle (disponible au format JSON plat et SQLite) qui mappe les entités suivantes :

- **Programmes budgétaires** (421 à 425)
- **Lignes budgétaires** (Montants CP 2025 sourcés PLF)
- **Thématiques** (Les 10 objectifs officiels de France 2030)
- **Mots-clés** (Taxonomie enrichie)
- **Mentions parlementaires** (Amendements et questions écrites extraits de l'Open Data)
- **Appels à projets (AAP)** (Soutien French Tech, i-Nov...)
- **Entreprises et Codes NAF** (Extraction des SIREN/NAF via l'API publique)
- **Corrélations** (Graphe reliant l'ensemble de ces entités)

Consultez le fichier [DATASETS.md](DATASETS.md) pour voir le diagramme Entité-Association complet.

## 🚀 Utilisation

Un environnement virtuel Python est nécessaire pour faire tourner la chaîne de scraping et d'ingestion.

### 1. Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Pipeline de génération des données

Les scripts doivent être exécutés dans l'ordre pour générer la base complète.

```bash
# 1. Extraction du PLF 2026 (Open Data Budget)
python3 scripts/01_extract_programs.py
python3 scripts/02_extract_budget_lines.py

# 2. Parsing des Objectifs de performance (PAP)
python3 scripts/03_parse_pap.py

# 3. Génération de la taxonomie (Thèmes et Mots-clés)
python3 scripts/04_generate_themes.py
python3 scripts/05_generate_keywords.py

# 4. Appels à projets et Mentions parlementaires
python3 scripts/06_scrape_calls_for_projects.py
python3 scripts/07_fetch_parliament_mentions.py

# 5. Extraction API Sirene (Entreprises)
python3 scripts/08_map_naf_codes.py
python3 scripts/09_fetch_companies.py

# 6. Compilation finale et base SQLite
python3 scripts/10_generate_correlations.py
python3 scripts/11_export_to_sqlite.py
```

## 📊 Base SQLite

Le pipeline génère un fichier `data/france2030.sqlite` prêt à être requêté par vos outils de Dataviz (Metabase, Streamlit, etc.).

### Exemples de requêtes rapides

*Top 5 des thèmes les plus discutés à l'Assemblée Nationale :*
```sql
SELECT t.themeName, COUNT(pm.mentionId) as nb_mentions 
FROM themes t 
LEFT JOIN parliament_mentions pm ON t.themeId = pm.relatedThemeId 
GROUP BY t.themeName 
ORDER BY nb_mentions DESC 
LIMIT 5;
```

*Budget 2025 par Programme France 2030 :*
```sql
SELECT p.programmeName, SUM(b.amount2025) as budget_2025 
FROM programs p 
JOIN budget_lines b ON p.programmeCode = b.programmeCode 
GROUP BY p.programmeName 
ORDER BY budget_2025 DESC;
```

## 📄 Licence
Open Data / POC Hackathon.
