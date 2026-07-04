import pytest
from scripts.lib.ids import generate_id
from scripts.lib.text import clean_and_normalize

def test_generate_id():
    id1 = generate_id("projet", "ADEME", "A123")
    id2 = generate_id("projet", "ADEME", "A123")
    id3 = generate_id("projet", "ademe", " a123 ")
    
    assert id1 == id2
    assert id1 == id3
    assert id1.startswith("projet-")

def test_clean_and_normalize():
    html_text = "<p>Un texte   avec \xa0 des espaces.</p>"
    clean_text = clean_and_normalize(html_text)
    assert clean_text == "Un texte avec des espaces."
