import json
import os
import sqlite3

def init_db(db_path):
    """Initialise la base de données et crée les tables si elles n'existent pas."""
    if os.path.exists(db_path):
        os.remove(db_path) # On repart d'une base propre pour le POC
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tables principales
    cursor.executescript("""
    CREATE TABLE programs (
        programmeCode TEXT PRIMARY KEY,
        programmeName TEXT,
        missionName TEXT
    );
    
    CREATE TABLE budget_lines (
        id TEXT PRIMARY KEY,
        programmeCode TEXT,
        expenseCategoryCode TEXT,
        expenseCategoryName TEXT,
        amount2024 REAL,
        amount2025 REAL,
        amount2026 REAL,
        sourceUrl TEXT,
        sourceDocument TEXT,
        qualityStatus TEXT,
        FOREIGN KEY (programmeCode) REFERENCES programs (programmeCode)
    );
    
    CREATE TABLE themes (
        themeId TEXT PRIMARY KEY,
        themeName TEXT,
        confidenceScore REAL
    );
    
    CREATE TABLE keywords (
        keywordId TEXT PRIMARY KEY,
        label TEXT,
        type TEXT,
        relatedThemeId TEXT,
        confidenceScore REAL,
        FOREIGN KEY (relatedThemeId) REFERENCES themes (themeId)
    );
    
    CREATE TABLE calls_for_projects (
        callId TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        operator TEXT,
        openingDate TEXT,
        closingDate TEXT,
        sourceUrl TEXT,
        themeId TEXT,
        FOREIGN KEY (themeId) REFERENCES themes (themeId)
    );
    
    CREATE TABLE parliament_mentions (
        mentionId TEXT PRIMARY KEY,
        date TEXT,
        chamber TEXT,
        speakerName TEXT,
        politicalGroup TEXT,
        matchedKeyword TEXT,
        relatedThemeId TEXT,
        relatedProgrammeCode TEXT,
        interventionText TEXT,
        contextBefore TEXT,
        contextAfter TEXT,
        sourceUrl TEXT,
        confidenceScore REAL,
        FOREIGN KEY (relatedThemeId) REFERENCES themes (themeId)
    );
    
    CREATE TABLE companies (
        companyId TEXT PRIMARY KEY,
        companyName TEXT,
        siren TEXT,
        nafCode TEXT,
        source TEXT,
        confidenceScore REAL
    );
    
    CREATE TABLE naf_codes (
        nafCode TEXT PRIMARY KEY,
        nafLabel TEXT,
        confidenceScore REAL
    );
    
    CREATE TABLE correlations (
        correlationId TEXT PRIMARY KEY,
        sourceEntityType TEXT,
        sourceEntityId TEXT,
        targetEntityType TEXT,
        targetEntityId TEXT,
        correlationType TEXT,
        confidenceScore REAL,
        evidenceSource TEXT,
        validationStatus TEXT
    );
    """)
    
    conn.commit()
    return conn

def insert_data(conn, table_name, data_list, keys):
    """Insère une liste de dictionnaires dans la table spécifiée."""
    if not data_list:
        return
        
    cursor = conn.cursor()
    placeholders = ", ".join(["?"] * len(keys))
    columns = ", ".join(keys)
    query = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
    
    values_list = []
    for item in data_list:
        values = [item.get(k) for k in keys]
        values_list.append(values)
        
    cursor.executemany(query, values_list)
    conn.commit()

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    print(f"⚠️ Fichier manquant: {filepath}")
    return []

def main():
    print("🚀 Conversion des JSON vers la base de données SQLite...")
    
    db_path = "data/france2030.sqlite"
    conn = init_db(db_path)
    
    # 1. Programs
    programs = load_json("data/programs.json")
    insert_data(conn, "programs", programs, ["programmeCode", "programmeName", "missionName"])
    
    # 2. Budget Lines
    budget_lines = load_json("data/budget_lines.json")
    insert_data(conn, "budget_lines", budget_lines, [
        "id", "programmeCode", "expenseCategoryCode", "expenseCategoryName",
        "amount2024", "amount2025", "amount2026", "sourceUrl", "sourceDocument", "qualityStatus"
    ])
    
    # 3. Themes
    themes = load_json("data/themes.json")
    insert_data(conn, "themes", themes, ["themeId", "themeName", "confidenceScore"])
    
    # 4. Keywords
    keywords = load_json("data/keywords.json")
    insert_data(conn, "keywords", keywords, ["keywordId", "label", "type", "relatedThemeId", "confidenceScore"])
    
    # 5. Calls for Projects
    calls = load_json("data/calls_for_projects.json")
    insert_data(conn, "calls_for_projects", calls, [
        "callId", "title", "description", "operator", "openingDate", "closingDate", "sourceUrl", "themeId"
    ])
    
    # 6. Parliament Mentions
    mentions = load_json("data/parliament_mentions.json")
    insert_data(conn, "parliament_mentions", mentions, [
        "mentionId", "date", "chamber", "speakerName", "politicalGroup", "matchedKeyword",
        "relatedThemeId", "relatedProgrammeCode", "interventionText", "contextBefore", "contextAfter",
        "sourceUrl", "confidenceScore"
    ])
    
    # 7. NAF Codes
    naf_codes = load_json("data/naf_codes.json")
    insert_data(conn, "naf_codes", naf_codes, ["nafCode", "nafLabel", "confidenceScore"])
    
    # 8. Companies
    companies = load_json("data/companies.json")
    insert_data(conn, "companies", companies, [
        "companyId", "companyName", "siren", "nafCode", "source", "confidenceScore"
    ])
    
    # 9. Correlations
    correlations = load_json("data/correlations.json")
    insert_data(conn, "correlations", correlations, [
        "correlationId", "sourceEntityType", "sourceEntityId", "targetEntityType", 
        "targetEntityId", "correlationType", "confidenceScore", "evidenceSource", "validationStatus"
    ])
    
    conn.close()
    print(f"✅ Base de données SQLite générée avec succès : {db_path}")

if __name__ == "__main__":
    main()
