import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const API = (import.meta as any).env.VITE_API_BASE || 'http://localhost:1788'

function todayISO() {
  const d = new Date()
  return d.toISOString().slice(0,10)
}

export default function Dashboard(){
  const [date, setDate] = useState(todayISO())
  const [kpi, setKpi] = useState({ meanDelay: 0, lateCount: 0, punctualRate: 0 })
  const [hist, setHist] = useState<{hour:number;trips:number}[]>([])
  const [rows, setRows] = useState<any[]>([])

  async function load(){
    const qs = new URLSearchParams({date}).toString()
    const [s,h,t] = await Promise.all([
      fetch(`${API}/metrics/summary?${qs}`).then(r=>r.json()),
      fetch(`${API}/metrics/histogram?${qs}`).then(r=>r.json()),
      fetch(`${API}/trips?${qs}&size=100`).then(r=>r.json())
    ])
    setKpi(s); setHist(h); setRows(t.items || [])
  }

  useEffect(()=>{ load() }, [date])

  return (
    <div style={{padding:16}}>
      <h1>SNCB Timing Dashboard</h1>
      <div style={{display:'flex', gap:12, margin:'12px 0'}}>
        <label>Date:&nbsp;
          <input type="date" value={date} onChange={e=>setDate(e.target.value)} />
        </label>
      </div>
      <div style={{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:12}}>
        <div style={{padding:16, border:'1px solid #eee', borderRadius:8}}>
          <div>Retard moyen</div>
          <div style={{fontSize:28}}>{kpi.meanDelay.toFixed(1)} min</div>
        </div>
        <div style={{padding:16, border:'1px solid #eee', borderRadius:8}}>
          <div>Trajets en retard</div>
          <div style={{fontSize:28, color:'#c00'}}>{kpi.lateCount}</div>
        </div>
        <div style={{padding:16, border:'1px solid #eee', borderRadius:8}}>
          <div>Taux de ponctualité</div>
          <div style={{fontSize:28, color:'#0a6'}}>{Math.round(kpi.punctualRate)}%</div>
        </div>
      </div>

      <div style={{padding:16, border:'1px solid #eee', borderRadius:8, marginTop:16}}>
        <div style={{marginBottom:8}}>Trajets par heure</div>
        <div style={{width:'100%', height:280}}>
          <ResponsiveContainer>
            <BarChart data={hist}>
              <XAxis dataKey="hour" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="trips" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{padding:16, border:'1px solid #eee', borderRadius:8, marginTop:16}}>
        <div>Détail des trajets</div>
        <table style={{width:'100%', borderCollapse:'collapse', marginTop:8}}>
          <thead>
            <tr>
              <th style={{textAlign:'left',borderBottom:'1px solid #ddd'}}>N° Train</th>
              <th style={{textAlign:'left',borderBottom:'1px solid #ddd'}}>Départ</th>
              <th style={{textAlign:'left',borderBottom:'1px solid #ddd'}}>Arrivée</th>
              <th style={{textAlign:'left',borderBottom:'1px solid #ddd'}}>Heure prévue</th>
              <th style={{textAlign:'left',borderBottom:'1px solid #ddd'}}>Heure réelle</th>
              <th style={{textAlign:'left',borderBottom:'1px solid #ddd'}}>Retard</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r:any)=>(
              <tr key={r.id}>
                <td>{r.vehicle_id}</td>
                <td>{r.from_station}</td>
                <td>{r.to_station}</td>
                <td>{(r.last_stop_planned||'').toString().replace('T',' ')}</td>
                <td>{(r.last_stop_real||'').toString().replace('T',' ')}</td>
                <td>{Math.round((r.delay_sec||0)/60)} min</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
