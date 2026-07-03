# TODO 05 - Mentions Parlementaires

**Script concerné** : 
- `scripts/07_fetch_parliament_mentions.py`

## 🎯 Objectif
Interroger l'Open Data de l'Assemblée nationale pour trouver toutes les fois où les députés parlent des mots-clés liés aux thématiques de France 2030, afin d'évaluer le "poids politique" des sujets.

## 📝 Checklist d'implémentation
- [x] **Investigation des sources** :
  - Aller sur `data.assemblee-nationale.fr`.
  - Chercher les jeux de données des comptes rendus des débats en séance publique ou en commission.
  - Alternative très puissante : Explorer l'API de `NosDéputés.fr` (Regards Citoyens) ou les dumps JSON de `LesTricoteuses` qui sont souvent bien mieux structurés.
- [x] **Test de requête** :
  - Tester une requête sur 1 mois d'historique avec le mot clé "France 2030" ou "hydrogène".
  - Vérifier les champs retournés : texte de l'intervention, ID du député, date, contexte.
- [x] **Mise à jour de `07_fetch_parliament_mentions.py`** :
  - Coder la boucle de téléchargement ou d'appel API.
  - Parser les JSON volumineux en streaming (ex: avec `ijson` si le fichier fait plusieurs Go) pour éviter les `MemoryError`.
  - Isoler les "phrases" exactes (Regex ou Tokenizer NLTK) pour renseigner les champs `contextBefore` et `contextAfter`.
  - Associer la mention au `themeId` du mot clé.

## ❓ Points d'interrogation potentiels (à creuser)
- **Volume de données** : Les dumps de l'Assemblée font plusieurs gigaoctets. Est-ce viable pour un script synchrone ? Faut-il plutôt utiliser SQLite pour l'ingestion brute avant export en JSON filtré ?
- **Identification des orateurs** : Les API de l'Assemblée donnent souvent un identifiant acteur (ex: `PA12345`). Il faudra faire une jointure avec le fichier des députés pour récupérer leur Nom et Groupe politique (Renaissance, LFI, RN, etc.).
- **Faux positifs** : Comment éviter qu'une intervention sur le "nucléaire iranien" ne remonte dans la thématique "Souveraineté et Nucléaire de France 2030" ?
