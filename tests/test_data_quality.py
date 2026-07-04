import json
import pytest

def test_no_duplicate_keywords():
    with open("data/keywords.json", "r") as f:
        keywords = json.load(f)
    
    seen = set()
    duplicates = set()
    for kw in keywords:
        label_lower = kw["label"].lower().strip()
        if label_lower in seen:
            duplicates.add(label_lower)
        seen.add(label_lower)
        
    assert len(duplicates) == 0, f"Doublons détectés: {duplicates}"
