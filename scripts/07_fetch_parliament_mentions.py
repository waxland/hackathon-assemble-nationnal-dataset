import json
import os
import asyncio
import aiohttp
import ssl
import re
from bs4 import BeautifulSoup

def clean_html(raw_html):
    if not raw_html: return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def extract_contexts(text, keyword):
    """
    Extrait les phrases contenant le mot clé, et la phrase juste avant/après.
    """
    text = clean_html(text)
    # Simple phrase splitter
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    for i, s in enumerate(sentences):
        if keyword.lower() in s.lower():
            matched_sentence = s
            context_before = sentences[i-1] if i > 0 else ""
            context_after = sentences[i+1] if i < len(sentences)-1 else ""
            return matched_sentence, context_before, context_after
            
    return text, "", ""

def is_relevant_mention(text):
    text_lower = text.lower()
    # Lexique ciblé
    buzzwords = ['france 2030', 'pia', 'investissement', 'subvention', 'budget', 'milliard', 'innovation', 'stratégie nationale']
    # Filtre strict : un mot clé de contexte DOIT être présent (sauf pour les gros textes > 500 chars où on tolère par defaut pour le POC)
    if len(text_lower) > 500:
        return True
    return any(word in text_lower for word in buzzwords)

async def fetch_doc(session, url):
    try:
        async with session.get(url, timeout=5) as response:
            if response.status == 200:
                text = await response.text()
                return json.loads(text)
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
                text = await response.text()
                data = json.loads(text)
                
                results = data.get("results", [])
                
                # Fetch documents in parallel (limit 5 to avoid spam)
                tasks = []
                valid_results = [r for r in results[:5] if r.get("document_type") in ["Amendement", "QuestionEcrite"] and r.get("document_url")]
                
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
                        
                        texte_complet = am.get("expose", "") + " " + am.get("texte", "")
                        texte_clean = clean_html(texte_complet)
                        
                        if not is_relevant_mention(texte_clean): continue
                        
                        matched_sent, ctx_bef, ctx_aft = extract_contexts(texte_clean, search_query)
                        
                        mentions.append({
                            "mentionId": f"an-amendement-{m_id}",
                            "date": am.get("date", ""),
                            "chamber": "Assemblée nationale",
                            "speakerName": am.get("signataires", ""),
                            "politicalGroup": am.get("auteur_groupe_acronyme", "Inconnu"),
                            "matchedKeyword": search_query,
                            "matchMethod": "keyword_with_context",
                            "relatedThemeId": kw["relatedThemeId"],
                            "relatedProgrammeCode": kw["relatedProgrammes"][0] if kw["relatedProgrammes"] else "",
                            "interventionText": matched_sent,
                            "contextBefore": ctx_bef,
                            "contextAfter": ctx_aft,
                            "sourceUrl": am.get("url_nosdeputes", ""),
                            "confidenceScore": 0.85,
                            "validationStatus": "to_validate"
                        })
                        mentions_ids.add(m_id)
                        
                    elif "question_ecrite" in doc_data:
                        qe = doc_data["question_ecrite"]
                        m_id = str(qe.get("id"))
                        if m_id in mentions_ids: continue
                        
                        texte_clean = clean_html(qe.get("question", ""))
                        if not is_relevant_mention(texte_clean): continue
                        
                        matched_sent, ctx_bef, ctx_aft = extract_contexts(texte_clean, search_query)
                        
                        mentions.append({
                            "mentionId": f"an-qe-{m_id}",
                            "date": qe.get("date", ""),
                            "chamber": "Assemblée nationale",
                            "speakerName": qe.get("auteur", ""),
                            "politicalGroup": qe.get("auteur_groupe", "Inconnu"),
                            "matchedKeyword": search_query,
                            "matchMethod": "keyword_with_context",
                            "relatedThemeId": kw["relatedThemeId"],
                            "relatedProgrammeCode": kw["relatedProgrammes"][0] if kw["relatedProgrammes"] else "",
                            "interventionText": matched_sent,
                            "contextBefore": ctx_bef,
                            "contextAfter": ctx_aft,
                            "sourceUrl": qe.get("url_nosdeputes", ""),
                            "confidenceScore": 0.85,
                            "validationStatus": "to_validate"
                        })
                        mentions_ids.add(m_id)
    except Exception as e:
        print(f"⚠️ Erreur sur {search_query}: {e}")

async def main_async():
    print("Récupération ASYNCHRONE et stricte des mentions parlementaires...")
    
    keywords_path = "data/keywords.json"
    if not os.path.exists(keywords_path):
        return
        
    with open(keywords_path, "r", encoding="utf-8") as f:
        keywords = json.load(f)

    mentions = []
    mentions_ids = set()
    
    # Selection plus large de keywords pour enrichir divers programmes
    keywords_to_test = [k for k in keywords if len(k["label"]) > 5][:20]
            
    print(f"📡 Interrogation de l'API pour {len(keywords_to_test)} mots-clés...")
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        tasks = [search_keyword(session, kw, mentions, mentions_ids) for kw in keywords_to_test]
        await asyncio.gather(*tasks)
            
    output_path = "data/parliament_mentions.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mentions, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(mentions)} mentions parlementaires extraites proprement dans {output_path}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
