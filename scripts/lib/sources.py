from .json_io import read_json, write_json_atomic

SOURCES_FILE = "data/sources.json"

def register_source(source_id, name, producer, url, license_name="Licence Ouverte / Open Licence version 2.0"):
    """
    Enregistre ou met à jour une source de données dans le registre central (data/sources.json).
    """
    sources = read_json(SOURCES_FILE, default=[])
    
    # Check if source already exists
    existing_index = next((i for i, s in enumerate(sources) if s.get("id") == source_id), None)
    
    new_source = {
        "id": source_id,
        "name": name,
        "producer": producer,
        "url": url,
        "license": license_name
    }
    
    if existing_index is not None:
        sources[existing_index] = new_source
    else:
        sources.append(new_source)
        
    write_json_atomic(SOURCES_FILE, sources)
    return new_source
