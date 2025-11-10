// Interroge le backend FastAPI (proxifié par Nginx via /api)
const API_BASE = (import.meta.env.VITE_API_BASE as string) || '/api';

export async function fetchTrainsFromBackend(stationName: string, date: Date) {
  const dateStr = date.toISOString().slice(0,10);
  const url = `${API_BASE}/trains?station=${encodeURIComponent(stationName)}&date=${dateStr}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Backend error ${res.status}`);
  const data = await res.json();
  // Convertit les timestamps ISO en Date
  return (data || []).map((t: any) => ({
    ...t,
    scheduledTime: t.scheduledTime ? new Date(t.scheduledTime) : null,
    actualTime: t.actualTime ? new Date(t.actualTime) : null,
  }));
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
];

export const MAIN_STATIONS = [
  'Brussels-Central/Brussel-Centraal',
  'Brussels-Midi/Brussel-Zuid',
  'Antwerpen-Centraal',
  'Gent-Sint-Pieters',
  'Liège-Guillemins',
];
