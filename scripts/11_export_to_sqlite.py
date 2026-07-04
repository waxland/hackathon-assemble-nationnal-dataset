import json
import os
import sqlite3
import argparse
from datetime import datetime, timezone
import uuid

def init_db(db_path):
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
        siren TEXT,
        denominationUniteLegale TEXT,
        nomUniteLegale TEXT,
        prenom1UniteLegale TEXT,
        categorieJuridiqueUniteLegale TEXT,
        activitePrincipaleUniteLegale TEXT,
        nomenclatureActivitePrincipaleUniteLegale TEXT,
        etatAdministratifUniteLegale TEXT,
        dateCreationUniteLegale TEXT,
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
    CREATE TABLE IF NOT EXISTS green_budget_lines (
        id TEXT PRIMARY KEY,
        programmeCode TEXT,
        actionCode TEXT,
        actionName TEXT,
        globalRating TEXT,
        amount2026 REAL,
        sourceUrl TEXT,
        confidenceScore REAL,
        FOREIGN KEY (programmeCode) REFERENCES programs (programmeCode)
    );
    CREATE TABLE IF NOT EXISTS projects (
        projectId TEXT PRIMARY KEY,
        projectName TEXT,
        description TEXT,
        operator TEXT,
        grantAmount REAL,
        sourceUrl TEXT,
        confidenceScore REAL
    );
    CREATE TABLE IF NOT EXISTS project_beneficiaries (
        beneficiaryId TEXT PRIMARY KEY,
        name TEXT,
        type TEXT,
        confidenceScore REAL
    );
    CREATE TABLE IF NOT EXISTS territories (
        territoryId TEXT PRIMARY KEY,
        communeCode TEXT,
        communeName TEXT,
        departement TEXT,
        region TEXT,
        confidenceScore REAL
    );
    CREATE TABLE IF NOT EXISTS patent_depositors (
        patentFamilyId TEXT PRIMARY KEY,
        siren TEXT,
        companyName TEXT,
        nbDemandes INTEGER,
        nbFamilles INTEGER,
        sourceUrl TEXT,
        confidenceScore REAL
    );
    CREATE TABLE IF NOT EXISTS ingestion_runs (
        runId TEXT PRIMARY KEY,
        startedAt TEXT,
        completedAt TEXT,
        status TEXT,
        sourceFiles TEXT
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

def log_ingestion_run(conn, run_id, started_at, completed_at, status, source_files):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ingestion_runs (runId, startedAt, completedAt, status, sourceFiles)
        VALUES (?, ?, ?, ?, ?)
    """, (run_id, started_at, completed_at, status, json.dumps(source_files)))
    conn.commit()

def main():
    parser = argparse.ArgumentParser(description="Export JSON data to SQLite")
    parser.add_argument("--reset", action="store_true", help="Recreate the database from scratch")
    args = parser.parse_args()

    print("🚀 Upsert des JSON vers la base de données SQLite...")
    db_path = "data/france2030.sqlite"
    
    if args.reset and os.path.exists(db_path):
        print("Suppression de la base existante (--reset)...")
        os.remove(db_path)
        
    run_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc).isoformat()
    source_files_loaded = []
    
    try:
        conn = init_db(db_path)
        
        files_and_tables = [
            ("data/programs.json", "programs", ["programmeCode", "programmeName", "missionName"]),
            ("data/budget_lines.json", "budget_lines", ["id", "programmeCode", "expenseCategoryCode", "expenseCategoryName", "amount2024", "amount2025", "amount2026", "sourceUrl", "sourceDocument", "qualityStatus"]),
            ("data/themes.json", "themes", ["themeId", "themeName", "confidenceScore"]),
            ("data/keywords.json", "keywords", ["keywordId", "label", "type", "relatedThemeId", "confidenceScore"]),
            ("data/calls_for_projects.json", "calls_for_projects", ["callId", "title", "description", "operator", "openingDate", "closingDate", "sourceUrl", "themeId"]),
            ("data/parliament_mentions.json", "parliament_mentions", ["mentionId", "date", "chamber", "speakerName", "politicalGroup", "matchedKeyword", "relatedThemeId", "relatedProgrammeCode", "interventionText", "contextBefore", "contextAfter", "sourceUrl", "confidenceScore"]),
            ("data/naf_codes.json", "naf_codes", ["nafCode", "nafLabel", "confidenceScore"]),
            ("data/companies.json", "companies", ["companyId", "siren", "denominationUniteLegale", "nomUniteLegale", "prenom1UniteLegale", "categorieJuridiqueUniteLegale", "activitePrincipaleUniteLegale", "nomenclatureActivitePrincipaleUniteLegale", "etatAdministratifUniteLegale", "dateCreationUniteLegale", "source", "confidenceScore"]),
            ("data/correlations.json", "correlations", ["correlationId", "sourceEntityType", "sourceEntityId", "targetEntityType", "targetEntityId", "correlationType", "confidenceScore", "evidenceSource", "validationStatus"]),
            ("data/green_budget_lines.json", "green_budget_lines", ["id", "programmeCode", "actionCode", "actionName", "globalRating", "amount2026", "sourceUrl", "confidenceScore"]),
            ("data/projects.json", "projects", ["projectId", "projectName", "description", "operator", "grantAmount", "sourceUrl", "confidenceScore"]),
            ("data/project_beneficiaries.json", "project_beneficiaries", ["beneficiaryId", "name", "type", "confidenceScore"]),
            ("data/territories.json", "territories", ["territoryId", "communeCode", "communeName", "departement", "region", "confidenceScore"]),
            ("data/patent_depositors.json", "patent_depositors", ["patentFamilyId", "siren", "companyName", "nbDemandes", "nbFamilles", "sourceUrl", "confidenceScore"])
        ]
        
        for filepath, table, keys in files_and_tables:
            data = load_json(filepath)
            if data:
                insert_data(conn, table, data, keys)
                source_files_loaded.append(filepath)
            else:
                print(f"⚠️ Fichier {filepath} ignoré car vide ou inexistant.")
                
        completed_at = datetime.now(timezone.utc).isoformat()
        log_ingestion_run(conn, run_id, started_at, completed_at, "success", source_files_loaded)
        
        conn.close()
        print(f"✅ Upsert SQLite terminé : {db_path} (Run ID: {run_id})")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'upsert : {e}")
        completed_at = datetime.now(timezone.utc).isoformat()
        if 'conn' in locals():
            log_ingestion_run(conn, run_id, started_at, completed_at, f"error: {str(e)}", source_files_loaded)
            conn.close()
        raise

if __name__ == "__main__":
    main()

    # Update des tables pour ajouter le siret/siren potentiel aux beneficiaires
    # Si besoin de forcer, on ne supprime pas la base mais on ajoute si manquantes dans le futur
    # Pour le moment, project_beneficiaries reste comme défini
