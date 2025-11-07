# SNCB Timing Dashboard

Application web temps réel pour la ponctualité ferroviaire belge construite autour de l'API [iRail](https://docs.irail.be/). L'architecture est composée de trois services exécutés dans Docker :

- **backend** : API FastAPI exposée sur le port `1788` qui ingère l'API iRail, stocke les trajets et fournit les données agrégées au front-end.
- **db** : base PostgreSQL persistant les trajets et leurs arrêts (sans le champ `connections`).
- **frontend** : application React qui reprend la charte graphique du tableau de bord fourni.

## Fonctionnalités clés

- Récupération périodique des données véhicules iRail pour un ensemble de gares configurables.
- Stockage de toutes les informations retournées (hors `connections`) avec gel des trajets 5 minutes après le dernier arrêt.
- Endpoints d'API REST pour déclencher une synchronisation manuelle, lister les gares connues et alimenter le tableau de bord.
- Tableau de bord interactif (filtres, cartes synthétiques, histogramme horaire, table détaillée) se rapprochant du rendu fourni.

## Démarrage rapide

### Prérequis

- Docker et Docker Compose installés localement.

### Lancement

```bash
docker compose up --build
```

Les services sont ensuite accessibles via :

- Front-end : http://localhost:5173
- Back-end : http://localhost:1788
- Base de données PostgreSQL : localhost:5432 (user/pass `irail`)

> ℹ️ Le backend déclenche automatiquement une collecte toutes les 3 minutes. Vous pouvez forcer une synchronisation ponctuelle via `POST http://localhost:1788/api/fetch`.

### Variables d'environnement

Les valeurs par défaut (voir `backend/.env`) peuvent être adaptées selon vos besoins :

| Variable | Description |
| --- | --- |
| `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Paramètres de connexion à PostgreSQL. |
| `FETCH_INTERVAL_SECONDS` | Fréquence de synchronisation en secondes (minimum 60). |
| `STATIONS` | Liste de gares surveillées séparées par des virgules. |
| `LOG_LEVEL` | Niveau de log du backend. |
| `VITE_API_URL` (front) | URL d'accès à l'API (défaut : `http://backend:1788`). |

## Structure du projet

```
.
├── backend
│   ├── app
│   │   ├── config.py         # Chargement des paramètres d'environnement
│   │   ├── crud.py           # Accès base & agrégations tableau de bord
│   │   ├── database.py       # Connexion SQLAlchemy et session
│   │   ├── irail.py          # Client API iRail + parsing
│   │   ├── main.py           # Application FastAPI et routes
│   │   ├── models.py         # Modèles SQLAlchemy
│   │   ├── prestart.py       # Création des tables au démarrage
│   │   └── services.py       # Logique d'ingestion et planificateur
│   ├── Dockerfile
│   ├── requirements.txt
│   └── start.sh
├── frontend
│   ├── src
│   │   ├── App.jsx           # Page principale du tableau de bord
│   │   ├── components        # Cartes et tableau
│   │   └── styles            # Feuilles de style
│   ├── Dockerfile
│   ├── package.json
│   └── .env
├── docker-compose.yml
└── README.md
```

## Notes complémentaires

- L'environnement de démonstration peut restreindre l'accès réseau direct à l'API iRail. Dans ce cas les requêtes planifiées échoueront, mais le code est prêt pour un environnement connecté.
- Le front-end utilise Chart.js pour l'histogramme et React-Select pour les filtres, conformément au design fourni.
