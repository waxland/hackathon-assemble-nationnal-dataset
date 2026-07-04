import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import json
import hashlib

def get_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    """Crée une session requests avec une stratégie de retry configurée."""
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    # Configuration par défaut
    session.headers.update({
        'User-Agent': 'France2030-Data-Bot/1.0 (Contact: data@france2030.gouv.fr)'
    })
    return session

def fetch_with_cache(url, cache_dir=".cache", params=None, timeout=10, use_cache=True):
    """Effectue une requête GET avec un cache optionnel sur disque."""
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)
        
    url_hash = hashlib.md5((url + str(params)).encode('utf-8')).hexdigest()
    cache_path = os.path.join(cache_dir, f"{url_hash}.json")
    
    if use_cache and os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    session = get_session()
    response = session.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    
    try:
        data = response.json()
    except ValueError:
        data = {"content": response.text} # Fallback
        
    if use_cache:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            
    return data
