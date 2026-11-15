// Fast headless full-match run of the SAME engine used in the browser.
// Usage: npx tsx scripts/headless.ts [home] [away] [seed] [flat|banded]
import { runHeadless, defaultSettings } from '../src/engine/match';
const [home = 'Ala Marauders', away = 'Xenar Ignite', seedS = '20261115', scoring = 'flat'] = process.argv.slice(2);
const s = defaultSettings(Number(seedS)); s.scoring = scoring as any;
const t0 = Date.now();
const e = runHeadless(home, away, s);
const ms = Date.now() - t0;
const by = (type: string, team?: number) => e.events.filter((v) => v.type === type && (team === undefined || v.team === team)).length;
const out: any = {
  home, away, seed: s.seed, scoring: s.scoring, phase: e.phase, period: e.period, ticks: e.tick, gameSeconds: +e.time.toFixed(1), wallMs: ms,
  score: [e.teams[0].score, e.teams[1].score], winner: e.winner >= 0 ? e.teams[e.winner].data.franchise : 'draw/incomplete', hash: e.hash(), checkpoints: e.checkpoints,
  breakdown: e.teams.map((t) => t.breakdown), possessionSeconds: e.teams.map((t) => +t.possTime.toFixed(1)), possessionChanges: e.possChanges,
  perTeam: [0, 1].map((ti) => {
    const A = e.ath.filter((a) => a.team === ti);
    const sum = (k: string) => A.reduce((n, a) => n + (a.stats as any)[k], 0);
    return { franchise: e.teams[ti].data.franchise, athletes: A.length, keeper: A.find((a) => a.role === 'keeper')!.d.name + ' (' + A.find((a) => a.role === 'keeper')!.d.pos + ')', archer: A.find((a) => a.role === 'archer')!.d.name + ' (' + A.find((a) => a.role === 'archer')!.d.pos + ')',
      shots: by('shot', ti), goals: sum('goals'), passAtt: sum('passAtt'), passComp: sum('passComp'), tackles: sum('tackles'), turnovers: sum('turnovers'), saves: sum('saves'), arrows: sum('arrows'), arrowHits: sum('arrowHits'), interceptions: sum('interceptions'), minors: sum('minors'), majors: sum('majors'),
      keeperTouches: e.events.filter((v) => (v.type === 'save') && v.team === ti).length };
  }),
  periodEnds: e.events.filter((v) => v.type === 'period_end').map((v) => v.text),
  scoring_events: e.events.filter((v) => v.type === 'score').map((v) => `${v.period}:${(v.clock).toFixed(0)} ${v.text}`),
};
console.log(JSON.stringify(out, null, 1));
