// frontend/src/lib/irailApi.ts

// Base de l'API backend (proxifiée par Nginx ou Vite)
const API_BASE = import.meta.env.VITE_API_BASE || '/api';

/**
 * Récupère la liste des trains depuis le backend FastAPI.
 * Encode correctement les caractères spéciaux (ex: Liège, Brussels-Central/Brussel-Centraal, etc.)
 */
export async function fetchTrainsFromBackend(stationName: string, date: Date) {
  const dateStr = date.toISOString().slice(0, 10);
  const url = `${API_BASE}/trains?station=${encodeURIComponent(stationName)}&date=${dateStr}`;

  console.log('🔎 Fetching:', url);

  const res = await fetch(url);
  if (!res.ok) {
    console.error(`❌ Backend error ${res.status} for ${url}`);
    throw new Error(`Backend error ${res.status}`);
  }

  const data = await res.json();
  return (data || []).map((t: any) => ({
    ...t,
    scheduledTime: t.scheduledTime ? new Date(t.scheduledTime) : null,
    actualTime: t.actualTime ? new Date(t.actualTime) : null,
  }));
}

/**
 * Liste des principales gares belges (menu déroulant)
 */
export const MAIN_STATIONS = [
  'Brussels-Central/Brussel-Centraal',
  'Brussels-Midi/Brussel-Zuid',
  'Antwerpen-Centraal',
  'Gent-Sint-Pieters',
  'Liège-Guillemins',
];

/**
 * Liste élargie des gares belges utilisées pour la collecte complète
 */
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
