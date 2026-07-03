#!/bin/bash
set -e

# Vérifier si la base de données existe
if [ ! -f "data/france2030.sqlite" ]; then
    echo "================================================================"
    echo "⚠️ Base SQLite introuvable. Exécution initiale de la pipeline..."
    echo "================================================================"
    make run-scraping
    make export-front
else
    echo "✅ Base de données existante détectée."
fi

# Lancer la commande principale (Streamlit)
exec "$@"
