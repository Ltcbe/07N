// /src/lib/irailApi.ts
import type { Train } from './utils'

const IRAIL_BASE_URL = 'https://api.irail.be'

function formatDateForIrail(date: Date): string {
  const d = String(date.getDate()).padStart(2, '0')
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const y = String(date.getFullYear()).slice(-2)
  return `${d}${m}${y}`
}

function formatTimeForIrail(date: Date): string {
  const h = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  return `${h}${min}`
}

type IrailDeparture = {
  id: string
  station: string
  time: string
  vehicle: string
  platform?: string
  canceled?: string
  delay?: string
}

type IrailLiveboardResponse = {
  station: string
  departures: { departure: IrailDeparture[] }
}

export function transformIrailDepartureToTrain(dep: IrailDeparture, departureStationName: string): Train {
  const scheduledTime = new Date(parseInt(dep.time) * 1000)
  const delaySeconds = parseInt(dep.delay || '0')
  const delayMinutes = Math.round(delaySeconds / 60)
  const actualTime = new Date(scheduledTime.getTime() + delaySeconds * 1000)
  const trainNumber = dep.vehicle.split('.').pop() || dep.vehicle
  const status: 'on-time' | 'delayed' | 'cancelled' =
    dep.canceled === '1' ? 'cancelled' : delayMinutes > 0 ? 'delayed' : 'on-time'

  return {
    id: `${dep.vehicle}-${dep.time}`,
    trainNumber,
    departureStation: departureStationName,
    arrivalStation: dep.station,
    scheduledTime,
    actualTime,
    delay: delayMinutes,
    status,
  }
}

export async function fetchLiveboard(stationName: string, date: Date = new Date()): Promise<Train[]> {
  const url = new URL(`${IRAIL_BASE_URL}/liveboard/`)
  url.searchParams.set('station', stationName)
  url.searchParams.set('date', formatDateForIrail(date))
  url.searchParams.set('time', formatTimeForIrail(date))
  url.searchParams.set('arrdep', 'departure')
  url.searchParams.set('format', 'json')
  url.searchParams.set('lang', 'fr')

  const res = await fetch(url.toString())
  if (!res.ok) throw new Error(`IRAIL HTTP ${res.status}`)
  const data = (await res.json()) as IrailLiveboardResponse
  if (!data?.departures?.departure) return []
  return data.departures.departure.map((d) => transformIrailDepartureToTrain(d, data.station))
}

export async function fetchMultipleStations(stations: string[], date: Date = new Date()): Promise<Train[]> {
  const out: Train[] = []
  const all = await Promise.allSettled(stations.map((s) => fetchLiveboard(s, date)))
  for (const r of all) if (r.status == 'fulfilled') out.push(...r.value)
  return out
}

export const BELGIAN_STATIONS = [
  'Brussels-Central/Brussel-Centraal',
  'Brussels-Midi/Brussel-Zuid',
  'Brussels-North/Brussel-Noord',
  'Antwerpen-Centraal',
  'Gent-Sint-Pieters',
  'Liège-Guillemins',
  'Charleroi-Sud',
  'Namur',
  'Leuven',
  'Brugge',
  'Oostende',
  'Mons',
  'Tournai',
  'Hasselt',
  'Mechelen',
  'Kortrijk',
  'Aalst',
  'Genk',
  'Ottignies',
]
export const MAIN_STATIONS = [
  'Brussels-Central/Brussel-Centraal',
  'Brussels-Midi/Brussel-Zuid',
  'Antwerpen-Centraal',
  'Gent-Sint-Pieters',
  'Liège-Guillemins',
]
