import React from 'react'
import type { Train } from '../lib/utils'
import { formatTime } from '../lib/utils'

export const TrainsTable: React.FC<{trains: Train[]}> = ({trains}) => {
  return (
    <div className="card">
      <div className="mb-2" style={{color:'#334155'}}>Trajets</div>
      <div style={{overflowX:'auto'}}>
        <table className="table">
          <thead>
            <tr>
              <th>Train</th>
              <th>Départ</th>
              <th>Arrivée</th>
              <th>Heure prévue</th>
              <th>Heure réelle</th>
              <th>Retard (min)</th>
              <th>Statut</th>
            </tr>
          </thead>
          <tbody>
            {trains.map((t,idx)=> (
              <tr key={t.id || idx}>
                <td>{t.trainNumber}</td>
                <td>{t.departureStation}</td>
                <td>{t.arrivalStation}</td>
                <td>{t.scheduledTime ? formatTime(t.scheduledTime) : '-'}</td>
                <td>{t.actualTime ? formatTime(t.actualTime) : '-'}</td>
                <td>{t.delay ?? 0}</td>
                <td>
                  <span className={'badge ' + (t.status==='on-time'?'success': (t.status==='delayed'?'warning':'danger'))}>
                    {t.status==='on-time'?'À l’heure': (t.status==='delayed'?'Retard':'Annulé')}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
