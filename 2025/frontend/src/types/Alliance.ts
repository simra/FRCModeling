import { Team } from "./TeamTypes";

export class Alliance {
    id: number;
    teams: Team[];
    winProbability: number | null;

    constructor(id: number, teams: Team[], winProbability?: number) {
        this.id = id;
        this.teams = teams;
        this.winProbability = winProbability || null;
    }
}