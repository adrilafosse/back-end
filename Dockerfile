# Utiliser l'image Python officielle
FROM python:3.10-slim

# Mettre à jour pip
RUN pip install --upgrade pip

# Installer les dépendances flask et flask-cors
RUN pip install Flask flask-cors

# Copier le code Flask dans le conteneur
COPY . /app

# Définir le répertoire de travail
WORKDIR /app

# Exposer le port sur lequel l'application Flask écoute
EXPOSE 8080

CMD ["python", "back-end.py"]

