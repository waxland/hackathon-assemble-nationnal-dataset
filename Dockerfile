# Utiliser une image Python officielle légère
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances
COPY requirements.txt .

# Installer les dépendances (sans utiliser de cache pour alléger l'image)
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'ensemble des fichiers du projet dans le conteneur
COPY . .

# Exposer le port par défaut de Streamlit
EXPOSE 8501

# Définir la commande par défaut pour lancer le dashboard
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
