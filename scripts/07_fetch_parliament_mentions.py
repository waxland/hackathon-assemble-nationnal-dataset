import json
import os
import requests
import time

def clean_text(text):
    if not text:
        return ""
    text = text.replace('\n', ' ').replace('\r', ' ')
    return " ".join(text.split())

def main():
    print("Récupération des mentions parlementaires via NosDéputés.fr...")
    
    keywords_path = "data/keywords.json"
    if not os.path.exists(keywords_path):
        print("❌ keywords.json manquant.")
        return
        
    with open(keywords_path, "r", encoding="utf-8") as f:
        keywords = json.load(f)

    mentions = []
    mentions_ids = set()
    
    # On va tester seulement les mots-clés les plus spécifiques pour ne pas surcharger l'API
    # On limite à max 2 mots-clés par thème pour ce POC
    tested_themes = set()
    keywords_to_test = []
    
    for kw in keywords:
        tid = kw["relatedThemeId"]
        # Limiter à quelques requêtes (Hackathon POC)
        if len(keywords_to_test) >= 15:
            break
        if tid not in tested_themes:
            keywords_to_test.append(kw)
            tested_themes.add(tid)
            
    print(f"📡 Interrogation de l'API pour {len(keywords_to_test)} mots-clés stratégiques...")
    
    for kw in keywords_to_test:
        search_query = kw["label"]
        print(f" -> Recherche de '{search_query}'...")
        url = f"https://www.nosdeputes.fr/recherche/{search_query}?format=json"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                # Prendre les 3 derniers résultats par mot-clé
                for res in results[:3]:
                    doc_type = res.get("document_type")
                    doc_url = res.get("document_url")
                    
                    if doc_type in ["Amendement", "QuestionEcrite"] and doc_url:
                        # Si l'URL a deux slashs comme renvoyé parfois par l'API
                        doc_url = doc_url.replace("nosdeputes.fr//api", "nosdeputes.fr/api")
                        
                        try:
                            doc_resp = requests.get(doc_url, timeout=5)
                            if doc_resp.status_code == 200:
                                doc_data = doc_resp.json()
                                
                                if "amendement" in doc_data:
                                    am = doc_data["amendement"]
                                    m_id = str(am.get("id"))
                                    if m_id in mentions_ids:
                                        continue
                                        
                                    texte = clean_text(am.get("expose", "") + " " + am.get("texte", ""))
                                    
                                    mentions.append({
                                        "mentionId": f"an-amendement-{m_id}",
                                        "date": am.get("date", ""),
                                        "chamber": "Assemblée nationale",
                                        "speakerName": am.get("signataires", ""),
                                        "politicalGroup": am.get("auteur_groupe_acronyme", "Inconnu"),
                                        "matchedKeyword": search_query,
                                        "relatedThemeId": kw["relatedThemeId"],
                                        "relatedProgrammeCode": kw["relatedProgrammes"][0] if kw["relatedProgrammes"] else "",
                                        "interventionText": texte[:500] + "..." if len(texte) > 500 else texte,
                                        "contextBefore": am.get("sujet", ""),
                                        "contextAfter": "",
                                        "sourceUrl": am.get("url_nosdeputes", ""),
                                        "confidenceScore": 0.95
                                    })
                                    mentions_ids.add(m_id)
                                    
                                elif "question_ecrite" in doc_data:
                                    qe = doc_data["question_ecrite"]
                                    m_id = str(qe.get("id"))
                                    if m_id in mentions_ids:
                                        continue
                                        
                                    texte = clean_text(qe.get("question", ""))
                                    
                                    mentions.append({
                                        "mentionId": f"an-qe-{m_id}",
                                        "date": qe.get("date", ""),
                                        "chamber": "Assemblée nationale",
                                        "speakerName": qe.get("auteur", ""),
                                        "politicalGroup": qe.get("auteur_groupe", "Inconnu"),
                                        "matchedKeyword": search_query,
                                        "relatedThemeId": kw["relatedThemeId"],
                                        "relatedProgrammeCode": kw["relatedProgrammes"][0] if kw["relatedProgrammes"] else "",
                                        "interventionText": texte[:500] + "..." if len(texte) > 500 else texte,
                                        "contextBefore": "Question Ecrite",
                                        "contextAfter": "",
                                        "sourceUrl": qe.get("url_nosdeputes", ""),
                                        "confidenceScore": 0.95
                                    })
                                    mentions_ids.add(m_id)
                        except Exception as e:
                            print(f"    ⚠️ Erreur détail document: {e}")
                            
            time.sleep(1) # Respect du rate limit de NosDeputes
            
        except Exception as e:
            print(f"⚠️ Erreur recherche {search_query}: {e}")
            
    output_path = "data/parliament_mentions.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mentions, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(mentions)} véritables mentions parlementaires extraites dans {output_path}")

if __name__ == "__main__":
    main()
