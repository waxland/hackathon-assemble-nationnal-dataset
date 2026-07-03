import requests
import json

def search_data_gouv():
    """
    On interroge l'API data.gouv.fr pour trouver un jeu de données contenant 
    les données chiffrées du PLF (Projet de Loi de Finances).
    """
    query = "PLF données chiffrées"
    url = f"https://www.data.gouv.fr/api/1/datasets/?q={query}&page_size=5"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(f"Trouvé {data['total']} résultats sur data.gouv.fr")
        
        for dataset in data['data']:
            print(f"\n--- Titre : {dataset['title']} ---")
            print(f"ID : {dataset['id']}")
            print(f"URL : {dataset['page']}")
            for resource in dataset.get('resources', []):
                print(f"  -> Ressource : {resource['title']} ({resource['format']})")
                print(f"     Lien : {resource['url']}")
    else:
        print(f"Erreur API: {response.status_code}")

if __name__ == "__main__":
    search_data_gouv()
