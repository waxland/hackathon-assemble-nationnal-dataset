## 🕵️ Méthodologie d'Acquisition et Origine des Données

La force de ce Proof of Concept (POC) repose sur la fiabilisation des données en s'appuyant exclusivement sur de l'**Open Data Gouvernemental**.

Voici les flux de données actuellement implémentés :

1. **Données Budgétaires** 💶 :
   - *Source* : data.economie.gouv.fr (Fichier "PLF 2025 - Dépenses du Budget Général").
   - *Traitement* : Filtrage par Pandas sur la mission "Investir pour la France de 2030" (Programmes 421 à 425) et agrégation par Titre.
2. **Mentions Parlementaires** 🏛️ :
   - *Source* : L'API open source de NosDéputés.fr (Regards Citoyens).
   - *Traitement* : Scraping asynchrone ciblé sur une taxonomie de mots-clés techniques (ex: SMR, Hydrogène) couplé à un filtre de proximité sémantique (NLP basique) pour valider que le discours concerne bien un financement.
3. **Entreprises & Codes NAF** 🏭 :
   - *Source* : L'API officielle Sirene (recherche-entreprises.api.gouv.fr).
   - *Traitement* : Résolution dynamique des SIREN et des codes d'activité pour une liste de startups emblématiques de la French Tech.
4. **Appels à Projets (AAP)** 📢 :
   - *Source* : Sites institutionnels (ADEME, Bpifrance).
   - *Statut actuel* : Données mockées car `info.gouv.fr` bloque les robots via un Anti-Bot Cloudflare (voir *Blocages*).

### 🚧 Points de blocages restants
- Le blocage Cloudflare empêche d'avoir la liste des 100% des AAP en temps réel (nécessite Playwright).
- Les faux positifs lors de la recherche dans les débats nécessitent idéalement le déploiement d'un LLM local pour classer la pertinence de la phrase prononcée par le député.
