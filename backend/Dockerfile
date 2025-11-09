FROM python:3.11-slim

# Empêche les prompts interactifs (utile pour apt)
ENV DEBIAN_FRONTEND=noninteractive

# Met à jour et installe les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Définit le répertoire de travail
WORKDIR /app

# Copie les fichiers du projet
COPY requirements.txt .

# Installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code applicatif
COPY . .

# Expose le port pour Uvicorn (backend uniquement)
EXPOSE 1788

# Commande par défaut
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "1788"]
