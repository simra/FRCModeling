export class BasicStats {
    mu: number;
    sigma: number;
  
    constructor(mu?: number, sigma?: number) {
      this.mu = mu || 0;
      this.sigma = sigma || 0;
    }
  
  }

  export class TeamStats {
    opr: BasicStats;
    dpr: BasicStats;
    tpr: BasicStats;
  
    constructor(opr?: BasicStats, dpr?: BasicStats, tpr?: BasicStats) {
      this.opr = opr || new BasicStats();
      this.dpr = dpr || new BasicStats();
      this.tpr = tpr || new BasicStats();
    }
  }
  
  export class  Team {
    team: string;
    nickname: string;
    number: number;
    stats: TeamStats

    constructor(team?: string, stats?: TeamStats, nickname?: string, number?: number) {
        this.team = team || "";
        this.stats = stats || new TeamStats();
        this.nickname = nickname || "";
        this.number = number || 0;
    }
  }