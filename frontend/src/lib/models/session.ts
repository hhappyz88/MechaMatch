export type SessionStatus = 'completed' | 'running' | 'failed' | 'pending';

export interface Session {
  id: string;
  name: string;
  status: SessionStatus;
  lastRun: string; // ISO date or display-friendly string
}

export const statusColours: Record<SessionStatus, string> = {
	completed: 'bg-green-100 text-green-700',
	running: 'bg-blue-100 text-blue-700',
	failed: 'bg-red-100 text-red-700',
	pending: 'bg-yellow-100 text-yellow-700'
};


export const mockSessions: Session[] = [
  {
    id: '001',
    name: 'Scrape: ShowZ',
    status: 'completed',
    lastRun: '2025-06-06T10:24:00Z',
  },
  {
    id: '002',
    name: 'Scrape: Sugo Toys',
    status: 'running',
    lastRun: '2025-06-06T11:15:00Z',
  },
];