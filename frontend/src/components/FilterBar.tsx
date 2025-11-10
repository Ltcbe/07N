import React from 'react'
import { BELGIAN_STATIONS } from '../lib/irailApi'

interface FilterBarProps {
  selectedDate: Date;
  onDateChange: (d: Date) => void;
  departureStation: string;
  onDepartureChange: (s: string) => void;
  arrivalStation: string;
  onArrivalChange: (s: string) => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  selectedDate, onDateChange, departureStation, onDepartureChange, arrivalStation, onArrivalChange
}) => {
  const dateStr = new Date(selectedDate.getTime() - selectedDate.getTimezoneOffset()*60000).toISOString().slice(0,10)
  return (
    <div className="card">
      <div className="grid" style={{gridTemplateColumns:'1fr 1fr 1fr 1fr', gap: '12px'}}>
        <div>
          <label className="block mb-2 text-sm text-slate-600">Date</label>
          <input className="input" type="date" value={dateStr} onChange={(e)=>onDateChange(new Date(e.target.value+'T00:00:00'))} />
        </div>
        <div>
          <label className="block mb-2 text-sm text-slate-600">Gare de départ</label>
          <input className="input" list="stations" value={departureStation} onChange={(e)=>onDepartureChange(e.target.value)} placeholder="Brussels-Central" />
        </div>
        <div>
          <label className="block mb-2 text-sm text-slate-600">Gare d'arrivée</label>
          <input className="input" list="stations" value={arrivalStation} onChange={(e)=>onArrivalChange(e.target.value)} placeholder="Antwerpen-Centraal" />
        </div>
        <div className="flex items-end">
          <datalist id="stations">
            {BELGIAN_STATIONS.map(s => <option key={s} value={s} />)}
          </datalist>
        </div>
      </div>
    </div>
  )
}
