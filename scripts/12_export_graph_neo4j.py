import json
import os
import sqlite3

def export_for_neo4j(db_path, output_dir):
    """
    Génère des fichiers CSV structurés pour un import facile dans Neo4j 
    (Nodes et Relationships).
    """
    os.makedirs(output_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    
    # 1. Export des Noeuds (Nodes)
    print("Export des noeuds (CSV)...")
    
    # Programmes
    pd = conn.execute("SELECT programmeCode, programmeName FROM programs").fetchall()
    with open(os.path.join(output_dir, "nodes_programs.csv"), "w") as f:
        f.write("id:ID(Program),name,:LABEL\n")
        for p in pd:
            f.write(f"{p[0]},\"{p[1]}\",Program\n")
            
    # Themes
    td = conn.execute("SELECT themeId, themeName FROM themes").fetchall()
    with open(os.path.join(output_dir, "nodes_themes.csv"), "w") as f:
        f.write("id:ID(Theme),name,:LABEL\n")
        for t in td:
            f.write(f"{t[0]},\"{t[1]}\",Theme\n")

    # Mentions (Assemblée)
    md = conn.execute("SELECT mentionId, speakerName, politicalGroup FROM parliament_mentions").fetchall()
    with open(os.path.join(output_dir, "nodes_mentions.csv"), "w") as f:
        f.write("id:ID(Mention),speaker,group,:LABEL\n")
        for m in md:
            f.write(f"{m[0]},\"{m[1]}\",\"{m[2]}\",ParliamentMention\n")
            
    # Entreprises
    cd = conn.execute("SELECT companyId, companyName, nafCode FROM companies").fetchall()
    with open(os.path.join(output_dir, "nodes_companies.csv"), "w") as f:
        f.write("id:ID(Company),name,naf,:LABEL\n")
        for c in cd:
            f.write(f"{c[0]},\"{c[1]}\",\"{c[2]}\",Company\n")

    # Appels à Projets
    aap = conn.execute("SELECT callId, title, operator FROM calls_for_projects").fetchall()
    with open(os.path.join(output_dir, "nodes_aaps.csv"), "w") as f:
        f.write("id:ID(CallForProject),title,operator,:LABEL\n")
        for a in aap:
            f.write(f"{a[0]},\"{a[1]}\",\"{a[2]}\",CallForProject\n")

    # 2. Export des Relations (Edges)
    print("Export des relations (CSV)...")
    
    # On lit la table correlations
    edges = conn.execute("SELECT sourceEntityId, targetEntityId, correlationType FROM correlations").fetchall()
    with open(os.path.join(output_dir, "relationships.csv"), "w") as f:
        f.write(":START_ID,:END_ID,:TYPE\n")
        for e in edges:
            f.write(f"{e[0]},{e[1]},{e[2].upper()}\n")

    conn.close()
    print(f"✅ Fichiers Neo4j exportés dans le dossier {output_dir}")

def main():
    db_path = "data/france2030.sqlite"
    output_dir = "data/neo4j_export"
    if not os.path.exists(db_path):
        print("❌ Base SQLite introuvable. Lancez le script 11 d'abord.")
        return
    export_for_neo4j(db_path, output_dir)

if __name__ == "__main__":
    main()
