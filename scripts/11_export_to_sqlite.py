import json
import os
import sqlite3

def init_db(db_path):
    """Initialise la base de données sans la supprimer si elle existe (Upsert)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS programs (
        programmeCode TEXT PRIMARY KEY,
        programmeName TEXT,
        missionName TEXT
    );
    CREATE TABLE IF NOT EXISTS budget_lines (
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
    CREATE TABLE IF NOT EXISTS themes (
        themeId TEXT PRIMARY KEY,
        themeName TEXT,
        confidenceScore REAL
    );
    CREATE TABLE IF NOT EXISTS keywords (
        keywordId TEXT PRIMARY KEY,
        label TEXT,
        type TEXT,
        relatedThemeId TEXT,
        confidenceScore REAL,
        FOREIGN KEY (relatedThemeId) REFERENCES themes (themeId)
    );
    CREATE TABLE IF NOT EXISTS calls_for_projects (
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
    CREATE TABLE IF NOT EXISTS parliament_mentions (
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
    CREATE TABLE IF NOT EXISTS companies (
        companyId TEXT PRIMARY KEY,
        companyName TEXT,
        siren TEXT,
        nafCode TEXT,
        source TEXT,
        confidenceScore REAL
    );
    CREATE TABLE IF NOT EXISTS naf_codes (
        nafCode TEXT PRIMARY KEY,
        nafLabel TEXT,
        confidenceScore REAL
    );
    CREATE TABLE IF NOT EXISTS correlations (
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
    if not data_list:
        return
    cursor = conn.cursor()
    placeholders = ", ".join(["?"] * len(keys))
    columns = ", ".join(keys)
    query = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
    
    values_list = [[item.get(k) for k in keys] for item in data_list]
    cursor.executemany(query, values_list)
    conn.commit()

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def main():
    print("🚀 Upsert des JSON vers la base de données SQLite...")
    db_path = "data/france2030.sqlite"
    conn = init_db(db_path)
    
    insert_data(conn, "programs", load_json("data/programs.json"), ["programmeCode", "programmeName", "missionName"])
    insert_data(conn, "budget_lines", load_json("data/budget_lines.json"), ["id", "programmeCode", "expenseCategoryCode", "expenseCategoryName", "amount2024", "amount2025", "amount2026", "sourceUrl", "sourceDocument", "qualityStatus"])
    insert_data(conn, "themes", load_json("data/themes.json"), ["themeId", "themeName", "confidenceScore"])
    insert_data(conn, "keywords", load_json("data/keywords.json"), ["keywordId", "label", "type", "relatedThemeId", "confidenceScore"])
    insert_data(conn, "calls_for_projects", load_json("data/calls_for_projects.json"), ["callId", "title", "description", "operator", "openingDate", "closingDate", "sourceUrl", "themeId"])
    insert_data(conn, "parliament_mentions", load_json("data/parliament_mentions.json"), ["mentionId", "date", "chamber", "speakerName", "politicalGroup", "matchedKeyword", "relatedThemeId", "relatedProgrammeCode", "interventionText", "contextBefore", "contextAfter", "sourceUrl", "confidenceScore"])
    insert_data(conn, "naf_codes", load_json("data/naf_codes.json"), ["nafCode", "nafLabel", "confidenceScore"])
    insert_data(conn, "companies", load_json("data/companies.json"), ["companyId", "companyName", "siren", "nafCode", "source", "confidenceScore"])
    insert_data(conn, "correlations", load_json("data/correlations.json"), ["correlationId", "sourceEntityType", "sourceEntityId", "targetEntityType", "targetEntityId", "correlationType", "confidenceScore", "evidenceSource", "validationStatus"])
    
    conn.close()
    print(f"✅ Upsert SQLite terminé : {db_path}")

if __name__ == "__main__":
    main()
