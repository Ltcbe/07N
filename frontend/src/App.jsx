import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import dayjs from 'dayjs';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js';
import Select from 'react-select';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import DashboardCard from './components/DashboardCard.jsx';
import JourneyTable from './components/JourneyTable.jsx';
import './styles/app.css';

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:1788';

const defaultFilters = {
  day: dayjs().format('YYYY-MM-DD'),
  departureStation: null,
  arrivalStation: null,
};

const customSelectStyles = {
  control: (base) => ({
    ...base,
    borderRadius: '12px',
    borderColor: 'rgba(37, 99, 235, 0.2)',
    boxShadow: 'none',
    minHeight: '48px',
    fontSize: '0.95rem',
  }),
};

function App() {
  const [filters, setFilters] = useState(defaultFilters);
  const [stations, setStations] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    axios
      .get(`${API_BASE_URL}/api/stations`)
      .then((response) => setStations(response.data.stations || []))
      .catch(() => setStations([]));
  }, []);

  useEffect(() => {
    const fetchDashboard = async () => {
      setIsLoading(true);
      try {
        const params = {};
        if (filters.day) params.day = filters.day;
        if (filters.departureStation) params.departure_station = filters.departureStation.value;
        if (filters.arrivalStation) params.arrival_station = filters.arrivalStation.value;

        const { data } = await axios.get(`${API_BASE_URL}/api/dashboard`, { params });
        setDashboard(data);
      } catch (error) {
        toast.error("Impossible de récupérer les données en temps réel.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboard();
  }, [filters]);

  const histogramData = useMemo(() => {
    if (!dashboard?.histogram) return null;
    const labels = dashboard.histogram.map((item) => `${item.hour}h`);
    const dataset = dashboard.histogram.map((item) => item.count);

    return {
      labels,
      datasets: [
        {
          label: 'Trajets',
          data: dataset,
          backgroundColor: 'rgba(37, 99, 235, 0.6)',
          borderRadius: 6,
        },
      ],
    };
  }, [dashboard]);

  const selectOptions = useMemo(
    () => stations.map((station) => ({ value: station, label: station })),
    [stations]
  );

  const summary = dashboard?.summary || { average_delay_minutes: 0, late_trains: 0, punctuality: 0 };

  return (
    <div className="page">
      <ToastContainer position="bottom-right" />
      <header className="page__header">
        <div>
          <h1>SNCB Timing Dashboard</h1>
          <p>Analyse en temps réel de la ponctualité ferroviaire</p>
        </div>
        <div className="header__meta">
          <span className="meta__label">Dernière mise à jour</span>
          <span className="meta__value">
            {dashboard?.last_updated ? dayjs(dashboard.last_updated).format('HH:mm:ss') : 'N/A'}
          </span>
        </div>
      </header>

      <section className="filters">
        <div className="filter__item">
          <label>Date</label>
          <input
            type="date"
            value={filters.day}
            onChange={(event) => setFilters((prev) => ({ ...prev, day: event.target.value }))}
          />
        </div>
        <div className="filter__item">
          <label>Gare de départ</label>
          <Select
            options={selectOptions}
            isClearable
            placeholder="Toutes les gares"
            styles={customSelectStyles}
            value={filters.departureStation}
            onChange={(value) => setFilters((prev) => ({ ...prev, departureStation: value }))}
          />
        </div>
        <div className="filter__item">
          <label>Gare d'arrivée</label>
          <Select
            options={selectOptions}
            isClearable
            placeholder="Toutes les gares"
            styles={customSelectStyles}
            value={filters.arrivalStation}
            onChange={(value) => setFilters((prev) => ({ ...prev, arrivalStation: value }))}
          />
        </div>
      </section>

      <section className="summary">
        <DashboardCard
          title="Retard moyen"
          value={`${summary.average_delay_minutes.toFixed(1)} min`}
          subtitle="Calculé sur les arrivées"
          variant="primary"
        />
        <DashboardCard
          title="Trajets en retard"
          value={summary.late_trains}
          subtitle="Nombre total"
          variant="danger"
        />
        <DashboardCard
          title="Taux de ponctualité"
          value={`${summary.punctuality.toFixed(0)}%`}
          subtitle="Trains à l'heure"
          variant="success"
        />
      </section>

      <section className="chart__section">
        <div className="chart__card">
          <div className="chart__header">
            <h2>Trajets par heure</h2>
            <span>Distribution des départs</span>
          </div>
          {histogramData ? (
            <Bar
              data={histogramData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                  y: { beginAtZero: true, ticks: { precision: 0 } },
                },
              }}
            />
          ) : (
            <div className="chart__placeholder">Aucune donnée disponible</div>
          )}
        </div>
      </section>

      <section className="table__section">
        <div className="table__header">
          <h2>Détail des trajets (D00)</h2>
          <span>{isLoading ? 'Chargement…' : `${dashboard?.journeys?.length || 0} trajets`}</span>
        </div>
        <JourneyTable journeys={dashboard?.journeys || []} />
      </section>
    </div>
  );
}

export default App;
