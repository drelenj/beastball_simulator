# BEASTBALL: ARCADE (Claude Code build)

Browser-playable 2.5D arcade Beastball. TypeScript + Vite + Canvas 2D, no backend, no paid assets.

```
cd arcade_claude
npm install && npm run dev          # http://localhost:5173
npm run build && npm run preview    # static build in dist/
npx tsx scripts/headless.ts "Ala Marauders" "Xenar Ignite" 20261115 flat   # fast headless full match
node tests/browser_check.cjs        # Playwright acceptance checks (dev server must be running)
```

* `src/engine/` — authoritative engine (fixed 60 Hz steps, seeded RNG, no rendering), AI controller, rules.
* `src/render.ts`, `src/sprites.ts` — oblique 2.5D renderer and procedural athlete sprites.
* `src/main.ts` — screens, HumanController (keyboard/gamepad), spectator controls, HUD.
* `data/rosters.json` — exported from the canon workbook by `scripts/export_rosters.py`.
* `data/team_colors.json`, `data/logos_manifest.json`, `assets/logos/` — produced by `scripts/extract_logos.py`.

This is a separate TypeScript arcade implementation of the canon (Rulebook 1.0), not the Python
simulator. Arcade results are not simulator evidence. See `REPORT.md`.

Re-running the logo extraction: put the original Drive PNGs (names unchanged) in
`arcade_claude/assets/logos_raw/` (git-ignored) or `arcade_claude/.scratch/logos_src/`, then
`python3 -I scripts/extract_logos.py`.
