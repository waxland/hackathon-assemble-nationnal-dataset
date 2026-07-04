import pandas as pd
import json
import os
import requests

URL_INPI = "https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/deposants-des-brevets/exports/csv?use_labels=true"
DATA_DIR = "data"
RAW_FILE = os.path.join(DATA_DIR, "raw", "raw_inpi.csv")

def download_data():
    os.makedirs(os.path.dirname(RAW_FILE), exist_ok=True)
    if not os.path.exists(RAW_FILE):
        print("Téléchargement du dataset INPI Déposants des brevets...")
        with requests.get(URL_INPI, stream=True) as r:
            r.raise_for_status()
            with open(RAW_FILE, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
    else:
        print("Dataset INPI déjà présent en cache.")
    
    return RAW_FILE

def main():
    print("Ingestion des brevets INPI...")
    
    try:
        raw_csv = download_data()
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement : {e}")
        return
        
    # Charger les entreprises cibles (Sirene + ADEME + Lauréats)
    companies = []
    comp_path = os.path.join(DATA_DIR, "companies.json")
    if os.path.exists(comp_path):
        with open(comp_path, "r", encoding="utf-8") as f:
            companies = json.load(f)
            
    # Extraire l'ensemble des SIREN cibles pour filtrage
    target_sirens = set(c.get("siren") for c in companies if c.get("siren"))
    
    if not target_sirens:
        print("❌ Aucun SIREN cible trouvé dans companies.json.")
        return
        
    print(f"Filtrage du CSV INPI sur {len(target_sirens)} SIREN cibles...")
    
    # On lit le CSV par chunk (pour éviter de saturer la RAM avec un fichier massif)
    chunksize = 100000
    df_filtered = pd.DataFrame()
    
    for chunk in pd.read_csv(raw_csv, sep=';', dtype=str, chunksize=chunksize):
        # Garder uniquement les lignes dont le SIREN est dans notre set
        matched = chunk[chunk['siren'].isin(target_sirens)]
        df_filtered = pd.concat([df_filtered, matched], ignore_index=True)
        
    if df_filtered.empty:
        print("⚠️ Aucun brevet trouvé pour les entreprises cibles.")
        return
        
    print(f"✅ {len(df_filtered)} brevets/dépôts trouvés.")
    
    # Agrégation par SIREN
    grouped = df_filtered.groupby('siren')
    
    patent_depositors = []
    correlations = []
    
    for siren, group in grouped:
        # Trouver la company associée
        company = next((c for c in companies if c.get("siren") == siren), None)
        if not company: continue
            
        company_id = company.get("companyId")
        
        # Familles de brevets uniques
        unique_families = group['nr_famille_docdb'].dropna().unique().tolist()
        # Nombre de demandes totales
        nb_demandes = group['key_appln_nr'].nunique()
        
        patent_id = f"patent-family-{siren}"
        
        patent_depositors.append({
            "patentFamilyId": patent_id,
            "siren": siren,
            "companyName": company.get("companyName") or company.get("nomUniteLegale") or company.get("denominationUniteLegale"),
            "nbDemandes": nb_demandes,
            "nbFamilles": len(unique_families),
            "famillesDocDb": unique_families[:5], # On garde 5 exemples max
            "sourceUrl": "https://www.data.gouv.fr/datasets/deposants-des-brevets-1",
            "confidenceScore": 1.0
        })
        
        # Correlation: Company -> PatentFamily
        import hashlib
        cid = "corr-" + hashlib.md5(f"{company_id}_{patent_id}_company_patent".encode('utf-8')).hexdigest()[:8]
        correlations.append({
            "correlationId": cid,
            "sourceEntityType": "company",
            "sourceEntityId": company_id,
            "targetEntityType": "patentFamily",
            "targetEntityId": patent_id,
            "correlationType": "company_patent",
            "confidenceScore": 1.0,
            "evidenceSource": "raw_inpi.csv",
            "validationStatus": "validated"
        })
        
    out_file = os.path.join(DATA_DIR, "patent_depositors.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(patent_depositors, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(patent_depositors)} déposants agrégés exportés dans {out_file}")
    
    # Update correlations.json
    corr_file = os.path.join(DATA_DIR, "correlations.json")
    existing_corrs = []
    if os.path.exists(corr_file):
        with open(corr_file, "r", encoding="utf-8") as f:
            existing_corrs = json.load(f)
            
    all_corrs = existing_corrs + correlations
    unique_corrs = {c["correlationId"]: c for c in all_corrs}.values()
    
    with open(corr_file, "w", encoding="utf-8") as f:
        json.dump(list(unique_corrs), f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
