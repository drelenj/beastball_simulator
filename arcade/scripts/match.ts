import { Engine, teams } from '../src/engine';
import { writeFileSync } from 'node:fs';
const seed = Number(process.argv[2] ?? 202627);
const e = new Engine({ home: teams.find(t => t.name === 'Ala Marauders')!, away: teams.find(t => t.name === 'Xenar Ignite')!, mode: 'spectator', seed, clockRate: Number(process.argv[3] ?? 1) });
while (e.phase !== 'final' && e.tick < 300000) e.step();
const result = e.result();
writeFileSync(`evidence/match-${seed}.json`, JSON.stringify(result, null, 2));
console.log(JSON.stringify({score:e.score,phase:e.phase,ticks:e.tick,quarters:e.events.filter(x=>x.type==='quarter').length,stats:e.teamStats},null,2));
