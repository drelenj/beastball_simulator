# Discovery inventory (first five minutes)

- Workspace `/workspace`: no valid Git checkout; `.git` and `.agents` were empty read-only mount directories. No uncommitted project files existed to preserve.
- Authenticated GitHub identified the private `drelenj/beastball_simulator` repository. Restored a normal clone to `/workspace/beastball_simulator`, inspected clean working tree, all 20 remote branches and the one baseline commit on main, then created `feat/ndagii-beastball-arcade` from `2abe497ca82588cb2d8c871a7aab61daaae95c12`.
- Main: Pocket 4 Python runtime, embedded Pocket 2 engine, PRISM field/Keeper/Archer/perception modules, experimental locomotion solvers and numerous existing tests. One HTML maneuver lab, no browser match framework or package.json. All original tracked files retained unchanged.
- Read `RULES_FLOW_v0.2.md`, `RULES_FLOW_v0.3.md`, `ARCHER_NOTES.md`, `PRISM_I_INSTALL_NOTES.md`, Pocket 4 entry point, and Pocket original goal/arrow/recovery implementation. Later v0.3 flat scoring and per-possession ammunition are experimental alternatives; selected v1.0 5/3 + requested quarter quiver for the arcade.
- Available MBL CSV sources: Ala Lady Reds and Xenar Dzaku. Kept separate; NBL addendum supplies the canonical initial league. No MBL names mixed into NBL franchises.
- Other accessible owner repository: `drelenj/Beast`, size 0. No supporting assets available there.
- Supplied NBL workbook: 26 franchises, 712 rows, exactly 12 projected starters per franchise, all required source fields. Cross-check exposed 674 rating differences; primary sheet preserved as directed.
- Authenticated official Drive folder: 26 PNGs. Twenty mapped by unique team names after diacritic normalization. One explicit Priya spelling discrepancy and five opaque/ambiguous filenames remain unmapped.
- Browser infrastructure available: Node 24, npm, Python/openpyxl/Pillow, system Chromium, Playwright. Chose TypeScript/Vite with native Canvas for an isolated static frontend. No external gameplay libraries imported.
