export interface Record {
  wins: number;
  losses: number;
  opponent: string;
}

export interface PlayerRecord {
  wins: number;
  losses: number;
  opponent: Player;
}

export interface Player {
  name: string;
  braacket_rank: number;
  colley_rank: number;
  colley_score: number;
  colley_strength_of_schedule: number;
  colley_strength_of_schedule_rank?: number;
  characters?: string[];
  records: Record[];
  player_records?: PlayerRecord[];
}
