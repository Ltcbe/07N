import React, { useMemo } from 'react'
import type { Train } from '../lib/utils'
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts'

export const HourlyChart: React.FC<{trains: Train[]}> = ({trains}) => {
  const data = useMemo(()=>{
    const buckets: Record<string, { hour: string, avgDelay: number, count: number }> = {}
    for (const t of trains) {
      const h = String(t.scheduledTime.getHours()).padStart(2,'0')
      if (!buckets[h]) buckets[h] = { hour: `${h}:00`, avgDelay: 0, count: 0 }
      buckets[h].avgDelay += t.delay
      buckets[h].count += 1
    }
    return Object.values(buckets).sort((a,b)=>a.hour.localeCompare(b.hour)).map(b=>({hour:b.hour, avgDelay: b.count? +(b.avgDelay/b.count).toFixed(1) : 0}))
  }, [trains])

  return (
    <div className="card" style={{height:'320px'}}>
      <div className="mb-4 text-slate-700">Retard moyen par heure</div>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="hour" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="avgDelay" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
