import json
import os
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional

# --- Schemas Pydantic ---

class ProgramSchema(BaseModel):
    programmeCode: str
    programmeName: str
    missionName: str
    budgetLines: list = []
    officialObjectives: list = []
    actions: list = []
    themes: list = []
    keywords: list = []
    callsForProjects: list = []
    parliamentMentions: list = []
    sourceDocuments: list = []

class BudgetLineSchema(BaseModel):
    id: str
    programmeCode: str
    expenseCategoryCode: str
    expenseCategoryName: str
    amount2024: Optional[float]
    amount2025: Optional[float]
    amount2026: Optional[float]
    sourceUrl: str
    sourceDocument: str
    sourcePage: str
    qualityStatus: str

class ThemeSchema(BaseModel):
    themeId: str
    themeName: str
    relatedProgrammes: List[str]
    confidenceScore: float

class KeywordSchema(BaseModel):
    keywordId: str
    label: str
    type: str
    relatedThemeId: str
    relatedProgrammes: List[str]
    confidenceScore: float

class CallForProjectSchema(BaseModel):
    callId: str
    title: str
    operator: str

class MentionSchema(BaseModel):
    mentionId: str
    date: str
    speakerName: str
    politicalGroup: Optional[str]
    matchedKeyword: str
    relatedThemeId: str
    interventionText: str
    confidenceScore: float

class CompanySchema(BaseModel):
    companyId: str
    siren: str
    activitePrincipaleUniteLegale: str
    source: str
    confidenceScore: float

class CorrelationSchema(BaseModel):
    correlationId: str
    sourceEntityType: str
    sourceEntityId: str
    targetEntityType: str
    targetEntityId: str
    correlationType: str
    confidenceScore: float
    validationStatus: str

# --- Validation Logic ---

def validate_file(filepath, schema_model):
    if not os.path.exists(filepath):
        print(f"⚠️ Ignoré (fichier absent): {filepath}")
        return True

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print(f"❌ Erreur: {filepath} doit être une liste.")
        return False

    errors = 0
    for i, item in enumerate(data):
        try:
            schema_model(**item)
        except ValidationError as e:
            print(f"❌ Erreur validation {filepath} à l'index {i}:")
            print(e)
            errors += 1
            if errors > 3:
                print("...trop d'erreurs, arrêt de l'affichage pour ce fichier.")
                break
    
    if errors == 0:
        print(f"✅ Schéma validé: {filepath} ({len(data)} items)")
        return True
    return False

def main():
    print("Validation des schémas JSON (contrats internes)...")
    
    files_to_validate = [
        ("data/programs.json", ProgramSchema),
        ("data/budget_lines.json", BudgetLineSchema),
        ("data/themes.json", ThemeSchema),
        ("data/keywords.json", KeywordSchema),
        ("data/companies.json", CompanySchema),
        ("data/parliament_mentions.json", MentionSchema),
        ("data/correlations.json", CorrelationSchema)
    ]
    
    all_valid = True
    for filepath, schema in files_to_validate:
        is_valid = validate_file(filepath, schema)
        all_valid = all_valid and is_valid
        
    if all_valid:
        print("🎉 Tous les contrats JSON internes sont valides.")
    else:
        print("💥 Des erreurs de validation ont été détectées.")

if __name__ == "__main__":
    main()
