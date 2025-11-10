# SNCB Project — Full Stack (iRail + Persistence)

## Démarrage (Docker Compose)
```bash
docker compose up -d --build
# Frontend: http://localhost:8080
# Backend:  http://localhost:1788/health
```

## Migration Alembic (si nécessaire)
```bash
docker compose exec backend alembic upgrade head
```

## Description
- Frontend (React/Vite) servi par Nginx, proxy `/api` vers le backend
- Backend (FastAPI) : `/trains?station=...&date=YYYY-MM-DD`
- MariaDB persiste les trajets téléchargés depuis iRail
