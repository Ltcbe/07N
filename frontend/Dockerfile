# Étape 1 : builder le frontend
FROM node:20 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install               # ← remplace "npm ci" par "npm install"
COPY . .
RUN npm run build

# Étape 2 : serveur statique (optionnel)
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
