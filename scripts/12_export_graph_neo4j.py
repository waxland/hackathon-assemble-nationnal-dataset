import os
import sqlite3
import csv

def export_for_neo4j(db_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    
    print("Export des noeuds (CSV)...")
    
    pd = conn.execute("SELECT programmeCode, programmeName FROM programs").fetchall()
    with open(os.path.join(output_dir, "nodes_programs.csv"), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id:ID(Program)", "name", ":LABEL"])
        for p in pd: writer.writerow([p[0], p[1], "Program"])
            
    td = conn.execute("SELECT themeId, themeName FROM themes").fetchall()
    with open(os.path.join(output_dir, "nodes_themes.csv"), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id:ID(Theme)", "name", ":LABEL"])
        for t in td: writer.writerow([t[0], t[1], "Theme"])

    md = conn.execute("SELECT mentionId, speakerName, politicalGroup FROM parliament_mentions").fetchall()
    with open(os.path.join(output_dir, "nodes_mentions.csv"), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id:ID(Mention)", "speaker", "group", ":LABEL"])
        for m in md: writer.writerow([m[0], m[1], m[2] if m[2] else "Inconnu", "ParliamentMention"])
            
    # Mise à jour avec les colonnes INSEE
    cd = conn.execute("SELECT companyId, denominationUniteLegale, activitePrincipaleUniteLegale FROM companies").fetchall()
    with open(os.path.join(output_dir, "nodes_companies.csv"), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id:ID(Company)", "name", "naf", ":LABEL"])
        for c in cd: writer.writerow([c[0], c[1], c[2], "Company"])

    aap = conn.execute("SELECT callId, title, operator FROM calls_for_projects").fetchall()
    with open(os.path.join(output_dir, "nodes_aaps.csv"), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id:ID(CallForProject)", "title", "operator", ":LABEL"])
        for a in aap: writer.writerow([a[0], a[1], a[2], "CallForProject"])

    print("Export des relations (CSV)...")
    
    edges = conn.execute("SELECT sourceEntityId, targetEntityId, correlationType, confidenceScore FROM correlations").fetchall()
    with open(os.path.join(output_dir, "relationships.csv"), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([":START_ID", ":END_ID", ":TYPE", "weight:float"])
        for e in edges:
            # Assurer que le poids a une valeur numerique par defaut si null
            weight = e[3] if e[3] is not None else 1.0
            writer.writerow([e[0], e[1], e[2].upper(), weight])

    conn.close()
    print(f"✅ Fichiers Neo4j exportés dans le dossier {output_dir} avec poids et csv propre")

def main():
    db_path = "data/france2030.sqlite"
    output_dir = "data/neo4j_export"
    if not os.path.exists(db_path):
        print("❌ Base SQLite introuvable. Lancez le script 11 d'abord.")
        return
    export_for_neo4j(db_path, output_dir)

if __name__ == "__main__":
    main()
