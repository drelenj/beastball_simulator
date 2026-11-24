"""Generate initial PRISM cognitive and technique ratings (ratings-0.2, DRAFT).

Owner rulings 24 Nov 2026:
- Ratings named as in the PRISM Ratings Registry (v0); scale 0-100, league average 70 (canon).
- Talent level T: half Opening-day OVR, half a fresh draw: T = 70 + 6 x (sqrt(.5) z_ovr + sqrt(.5) z_draw).
- Rating = T + position shape + cognitive archetype + noise (sd 2); each rating re-centred to average 70
  (field players; Keepers for Goalkeeping; Archers for Disruption, Archery Accuracy); clamped 40-99.
- Kamasi Sinella: generated, then floored at 90 in every generated rating.
- Field General for Guards and Sentinels: no Takedown penalty (moved to Finishing). Savant added (very rare).
Physical ratings and bodies are untouched. Deterministic: per-player seed sha256(version|player id).
Usage: python generate_ratings_v02.py <source.xlsx> <out.xlsx>
"""
import copy, hashlib, math, random, statistics as st, sys
from collections import Counter, defaultdict
import openpyxl
from openpyxl.styles import Alignment, PatternFill

VERSION = "ratings-0.2"
AVG, T_SD, NOISE_SD, LO, HI = 70.0, 6.0, 2.0, 40, 99
FLOOR_90 = {"Kamasi Sinella"}

# key -> header the engine loader reads (key.replace('_',' ').title() + ' (rating)')
COG = ["vision", "awareness", "clarity", "focus", "reaction", "instinct", "anticipation",
       "playmaking", "defending", "zone_coverage", "in_air_ball_pursuit", "live_ball_pursuit",
       "passing", "finishing", "evasion", "takedown", "reflex"]
TECH = ["tackling", "blocking", "ball_handling", "throw_accuracy", "touch", "catching",
        "juke", "spin", "hurdle", "stiff_arm", "truck"]
SPECIAL = {"KPR": "goalkeeping", "ARC": "disruption"}
ARCHERY = "archery_accuracy"
ALL = COG + TECH + ["goalkeeping", "disruption", ARCHERY]
HDR = {k: k.replace("_", " ").title() + " (rating)" for k in ALL}

# Position shapes: offsets in rating points. Field positions are centred (zero-sum) within each set,
# so every position averages the league level; Keepers and Archers are not centred.
C = dict(zip(COG, range(len(COG))))
COG_SHAPE = {  # Vis Awa Cla Foc Rea Ins Ant Pla Def Zon Air Liv Pas Fin Eva Tak Rfx
    "PDR": [0, 2, 2, 0, 4, 4, 0, 2, -6, -6, 0, 2, -2, 6, 8, -6, 4],
    "STR": [-2, 0, 4, 0, 0, 2, 0, 0, -4, -6, 4, 2, -4, 8, 2, -4, 4],
    "SCT": [4, 2, 4, 2, 2, 2, 2, 2, -6, -6, 2, 2, 2, 6, 2, -6, 0],
    "PFD": [8, 4, 2, 4, 0, 2, 4, 8, -4, -2, 0, 0, 8, -2, 0, -4, 0],
    "HNT": [2, 4, 2, 2, 2, 4, 4, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2],
    "TRK": [2, 2, 0, 4, 2, 0, 2, 2, 2, 2, 2, 4, 2, -4, 0, 2, 0],
    "SEN": [4, 4, 0, 4, 0, 2, 4, 4, 4, 6, 4, 0, 4, -6, -4, 4, -2],
    "TRP": [2, 4, 2, 4, 4, 2, 8, -2, 4, 6, 4, 2, -2, -8, -4, 4, 2],
    "GRD": [0, 2, 0, 2, 2, 2, 4, -4, 8, 4, 2, 2, -4, -8, -4, 8, 0],
    "KPR": [2, 2, 6, 4, 4, 4, 6, 0, -10, -10, 4, 0, 2, -10, -10, -10, 8],
    "ARC": [6, 6, 6, 6, 4, 4, 6, -10, -10, -10, -10, -10, -10, -10, -10, -10, 0],
}
TECH_SHAPE = {  # Tck Blk BH TA Tch Cat Juk Spn Hrd SA Trk
    "PDR": [-6, -6, 6, 0, 0, 2, 8, 6, 4, 2, 2],
    "STR": [-4, 4, 4, -2, 0, 6, 0, 2, 0, 4, 6],
    "SCT": [-6, -6, 2, 8, 6, 4, 4, 2, 2, -2, -2],
    "PFD": [-4, -4, 6, 8, 8, 4, 2, 2, 0, -2, -2],
    "HNT": [2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    "TRK": [2, 0, 2, 4, 2, 2, 0, 0, 0, 0, 0],
    "SEN": [6, 4, 2, 4, 2, 2, -4, -4, -4, 0, 0],
    "TRP": [6, 2, -2, 0, 0, 4, -4, -4, -4, -2, 0],
    "GRD": [8, 8, 0, -2, -2, 0, -6, -6, -6, 2, 4],
    "KPR": [-10, -10, 2, 4, 4, 8, -10, -10, -10, -10, -10],
    "ARC": [-15] * 11,
}
SPECIAL_OFFSET = 10   # Goalkeeping (KPR), Disruption and Archery Accuracy (ARC)
FIELD = ("PDR", "STR", "SCT", "PFD", "HNT", "TRK", "SEN", "TRP", "GRD")


def centred(v):
    m = sum(v) / len(v)
    return [x - m for x in v]


for p in FIELD:
    COG_SHAPE[p] = centred(COG_SHAPE[p])
    TECH_SHAPE[p] = centred(TECH_SHAPE[p])

# Cognitive archetypes: zero-sum offsets (points). weight = base x 2 if the position is a likely home.
ARCH = [
    ("Balanced", 30, "ALL", {}, {}),
    ("Field General", 10, "PFD SEN GRD",
     dict(vision=6, anticipation=5, playmaking=5, passing=4), dict(reflex=-6, evasion=-5, takedown=-5, reaction=-4)),
    ("Metronome", 10, "PFD TRK SEN",
     dict(passing=6, focus=5, clarity=5, playmaking=4), dict(evasion=-6, reflex=-5, takedown=-5, reaction=-4)),
    ("Radar", 10, "SEN GRD PFD",
     dict(awareness=7, vision=5, zone_coverage=4, instinct=4), dict(clarity=-6, finishing=-5, takedown=-5, reflex=-4)),
    ("Film Student", 10, "GRD TRP SEN",
     dict(anticipation=6, focus=6, zone_coverage=5, instinct=3), dict(reflex=-6, reaction=-6, evasion=-4, finishing=-4)),
    ("Live Wire", 10, "PDR SCT TRK",
     dict(reaction=6, reflex=6, evasion=5, live_ball_pursuit=3), dict(focus=-6, anticipation=-5, zone_coverage=-5, passing=-4)),
    ("Natural", 10, "PDR STR HNT",
     dict(instinct=6, reflex=6, clarity=4, finishing=4), dict(focus=-5, zone_coverage=-5, passing=-5, anticipation=-5)),
    ("Tunnel Finisher", 10, "STR PDR",
     dict(finishing=7, clarity=6, reflex=4, focus=3), dict(vision=-6, awareness=-5, passing=-5, playmaking=-4)),
    ("Escape Artist", 10, "PDR PFD HNT",
     dict(evasion=7, awareness=6, instinct=4, reflex=3), dict(passing=-6, zone_coverage=-5, defending=-5, focus=-4)),
    ("Ballhawk", 10, "TRP HNT SCT",
     dict(in_air_ball_pursuit=6, anticipation=6, live_ball_pursuit=4, clarity=4), dict(takedown=-6, defending=-5, passing=-5, playmaking=-4)),
    ("Enforcer", 10, "GRD TRK",
     dict(takedown=7, defending=6, reaction=4, awareness=3), dict(vision=-6, passing=-5, zone_coverage=-5, anticipation=-4)),
    ("Savant", 2, "",
     dict(anticipation=10, vision=8, playmaking=7, instinct=5), dict(reflex=-8, reaction=-8, evasion=-7, takedown=-7)),
]
SPEC_ARCH = {
    "KPR": [("Balanced", 30, {}, {}),
            ("Shot Reader", 15, dict(anticipation=7, goalkeeping=6, clarity=4, focus=3), dict(reflex=-7, reaction=-6, passing=-4, live_ball_pursuit=-3)),
            ("Reflex Keeper", 15, dict(reflex=8, reaction=6, goalkeeping=3, clarity=3), dict(anticipation=-7, focus=-5, passing=-4, vision=-4))],
    "ARC": [("Balanced", 30, {}, {}),
            ("Sniper Mind", 15, dict(clarity=7, focus=6, disruption=4, reflex=3), dict(vision=-6, awareness=-6, reaction=-4, anticipation=-4)),
            ("Hunter Mind", 15, dict(vision=6, anticipation=6, disruption=5, awareness=3), dict(clarity=-6, focus=-6, reflex=-4, reaction=-4))],
}
for _, _, _, plus, minus in ARCH:
    assert sum(plus.values()) + sum(minus.values()) == 0
for lst in SPEC_ARCH.values():
    for _, _, plus, minus in lst:
        assert sum(plus.values()) + sum(minus.values()) == 0


def archetype_offsets(name, plus, minus, pos):
    off = dict(plus)
    off.update(minus)
    if name == "Field General" and pos in ("GRD", "SEN"):      # owner: no Takedown penalty for these
        off.pop("takedown")
        off["finishing"] = off.get("finishing", 0) - 5
    return off


def main(src, out):
    wb = openpyxl.load_workbook(src)
    ws = wb["All 712 Players"]
    head = [c.value for c in ws[1]]
    col = {h: i for i, h in enumerate(head)}
    rows = [list(r) for r in ws.iter_rows(min_row=2, values_only=True) if r[1]]
    ovr = [float(r[col["Opening-day OVR"]]) for r in rows]
    om, osd = st.mean(ovr), st.pstdev(ovr)

    gen = {}
    for r in rows:
        pid, name, pos = r[col["Player ID"]], r[col["Player"]], r[col["Position"]]
        rng = random.Random(int(hashlib.sha256(f"{VERSION}|{pid}".encode()).hexdigest()[:16], 16))
        z_ovr = (float(r[col["Opening-day OVR"]]) - om) / osd
        T = AVG + T_SD * (math.sqrt(.5) * z_ovr + math.sqrt(.5) * rng.gauss(0, 1))
        if pos in SPEC_ARCH:
            cands = SPEC_ARCH[pos]
            a = rng.choices(cands, weights=[c[1] for c in cands])[0]
            aname, off = a[0], archetype_offsets(a[0], a[2], a[3], pos)
        else:
            w = [base * (2 if pos in home.split() else 1) for _, base, home, _, _ in ARCH]
            a = rng.choices(ARCH, weights=w)[0]
            aname, off = a[0], archetype_offsets(a[0], a[3], a[4], pos)
        vals = {}
        for i, k in enumerate(COG):
            vals[k] = T + COG_SHAPE[pos][i] + off.get(k, 0) + rng.gauss(0, NOISE_SD)
        for i, k in enumerate(TECH):
            vals[k] = T + TECH_SHAPE[pos][i] + rng.gauss(0, NOISE_SD)
        g, d, ar = rng.gauss(0, NOISE_SD), rng.gauss(0, NOISE_SD), rng.gauss(0, NOISE_SD)
        vals["goalkeeping"] = T + SPECIAL_OFFSET + off.get("goalkeeping", 0) + g if pos == "KPR" else None
        vals["disruption"] = T + SPECIAL_OFFSET + off.get("disruption", 0) + d if pos == "ARC" else None
        vals[ARCHERY] = T + SPECIAL_OFFSET + ar if pos == "ARC" else None
        gen[pid] = dict(arch=aname, T=round(T, 1), vals=vals, pos=pos, name=name,
                        note="generated; floored at 90 (owner)" if name in FLOOR_90 else "generated")

    # Re-centre: league average exactly 70 per rating (field players for field ratings; Keepers for
    # Goalkeeping; Archers for Disruption and Archery Accuracy), then clamp and apply the owner floor.
    shift = {}
    for k in ALL:
        grp = "KPR" if k == "goalkeeping" else "ARC" if k in ("disruption", ARCHERY) else None
        v = [g["vals"][k] for g in gen.values() if g["vals"][k] is not None and
             (g["pos"] == grp if grp else g["pos"] in FIELD)]
        shift[k] = AVG - st.mean(v)
    for g in gen.values():
        floor = 90 if g["name"] in FLOOR_90 else LO
        g["vals"] = {k: (None if v is None else int(min(HI, max(floor, round(v + shift[k])))))
                     for k, v in g["vals"].items()}

    new_cols = ["Cognitive archetype", "Talent level T"] + [HDR[k] for k in ALL] + \
               ["Ratings source", "Ratings seed", "Ratings version"]
    fill = PatternFill("solid", fgColor="FF2E5E4E")
    hf = copy.copy(ws.cell(1, 1).font)

    def extend(sheet, id_idx):
        start = sheet.max_column + 1
        for j, h in enumerate(new_cols):
            c = sheet.cell(1, start + j, h)
            c.font, c.fill = hf, fill
            c.alignment = Alignment(wrap_text=True, vertical="center")
            sheet.column_dimensions[c.column_letter].width = 13 if j else 18
        for i in range(2, sheet.max_row + 1):
            pid = sheet.cell(i, id_idx).value
            if pid in gen:
                g = gen[pid]
                vals = [g["arch"], g["T"]] + [g["vals"][k] for k in ALL] + \
                       [g["note"], f"sha256({VERSION}|{pid})", VERSION]
                for j, v in enumerate(vals):
                    sheet.cell(i, start + j, v)
        if sheet.auto_filter.ref:
            sheet.auto_filter.ref = f"A1:{sheet.cell(1, sheet.max_column).column_letter}{sheet.max_row}"

    extend(ws, col["Player ID"] + 1)
    for sh in wb.worksheets:
        if sh.title[:2].isdigit():
            h = [c.value for c in sh[1]]
            if "Player ID" in h:
                extend(sh, h.index("Player ID") + 1)

    def table(title, header, body, widths=None):
        s = wb.create_sheet(title)
        s.append(header)
        for c in s[1]:
            c.font, c.fill = hf, copy.copy(ws.cell(1, 1).fill)
        for b in body:
            s.append(b)
        s.freeze_panes = "B2"
        for i in range(len(header)):
            s.column_dimensions[s.cell(1, i + 1).column_letter].width = (widths or {}).get(i, 12)
        return s

    poss = list(COG_SHAPE)
    table("Cognitive Shapes", ["Rating"] + poss,
          [[HDR[k].replace(" (rating)", "")] + [round(COG_SHAPE[p][i], 1) for p in poss] for i, k in enumerate(COG)],
          {0: 22})
    table("Technique Shapes", ["Rating"] + poss,
          [[HDR[k].replace(" (rating)", "")] + [round(TECH_SHAPE[p][i], 1) for p in poss] for i, k in enumerate(TECH)],
          {0: 22})
    cnt = Counter((r[col["Position"]], gen[r[col["Player ID"]]]["arch"]) for r in rows)
    body = []
    for name, base, home, plus, minus in ARCH:
        fmt = lambda d: ", ".join(f"{HDR[k].replace(' (rating)', '')} {v:+d}" for k, v in d.items())
        body.append([name, "field", base, home, fmt(plus), fmt(minus),
                     sum(n for (p, a), n in cnt.items() if a == name and p in FIELD)])
    for pos, lst in SPEC_ARCH.items():
        for name, base, plus, minus in lst:
            fmt = lambda d: ", ".join(f"{HDR[k].replace(' (rating)', '')} {v:+d}" for k, v in d.items())
            body.append([name, pos, base, pos, fmt(plus), fmt(minus), cnt[(pos, name)]])
    table("Cognitive Archetypes", ["Archetype", "Group", "Base weight", "Likely home (x2)", "Strengths", "Weaknesses", "Players"],
          body, {0: 18, 3: 16, 4: 60, 5: 60})
    audit = []
    for k in ALL:
        v = [g["vals"][k] for g in gen.values() if g["vals"][k] is not None]
        audit.append([HDR[k].replace(" (rating)", ""), len(v), round(st.mean(v), 1), round(st.pstdev(v), 1),
                      min(v), max(v), sum(x == HI for x in v), sum(x == LO for x in v)])
    table("Ratings Audit 0.2", ["Rating", "Players", "Mean", "SD", "Min", "Max", "At 99", "At 40"], audit, {0: 22})
    mc = wb["Method & Canon"]
    for line in [
        ("PRISM and technique ratings", f"{VERSION} DRAFT: names per PRISM Ratings Registry (v0); scale 0-100, league average 70"),
        ("Talent level", "T = 70 + 6 x (0.707 z(Opening-day OVR) + 0.707 z(fresh draw)) (owner: half OVR, half draw)"),
        ("Rating formula", "T + position shape + cognitive archetype (zero-sum) + noise sd 2; each rating re-centred to a league average of 70; clamped 40-99"),
        ("Specialists", "Goalkeeping only KPR; Disruption and Archery Accuracy only ARC; each averages 70 within its own group"),
        ("Owner-locked", "Kamasi Sinella: generated, floored at 90 in every generated rating"),
        ("Engine use", "Read by the loader with technical='explicit'; physical ratings unchanged"),
    ]:
        mc.append(list(line))
    wb.save(out)

    print("players", len(gen), "OVR mean/sd", round(om, 1), round(osd, 1))
    for a in audit:
        print(a)
    print(sorted(Counter(g["arch"] for g in gen.values()).items(), key=lambda x: -x[1]))
    for n in ("Kamasi Sinella", "Dante Sinella", "Julian Starhunter"):
        r = next(r for r in rows if r[col["Player"]] == n)
        g = gen[r[col["Player ID"]]]
        print(n, r[col["Position"]], r[col["Opening-day OVR"]], g["arch"], g["T"], {k: v for k, v in g["vals"].items() if v is not None})


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
