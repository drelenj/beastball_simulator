#!/usr/bin/env python3
"""Adds the nine natural physical attributes (Physical Attribute Generation v1.0) to a morphology-stamped roster workbook.
Reads height, physique and ancestry from the workbook; never touches existing columns. Own RNG stream per athlete:
random.Random(f"{seed}|{PHYS_VERSION}|{pid}|attr"). Usage: generate_physical.py in.xlsx out.xlsx [--seed N]
"""
import argparse, collections, json, random, statistics, sys
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
import physical_attributes as PA

PHYS_VERSION = "phys-1.0"
# Owner lock (Nov 16 2026): exceptional in every physical category for his size (the league's "Miami LeBron"), applied to the size baseline before tribal bonus.
ELITE = {"Kamasi Sinella": (14, 85)}  # (mu shift, rating floor)
MASTER_SEED = 20261116
RATING_COLS = [f"{a} (rating)" for a in PA.ATTRS]
EXTRA = ["Primary attributes", "Secondary attributes", "Secondary slot shortfall", "Physical seed", "Physical version"]

def prng(seed, pid): return random.Random(f"{seed}|{PHYS_VERSION}|{pid}|attr")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--seed", type=int, default=MASTER_SEED)
    a = ap.parse_args()
    wb = openpyxl.load_workbook(a.inp)
    ws = wb["All 712 Players"]
    head = [c.value for c in ws[1]]; ix = {h: i for i, h in enumerate(head)}
    rows = [[c.value for c in r] for r in ws.iter_rows(min_row=2)]
    elite_by_id = {}
    for nm, sh_ in ELITE.items():
        m = [r for r in rows if r[ix["Player"]] == nm]; assert len(m) == 1, nm
        elite_by_id[m[0][ix["Player ID"]]] = sh_  # tuple
    gen = {}
    for r in rows:
        pid = r[ix["Player ID"]]
        tribes = r[ix["Ancestry"]].split("/")
        g = PA.generate_physical(r[ix["Height (in)"]], r[ix["Physique"]], tribes, prng(a.seed, pid), *elite_by_id.get(pid, (0, 0)))
        g["_tribes"] = tribes; g["_h"] = r[ix["Height (in)"]]; g["_phys"] = r[ix["Physique"]]
        gen[pid] = g
    def labs(g, L): return ", ".join(x for x in PA.ATTRS if g[x]["affinity"] == L)
    def vals(g):
        return [g[x]["rating"] for x in PA.ATTRS] + [labs(g, "P"), labs(g, "S"), g["_shortfall"] or "", a.seed, PHYS_VERSION]
    cols = RATING_COLS + EXTRA
    hf = PatternFill("solid", fgColor="375623"); hfont = Font(bold=True, color="FFFFFF")
    touched = {}
    for name in wb.sheetnames:
        if name in ("League Overview", "Method & Canon"): continue
        sh = wb[name]; h = [c.value for c in sh[1]]
        if "Player ID" not in h: continue
        pi = h.index("Player ID"); start = sh.max_column + 1
        for k, c in enumerate(cols):
            cell = sh.cell(row=1, column=start + k, value=c); cell.fill = hf; cell.font = hfont
            sh.column_dimensions[get_column_letter(start + k)].width = 14 if k < 9 else 22
        n = 0
        for rr in range(2, sh.max_row + 1):
            pid = sh.cell(row=rr, column=pi + 1).value
            if pid in gen:
                for k, v in enumerate(vals(gen[pid])): sh.cell(row=rr, column=start + k, value=v)
                n += 1
        touched[name] = n
    aud = wb.create_sheet("Physical Audit")
    aud.append(["Generator version", PHYS_VERSION]); aud.append(["Master seed", a.seed])
    aud.append(["Spec", "Beastball_Physical_Attribute_Generation_v1.0.md (LOCKED). mu = 78 + height shift + physique shift + ancestry shift; discrete truncated normal, SD 7, integers 65-100."])
    aud.append(["Infeasible ancestries", "Where an ancestry cannot supply the locked secondary-slot count from supported attributes, available supported secondaries are applied, the shortfall stays neutral (0) and is flagged in 'Secondary slot shortfall'. OWNER RULING Nov 16 2026 (Option A): neutral shortfall accepted as canon for these combinations (Ly’Kun/Shynän, Ly’Kun/Fefmial, Shynän/Fefmial, Dryqona/Yubu/Vygari)."])
    aud.append(["Note", "Owner lock: Kamasi Sinella +14 on every attribute mu (exceptional for his size, added to the size baseline with tribal bonus on top) and a rating floor of 85. Ratings are natural capability only. OVR is independent. Skill attributes are not covered by this spec."])
    aud.append([])
    hdr = ["Player ID", "Player", "Franchise", "Ancestry", "Height (in)", "Physique", "Shortfall", "Owner elite shift"]
    for x in PA.ATTRS: hdr += [f"{x} mu", f"{x} H", f"{x} Ph", f"{x} An", f"{x} aff", f"{x} rating"]
    aud.append(hdr)
    for r in rows:
        pid = r[ix["Player ID"]]; g = gen[pid]
        line = [pid, r[ix["Player"]], r[ix["Franchise"]], "/".join(g["_tribes"]), g["_h"], g["_phys"], g["_shortfall"] or "", ("+%d, floor %d" % elite_by_id[pid]) if pid in elite_by_id else ""]
        for x in PA.ATTRS:
            d = g[x]; line += [round(d["mu"], 2), round(d["height_shift"], 2), d["physique_shift"], d["ancestry_shift"], d["affinity"], d["rating"]]
        aud.append(line)
    wb.save(a.out)

    # ---- validation + population report
    errs = []
    for pid, g in gen.items():
        for x in PA.ATTRS:
            r_ = g[x]["rating"]
            if not (isinstance(r_, int) and PA.LO <= r_ <= PA.HI): errs.append((pid, x, "rating out of range"))
            if abs(g[x]["mu"] - (78 + g[x]["height_shift"] + g[x]["physique_shift"] + g[x]["ancestry_shift"] + g[x]["elite_shift"])) > 1e-9: errs.append((pid, x, "mu mismatch"))
        n = len(g["_tribes"]); ps, _, ss, _, _ = PA.BONUS[n]
        np_ = sum(g[x]["affinity"] == "P" for x in PA.ATTRS); ns = sum(g[x]["affinity"] == "S" for x in PA.ATTRS)
        if np_ != ps: errs.append((pid, "primary count", np_))
        if ns != ss - (g["_shortfall"] or 0): errs.append((pid, "secondary count", ns))
    # spec checks
    chk = {}
    for t in PA.TRIBES:
        c = collections.Counter(PA.AFFINITY[t].values()); chk[f"{t} 2/4/3"] = (c["P"], c["S"], c["-"]) == (2, 4, 3)
    chk["neutral zero shift"] = all(abs(v) < 1e-12 for v in PA.height_shift(90)) and all(v == 0 for v in PA.PHYSIQUE_SHIFT["Athletic"])
    chk["height anchors exact"] = all(PA.height_shift(h) == [float(x) for x in v] for h, v in PA.HEIGHT_ANCHORS)
    chk["pmf normalised, 100 nonzero, no endpoint spike"] = all(abs(sum(PA.pmf(m)) - 1) < 1e-12 and PA.pmf(m)[-1] > 0 for m in (60, 78, 95, 110))
    def pct(v, q): v = sorted(v); return v[min(len(v) - 1, int(q * len(v)))]
    def stats(v): return dict(n=len(v), mean=round(statistics.mean(v), 2), median=statistics.median(v), p10=pct(v, .1), p90=pct(v, .9),
                               ge85=round(sum(x >= 85 for x in v) / len(v), 3), ge93=round(sum(x >= 93 for x in v) / len(v), 3), eq100=round(sum(x == 100 for x in v) / len(v), 4))
    def bucket(h): return "72-84" if h < 84 else "84-96" if h < 96 else "96-108" if h < 108 else "108-120" if h < 120 else "120+"
    pop = {"overall": {x: stats([g[x]["rating"] for g in gen.values()]) for x in PA.ATTRS}}
    for label, key in (("by height", lambda g: bucket(g["_h"])), ("by physique", lambda g: g["_phys"]), ("by ancestry count", lambda g: str(len(g["_tribes"])))):
        grp = collections.defaultdict(list)
        for g in gen.values(): grp[key(g)].append(g)
        pop[label] = {k: {x: round(statistics.mean(gg[x]["rating"] for gg in v), 1) for x in PA.ATTRS} | {"n": len(v)} for k, v in sorted(grp.items())}
    tr = collections.defaultdict(list)
    for g in gen.values():
        if len(g["_tribes"]) == 1: tr[g["_tribes"][0]].append(g)
    pop["pureblood by tribe"] = {k: {x: round(statistics.mean(gg[x]["rating"] for gg in v), 1) for x in PA.ATTRS} | {"n": len(v)} for k, v in sorted(tr.items())}
    short = collections.Counter("/".join(g["_tribes"]) for g in gen.values() if g["_shortfall"])
    rep = dict(version=PHYS_VERSION, seed=a.seed, players=len(gen), spec_checks=chk, errors=errs, infeasible_players=dict(short),
               infeasible_player_total=sum(short.values()), population=pop, sheets_updated=touched)
    Path(a.out).with_suffix(".validation.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    print(json.dumps({k: rep[k] for k in ("spec_checks", "errors", "infeasible_players", "infeasible_player_total", "sheets_updated")}, indent=1, ensure_ascii=False))
    if errs or not all(chk.values()): sys.exit(1)

if __name__ == "__main__":
    main()
