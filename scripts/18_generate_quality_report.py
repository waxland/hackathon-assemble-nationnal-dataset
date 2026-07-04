import json
import os
from collections import Counter

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def main():
    print("Analyse de la qualité des données...")
    report = {
        "volumes": {},
        "duplicate_ids": {},
        "missing_critical_fields": {},
        "front_files_with_mocks": [],
        "low_confidence_relations": 0
    }

    # Fichiers de données
    data_files = {
        "budget_lines": ("data/budget_lines.json", "id"),
        "programs": ("data/programs.json", "programmeCode"),
        "themes": ("data/themes.json", "themeId"),
        "keywords": ("data/keywords.json", "keywordId"),
        "calls_for_projects": ("data/calls_for_projects.json", "callId"),
        "parliament_mentions": ("data/parliament_mentions.json", "mentionId"),
        "naf_codes": ("data/naf_codes.json", "nafCode"),
        "companies": ("data/companies.json", "companyId"),
        "correlations": ("data/correlations.json", "correlationId")
    }

    # Check volumes and duplicates
    for name, (path, id_field) in data_files.items():
        data = load_json(path)
        report["volumes"][name] = len(data)
        ids = [item.get(id_field) for item in data if item.get(id_field)]
        counts = Counter(ids)
        dupes = {k: v for k, v in counts.items() if v > 1}
        if dupes:
            report["duplicate_ids"][name] = dupes

    # Check missing fields
    missing_fields_counts = {
        "sourceUrl": 0,
        "confidenceScore": 0,
        "validationStatus": 0,
        "amount2026": 0,
        "contextAfter": 0
    }

    budget_lines = load_json("data/budget_lines.json")
    for bl in budget_lines:
        if bl.get("amount2026") is None:
            missing_fields_counts["amount2026"] += 1

    correlations = load_json("data/correlations.json")
    for c in correlations:
        if c.get("confidenceScore") is None:
            missing_fields_counts["confidenceScore"] += 1
        if c.get("validationStatus") is None:
            missing_fields_counts["validationStatus"] += 1
        if c.get("confidenceScore", 1.0) < 0.7:
            report["low_confidence_relations"] += 1

    mentions = load_json("data/parliament_mentions.json")
    for m in mentions:
        if not m.get("sourceUrl"):
            missing_fields_counts["sourceUrl"] += 1
        if not m.get("contextAfter"):
            missing_fields_counts["contextAfter"] += 1

    report["missing_critical_fields"] = missing_fields_counts

    # Check mock in front files
    front_dir = "dataset"
    for root, dirs, files in os.walk(front_dir):
        for f in files:
            if f.endswith(".json"):
                path = os.path.join(root, f)
                data = load_json(path)
                has_mock = False
                if isinstance(data, dict) and "programmes" in data:
                    has_mock = any(p.get("isMock") for p in data["programmes"])
                elif isinstance(data, list):
                    has_mock = any(p.get("isMock") for p in data)
                if has_mock:
                    report["front_files_with_mocks"].append(f)

    os.makedirs("data", exist_ok=True)
    with open("data/quality_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("✅ Rapport qualité généré dans data/quality_report.json")

if __name__ == "__main__":
    main()
