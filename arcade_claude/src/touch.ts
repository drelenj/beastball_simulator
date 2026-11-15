// Touch input for phones/tablets: floating joystick (left thumb) + action buttons (right thumb).
// Produces the same signals as keyboard/gamepad; HumanController merges them. Multi-touch safe
// (each control tracks its own pointer id).
export const touch = {
  enabled: false,
  mx: 0, my: 0, stickSprint: false, sprintBtn: false,
  // edge-triggered actions, consumed once per frame by main.ts
  pass: false, tackle: false, shoot: false, sw: false, fire: false,
};

const R = 58; // stick radius in CSS px
const DEAD = 0.12;
const SPRINT_AT = 0.92;

export function consumeTouchEdges() { touch.pass = touch.tackle = touch.shoot = touch.sw = touch.fire = false; }

export function detectTouch(forced: boolean) {
  return forced || (window.matchMedia && window.matchMedia('(pointer: coarse)').matches);
}

export function initTouch(opts: { onPause: () => void; onFirstTouch: () => void }) {
  const zone = document.getElementById('tzone')!;
  const stick = document.getElementById('stick')!;
  const knob = document.getElementById('knob')!;
  const home = () => ({ x: 96, y: window.innerHeight - 100 });
  const placeStick = (x: number, y: number) => { stick.style.left = x + 'px'; stick.style.top = y + 'px'; };
  const resetKnob = () => { knob.style.transform = 'translate(0,0)'; stick.classList.remove('on', 'sprint'); };
  const parkStick = () => { const h = home(); placeStick(h.x, h.y); };
  parkStick(); window.addEventListener('resize', () => { if (!stickId.active) parkStick(); });

  const stickId = { active: false, id: -1, cx: 0, cy: 0 };
  const move = (px: number, py: number) => {
    let dx = px - stickId.cx, dy = py - stickId.cy;
    const len = Math.hypot(dx, dy);
    if (len > R) { // drag the base along so the thumb never leaves the stick
      const k = (len - R) / len; stickId.cx += dx * k; stickId.cy += dy * k; placeStick(stickId.cx, stickId.cy);
      dx = px - stickId.cx; dy = py - stickId.cy;
    }
    const l = Math.min(R, Math.hypot(dx, dy)); const m = l / R;
    const ang = Math.atan2(dy, dx);
    knob.style.transform = `translate(${Math.cos(ang) * l}px, ${Math.sin(ang) * l}px)`;
    if (m < DEAD) { touch.mx = touch.my = 0; touch.stickSprint = false; }
    else { const mm = (m - DEAD) / (1 - DEAD); touch.mx = Math.cos(ang) * Math.min(1, mm * 1.15); touch.my = Math.sin(ang) * Math.min(1, mm * 1.15); touch.stickSprint = m >= SPRINT_AT; }
    stick.classList.toggle('sprint', touch.stickSprint);
  };
  const release = () => { stickId.active = false; stickId.id = -1; touch.mx = touch.my = 0; touch.stickSprint = false; resetKnob(); parkStick(); };

  zone.addEventListener('pointerdown', (ev) => {
    if (stickId.active) return;
    opts.onFirstTouch();
    stickId.active = true; stickId.id = ev.pointerId; zone.setPointerCapture(ev.pointerId);
    stickId.cx = Math.max(R, Math.min(window.innerWidth * 0.5, ev.clientX)); stickId.cy = Math.max(R, Math.min(window.innerHeight - R, ev.clientY));
    placeStick(stickId.cx, stickId.cy); stick.classList.add('on'); move(ev.clientX, ev.clientY); ev.preventDefault();
  });
  zone.addEventListener('pointermove', (ev) => { if (stickId.active && ev.pointerId === stickId.id) { move(ev.clientX, ev.clientY); ev.preventDefault(); } });
  for (const t of ['pointerup', 'pointercancel', 'lostpointercapture'] as const) zone.addEventListener(t, (ev) => { if (stickId.active && ev.pointerId === stickId.id) release(); });

  document.querySelectorAll<HTMLElement>('#touch .tb').forEach((b) => {
    const key = b.dataset.t as 'pass' | 'tackle' | 'shoot' | 'sw' | 'fire' | 'sprint';
    let pid = -1;
    b.addEventListener('pointerdown', (ev) => {
      if (pid >= 0) return;
      opts.onFirstTouch();
      pid = ev.pointerId; b.setPointerCapture(ev.pointerId); b.classList.add('down'); ev.preventDefault();
      if (key === 'sprint') touch.sprintBtn = true; else touch[key] = true;
      if ((navigator as any).vibrate) (navigator as any).vibrate(8);
    });
    const up = (ev: PointerEvent) => { if (ev.pointerId !== pid) return; pid = -1; b.classList.remove('down'); if (key === 'sprint') touch.sprintBtn = false; };
    for (const t of ['pointerup', 'pointercancel', 'lostpointercapture'] as const) b.addEventListener(t, up);
    b.addEventListener('contextmenu', (ev) => ev.preventDefault());
  });
  document.getElementById('tPause')!.addEventListener('pointerdown', (ev) => { ev.preventDefault(); opts.onPause(); });

  // iOS Safari: block pinch / double-tap zoom and rubber-banding while playing
  for (const t of ['gesturestart', 'gesturechange', 'gestureend']) document.addEventListener(t, (e) => e.preventDefault());
  // (screens such as the final stats must still scroll, so only block when no screen is open)
  document.addEventListener('touchmove', (e) => { if (document.body.classList.contains('playing') && !document.querySelector('.screen.on')) e.preventDefault(); }, { passive: false });
  document.addEventListener('contextmenu', (e) => { if (document.body.classList.contains('playing')) e.preventDefault(); });
}
