export type PosCode = 'STR' | 'SCT' | 'SEN' | 'TRK' | 'HNT' | 'TRP' | 'GRD' | 'PDR' | 'PFD' | 'KPR' | 'ARC';

export interface PlayerData {
  id: string; name: string; pos: PosCode; age: number; yoe: number;
  ovr: number; ovrPreCamp: number; ovrChange: number; campScore: number; readiness: number;
  roleFamiliarity: string; role: string; formation: string; salaryMMEL: number; development: string;
  jersey: number;
}
export interface TeamData { franchise: string; formation: string; registered: number; players: PlayerData[] }
export interface TeamColors { abbr: string; slug: string; primary: string; secondary: string; accent: string; number: string; palette: string }

/** ARCADE PLACEHOLDER attributes derived from the single canon OVR. Not canon. */
export interface Attr {
  speedRating: number; top: number; accel: number; throwV: number; acc: number;
  catchS: number; tackle: number; strength: number; view: number; react: number; archery: number;
}

export interface Intent {
  mx: number; my: number; sprint: boolean;
  pass: number;        // teammate athlete index or -1
  shoot: boolean;
  tackle: boolean;
  fire: number;        // archer: target athlete index or -1
}
export const NO_INTENT = (): Intent => ({ mx: 0, my: 0, sprint: false, pass: -1, shoot: false, tackle: false, fire: -1 });

export interface Stats {
  points: number; goals: number; passAtt: number; passComp: number; tackles: number; turnovers: number;
  saves: number; arrows: number; arrowHits: number; interceptions: number; minors: number; majors: number;
}
export const newStats = (): Stats => ({ points: 0, goals: 0, passAtt: 0, passComp: 0, tackles: 0, turnovers: 0, saves: 0, arrows: 0, arrowHits: 0, interceptions: 0, minors: 0, majors: 0 });

export type Role = 'field' | 'keeper' | 'archer';

export interface Memory { x: number; y: number; vx: number; vy: number; t: number; frozen: boolean }

export interface Athlete {
  idx: number; team: 0 | 1; d: PlayerData; a: Attr; role: Role;
  line: number; slotY: number;          // formation slot (line 0 back,1 mid,2 fwd)
  x: number; y: number; z: number; vx: number; vy: number; facing: number;
  intent: Intent;
  frozenT: number; immuneT: number; recoverT: number;
  groundedT: number; stumbleT: number; actT: number; act: string; celebrateT: number;
  noCatchT: number;
  excludedT: number; dq: boolean; minors: number; majors: number;
  kzT: number;
  // AI state (perception-bounded)
  mem: Map<number, Memory>; ballMem: { x: number; y: number; z: number; vx: number; vy: number; vz: number; t: number; holder: number };
  rolledPass: number;
  nextThink: number; tx: number; ty: number; aiSprint: boolean; aiPassAt: number; plan: Intent; lastFire: number;
  stats: Stats;
  look: { skin: number; hair: number; build: number; height: number; face: number };
}

export interface Arrow { team: 0 | 1; x: number; y: number; z: number; vx: number; vy: number; vz: number; target: number; life: number; tx: number; ty: number; resolved: boolean }

export interface GameEvent { t: number; period: number; clock: number; type: string; team: number; who: number; text: string; pts?: number; kind?: string; dist?: number }

export type Phase = 'pregame' | 'set' | 'live' | 'snap' | 'dead' | 'break' | 'final';

export interface Settings {
  seed: number;
  scoring: 'flat' | 'banded';
  periodLen: number;     // 600 canon; accelerated clock is a visible setting, off by default
  otLen: number;
}
