# HP-002: PyPy trial, one full match (Claude, 25 Nov 2026)

Match: RB-3.32 combined, Garvian Guardians vs Ala Apex, seed 1, PLANNED rotation (gate h), code at 33c932b,
ratings 0.4 workbook (SHA-256 47b48af7...). Run in this sandbox, one process each, same machine.

| Runtime | Score | Gate h hashes | CPU-s | Steps |
|---|---|---|---|---|
| CPython 3.13.18, numpy 2.5.3 | 99-74 | match | 170.6 | 32,830 |
| PyPy 7.3.15 (Python 3.9), numpy 2.0.2 | 82-119 | differ | 306.4 | 31,838 |

- The only PyPy reachable here is the 3.9 build; the code needs 3.10 syntax, so the PyPy copy got
  `from __future__ import annotations` in every module (annotations only, no behaviour change).
- PyPy was 1.8x SLOWER. Likely cause: numpy (native/perception.py line-of-sight) runs through PyPy's slow C-extension bridge. Not profiled.
- PyPy played a different game. Unverified candidate causes: CPython 3.12+ float sum() is compensated
  (Neumaier) while 3.9 is not; numpy version; libm differences. Determinism is therefore tied to the
  runtime and Python version: pin both, and judge any port by statistics, not hashes.
- Conclusion: PyPy is not a speed path for this code as it stands. Profile CPython instead.
