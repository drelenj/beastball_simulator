import rosters from '../../data/rosters.json';
import colors from '../../data/team_colors.json';
import { Engine } from './engine';
import { Settings, TeamData, TeamColors } from './types';
import * as C from './constants';

export const TEAMS: TeamData[] = (rosters as any).teams;
export const COLORS: Record<string, TeamColors> = (colors as any).teams;
export const teamByName = (n: string) => TEAMS.find((t) => t.franchise === n)!;
export const defaultSettings = (seed = 20261115): Settings => ({ seed, scoring: 'flat', periodLen: C.PERIOD_LEN, otLen: C.OT_LEN });

/** Run a full match headless with the same engine (breaks auto-skipped). */
export function runHeadless(home: string, away: string, s: Settings, maxSteps = 60 * 60 * 120) {
  const e = new Engine(teamByName(home), teamByName(away), s);
  let steps = 0;
  while (e.phase !== 'final' && steps < maxSteps) {
    if (e.phase === 'break') e.resumeFromBreak();
    e.step(); steps++;
  }
  return e;
}
