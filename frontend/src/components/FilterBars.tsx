import React from 'react'
import { BELGIAN_STATIONS } from '../lib/irailApi'

interface FilterBarProps {
  selectedDate: Date
  onDateChange: (d: Date) => void
  departureStation: string
  onDepartureChange: (s: string) => void
  arrivalStation: string
  onArrivalChange: (s: string) => void
}

export const FilterBar: React.FC<FilterBarProps> = ({
  selectedDate,
  onDateChange,
  departureStation,
  onDepartureChange,
  arrivalStation,
  onArrivalChange,
}) => {
  const dateStr = new Date(
    selectedDate.getTime() - selectedDate.getTimezoneOffset() * 60000
  )
    .toISOString()
    .slice(0, 10)

  return (
    <div className="card">
      <div
        className="grid"
        style={{ gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}
      >
        {/* Sélection de la date */}
        <div>
          <label className="block mb-2 text-sm text-slate-600">Date</label>
          <input
            className="input w-full"
            type="date"
            value={dateStr}
            onChange={(e) =>
              onDateChange(new Date(e.target.value + 'T00:00:00'))
            }
          />
        </div>

        {/* Gare de départ */}
        <div>
          <label className="block mb-2 text-sm text-slate-600">
            Gare de départ
          </label>
          <select
            className="input w-full"
            value={departureStation}
            onChange={(e) => onDepartureChange(e.target.value)}
          >
            <option value="">-- Sélectionner une gare --</option>
            {BELGIAN_STATIONS.map((station) => (
              <option key={station} value={station}>
                {station}
              </option>
            ))}
          </select>
        </div>

        {/* Gare d’arrivée */}
        <div>
          <label className="block mb-2 text-sm text-slate-600">
            Gare d’arrivée
          </label>
          <select
            className="input w-full"
            value={arrivalStation}
            onChange={(e) => onArrivalChange(e.target.value)}
          >
            <option value="">-- Sélectionner une gare --</option>
            {BELGIAN_STATIONS.map((station) => (
              <option key={station} value={station}>
                {station}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  )
}
