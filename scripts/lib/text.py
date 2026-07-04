import re
import unicodedata

def clean_html(raw_html):
    """Supprime les balises HTML d'une chaîne de caractères."""
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', str(raw_html))
    return cleantext

def normalize_text(text):
    """
    Nettoie et normalise le texte :
    - Supprime les espaces invisibles/insécables (ex: \xa0)
    - Normalise les espaces multiples
    - Supprime les espaces en début/fin
    """
    if not text:
        return ""
    # Normalisation Unicode pour remplacer les espaces insécables etc.
    text = unicodedata.normalize("NFKD", str(text))
    # Remplacement des espaces multiples, sauts de ligne multiples par un seul espace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_and_normalize(text):
    """Combine le nettoyage HTML et la normalisation de texte."""
    return normalize_text(clean_html(text))
