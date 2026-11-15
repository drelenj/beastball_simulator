import { Engine, Athlete, Side, DT, clamp } from './engine';

export class Renderer {
  canvas: HTMLCanvasElement; ctx: CanvasRenderingContext2D; width = 0; height = 0;
  focus = { x: 50, y: 50 }; scale = 8; wide = false;
  constructor(canvas: HTMLCanvasElement) { this.canvas = canvas; this.ctx = canvas.getContext('2d')!; }
  resize() {
    const rect = this.canvas.getBoundingClientRect(), dpr = Math.min(2, window.devicePixelRatio || 1);
    if (this.width !== rect.width || this.height !== rect.height) {
      this.width = rect.width; this.height = rect.height;
      this.canvas.width = Math.round(rect.width * dpr); this.canvas.height = Math.round(rect.height * dpr);
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
  }
  project(x: number, y: number, z = 0) {
    return { x: this.width * .5 + ((x - this.focus.x) + (y - this.focus.y) * .23) * this.scale,
      y: this.height * .54 + (y - this.focus.y) * this.scale * .57 - z * this.scale * .9 };
  }
  path(points: number[][], fill?: string, stroke?: string, width = 1) {
    const c = this.ctx; c.beginPath();
    points.forEach(([x, y, z], i) => { const p = this.project(x, y, z); if (!i) c.moveTo(p.x, p.y); else c.lineTo(p.x, p.y); });
    if (fill) { c.closePath(); c.fillStyle = fill; c.fill(); }
    if (stroke) { c.strokeStyle = stroke; c.lineWidth = width; c.stroke(); }
  }
  rect(x: number, y: number, w: number, h: number, fill: string, stroke?: string) { this.path([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], fill, stroke); }
  circle(x: number, y: number, r: number, fill?: string, stroke?: string, width = 1) {
    this.path(Array.from({ length: 65 }, (_, i) => [x + Math.cos(i * Math.PI / 32) * r, y + Math.sin(i * Math.PI / 32) * r]), fill, stroke, width);
  }
  label(text: string, x: number, y: number, color: string, font = 'bold 10px monospace', z = 0) {
    const p = this.project(x, y, z), c = this.ctx; c.font = font; c.textAlign = 'center';
    c.lineWidth = 3; c.strokeStyle = '#0a1a20'; c.strokeText(text, p.x, p.y); c.fillStyle = color; c.fillText(text, p.x, p.y);
  }
  draw(e: Engine, elapsed: number, menu = false) {
    this.resize(); const c = this.ctx;
    const wide = menu || this.wide;
    const tx = wide ? 50 : 50 + (e.ball.x - 50) * .52, ty = wide ? 50 : 50 + (e.ball.y - 50) * .32;
    const smooth = Math.min(1, elapsed * 4);
    this.focus.x += (tx - this.focus.x) * smooth; this.focus.y += (ty - this.focus.y) * smooth;
    const desiredScale = Math.min(this.width / (wide ? 139 : 108), this.height / (wide ? 83 : 70));
    this.scale += (desiredScale - this.scale) * Math.min(1, elapsed * 3);
    c.clearRect(0, 0, this.width, this.height);
    const bg = c.createLinearGradient(0, 0, 0, this.height); bg.addColorStop(0, '#102230'); bg.addColorStop(1, '#0a151b');
    c.fillStyle = bg; c.fillRect(0, 0, this.width, this.height);
    this.stadium(e);
    this.rect(-3, -4, 106, 108, '#173d3c');
    this.rect(0, 0, 100, 100, '#28604b');
    for (let i = 0; i < 10; i++) this.rect(i * 10, 0, 10, 100, i % 2 ? '#2b624c' : '#285b48');
    // Fine pitch texture is stable, independent of simulation or global randomness.
    c.globalAlpha = .08;
    for (let i = 0; i < 100; i++) this.path([[i, 0], [i, 100]], undefined, '#cbe3a6');
    c.globalAlpha = 1;
    const white = '#d7e2c9';
    this.path([[0, 0], [100, 0], [100, 100], [0, 100], [0, 0]], undefined, white, 2);
    this.path([[50, 0], [50, 100]], undefined, '#c1d8b9aa', 1.5);
    this.circle(50, 50, 8, undefined, white, 1.5); this.circle(50, 50, .45, white);
    for (const x of [0, 100]) {
      const side = e.ownGoal(0) === x ? 0 : 1;
      const color = side === 0 ? e.settings.home.color : e.settings.away.color;
      const arc = (r: number) => Array.from({ length: 49 }, (_, i) => { const t = -Math.PI / 2 + i * Math.PI / 48; return [x + (x === 0 ? 1 : -1) * Math.cos(t) * r, 50 + Math.sin(t) * r]; });
      this.path(arc(20), color + '22', '#dbe3ccaa', 1.5);
      this.path(arc(6), color + '55', '#f3e2a0', 2);
      this.circle(x === 0 ? 25 : 75, 50, .65, '#f1d99c');
      this.label('25', x === 0 ? 25 : 75, 53.7, '#d6d9b3', `bold ${Math.max(8, this.scale)}px monospace`);
      this.label('KEEPER ZONE', x === 0 ? 11 : 89, 72.8, '#e1e4c68a', `bold ${Math.max(7, this.scale * .78)}px monospace`);
    }
    // Two assigned Archer lanes beyond the playing boundaries.
    for (const side of [0, 1] as Side[]) {
      const y = side === 0 ? -9 : 104, team = side === 0 ? e.settings.home : e.settings.away;
      this.rect(0, y, 100, 5, team.color + '35', team.color + '77');
      for (let x = 0; x < 100; x += 4) this.path([[x, y], [x + 2, y + 5]], undefined, team.color + '44');
      this.label('A R C H E R   L A N E', 50, y + 3.5, '#e2ddca', `bold ${Math.max(8, this.scale * .85)}px monospace`);
    }
    this.goalStructure(0); this.goalStructure(100);
    this.label('N D A G Ï', 50, 29, '#d0dab526', `900 ${this.scale * 3.4}px sans-serif`);
    this.label('B E A S T B A L L', 50, 77, '#d0dab535', `900 ${this.scale * 1.75}px sans-serif`);
    if (e.recovery) this.circle(e.recovery.x, e.recovery.y, 3, '#e9c67a22', '#f5db86', 2);
    const selected = e.players[e.selected];
    const target = e.carrier;
    if (e.settings.mode === 'human' && target && target.side === 1 && target.immune <= 0) {
      this.circle(target.x, target.y, 2.6, undefined, '#ffd36f88', 1);
    }
    [...e.players].sort((a, b) => a.y - b.y || a.x - b.x).forEach(p => this.athlete(e, p, p === selected && e.settings.mode === 'human'));
    for (const a of e.arrows) {
      this.path([[a.x - a.vx * .065, a.y - a.vy * .065, a.z], [a.x, a.y, a.z]], undefined, '#ffd776', 2.5);
      const pt = this.project(a.x, a.y, a.z); c.fillStyle = '#fff4c5'; c.beginPath(); c.arc(pt.x, pt.y, 2, 0, Math.PI * 2); c.fill();
    }
    if (e.ball.carrier === null) {
      const p = this.project(e.ball.x, e.ball.y), b = this.project(e.ball.x, e.ball.y, e.ball.z);
      c.fillStyle = '#07150f70'; c.beginPath(); c.ellipse(p.x, p.y, this.scale * .7, this.scale * .29, 0, 0, Math.PI * 2); c.fill();
      c.shadowColor = '#ffdb7c'; c.shadowBlur = 12; c.fillStyle = '#ffe2a0'; c.beginPath(); c.ellipse(b.x, b.y, Math.max(3.5, this.scale * .45), Math.max(2.6, this.scale * .3), -.4, 0, Math.PI * 2); c.fill(); c.shadowBlur = 0;
      c.strokeStyle = '#7b5223'; c.lineWidth = 1; c.beginPath(); c.moveTo(b.x - 2, b.y); c.lineTo(b.x + 2, b.y); c.stroke();
    }
    this.effects(e);
    if (!menu) this.minimap(e);
    const vignette = c.createRadialGradient(this.width * .5, this.height * .5, this.height * .2, this.width * .5, this.height * .5, this.width * .65);
    vignette.addColorStop(0, '#050b1000'); vignette.addColorStop(1, '#050b1055'); c.fillStyle = vignette; c.fillRect(0, 0, this.width, this.height);
  }
  stadium(e: Engine) {
    this.rect(-16, -25, 132, 150, '#101e29');
    for (const top of [-24, 112]) {
      this.rect(-12, top, 124, 12, '#192b38');
      for (let row = 0; row < 5; row++) for (let seat = 0; seat < 106; seat++) {
        const h = (seat * 31 + row * 97) % 13;
        this.rect(-8 + seat * 1.1, top + row * 2, .55, .8, ['#a69362', '#5c7c8b', '#d0ae8a', '#426963', e.settings.home.color, e.settings.away.color][h % 6] + (h < 5 ? 'bb' : '66'));
      }
    }
    this.rect(-8, -14, 116, 2, '#e3c784'); this.rect(-8, 111, 116, 2, '#c9d0b5');
    this.label('NBL  /  OPENING NIGHT 2026–27', 50, -12.5, '#14242a', `bold ${this.scale * 1.1}px monospace`);
    this.label('12 ATHLETES.  ONE HUNT.', 50, 112.5, '#14242a', `bold ${this.scale * 1.1}px monospace`);
    for (const x of [-9, 109]) {
      this.rect(x, -7, 3, 114, '#1b3038');
      for (let i = 0; i < 14; i++) this.rect(x + .4, i * 8, 2.2, 5, i % 2 ? e.settings.home.color + '88' : e.settings.away.color + '88');
    }
  }
  goalStructure(x: number) {
    const c = this.ctx, back = x === 0 ? -4 : 104;
    const arch = (xx: number) => Array.from({ length: 33 }, (_, i) => { const t = Math.PI * i / 32; return [xx, 50 + Math.cos(t) * 6, Math.sin(t) * 6]; });
    this.path(arch(back), undefined, '#86a6a766', 1.5);
    for (let i = 0; i <= 8; i++) {
      const t = Math.PI * i / 8, y = 50 + Math.cos(t) * 6, z = Math.sin(t) * 6;
      this.path([[x, y, z], [back, y, z]], undefined, '#c9dfd244', .8);
    }
    for (let i = 1; i < 4; i++) this.path(arch(x + (back - x) * i / 4), undefined, '#a1b7b233', .75);
    c.shadowColor = '#f3d798'; c.shadowBlur = 8;
    this.path(arch(x), undefined, '#f5e8b5', Math.max(2, this.scale * .22)); c.shadowBlur = 0;
  }
  athlete(e: Engine, p: Athlete, selected: boolean) {
    const c = this.ctx, pos = this.project(p.x, p.y), s = this.scale;
    const color = p.side === 0 ? e.settings.home.color : e.settings.away.color;
    const speed = Math.hypot(p.vx, p.vy), moving = speed > 1;
    const phase = e.tick * DT * (moving ? 18 : 2) + p.id * 1.6;
    const run = moving ? Math.sin(phase) : Math.sin(phase) * .1;
    const tall = p.role === 'keeper' ? 1.25 : 1;
    c.save(); c.translate(pos.x, pos.y);
    c.fillStyle = '#03171466'; c.beginPath(); c.ellipse(1, 1, s * 1.05, s * .4, -.08, 0, Math.PI * 2); c.fill();
    if (selected) {
      c.strokeStyle = '#a7ffe0'; c.lineWidth = 2.2; c.beginPath(); c.ellipse(0, 0, s * 1.3, s * .57, 0, 0, Math.PI * 2); c.stroke();
      c.fillStyle = '#a7ffe0'; c.beginPath(); c.moveTo(0, -s * 4.8); c.lineTo(-4, -s * 5.5); c.lineTo(4, -s * 5.5); c.fill();
    }
    if (p.id === e.ball.carrier) {
      c.strokeStyle = '#ffdb7c'; c.lineWidth = 1.5; c.beginPath(); c.ellipse(0, 1, s * 1.5, s * .68, 0, 0, Math.PI * 2); c.stroke();
    }
    if (p.down > 0) { c.rotate(-1.15); c.translate(s * .7, s * .1); }
    const bob = moving ? Math.abs(run) * s * .2 : 0;
    c.translate(0, -bob); c.scale(tall, tall);
    const skin = ['#b47e58', '#784e39', '#ce9e74', '#906247', '#573e33'][p.id % 5];
    c.lineCap = 'round'; c.lineJoin = 'round';
    // Running legs, socks and solid boots make the sprites read as athletes.
    for (const sign of [-1, 1]) {
      const legX = sign * s * .35, kneeX = legX + run * sign * s * .28;
      c.strokeStyle = '#142027'; c.lineWidth = s * .48; c.beginPath(); c.moveTo(legX, -s * 1.25); c.lineTo(kneeX, -s * .6); c.stroke();
      c.strokeStyle = '#eee5ce'; c.lineWidth = s * .28; c.beginPath(); c.moveTo(kneeX, -s * .55); c.lineTo(legX - run * sign * s * .4, -s * .1); c.stroke();
      c.fillStyle = '#111b22'; c.fillRect(legX - run * sign * s * .4 - s * .22, -s * .22, s * .55, s * .28);
    }
    c.fillStyle = '#101c24'; c.fillRect(-s * .65, -s * 1.55, s * 1.3, s * .5);
    c.fillStyle = color; c.strokeStyle = '#0d2026'; c.lineWidth = 1.3;
    c.beginPath(); c.moveTo(-s * .95, -s * 3); c.lineTo(s * .95, -s * 3); c.lineTo(s * .63, -s * 1.45); c.lineTo(-s * .63, -s * 1.45); c.closePath(); c.fill(); c.stroke();
    c.fillStyle = '#ffffff35'; c.fillRect(-s * .55, -s * 2.97, s * 1.1, s * .15);
    for (const sign of [-1, 1]) {
      const throwing = p.action === 'throw' && p.animation > 0;
      const tackling = p.action === 'tackle' && p.animation > 0;
      const handX = sign * s * (tackling ? 1.5 : 1) + (throwing ? s * .4 : run * sign * s * .3);
      const handY = -s * (throwing ? 3.8 : tackling ? 2.7 : 1.9 + run * sign * .3);
      c.strokeStyle = color; c.lineWidth = s * .42; c.beginPath(); c.moveTo(sign * s * .7, -s * 2.8); c.lineTo(handX, handY); c.stroke();
      c.fillStyle = skin; c.beginPath(); c.arc(handX, handY, s * .22, 0, Math.PI * 2); c.fill();
    }
    c.fillStyle = skin; c.beginPath(); c.arc(0, -s * 3.5, s * .57, 0, Math.PI * 2); c.fill();
    c.fillStyle = '#172028'; c.beginPath(); c.ellipse(0, -s * 3.76, s * .59, s * .34, 0, Math.PI, Math.PI * 2); c.fill();
    c.fillStyle = '#fff2da'; c.fillRect(-s * .37, -s * 3.56, s * .74, s * .12);
    c.font = `900 ${Math.max(7, s * 1.06)}px sans-serif`; c.textAlign = 'center'; c.fillStyle = '#fff7e3'; c.fillText(p.role === 'keeper' ? 'K' : p.role === 'archer' ? 'A' : String(p.bib), 0, -s * 2.04);
    if (p.role === 'archer') {
      c.strokeStyle = '#f2d49a'; c.lineWidth = 1.6; c.beginPath(); c.arc(s * 1.1, -s * 2.3, s * .9, -1.5, 1.5); c.stroke();
      c.strokeStyle = '#f1e0b999'; c.lineWidth = .7; c.beginPath(); c.moveTo(s * 1.16, -s * 3.2); c.lineTo(s * 1.16, -s * 1.4); c.stroke();
    }
    if (p.id === e.ball.carrier) {
      c.fillStyle = '#ffdf95'; c.strokeStyle = '#75522d'; c.lineWidth = .7; c.beginPath(); c.ellipse(s * .84, -s * 2.25, s * .44, s * .28, -.6, 0, Math.PI * 2); c.fill(); c.stroke();
    }
    if (p.freeze > 0) {
      c.fillStyle = '#8adeff66'; c.strokeStyle = '#a8f1ff'; c.lineWidth = 1.4;
      c.beginPath(); c.moveTo(-s * 1.1, 0); c.lineTo(-s * 1.5, -s * 2.5); c.lineTo(-s * .5, -s * 4.5); c.lineTo(s, -s * 4.2); c.lineTo(s * 1.4, -s * 1); c.lineTo(s * .9, 0); c.closePath(); c.fill(); c.stroke();
      c.fillStyle = '#e1fbff'; c.font = `bold ${s * 1.3}px monospace`; c.fillText('❄', 0, -s * 4.9);
    } else if (p.immune > 0 || p.protected > .5) {
      c.strokeStyle = p.protected > .5 ? '#efd88a99' : '#8adeff66'; c.lineWidth = 1; c.beginPath(); c.ellipse(0, -s * 2, s * 1.4, s * 2.3, 0, 0, Math.PI * 2); c.stroke();
    }
    c.restore();
    if (selected || p.id === e.ball.carrier || p.role !== 'field' || p.freeze > 0) {
      const name = p.data.Player.split(' ').slice(-1)[0];
      this.label(name.toUpperCase(), p.x, p.y + 2.7, p.freeze > 0 ? '#a5eeff' : '#fff6de', `bold ${Math.max(8, s * .91)}px monospace`);
      if (p.role === 'archer') {
        const q = e.quivers[p.side]; this.label(q.reload > 0 ? `RELOAD ${q.reload.toFixed(1)}s` : `${q.loaded} / ${20 - q.spent}`, p.x, p.y + 4.6, '#e8c77d', `bold ${Math.max(7, s * .8)}px monospace`);
      }
    }
  }
  effects(e: Engine) {
    const c = this.ctx;
    for (const event of e.events.slice(-18)) {
      const age = (e.tick - event.tick) * DT;
      if (age > 1.2 || event.player === null || !['tackle', 'freeze', 'save', 'goal'].includes(event.type)) continue;
      const p = e.players[event.player], pt = this.project(p.x, p.y, 4 + age * 3);
      c.globalAlpha = clamp(1 - age / 1.2, 0, 1); c.font = `900 ${Math.max(12, this.scale * 1.4)}px sans-serif`; c.textAlign = 'center';
      c.fillStyle = event.type === 'freeze' ? '#97e8ff' : '#ffdc83'; c.fillText(event.type === 'tackle' ? 'IMPACT!' : event.type === 'freeze' ? 'FROZEN!' : event.type === 'save' ? 'SAVED!' : `+${event.points}`, pt.x, pt.y);
      c.globalAlpha = 1;
    }
  }
  minimap(e: Engine) {
    if (this.width < 650) return;
    const c = this.ctx, w = 114, h = 84, x = this.width - w - 22, y = this.height - h - 20;
    c.fillStyle = '#08151ee8'; c.fillRect(x - 8, y - 19, w + 16, h + 27); c.strokeStyle = '#c5dbc035'; c.strokeRect(x, y, w, h);
    c.strokeStyle = '#c5dbc025'; c.beginPath(); c.moveTo(x + w / 2, y); c.lineTo(x + w / 2, y + h); c.stroke();
    c.font = '8px monospace'; c.textAlign = 'left'; c.fillStyle = '#99aca8'; c.fillText('LIVE FIELD / 100 × 100 m', x, y - 7);
    for (const p of e.players) {
      c.fillStyle = p.side === 0 ? e.settings.home.color : e.settings.away.color;
      c.beginPath(); c.arc(x + p.x / 100 * w, y + p.y / 100 * h, p.role === 'archer' ? 1.4 : 2, 0, Math.PI * 2); c.fill();
    }
    c.fillStyle = '#ffdf8c'; c.beginPath(); c.arc(x + e.ball.x / 100 * w, y + e.ball.y / 100 * h, 2.4, 0, Math.PI * 2); c.fill();
  }
}
