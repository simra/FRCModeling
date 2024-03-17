export interface TeamStats {
    opr: number;
    sigma: number;
  }
  
  export class  Team {
    team: string;
    stats: TeamStats;

    constructor(team?: string, stats?: TeamStats | null) {
        this.team = team || "";
        this.stats = stats || { opr: 0, sigma: 0 };
    }
  }