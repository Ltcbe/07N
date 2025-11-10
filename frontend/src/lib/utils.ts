export interface Train {
  id: string;
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
    const d = t.scheduledTime;
    const isSameDay =
      d.getDate() === criteria.date.getDate() &&
      d.getMonth() === criteria.date.getMonth() &&
      d.getFullYear() === criteria.date.getFullYear();

    if (!isSameDay) return false;

    if (criteria.departure && !t.departureStation.toLowerCase().includes(criteria.departure.toLowerCase())) {
      return false;
    }
    if (criteria.arrival && !t.arrivalStation.toLowerCase().includes(criteria.arrival.toLowerCase())) {
      return false;
    }
    return true;
  });
}

export function calculateKPIs(trains: Train[]) {
  if (trains.length === 0) {
    return { averageDelay: 0, delayedCount: 0, punctualityRate: 100 };
  }
  const totalDelay = trains.reduce((sum, t) => sum + t.delay, 0);
  const averageDelay = totalDelay / trains.length;
  const delayedCount = trains.filter((t) => t.delay > 0).length;
  const punctualityRate = ((trains.length - delayedCount) / trains.length) * 100;
  return {
    averageDelay: Math.round(averageDelay * 10) / 10,
    delayedCount,
    punctualityRate: Math.round(punctualityRate * 10) / 10,
  };
}

export function formatTime(d: Date): string {
  return d.toLocaleTimeString('fr-BE', { hour: '2-digit', minute: '2-digit' });
}
