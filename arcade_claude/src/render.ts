// Elevated oblique 2.5D renderer (Canvas 2D). Reads engine state; never mutates it.
import * as C from './engine/constants';
import type { Engine } from './engine/engine';
import type { TeamColors } from './engine/types';
import { animFor, drawAthlete, roundRect } from './sprites';

const SQ = 0.58;   // vertical squash of the ground plane (camera elevation)
const ZK = 0.92;   // height projection

export class Camera {
  x = 0; y = 0; s = 15; mode: 'ball' | 'athlete' = 'ball'; follow = -1;
  update(e: Engine, w: number, h: number, dt: number) {
    let tx = e.ball.x, ty = e.ball.y;
    if (this.mode === 'athlete' && this.follow >= 0) { const a = e.ath[this.follow]; tx = a.x; ty = a.y; }
    this.s = Math.max(12, Math.min(30, w / 50));
    const k = 1 - Math.exp(-dt * 4);
    this.x += (tx - this.x) * k; this.y += (ty - this.y) * k;
    const hw = w / 2 / this.s, hh = h / 2 / this.s / SQ;
    this.x = Math.max(-C.FIELD_HALF - 12 + hw, Math.min(C.FIELD_HALF + 12 - hw, this.x));
    this.y = Math.max(-C.FIELD_HALF - 14 + hh * 0.8, Math.min(C.FIELD_HALF + 10 - hh * 0.8, this.y));
  }
}

export class Renderer {
  cam = new Camera();
  dpr = 1;
  trail: [number, number, number][] = [];
  logos: Record<string, HTMLImageElement> = {};
  constructor(public ctx: CanvasRenderingContext2D) {}
  P(x: number, y: number, z = 0): [number, number] {
    const c = this.ctx.canvas;
    return [c.width / this.dpr / 2 + (x - this.cam.x) * this.cam.s, c.height / this.dpr / 2 + (y - this.cam.y) * this.cam.s * SQ - z * this.cam.s * ZK];
  }
  poly(pts: [number, number, number?][], fill?: string, stroke?: string, lw = 1) {
    const ctx = this.ctx; ctx.beginPath();
    pts.forEach((p, i) => { const [sx, sy] = this.P(p[0], p[1], p[2] ?? 0); i ? ctx.lineTo(sx, sy) : ctx.moveTo(sx, sy); });
    ctx.closePath();
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); }
  }
  groundCircle(cx: number, cy: number, r: number, a0: number, a1: number, stroke: string, lw = 2, clip = true) {
    const ctx = this.ctx; ctx.beginPath();
    for (let i = 0; i <= 48; i++) {
      const a = a0 + (a1 - a0) * i / 48; let x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r;
      if (clip) { x = Math.max(-C.FIELD_HALF, Math.min(C.FIELD_HALF, x)); y = Math.max(-C.FIELD_HALF, Math.min(C.FIELD_HALF, y)); }
      const [sx, sy] = this.P(x, y); i ? ctx.lineTo(sx, sy) : ctx.moveTo(sx, sy);
    }
    ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke();
  }

  draw(e: Engine, cols: [TeamColors, TeamColors], wallT: number, selected: number[]) {
    const ctx = this.ctx, W = ctx.canvas.width / this.dpr, H = ctx.canvas.height / this.dpr, F = C.FIELD_HALF;
    ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    ctx.fillStyle = '#0d1018'; ctx.fillRect(0, 0, W, H);
    // stadium bowl + crowd
    for (let ring = 0; ring < 7; ring++) {
      const m = F + 9 + ring * 4, z = 1 + ring * 2.2;
      this.poly([[-m, -m, z], [m, -m, z], [m, m, z], [-m, m, z]], ring % 2 ? '#1b2030' : '#20263a');
    }
    // crowd dots (deterministic)
    let seed = 7;
    const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
    const crowdCols = [cols[0].primary, cols[1].primary, '#d8d0c0', cols[0].secondary, cols[1].secondary, '#8a7f6a'];
    for (let i = 0; i < 1400; i++) {
      const side = i % 4, t = rnd() * 2 - 1, ring = rnd();
      const m = F + 10 + ring * 26, z = 1.3 + ring * 13;
      const x = side === 0 ? t * m : side === 1 ? t * m : side === 2 ? -m : m;
      const y = side === 0 ? -m : side === 1 ? m : t * m;
      if (side === 1 && ring > 0.25) continue; // keep the near stand low so it doesn't block play
      const [sx, sy] = this.P(x, y, z);
      if (sx < -5 || sx > W + 5 || sy < -5 || sy > H + 5) continue;
      ctx.fillStyle = crowdCols[i % crowdCols.length];
      const bounce = Math.sin(wallT * 6 + i) > 0.85 ? 2 : 0;
      ctx.fillRect(sx, sy - bounce, 3, 3);
    }
    // pitch with stripes
    this.poly([[-F - 4, -F - 4], [F + 4, -F - 4], [F + 4, F + 4], [-F - 4, F + 4]], '#2a5a2e');
    for (let i = 0; i < 10; i++) { const x0 = -F + i * 10; this.poly([[x0, -F], [x0 + 10, -F], [x0 + 10, F], [x0, F]], i % 2 ? '#3a7a3c' : '#357236'); }
    const line = 'rgba(255,255,255,0.85)';
    this.poly([[-F, -F], [F, -F], [F, F], [-F, F]], undefined, line, 2.5);
    { const [a1, b1] = this.P(0, -F), [a2, b2] = this.P(0, F); ctx.strokeStyle = line; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(a1, b1); ctx.lineTo(a2, b2); ctx.stroke(); }
    this.groundCircle(0, 0, C.CENTRE_CIRCLE_R, 0, Math.PI * 2, line, 2, false);
    // 40 m scrimmage lines (dashed)
    ctx.setLineDash([8, 6]);
    for (const gx of [-F, F]) { const x = gx - Math.sign(gx) * C.SCRIM_LINE; const [a1, b1] = this.P(x, -F), [a2, b2] = this.P(x, F); ctx.strokeStyle = 'rgba(255,255,255,0.6)'; ctx.beginPath(); ctx.moveTo(a1, b1); ctx.lineTo(a2, b2); ctx.stroke(); }
    ctx.setLineDash([]);
    // keeper zones (20 m from goal centre), tinted by defending team
    for (const ti of [0, 1]) {
      const gx = e.ownGoalX(ti);
      const a0 = gx < 0 ? -Math.PI / 2 : Math.PI / 2, a1 = gx < 0 ? Math.PI / 2 : Math.PI * 1.5;
      ctx.save(); ctx.globalAlpha = 0.16; ctx.beginPath();
      for (let i = 0; i <= 40; i++) { const a = a0 + (a1 - a0) * i / 40; const [sx, sy] = this.P(gx + Math.cos(a) * C.KEEPER_ZONE_R, Math.sin(a) * C.KEEPER_ZONE_R); i ? ctx.lineTo(sx, sy) : ctx.moveTo(sx, sy); }
      ctx.closePath(); ctx.fillStyle = cols[ti].primary; ctx.fill(); ctx.restore();
      this.groundCircle(gx, 0, C.KEEPER_ZONE_R, a0, a1, 'rgba(255,255,255,0.75)', 2);
    }
    // logos at centre
    const l0 = this.logos[cols[0].slug + '_128'];
    if (l0?.complete) { const [sx, sy] = this.P(0, 0); ctx.globalAlpha = 0.25; ctx.drawImage(l0, sx - 30, sy - 18, 60, 36 * (l0.height / l0.width) * 1.6); ctx.globalAlpha = 1; }

    // back goal/platform parts first, then entities depth-sorted, front parts last
    const drawGoal = (gx: number, ti: number) => {
      // ground shadow of goal mouth + net
      const pts: [number, number, number][] = [];
      for (let i = 0; i <= 24; i++) { const a = Math.PI * i / 24; pts.push([gx, -Math.cos(a) * C.GOAL_R, Math.sin(a) * C.GOAL_R]); }
      // net (quadrant side view, 3 m back)
      ctx.strokeStyle = 'rgba(255,255,255,0.35)'; ctx.lineWidth = 1;
      for (let i = 0; i <= 12; i++) {
        const a = Math.PI * i / 12, y = -Math.cos(a) * C.GOAL_R, z = Math.sin(a) * C.GOAL_R;
        const [x1, y1] = this.P(gx, y, z), [x2, y2] = this.P(gx + Math.sign(gx) * Math.max(0.2, z), y, 0);
        ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
      }
      ctx.strokeStyle = '#f2f2f2'; ctx.lineWidth = 4; ctx.beginPath();
      pts.forEach((p, i) => { const [sx, sy] = this.P(p[0], p[1], p[2]); i ? ctx.lineTo(sx, sy) : ctx.moveTo(sx, sy); }); ctx.stroke();
      ctx.strokeStyle = cols[ti].primary; ctx.lineWidth = 2; ctx.stroke();
    };
    const drawPlatform = (ti: number) => {
      const gx = e.ownGoalX(ti), px = gx + Math.sign(gx) * C.PLATFORM_BACK, h = C.PLATFORM_H;
      const w = 1.6;
      this.poly([[px - w, -w, h], [px + w, -w, h], [px + w, w, h], [px - w, w, h]], cols[ti].primary, '#fff', 1.5);
      this.poly([[px - w, w, 0], [px + w, w, 0], [px + w, w, h], [px - w, w, h]], 'rgba(40,40,50,0.9)', '#777', 1);
      for (const yy of [-w, w]) { const [a1, b1] = this.P(px - w, yy, 0), [a2, b2] = this.P(px - w, yy, h); ctx.strokeStyle = '#999'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(a1, b1); ctx.lineTo(a2, b2); ctx.stroke(); }
    };
    drawPlatform(0); drawPlatform(1);

    type Item = { y: number; f: () => void };
    const items: Item[] = [];
    items.push({ y: 0.01, f: () => drawGoal(-F, e.ownGoalX(0) === -F ? 0 : 1) });
    items.push({ y: 0.02, f: () => drawGoal(F, e.ownGoalX(0) === F ? 0 : 1) });
    for (const a of e.ath) {
      if (!e.active(a)) continue;
      items.push({ y: a.role === 'archer' ? 1.7 : a.y, f: () => {
        const col = cols[a.team];
        const [sx, sy] = this.P(a.x, a.y, a.role === 'archer' ? C.PLATFORM_H : 0);
        // shadow
        if (a.role !== 'archer') { ctx.fillStyle = 'rgba(0,0,0,0.32)'; ctx.beginPath(); ctx.ellipse(sx, sy, this.cam.s * 0.45, this.cam.s * 0.2, 0, 0, 7); ctx.fill(); }
        if (selected.includes(a.idx)) {
          ctx.strokeStyle = a.team === 0 ? '#ffe14d' : '#4dd2ff'; ctx.lineWidth = 2.5;
          ctx.beginPath(); ctx.ellipse(sx, sy, this.cam.s * 0.75, this.cam.s * 0.36, 0, 0, 7); ctx.stroke();
        }
        if (e.ball.holder === a.idx) { ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.5; ctx.setLineDash([3, 3]); ctx.beginPath(); ctx.ellipse(sx, sy, this.cam.s * 0.95, this.cam.s * 0.46, 0, 0, 7); ctx.stroke(); ctx.setLineDash([]); }
        const facingLeft = Math.cos(a.facing) < -0.05;
        drawAthlete(ctx, a, col, sx, sy, this.cam.s, { anim: animFor(a, e.ball.holder === a.idx), t: wallT + a.idx * 0.37, speed: 0, facingLeft });
        if (selected.includes(a.idx) || e.ball.holder === a.idx) {
          ctx.font = 'bold 11px Arial'; ctx.textAlign = 'center'; ctx.fillStyle = '#000a'; const label = `${a.d.jersey} ${a.d.name.split(' ').slice(-1)[0]} · ${a.d.pos}`;
          const tw = ctx.measureText(label).width; ctx.fillRect(sx - tw / 2 - 3, sy - this.cam.s * 2.45 - 11, tw + 6, 14);
          ctx.fillStyle = '#fff'; ctx.fillText(label, sx, sy - this.cam.s * 2.45);
        }
      } });
    }
    const b = e.ball;
    items.push({ y: b.holder >= 0 ? e.ath[b.holder].y + 0.05 : b.y, f: () => {
      const [gx, gy] = this.P(b.x, b.y, 0); const [bx, by] = this.P(b.x, b.y, b.z);
      const speed = Math.sqrt(b.vx * b.vx + b.vy * b.vy + b.vz * b.vz);
      const flying = b.holder < 0 && speed > 7;
      // motion trail (visual only)
      if (flying) { this.trail.push([b.x, b.y, b.z]); if (this.trail.length > 9) this.trail.shift(); } else this.trail.length = 0;
      if (this.trail.length > 1) {
        for (let i = 1; i < this.trail.length; i++) {
          const [x0, y0] = this.P(this.trail[i - 1][0], this.trail[i - 1][1], this.trail[i - 1][2]); const [x1, y1] = this.P(this.trail[i][0], this.trail[i][1], this.trail[i][2]);
          ctx.strokeStyle = `rgba(255,244,214,${(i / this.trail.length) * 0.55})`; ctx.lineWidth = Math.max(1.5, this.cam.s * 0.22 * (i / this.trail.length)); ctx.lineCap = 'round';
          ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
        }
        ctx.lineCap = 'butt';
      }
      ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.beginPath(); ctx.ellipse(gx, gy, this.cam.s * 0.2, this.cam.s * 0.09, 0, 0, 7); ctx.fill();
      // round ball; seams rotate with the flight to show spin
      const r = Math.max(4, this.cam.s * 0.2);
      const rot = flying ? wallT * 26 + b.x * 0.7 : 0.6;
      ctx.save(); ctx.translate(bx, by);
      ctx.fillStyle = '#f2e6c9'; ctx.strokeStyle = '#6b3d14'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); ctx.fill(); ctx.stroke();
      ctx.save(); ctx.beginPath(); ctx.arc(0, 0, r - 0.5, 0, 7); ctx.clip(); ctx.rotate(rot);
      ctx.strokeStyle = '#6b3d14'; ctx.lineWidth = Math.max(1, r * 0.16);
      ctx.beginPath(); ctx.moveTo(-r, 0); ctx.lineTo(r, 0); ctx.stroke();                         // seam
      ctx.beginPath(); ctx.ellipse(0, 0, r * 0.45, r * 1.05, 0, 0, 7); ctx.stroke();               // curved seam
      ctx.restore(); ctx.restore();
    } });
    items.sort((p, q) => p.y - q.y);
    for (const it of items) it.f();
    // arrows: fast tracers
    for (const ar of e.arrows) {
      const [x1, y1] = this.P(ar.x, ar.y, ar.z), [x0, y0] = this.P(ar.x - ar.vx * 0.06, ar.y - ar.vy * 0.06, ar.z - ar.vz * 0.06);
      ctx.strokeStyle = ar.team === 0 ? '#ffe14d' : '#4dd2ff'; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
      if (ar.resolved) { ctx.fillStyle = '#fff8'; ctx.beginPath(); ctx.arc(x1, y1, 6, 0, 7); ctx.fill(); }
    }
  }
}

export function fmtClock(t: number) { t = Math.max(0, t); const m = Math.floor(t / 60), s = Math.floor(t % 60); return `${m}:${s.toString().padStart(2, '0')}`; }
export { roundRect };
