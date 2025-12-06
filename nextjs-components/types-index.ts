// types/index.ts
// TypeScript type definitions for the application

export interface LiveData {
  vibration: number;
  temperature: number;
  score: number;
  status: 'NORMAL' | 'WARNING' | 'ANOMALY';
  timestamp: string;
}

export interface HistoricalData {
  timestamp: string;
  vibration: number;
  temperature: number;
  score: number;
  status: string;
}

export interface Statistics {
  vibration: {
    average: number;
    max: number;
  };
  temperature: {
    average: number;
    max: number;
  };
  ai_score: {
    average: number;
    min: number;
  };
}
