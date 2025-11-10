import React, { useEffect, useMemo, useState } from 'react'
import { FilterBar } from './components/FilterBar'
import { KPICards } from './components/KPICards'
import { HourlyChart } from './components/HourlyChart'
import { TrainsTable } from './components/TrainsTable'
import type { Train } from './lib/utils'
import { filterTrains } from './lib/utils'
import { fetchTrainsFromBackend, MAIN_STATIONS } from './lib/irailApi'
import { Button } from './components/ui/button'

export default function App() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [departureStation, setDepartureStation] = useState<string>('')
  const [arrivalStation, setArrivalStation] = useState<string>('')

  const [trains, setTrains] = useState<Train[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true); setError(null)
      try {
        // Charge un échantillon multi-gares (peut être remplacé par une gare choisie)
        const results = await Promise.allSettled(MAIN_STATIONS.map(s => fetchTrainsFromBackend(s, selectedDate)))
        const merged: Train[] = []
        results.forEach(r => { if (r.status === 'fulfilled') merged.push(...r.value) })
        if (!cancelled) setTrains(merged)
      } catch (e) {
        console.error(e)
        if (!cancelled) setError('Impossible de charger les données')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [selectedDate])

  const filteredTrains = useMemo(() => filterTrains(trains, {
    date: selectedDate, departure: departureStation, arrival: arrivalStation
  }), [trains, selectedDate, departureStation, arrivalStation])

  return (
    <div>
      <header>
        <div className="container px-4 py-6 flex items-center justify-between">
          <h1 style={{fontSize: '24px', fontWeight: 600}}>SNCB Timing Dashboard</h1>
          <Button onClick={()=> setSelectedDate(new Date())} disabled={loading}>
            {loading ? 'Chargement…' : 'Actualiser'}
          </Button>
        </div>
      </header>
      <main className="container px-4 py-6">
        <FilterBar
          selectedDate={selectedDate}
          onDateChange={setSelectedDate}
          departureStation={departureStation}
          onDepartureChange={setDepartureStation}
          arrivalStation={arrivalStation}
          onArrivalChange={setArrivalStation}
        />
        {error && <div className="card" style={{borderColor:'#fecaca', color:'#991b1b'}}> {error} </div>}
        {loading && <div className="card">Chargement des données…</div>}
        {!loading && !error && (
          <>
            <div className="mt-4"><KPICards trains={filteredTrains} /></div>
            <div className="mt-4"><HourlyChart trains={filteredTrains} /></div>
            <div className="mt-4"><TrainsTable trains={filteredTrains} /></div>
            <div className="mt-4" style={{color:'#64748b', fontSize: 12}}>
              Données fournies par iRail (persistées en DB via backend) — {new Date().toLocaleTimeString('fr-BE')}
            </div>
          </>
        )}
      </main>
    </div>
  )
}
