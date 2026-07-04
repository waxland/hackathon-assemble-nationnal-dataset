import json
import os
import tempfile

def read_json(filepath, default=None):
    """Lit un fichier JSON et retourne son contenu. Retourne `default` si le fichier n'existe pas."""
    if not os.path.exists(filepath):
        return default if default is not None else []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Erreur de lecture du JSON {filepath}: {e}")
        return default if default is not None else []

def write_json_atomic(filepath, data):
    """Écrit des données dans un fichier JSON de manière atomique pour éviter les corruptions."""
    dir_name = os.path.dirname(filepath)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
        
    fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix="tmp_", suffix=".json")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Remplacement atomique (fonctionne bien sur la plupart des OS POSIX)
        os.replace(temp_path, filepath)
    except Exception as e:
        os.remove(temp_path)
        raise e
