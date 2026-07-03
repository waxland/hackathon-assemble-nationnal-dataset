FROM python:3.11-slim

# Empêcher Python de bufferiser stdout/stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installer Make pour pouvoir utiliser le Makefile
RUN apt-get update && apt-get install -y make && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Définir l'entrypoint pour vérifier la BDD
ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
