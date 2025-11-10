# SNCB Timing Dashboard — Frontend prêt à l'emploi

## Lancer en développement
```bash
npm install
npm run dev
# http://localhost:5173
```

## Build de production (Docker + Nginx)
```bash
docker build -t sncb-frontend .
docker run -p 8080:80 sncb-frontend
# http://localhost:8080
```

## Configuration
- API IRAIL consommée directement depuis le navigateur
- Composants inclus : FilterBar, KPICards, HourlyChart, TrainsTable
- Graphiques via `recharts`
