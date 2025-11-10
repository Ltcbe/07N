import React from 'react'
import type { Train } from '../lib/utils'
import { calculateKPIs } from '../lib/utils'

export const KPICards: React.FC<{trains: Train[]}> = ({trains}) => {
  const k = calculateKPIs(trains)
  const items = [
    { label: 'Retard moyen (min)', value: k.averageDelay },
    { label: 'Trains en retard', value: k.delayedCount },
    { label: 'Taux de ponctualité (%)', value: k.punctualityRate },
  ]
  return (
    <div className="grid grid-3">
      {items.map((i)=> (
        <div key={i.label} className="card">
          <div className="text-sm text-slate-500">{i.label}</div>
          <div className="text-2xl mt-2">{i.value}</div>
        </div>
      ))}
    </div>
  )
}
