import json
import os
import asyncio
import aiohttp

def clean_text(text):
    if not text:
        return ""
    return " ".join(text.replace('\n', ' ').replace('\r', ' ').split())

def is_relevant_mention(text):
    """
    Filtre NLP basique pour réduire les faux positifs.
    On vérifie que le verbatim s'inscrit dans un contexte pertinent
    ('France 2030', 'milliard', 'subvention', 'souveraineté', 'innovation').
    """
    text_lower = text.lower()
    buzzwords = ['france 2030', 'milliard', 'subvention', 'souveraineté', 'innovation', 'investissement', 'budget']
    return any(word in text_lower for word in buzzwords)

async def fetch_doc(session, url):
    try:
        async with session.get(url, timeout=5) as response:
            if response.status == 200:
                return await response.json()
    except Exception:
        pass
    return None

async def search_keyword(session, kw, mentions, mentions_ids):
    search_query = kw["label"]
    url = f"https://www.nosdeputes.fr/recherche/{search_query}?format=json"
    
    print(f" -> Recherche asynchrone de '{search_query}'...")
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                data = await response.json()
                results = data.get("results", [])
                
                # Fetch documents in parallel
                tasks = []
                valid_results = [r for r in results[:10] if r.get("document_type") in ["Amendement", "QuestionEcrite"] and r.get("document_url")]
                
                for res in valid_results:
                    doc_url = res["document_url"].replace("nosdeputes.fr//api", "nosdeputes.fr/api")
                    tasks.append(fetch_doc(session, doc_url))
                
                docs = await asyncio.gather(*tasks)
                
                for doc_data in docs:
                    if not doc_data: continue
                    
                    if "amendement" in doc_data:
                        am = doc_data["amendement"]
                        m_id = str(am.get("id"))
                        if m_id in mentions_ids: continue
                        
                        texte = clean_text(am.get("expose", "") + " " + am.get("texte", ""))
                        if not is_relevant_mention(texte): continue
                        
                        mentions.append({
                            "mentionId": f"an-amendement-{m_id}",
                            "date": am.get("date", ""),
                            "chamber": "Assemblée nationale",
                            "speakerName": am.get("signataires", ""),
                            "politicalGroup": am.get("auteur_groupe_acronyme", "Inconnu"),
                            "matchedKeyword": search_query,
                            "relatedThemeId": kw["relatedThemeId"],
                            "relatedProgrammeCode": kw["relatedProgrammes"][0] if kw["relatedProgrammes"] else "",
                            "interventionText": texte[:800] + "..." if len(texte) > 800 else texte,
                            "contextBefore": am.get("sujet", ""),
                            "contextAfter": "",
                            "sourceUrl": am.get("url_nosdeputes", ""),
                            "confidenceScore": 0.85
                        })
                        mentions_ids.add(m_id)
                        
                    elif "question_ecrite" in doc_data:
                        qe = doc_data["question_ecrite"]
                        m_id = str(qe.get("id"))
                        if m_id in mentions_ids: continue
                        
                        texte = clean_text(qe.get("question", ""))
                        if not is_relevant_mention(texte): continue
                        
                        mentions.append({
                            "mentionId": f"an-qe-{m_id}",
                            "date": qe.get("date", ""),
                            "chamber": "Assemblée nationale",
                            "speakerName": qe.get("auteur", ""),
                            "politicalGroup": qe.get("auteur_groupe", "Inconnu"),
                            "matchedKeyword": search_query,
                            "relatedThemeId": kw["relatedThemeId"],
                            "relatedProgrammeCode": kw["relatedProgrammes"][0] if kw["relatedProgrammes"] else "",
                            "interventionText": texte[:800] + "..." if len(texte) > 800 else texte,
                            "contextBefore": "Question Ecrite",
                            "contextAfter": "",
                            "sourceUrl": qe.get("url_nosdeputes", ""),
                            "confidenceScore": 0.85
                        })
                        mentions_ids.add(m_id)
    except Exception as e:
        print(f"⚠️ Erreur sur {search_query}: {e}")

async def main_async():
    print("Récupération ASYNCHRONE et filtrée des mentions parlementaires...")
    
    keywords_path = "data/keywords.json"
    if not os.path.exists(keywords_path):
        print("❌ keywords.json manquant.")
        return
        
    with open(keywords_path, "r", encoding="utf-8") as f:
        keywords = json.load(f)

    mentions = []
    mentions_ids = set()
    
    tested_themes = set()
    keywords_to_test = []
    
    # Prendre un peu plus de mots clés pour tester l'async
    for kw in keywords:
        tid = kw["relatedThemeId"]
        if len(keywords_to_test) >= 30:
            break
        if tid not in tested_themes:
            keywords_to_test.append(kw)
            tested_themes.add(tid)
            
    print(f"📡 Interrogation massive de l'API pour {len(keywords_to_test)} mots-clés stratégiques...")
    
    async with aiohttp.ClientSession() as session:
        tasks = [search_keyword(session, kw, mentions, mentions_ids) for kw in keywords_to_test]
        await asyncio.gather(*tasks)
            
    output_path = "data/parliament_mentions.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mentions, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(mentions)} véritables mentions parlementaires pertinentes extraites dans {output_path}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
