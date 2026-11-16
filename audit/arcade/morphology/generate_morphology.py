#!/usr/bin/env python3
"""Beastball morphology + ancestry roster generator.
Implements Ancestry Generation Guideline v1.0 and Morphology Generator v1.0 (both in this folder).
Deterministic: each athlete draws from random.Random(f"{MASTER_SEED}|{GEN_VERSION}|{player_id}"), so results do not depend on row order.
Locks (owner, 16 Nov 2026) fix the ANCESTRY tuple only; height and physique are still sampled from it.
Usage: python generate_morphology.py INPUT.xlsx OUTPUT.xlsx [--seed N]
"""
import re, sys, math, json, random, hashlib, argparse, collections
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill

GEN_VERSION = "morph-1.0/anc-1.0"
MASTER_SEED = 20261116
HERE = Path(__file__).parent
TRIBES = ["Ly’Kun", "Dryqona", "Yubu", "Shynän", "Psolari", "Vygari", "Fefmial"]
NORM = {"ly’kun": "Ly’Kun", "lykun": "Ly’Kun", "ly'kun": "Ly’Kun", "dryqona": "Dryqona", "yubu": "Yubu",
        "shynän": "Shynän", "shynan": "Shynän", "psolari": "Psolari", "vygari": "Vygari", "fefmial": "Fefmial"}
def tribe(s):
    k = s.strip().lower().replace("'", "’") if s.strip().lower() not in NORM else s.strip().lower()
    k = NORM.get(s.strip().lower(), NORM.get(k))
    if k is None: raise ValueError("unknown tribe " + s)
    return k

# Locks (owner): ancestry only. Matched by exact name; IDs verified at run time.
LOCKS = {
    "Miles Starlight": ("Ly’Kun",),
    "Kamasi Sinella": ("Ly’Kun", "Dryqona", "Shynän", "Yubu"),
    "Dante Sinella": ("Shynän", "Yubu"),
    "Damon Sinella": ("Shynän", "Yubu"),
}

def load_profiles():
    """Parse the 65 profiles from the Ancestry Guideline tables (sections 4-7). Weights are % of all players."""
    text = (HERE / "Beastball_Ancestry_Generation_Guideline_v1.0.md").read_text(encoding="utf-8")
    profs = []
    sec = None
    for line in text.splitlines():
        m = re.match(r"## (\d+)\.", line)
        if m: sec = int(m.group(1))
        if sec in (4, 5, 6, 7) and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 2 and cells[1].endswith("%") and not cells[0].startswith("**") and "Ancestry" not in cells[0] and "Tribe" not in cells[0]:
                combo = tuple(sorted((tribe(t) for t in cells[0].split("/")), key=TRIBES.index))
                profs.append((combo, float(cells[1].rstrip("%"))))
    return profs

# Height: truncated normal, inches
HEIGHT = {"Ly’Kun": (72, 108, 90, 9), "Dryqona": (96, 144, 102, 12), "Yubu": (72, 108, 90, 9),
          "Shynän": (72, 96, 90, 9), "Psolari": (72, 108, 90, 9), "Vygari": (72, 108, 90, 9), "Fefmial": (72, 84, 90, 9)}
MASS_CATS = ["Light", "Moderate", "Heavy"]; ARM_CATS = ["Short", "Moderate", "Long"]
PHYS_NAMES = {("Light","Short"):"Compact",("Light","Moderate"):"Lean",("Light","Long"):"Lanky",
              ("Moderate","Short"):"Stocky",("Moderate","Moderate"):"Athletic",("Moderate","Long"):"Rangy",
              ("Heavy","Short"):"Bulky",("Heavy","Moderate"):"Powerful",("Heavy","Long"):"Hulking"}
T = 1/3
MASS_P = {"Ly’Kun": (T,T,T), "Dryqona": (.05,.30,.65), "Yubu": (.10,.45,.45), "Shynän": (.60,.30,.10),
          "Psolari": (.10,.65,.25), "Vygari": (.05,.30,.65), "Fefmial": (.20,.60,.20)}
ARM_P = {"Ly’Kun": (T,T,T), "Dryqona": (.10,.30,.60), "Yubu": (.10,.45,.45), "Shynän": (.05,.15,.80),
         "Psolari": (.20,.65,.15), "Vygari": (T,T,T), "Fefmial": (.20,.60,.20)}
MASS_REF = {"Light": (185, 215), "Moderate": (215, 245), "Heavy": (245, 275)}
ARM_RATIO = {"Short": (0.94, 1.00), "Moderate": (1.00, 1.07), "Long": (1.07, 1.15)}
IN_M, LB_KG = 0.0254, 0.45359237

def height_weights(anc):
    n = len(anc); has_d = "Dryqona" in anc
    if n == 1: return {anc[0]: 1.0}
    if not has_d: return {t: 1/n for t in anc}
    dom = {2: 0.70, 3: 0.60, 4: 0.55}[n]
    return {t: (dom if t == "Dryqona" else (1 - dom) / (n - 1)) for t in anc}

def physique_dist(anc):
    d = collections.OrderedDict(((m, a), 0.0) for m in MASS_CATS for a in ARM_CATS)
    for t in anc:
        for i, m in enumerate(MASS_CATS):
            for j, a in enumerate(ARM_CATS):
                d[(m, a)] += MASS_P[t][i] * ARM_P[t][j] / len(anc)
    return d

def trunc_normal(rng, lo, hi, mu, sd):
    while True:
        x = rng.gauss(mu, sd)
        if lo <= x <= hi: return x

def athlete_rng(pid, seed):
    return random.Random(f"{seed}|{GEN_VERSION}|{pid}")

def generate(pid, name, profiles, seed, lock=None):
    rng = athlete_rng(pid, seed)
    # draw order is fixed so a lock never shifts later draws
    combos, weights = zip(*profiles)
    drawn = rng.choices(combos, weights=weights, k=1)[0]
    anc = tuple(sorted(lock, key=TRIBES.index)) if lock else drawn
    hw = height_weights(anc)
    src = rng.choices(list(hw), weights=list(hw.values()), k=1)[0]
    lo, hi, mu, sd = HEIGHT[src]
    h = trunc_normal(rng, lo, hi, mu, sd)
    pd = physique_dist(anc)
    mc, ac = rng.choices(list(pd), weights=list(pd.values()), k=1)[0]
    ref = rng.uniform(*MASS_REF[mc]); ratio = rng.uniform(*ARM_RATIO[ac])
    mass_lb = ref * (h / 72) ** 3
    span = h * ratio
    reach = 0.75 * h + 0.5 * span
    return dict(ancestry=anc, ancestry_class=["", "Pureblood", "Dual", "Tri", "Quad"][len(anc)],
                height_source=src, physique=PHYS_NAMES[(mc, ac)], mass_cat=mc, arm_cat=ac,
                height_in=h, mass_lb=mass_lb, arm_span_in=span, arm_ratio=ratio, reach_in=reach,
                locked=bool(lock), draw_profile_before_lock="/".join(drawn))

def ft_in(x): f = int(x // 12); return f"{f}′{x - 12*f:.1f}″"

COLS = ["Ancestry", "Ancestry class", "Height source tribe", "Physique", "Height (in)", "Height (ft/in)", "Height (m)",
        "Mass (lb)", "Mass (kg)", "Arm span (in)", "Arm span (m)", "Arm-span ratio", "Standing reach (in)", "Standing reach (m)",
        "Morphology locked", "Morphology seed", "Generator version"]
def row_values(g, seed):
    return ["/".join(g["ancestry"]), g["ancestry_class"], g["height_source"], g["physique"],
            round(g["height_in"], 2), ft_in(g["height_in"]), round(g["height_in"] * IN_M, 3),
            round(g["mass_lb"], 1), round(g["mass_lb"] * LB_KG, 1), round(g["arm_span_in"], 2), round(g["arm_span_in"] * IN_M, 3),
            round(g["arm_ratio"], 4), round(g["reach_in"], 2), round(g["reach_in"] * IN_M, 3),
            "YES (ancestry)" if g["locked"] else "", seed, GEN_VERSION]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--seed", type=int, default=MASTER_SEED)
    a = ap.parse_args()
    profiles = load_profiles()
    assert len(profiles) == 65, len(profiles)
    tot = sum(w for _, w in profiles); assert abs(tot - 100) < 1e-6, tot
    wb = openpyxl.load_workbook(a.inp)
    ws = wb["All 712 Players"]
    head = [c.value for c in ws[1]]
    ix = {h: i for i, h in enumerate(head)}
    rows = [[c.value for c in r] for r in ws.iter_rows(min_row=2)]
    names = collections.Counter(r[ix["Player"]] for r in rows)
    ids = collections.Counter(r[ix["Player ID"]] for r in rows)
    assert all(v == 1 for v in ids.values()), "duplicate Player ID"
    lock_by_id = {}
    for nm, anc in LOCKS.items():
        assert names[nm] == 1, f"lock name {nm!r} matches {names[nm]} players"
        pid = next(r[ix["Player ID"]] for r in rows if r[ix["Player"]] == nm)
        lock_by_id[pid] = anc
    gen = {}
    for r in rows:
        pid = r[ix["Player ID"]]
        gen[pid] = generate(pid, r[ix["Player"]], profiles, a.seed, lock_by_id.get(pid))
    # write columns onto All 712 and every team sheet (matched by Player ID)
    hdr_fill = PatternFill("solid", fgColor="1F3864"); hdr_font = Font(bold=True, color="FFFFFF")
    def add_cols(sheet):
        h = [c.value for c in sheet[1]]
        if "Player ID" not in h: return 0
        pi = h.index("Player ID"); start = sheet.max_column + 1
        for k, c in enumerate(COLS):
            cell = sheet.cell(row=1, column=start + k, value=c); cell.fill = hdr_fill; cell.font = hdr_font
        n = 0
        for rr in range(2, sheet.max_row + 1):
            pid = sheet.cell(row=rr, column=pi + 1).value
            if pid in gen:
                for k, v in enumerate(row_values(gen[pid], a.seed)): sheet.cell(row=rr, column=start + k, value=v)
                n += 1
        for k in range(len(COLS)): sheet.column_dimensions[openpyxl.utils.get_column_letter(start + k)].width = 16
        return n
    touched = {}
    for name in wb.sheetnames:
        if name in ("League Overview", "Method & Canon"): continue
        touched[name] = add_cols(wb[name])
    # audit sheet
    aud = wb.create_sheet("Morphology Audit")
    aud.append(["Generator version", GEN_VERSION]); aud.append(["Master seed", a.seed])
    aud.append(["Spec files", "Beastball_Morphology_Generator_v1.0.md; Beastball_Ancestry_Generation_Guideline_v1.0.md"])
    aud.append(["Locks (ancestry only)", "; ".join(f"{k} = {'/'.join(v)}" for k, v in LOCKS.items())])
    aud.append(["Note", "Ancestry and measurements are generated per the specs. Realized counts are NOT repaired to match target percentages."])
    aud.append([]); aud.append(["Player ID", "Player", "Franchise", "Ancestry", "Height-source tribe", "Physique", "Height (in)", "Mass (lb)", "Arm span (in)", "Standing reach (in)", "Locked", "Ancestry drawn before lock"])
    for r in rows:
        pid = r[ix["Player ID"]]; g = gen[pid]
        aud.append([pid, r[ix["Player"]], r[ix["Franchise"]], "/".join(g["ancestry"]), g["height_source"], g["physique"],
                    round(g["height_in"], 2), round(g["mass_lb"], 1), round(g["arm_span_in"], 2), round(g["reach_in"], 2), g["locked"], g["draw_profile_before_lock"]])
    wb.save(a.out)
    # validation report (informational: realized counts are not required to match targets)
    cls = collections.Counter(g["ancestry_class"] for g in gen.values())
    anyt = {t: sum(1 for g in gen.values() if t in g["ancestry"]) for t in TRIBES}
    hs = [g["height_in"] for g in gen.values()]
    errs = []
    for pid, g in gen.items():
        lo = min(HEIGHT[t][0] for t in g["ancestry"]); hi = max(HEIGHT[t][1] for t in g["ancestry"])
        if not (lo <= g["height_in"] <= hi): errs.append((pid, "height outside union of tribal bounds"))
        lo2, hi2 = HEIGHT[g["height_source"]][:2]
        if not (lo2 <= g["height_in"] <= hi2): errs.append((pid, "height outside selected tribe bounds"))
        if not (MASS_REF[g["mass_cat"]][0] * (g["height_in"]/72)**3 - 1e-6 <= g["mass_lb"] <= MASS_REF[g["mass_cat"]][1] * (g["height_in"]/72)**3 + 1e-6): errs.append((pid, "mass outside category"))
        if not (ARM_RATIO[g["arm_cat"]][0] - 1e-9 <= g["arm_ratio"] <= ARM_RATIO[g["arm_cat"]][1] + 1e-9): errs.append((pid, "arm ratio outside category"))
        if abs(g["reach_in"] - (1.25 * g["height_in"] + 0.5 * (g["arm_span_in"] - g["height_in"]))) > 1e-9: errs.append((pid, "reach formula"))
    rep = dict(version=GEN_VERSION, seed=a.seed, players=len(gen), profiles=len(profiles), profile_weight_total=tot,
               class_counts=cls, tribe_membership_counts=anyt,
               height_in=dict(min=round(min(hs), 1), max=round(max(hs), 1), mean=round(sum(hs)/len(hs), 2)),
               mass_kg=dict(min=round(min(g["mass_lb"] for g in gen.values())*LB_KG, 1), max=round(max(g["mass_lb"] for g in gen.values())*LB_KG, 1)),
               reach_m_max=round(max(g["reach_in"] for g in gen.values())*IN_M, 2),
               locked={k: "/".join(v) for k, v in LOCKS.items()}, errors=errs, sheets_updated=touched)
    Path(a.out).with_suffix(".validation.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    print(json.dumps(rep, indent=1, ensure_ascii=False))
    if errs: sys.exit(1)

if __name__ == "__main__":
    main()
