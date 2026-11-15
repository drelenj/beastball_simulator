import { Attr, PlayerData, PosCode, TeamData } from './types';
import { SPEED_UNIT } from './constants';

/**
 * ARCADE PLACEHOLDER: OVR -> attribute mapping. The workbook has ONE OVR per player and no
 * per-skill ratings, so every attribute here is a labelled arcade placeholder, never canon.
 * Speed follows the canon scale: speed rating r -> r x 44.704 m/s.
 */
export function attrsFromOvr(ovr: number, pos: PosCode): Attr {
  const q = Math.max(0, Math.min(1, (ovr - 40) / 60)); // 0..1
  const posSpeed: Record<string, number> = { STR: 0.006, SCT: 0.01, HNT: 0.008, TRK: 0.008, PFD: 0.002, PDR: 0, SEN: 0, TRP: 0, GRD: -0.004, KPR: -0.012, ARC: -0.015 };
  const speedRating = 0.17 + 0.045 * q + (posSpeed[pos] ?? 0); // ~7.6..10.1 m/s sprint
  const strong = pos === 'GRD' || pos === 'PFD' || pos === 'SEN' || pos === 'TRP';
  return {
    speedRating,
    top: speedRating * SPEED_UNIT,
    accel: 5.5 + 2.5 * q,
    throwV: 19 + 9 * q + (pos === 'STR' || pos === 'PDR' ? 2 : 0),
    acc: 0.55 + 0.4 * q + (pos === 'PDR' ? 0.05 : 0),
    catchS: 0.6 + 0.35 * q + (pos === 'KPR' ? 0.05 : 0),
    tackle: 0.4 + 0.45 * q + (pos === 'TRK' || pos === 'GRD' || pos === 'HNT' ? 0.08 : 0),
    strength: 0.4 + 0.4 * q + (strong ? 0.1 : 0),
    view: 45 + 30 * q,
    react: 0.32 - 0.16 * q,
    archery: 0.35 + 0.6 * q,
  };
}

/** ARCADE PLACEHOLDER: position -> behaviour line preference (0 back .. 1 forward). */
export const LINE_PREF: Record<string, number> = { GRD: 0, TRP: 0.2, SEN: 0.35, TRK: 0.5, PDR: 0.6, HNT: 0.7, PFD: 0.8, SCT: 0.9, STR: 1 };
export const POS_LABEL: Record<string, string> = {
  STR: 'Striker (finisher)', SCT: 'Scout (wide receiver)', SEN: 'Sentinel (screen)', TRK: 'Tracker (pursuer)',
  HNT: 'Hunter (ball hawk)', TRP: 'Trapper (interceptor)', GRD: 'Guard (goal-side)', PDR: 'Playdriver (passer)',
  PFD: 'Power forward (carrier)', KPR: 'Keeper', ARC: 'Archer',
};

export function parseFormation(f: string): [number, number, number] {
  const p = f.split(/[–\-]/).map((s) => parseInt(s, 10));
  if (p.length === 3 && p.every((n) => n > 0) && p[0] + p[1] + p[2] === 10) return [p[0], p[1], p[2]];
  return [3, 4, 3];
}

export interface Lineup { field: { p: PlayerData; line: number; slotY: number }[]; keeper: PlayerData; archer: PlayerData; bench: PlayerData[] }

export function buildLineup(t: TeamData): Lineup {
  const starters = t.players.filter((p) => p.role === 'Projected starter');
  const keeper = starters.find((p) => p.pos === 'KPR') ?? t.players.find((p) => p.pos === 'KPR')!;
  const archer = starters.find((p) => p.pos === 'ARC') ?? t.players.find((p) => p.pos === 'ARC')!;
  let fieldP = starters.filter((p) => p.pos !== 'KPR' && p.pos !== 'ARC');
  if (fieldP.length < 10) {
    const extra = t.players.filter((p) => !starters.includes(p) && p.pos !== 'KPR' && p.pos !== 'ARC').sort((a, b) => b.ovr - a.ovr);
    fieldP = fieldP.concat(extra.slice(0, 10 - fieldP.length));
  }
  fieldP = fieldP.slice(0, 10).sort((a, b) => (LINE_PREF[a.pos] ?? 0.5) - (LINE_PREF[b.pos] ?? 0.5) || a.id.localeCompare(b.id));
  const [nb, nm, nf] = parseFormation(t.formation || starters[0]?.formation || '3–4–3');
  const counts = [nb, nm, nf];
  const field: Lineup['field'] = [];
  let k = 0;
  for (let line = 0; line < 3; line++) {
    const n = counts[line];
    for (let i = 0; i < n; i++) {
      const slotY = n === 1 ? 0 : -1 + (2 * i) / (n - 1);
      field.push({ p: fieldP[k++], line, slotY });
    }
  }
  const used = new Set([keeper.id, archer.id, ...fieldP.map((p) => p.id)]);
  const bench = t.players.filter((p) => !used.has(p.id) && p.role !== 'Outside projected 25').slice(0, 10);
  return { field, keeper, archer, bench };
}

/** Deterministic, varied appearance from Player ID (skin tone, hair, build, height, face). */
export function lookFor(id: string, pos: PosCode) {
  let h = 2166136261;
  for (let i = 0; i < id.length; i++) { h ^= id.charCodeAt(i); h = Math.imul(h, 16777619); }
  const r = (n: number) => { h = Math.imul(h ^ (h >>> 13), 1597334677); return ((h >>> 0) % n); };
  const buildBias = pos === 'GRD' || pos === 'PFD' || pos === 'KPR' ? 2 : pos === 'SCT' || pos === 'STR' || pos === 'ARC' ? 0 : 1;
  const build = Math.max(0, Math.min(2, buildBias + (r(3) - 1) * (r(2))));
  return { skin: r(4), hair: r(4), build, height: 0.92 + r(17) / 100, face: r(4) };
}
