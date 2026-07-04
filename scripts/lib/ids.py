import hashlib

def generate_id(prefix, *args):
    """
    Génère un identifiant déterministe basé sur un préfixe et une liste d'arguments.
    Exemple: generate_id("project", "Ademe", "12345") -> "project-a1b2c3d4"
    """
    raw_string = "|".join(str(arg).strip().lower() for arg in args if arg is not None)
    md5_hash = hashlib.md5(raw_string.encode('utf-8')).hexdigest()
    # On garde les 8 premiers caractères du hash pour des IDs courts mais uniques
    short_hash = md5_hash[:8]
    return f"{prefix}-{short_hash}"
