# Étape 1 : build du frontend React/Vite
FROM node:20 AS build
WORKDIR /app

# Copier les fichiers de configuration
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier le reste du code source
COPY . .

# ✅ Injecter la variable au build (depuis docker-compose)
ARG VITE_API_BASE
ENV VITE_API_BASE=${VITE_API_BASE}

# Compiler le frontend avec la variable intégrée
RUN npm run build

# Étape 2 : Nginx pour servir le build
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
