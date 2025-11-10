export interface Train {
  id?: string;
  trainNumber: string;
  departureStation: string;
  arrivalStation: string;
  scheduledTime: Date;
  actualTime: Date;
  delay: number;
  status: 'on-time' | 'delayed' | 'cancelled';
}

export interface FilterCriteria {
  date: Date;
  departure: string;
  arrival: string;
}

export function filterTrains(trains: Train[], criteria: FilterCriteria): Train[] {
  return trains.filter((t) => {
    const d = new Date(t.scheduledTime);
    const isSameDay = d.toISOString().slice(0,10) === criteria.date.toISOString().slice(0,10);
    if (!isSameDay) return false;
    if (criteria.departure && !t.departureStation.toLowerCase().includes(criteria.departure.toLowerCase())) return false;
    if (criteria.arrival && !t.arrivalStation.toLowerCase().includes(criteria.arrival.toLowerCase())) return false;
    return true;
  });
}

export function calculateKPIs(trains: Train[]) {
  if (trains.length === 0) return { averageDelay: 0, delayedCount: 0, punctualityRate: 100 };
  const totalDelay = trains.reduce((sum, t) => sum + (t.delay || 0), 0);
  const averageDelay = totalDelay / trains.length;
  const delayedCount = trains.filter((t) => (t.delay || 0) > 0).length;
  const punctualityRate = ((trains.length - delayedCount) / trains.length) * 100;
  return { averageDelay: +averageDelay.toFixed(1), delayedCount, punctualityRate: +punctualityRate.toFixed(1) };
}

export function formatTime(d: Date | string): string {
  const date = new Date(d);
  return date.toLocaleTimeString('fr-BE', { hour: '2-digit', minute: '2-digit' });
}
