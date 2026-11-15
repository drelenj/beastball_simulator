// Procedural athlete sprites (original art, no image assets). Shared body "sheets" are
// parameterised: 3 builds x 4 skin tones x 4 hair options x 4 face options, tinted with
// team colours and numbered at runtime. All athletes are Black men (NBL is the men's league).
import type { Athlete, TeamColors } from './engine/types';

export const SKIN = ['#4a2e1f', '#603b27', '#7d4f33', '#9a6544'];
const SKIN_SH = ['#3a2318', '#4c2e1e', '#653f28', '#7e5236'];
const HAIR = '#15100d';
const BUILD_W = [0.42, 0.5, 0.6];

export function lighten(hex: string, k: number) {
  const n = parseInt(hex.slice(1), 16);
  let r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
  r = Math.round(r + (255 - r) * k); g = Math.round(g + (255 - g) * k); b = Math.round(b + (255 - b) * k);
  return `rgb(${r},${g},${b})`;
}
export function darken(hex: string, k: number) {
  const n = parseInt(hex.slice(1), 16);
  const r = Math.round(((n >> 16) & 255) * (1 - k)), g = Math.round(((n >> 8) & 255) * (1 - k)), b = Math.round((n & 255) * (1 - k));
  return `rgb(${r},${g},${b})`;
}

export interface Pose { anim: string; t: number; speed: number; facingLeft: boolean }

/** Draw athlete with feet at (sx, sy). s = pixels per metre. */
export function drawAthlete(ctx: CanvasRenderingContext2D, a: Athlete, col: TeamColors, sx: number, sy: number, s: number, pose: Pose) {
  const L = a.look;
  const H = 1.86 * L.height * s;           // standing height px
  const bw = BUILD_W[L.build] * s * (a.role === 'archer' ? 0.92 : 1);
  const skin = SKIN[L.skin], skinSh = SKIN_SH[L.skin];
  const keeper = a.role === 'keeper', archer = a.role === 'archer';
  const jersey = keeper ? col.accent : archer ? lighten(col.primary, 0.45) : col.primary;
  const trim = keeper ? col.primary : col.secondary;
  const shorts = keeper ? darken(col.accent, 0.35) : darken(col.primary, 0.35);
  const anim = pose.anim;
  const t = pose.t;
  ctx.save();
  ctx.translate(sx, sy);
  if (pose.facingLeft) ctx.scale(-1, 1);
  if (anim === 'tackled') { ctx.rotate(-Math.PI / 2 + 0.15); ctx.translate(-H * 0.05, -H * 0.12); }
  if (anim === 'tackle') ctx.rotate(0.55);
  const runAmp = anim === 'sprint' ? 0.9 : anim === 'run' ? 0.55 : 0;
  const ph = Math.sin(t * (anim === 'sprint' ? 15 : 11));
  const bob = anim === 'idle' ? Math.sin(t * 2.2) * s * 0.02 : Math.abs(ph) * s * 0.05 * runAmp;
  const jump = anim === 'celebrate' ? Math.abs(Math.sin(t * 6)) * s * 0.35 : 0;
  ctx.translate(0, -bob - jump);
  const lean = anim === 'sprint' ? 0.18 : anim === 'run' ? 0.08 : 0;
  // legs
  const hipY = -H * 0.48, legLen = H * 0.48;
  const leg = (sgn: number) => {
    const sw = sgn * ph * runAmp * 0.7;
    ctx.save(); ctx.translate(sgn * bw * 0.18, hipY); ctx.rotate(sw);
    ctx.fillStyle = skinSh; ctx.fillRect(-bw * 0.11, legLen * 0.35, bw * 0.22, legLen * 0.55);
    ctx.fillStyle = shorts; ctx.fillRect(-bw * 0.15, 0, bw * 0.3, legLen * 0.42);
    // thigh strike panel
    ctx.fillStyle = trim; ctx.fillRect(-bw * 0.1, legLen * 0.1, bw * 0.2, legLen * 0.18);
    ctx.fillStyle = '#111'; ctx.fillRect(-bw * 0.13, legLen * 0.88, bw * 0.3, legLen * 0.1); // shoe
    ctx.restore();
  };
  leg(-1); leg(1);
  ctx.save(); ctx.translate(0, hipY); ctx.rotate(lean);
  // torso
  const tH = H * 0.33;
  ctx.fillStyle = jersey;
  roundRect(ctx, -bw / 2, -tH, bw, tH, bw * 0.18); ctx.fill();
  // low-profile shoulder pads
  ctx.fillStyle = darken(jersey.startsWith('#') ? jersey : col.primary, 0.15);
  roundRect(ctx, -bw * 0.58, -tH * 1.02, bw * 1.16, tH * 0.2, tH * 0.1); ctx.fill();
  ctx.fillStyle = trim; ctx.fillRect(-bw / 2, -tH * 0.18, bw, tH * 0.07);
  if (keeper) { ctx.fillStyle = col.primary; ctx.fillRect(-bw / 2, -tH * 0.7, bw, tH * 0.08); }
  // torso strike panel + number
  const fs = Math.max(7, Math.round(tH * 0.46));
  ctx.fillStyle = col.number; ctx.globalAlpha = 0.18; ctx.fillRect(-bw * 0.36, -tH * 0.84, bw * 0.72, tH * 0.56); ctx.globalAlpha = 1;
  ctx.save(); if (pose.facingLeft) ctx.scale(-1, 1);
  ctx.font = `900 ${fs}px Arial Black, Arial, sans-serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.lineWidth = Math.max(1.5, fs * 0.16); ctx.strokeStyle = darken(col.number === '#ffffff' ? '#202020' : col.primary, 0.3);
  ctx.strokeText(String(a.d.jersey), 0, -tH * 0.55); ctx.fillStyle = col.number; ctx.fillText(String(a.d.jersey), 0, -tH * 0.55);
  ctx.restore();
  // arms
  const arm = (sgn: number) => {
    let ang = sgn * -ph * runAmp * 0.8;
    if (anim === 'throw') ang = sgn > 0 ? -2.6 + t * 6 : 0.4;
    if (anim === 'catch') ang = -1.3;
    if (anim === 'celebrate') ang = -2.8 + sgn * 0.3;
    if (anim === 'tackle') ang = -1.5;
    if (anim === 'frozen') ang = 0.25 * sgn;
    if (archer && anim !== 'celebrate') ang = sgn > 0 ? -1.45 : -1.6;
    ctx.save(); ctx.translate(sgn * bw * 0.5, -tH * 0.9); ctx.rotate(ang);
    ctx.fillStyle = jersey; ctx.fillRect(-bw * 0.1, 0, bw * 0.2, tH * 0.28);
    ctx.fillStyle = skin; ctx.fillRect(-bw * 0.08, tH * 0.26, bw * 0.16, tH * 0.55);
    ctx.fillStyle = keeper ? col.secondary : skinSh; ctx.beginPath(); ctx.arc(0, tH * 0.86, bw * (keeper ? 0.13 : 0.09), 0, 7); ctx.fill();
    ctx.restore();
  };
  arm(-1);
  if (archer) { // bow
    ctx.strokeStyle = '#d9c7a0'; ctx.lineWidth = Math.max(1.2, s * 0.05);
    ctx.beginPath(); ctx.arc(bw * 0.9 + tH * 0.75, -tH * 0.95, tH * 0.55, -1.2, 1.2); ctx.stroke();
    ctx.strokeStyle = 'rgba(255,255,255,0.7)'; ctx.lineWidth = 0.8;
    ctx.beginPath(); ctx.moveTo(bw * 0.9 + tH * 0.95, -tH * 1.45); ctx.lineTo(bw * 0.9 + tH * 0.95, -tH * 0.45); ctx.stroke();
  }
  // head + helmet
  const hr = H * 0.085;
  const hy = -tH - hr * 1.05;
  ctx.fillStyle = skinSh; ctx.fillRect(-hr * 0.35, -tH - hr * 0.3, hr * 0.7, hr * 0.4); // neck
  // hair under/beside helmet
  ctx.fillStyle = HAIR; ctx.strokeStyle = HAIR;
  if (L.hair === 2) { // locs down the back
    ctx.lineWidth = Math.max(1.2, hr * 0.22);
    for (let i = 0; i < 4; i++) { ctx.beginPath(); ctx.moveTo(-hr * 0.7 + i * hr * 0.12, hy); ctx.quadraticCurveTo(-hr * 1.0 - i * 0.6, hy + hr * 1.2, -hr * 0.8 + i * hr * 0.15, hy + hr * 2.0); ctx.stroke(); }
  } else if (L.hair === 3) { // braids
    ctx.lineWidth = Math.max(0.8, hr * 0.12);
    for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.moveTo(-hr * 0.85 + i * hr * 0.1, hy + hr * 0.2); ctx.lineTo(-hr * 0.9 + i * hr * 0.1, hy + hr * 1.45); ctx.stroke(); }
  } else if (L.hair === 1) { // fade: short dark band at the nape
    ctx.fillRect(-hr * 0.95, hy + hr * 0.1, hr * 0.5, hr * 0.55);
  } else { ctx.fillRect(-hr * 0.95, hy + hr * 0.1, hr * 0.35, hr * 0.35); }
  ctx.fillStyle = skin; ctx.beginPath(); ctx.ellipse(hr * 0.08, hy + hr * 0.15, hr * 0.82, hr * 0.92, 0, 0, 7); ctx.fill();
  // face features (side view): eye, brow, nose, facial hair variants
  ctx.fillStyle = '#f4efe6'; ctx.beginPath(); ctx.arc(hr * 0.5, hy + hr * 0.05, hr * 0.13, 0, 7); ctx.fill();
  ctx.fillStyle = '#20140e'; ctx.beginPath(); ctx.arc(hr * 0.55, hy + hr * 0.05, hr * 0.07, 0, 7); ctx.fill();
  ctx.fillStyle = skinSh; ctx.beginPath(); ctx.moveTo(hr * 0.82, hy + hr * 0.1); ctx.lineTo(hr * 1.0, hy + hr * 0.38); ctx.lineTo(hr * 0.8, hy + hr * 0.42); ctx.fill();
  if (L.face === 1 || L.face === 3) { ctx.fillStyle = HAIR; ctx.globalAlpha = 0.85; ctx.beginPath(); ctx.ellipse(hr * 0.35, hy + hr * 0.75, hr * 0.5, hr * (L.face === 3 ? 0.32 : 0.2), 0, 0, 7); ctx.fill(); ctx.globalAlpha = 1; }
  if (L.face === 2) { ctx.fillStyle = HAIR; ctx.fillRect(hr * 0.55, hy + hr * 0.52, hr * 0.35, hr * 0.1); }
  // compact padded helmet (team secondary / keeper primary) with clear visor
  const helm = keeper ? col.primary : darken(col.secondary, 0.1);
  ctx.fillStyle = helm; ctx.beginPath(); ctx.ellipse(-hr * 0.05, hy - hr * 0.18, hr * 1.0, hr * 0.78, 0, Math.PI * 0.98, Math.PI * 2.08); ctx.fill();
  ctx.fillRect(-hr * 1.0, hy - hr * 0.25, hr * 0.55, hr * 0.75);
  ctx.fillStyle = 'rgba(190,230,255,0.38)'; ctx.strokeStyle = 'rgba(230,248,255,0.85)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.ellipse(hr * 0.55, hy + hr * 0.12, hr * 0.5, hr * 0.42, 0, -1.4, 1.4); ctx.fill(); ctx.stroke();
  // status lights: red (frozen) / amber (immune)
  const frozen = a.frozenT > 0 || a.recoverT > 0, immune = a.immuneT > 0;
  ctx.fillStyle = frozen ? '#ff2a2a' : '#3a1010'; ctx.beginPath(); ctx.arc(-hr * 0.35, hy - hr * 0.85, Math.max(1.4, hr * 0.17), 0, 7); ctx.fill();
  ctx.fillStyle = immune ? '#ffb000' : '#3a2a08'; ctx.beginPath(); ctx.arc(hr * 0.05, hy - hr * 0.92, Math.max(1.4, hr * 0.17), 0, 7); ctx.fill();
  if (frozen && a.frozenT > 0) { ctx.shadowColor = '#ff2a2a'; ctx.shadowBlur = 8; ctx.fillStyle = '#ff2a2a'; ctx.beginPath(); ctx.arc(-hr * 0.35, hy - hr * 0.85, hr * 0.17, 0, 7); ctx.fill(); ctx.shadowBlur = 0; }
  if (immune) { ctx.shadowColor = '#ffb000'; ctx.shadowBlur = 8; ctx.fillStyle = '#ffb000'; ctx.beginPath(); ctx.arc(hr * 0.05, hy - hr * 0.92, hr * 0.17, 0, 7); ctx.fill(); ctx.shadowBlur = 0; }
  arm(1);
  ctx.restore();
  if (a.frozenT > 0) { // ice tint
    ctx.fillStyle = 'rgba(170,220,255,0.35)'; roundRect(ctx, -bw * 0.75, -H * 1.02, bw * 1.5, H * 1.02, 6); ctx.fill();
  }
  ctx.restore();
}

export function roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}

export function animFor(a: Athlete, holder: boolean): string {
  if (a.groundedT > 0) return 'tackled';
  if (a.frozenT > 0) return 'frozen';
  if (a.celebrateT > 0) return 'celebrate';
  if (a.act === 'tackle') return 'tackle';
  if (a.act === 'throw') return 'throw';
  if (a.act === 'catch') return 'catch';
  const sp = Math.hypot(a.vx, a.vy);
  if (sp > a.a.top * 0.78) return 'sprint';
  if (sp > 0.8) return 'run';
  return holder ? 'idle' : 'idle';
}
