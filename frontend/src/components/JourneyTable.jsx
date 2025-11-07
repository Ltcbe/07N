import React from 'react';
import PropTypes from 'prop-types';
import dayjs from 'dayjs';

function StatusBadge({ status }) {
  const classes = {
    "À l'heure": 'badge badge--success',
    'Léger retard': 'badge badge--warning',
    Retard: 'badge badge--danger',
    Annulé: 'badge badge--neutral',
  };
  const className = classes[status] || 'badge';
  return <span className={className}>{status}</span>;
}

StatusBadge.propTypes = {
  status: PropTypes.string.isRequired,
};

function JourneyTable({ journeys }) {
  return (
    <div className="table__wrapper">
      <table>
        <thead>
          <tr>
            <th>Train</th>
            <th>Type</th>
            <th>Gare de départ</th>
            <th>Gare d'arrivée</th>
            <th>Heure départ</th>
            <th>Heure arrivée</th>
            <th>Retard</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {journeys.length === 0 ? (
            <tr>
              <td colSpan={8} className="table__empty">
                Aucun trajet trouvé pour les filtres sélectionnés.
              </td>
            </tr>
          ) : (
            journeys.map((journey) => (
              <tr key={journey.id}>
                <td>{journey.train}</td>
                <td>{journey.type || '—'}</td>
                <td>{journey.departure_station}</td>
                <td>{journey.arrival_station || '—'}</td>
                <td>{journey.departure_time ? dayjs(journey.departure_time).format('HH:mm') : '—'}</td>
                <td>{journey.arrival_time ? dayjs(journey.arrival_time).format('HH:mm') : '—'}</td>
                <td>{journey.delay_minutes.toFixed(2)} min</td>
                <td>
                  <StatusBadge status={journey.status} />
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

JourneyTable.propTypes = {
  journeys: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      train: PropTypes.string,
      type: PropTypes.string,
      departure_station: PropTypes.string,
      arrival_station: PropTypes.string,
      departure_time: PropTypes.string,
      arrival_time: PropTypes.string,
      delay_minutes: PropTypes.number,
      status: PropTypes.string,
    })
  ),
};

JourneyTable.defaultProps = {
  journeys: [],
};

export default JourneyTable;
