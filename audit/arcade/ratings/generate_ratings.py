"""Generate initial technical and mental ratings (ratings-0.1, DRAFT).

Implements "How ratings are generated" in the Beastball Technical Ratings Spec
(draft v0): rating = T + position shape + archetype offsets + noise(sd 2),
clamped 40-99. T = Opening-day OVR (option A). Archetype drawn by frequency
weight x body fit. Shapes read from rating_shapes_v0.json (Rating shapes tab).

Usage: python generate_ratings.py <source.xlsx> <out.xlsx>
Deterministic: each player's draws come from sha256(version|player id).
"""
import copy, hashlib, json, math, random, statistics as st, sys
from collections import Counter, defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

VERSION = "ratings-0.1"
TECH = ["Tackling", "Blocking", "Ball security", "Passing", "Finishing",
        "Long shot", "Catching", "Evasion", "Keeping", "Archery"]
MENTAL = ["Vision", "Anticipation", "Reaction", "Judgment", "Composure",
          "Discipline", "Aggression", "Work rate"]
PHYS = ["Speed", "Strength", "Jumping", "Acceleration", "Agility", "Balance",
        "Throw Power", "Stamina", "Durability"]
FREQ = {"common": 30, "uncommon": 20, "rare": 5, "very rare": 1}
FIT_GAIN = 0.8          # weight multiplier exp(0.8 x mean z of fit attributes)
NOISE_SD = 2.0
LO, HI = 40, 99
OWNER_TO_SET = {"Kamasi Sinella", "Dante Sinella"}   # spec decision 9
FIT_COL = {"speed": "Speed (rating)", "acceleration": "Acceleration (rating)",
           "agility": "Agility (rating)", "strength": "Strength (rating)",
           "stamina": "Stamina (rating)", "balance": "Balance (rating)",
           "throw power": "Throw Power (rating)", "mass": "Mass (kg)",
           "height": "Height (m)", "reach": "Standing reach (m)"}


def parse_offsets(s, ratings):
    if s.startswith("+4 on every rating"):
        return {r: 4 for r in ratings}
    out = {}
    for part in s.split(","):
        name, val = part.strip().rsplit(" ", 1)
        out[name] = int(val.replace("+", ""))
    return out


def fit_score(fit, z):
    f = fit.strip().lower()
    if f == "none":
        return 0.0
    if f == "lighter frame":
        return -z["mass"]
    if f == "mass and speed together":
        return min(z["mass"], z["speed"])
    terms = []
    for t in f.split(","):
        t = t.strip()
        terms.append(-z["mass"] if t == "lighter frame" else z[t])
    return sum(terms) / len(terms)


def main(src, out):
    shapes = json.load(open(__file__.rsplit("/", 1)[0] + "/rating_shapes_v0.json"))
    pos_shape = shapes["position_shapes"]
    arch_by_pos = defaultdict(list)
    for a in shapes["archetypes"]:
        arch_by_pos[a["position"]].append(a)

    wb = openpyxl.load_workbook(src)
    ws = wb["All 712 Players"]
    head = [c.value for c in ws[1]]
    col = {h: i for i, h in enumerate(head)}
    rows = [list(r) for r in ws.iter_rows(min_row=2, values_only=True) if r[1]]

    # z-scores of fit attributes within each legacy position
    z = {}
    for p in pos_shape:
        grp = [r for r in rows if r[col["Position"]] == p]
        for key, c in FIT_COL.items():
            vals = [float(r[col[c]]) for r in grp]
            m, s = st.mean(vals), st.pstdev(vals) or 1.0
            for r in grp:
                z.setdefault(r[col["Player ID"]], {})[key] = (float(r[col[c]]) - m) / s

    gen = {}
    for r in rows:
        pid, name, p = r[col["Player ID"]], r[col["Player"]], r[col["Position"]]
        rng = random.Random(int(hashlib.sha256(f"{VERSION}|{pid}".encode()).hexdigest()[:16], 16))
        T = float(r[col["Opening-day OVR"]])
        shape = pos_shape[p]
        ratings = [k for k in TECH + MENTAL if k in shape]
        cands = arch_by_pos[p]
        w = [FREQ[a["frequency"]] * math.exp(FIT_GAIN * fit_score(a["body_fit"], z[pid])) for a in cands]
        a = rng.choices(cands, weights=w)[0]
        off = parse_offsets(a["offsets"], ratings)
        vals = {}
        for k in TECH + MENTAL:
            noise = rng.gauss(0, NOISE_SD)        # always drawn: stable stream
            if k in shape:
                v = T + shape[k] + off.get(k, 0) + noise
                vals[k] = int(min(HI, max(LO, round(v))))
            else:
                vals[k] = None
        src_note = ("generated; OWNER TO SET (locked player, spec decision 9)"
                    if name in OWNER_TO_SET else "generated")
        gen[pid] = dict(archetype=a["archetype"], vals=vals, note=src_note,
                        seed=f"sha256({VERSION}|{pid})")

    # placeholder Overall: equal weights inside each role set; specialist rating x5
    def role(p):
        return "KPR" if p == "KPR" else "ARC" if p == "ARC" else "FIELD"
    raw = {}
    for r in rows:
        pid, p = r[col["Player ID"]], r[col["Position"]]
        g = gen[pid]["vals"]
        items = [(float(r[col[f"{k} (rating)"]]), 1) for k in PHYS]
        items += [(g[k], 1) for k in MENTAL]
        if role(p) == "FIELD":
            items += [(g[k], 1) for k in TECH[:8]]
        elif role(p) == "KPR":
            items += [(g[k], 1) for k in TECH[:8]] + [(g["Keeping"], 5)]
        else:
            items += [(g["Archery"], 5)]
        raw[pid] = (role(p), sum(v * wt for v, wt in items) / sum(wt for _, wt in items))
    stats = {}
    for rl in ("FIELD", "KPR", "ARC"):
        v = [s for (q, s) in raw.values() if q == rl]
        stats[rl] = (st.mean(v), st.pstdev(v))
    covr = {pid: int(min(HI, max(LO, round(78 + 6 * (s - stats[q][0]) / stats[q][1]))))
            for pid, (q, s) in raw.items()}

    # starters by computed Overall: 2 KPR, 2 ARC, 18 field per franchise
    starter = {}
    by_team = defaultdict(list)
    for r in rows:
        by_team[r[col["Franchise"]]].append(r)
    for team, rs in by_team.items():
        for rl, n in (("KPR", 2), ("ARC", 2), ("FIELD", 18)):
            pool = sorted([r for r in rs if role(r[col["Position"]]) == rl],
                          key=lambda r: (-covr[r[col["Player ID"]]], r[col["Player ID"]]))
            for i, r in enumerate(pool):
                starter[r[col["Player ID"]]] = "Yes" if i < n else ""

    new_cols = (["Archetype"] + TECH + MENTAL +
                ["Computed OVR (placeholder weights)", "Starter by computed OVR",
                 "Ratings source", "Ratings seed", "Ratings version"])

    def row_vals(pid):
        g = gen[pid]
        return ([g["archetype"]] + [g["vals"][k] for k in TECH + MENTAL] +
                [covr[pid], starter[pid], g["note"], g["seed"], VERSION])

    hdr_font = copy.copy(ws.cell(1, 1).font)
    hdr_fill = copy.copy(ws.cell(1, 1).fill)
    new_fill = PatternFill("solid", fgColor="FF2E5E4E")

    def extend(sheet, id_col_idx):
        start = sheet.max_column + 1
        for j, h in enumerate(new_cols):
            c = sheet.cell(1, start + j, h)
            c.font = hdr_font
            c.fill = new_fill
            c.alignment = Alignment(wrap_text=True, vertical="center")
            sheet.column_dimensions[c.column_letter].width = 13 if j else 22
        for i in range(2, sheet.max_row + 1):
            pid = sheet.cell(i, id_col_idx).value
            if pid in gen:
                for j, v in enumerate(row_vals(pid)):
                    sheet.cell(i, start + j, v)
        if sheet.auto_filter.ref:
            sheet.auto_filter.ref = f"A1:{sheet.cell(1, sheet.max_column).column_letter}{sheet.max_row}"

    extend(ws, col["Player ID"] + 1)
    for sh in wb.worksheets:
        if sh.title[:2].isdigit():
            h = [c.value for c in sh[1]]
            if "Player ID" in h:
                extend(sh, h.index("Player ID") + 1)

    # reference sheets
    def table(sheet, header, body):
        sheet.append(header)
        for c in sheet[1]:
            c.font = hdr_font
            c.fill = hdr_fill
        for b in body:
            sheet.append(b)
        sheet.freeze_panes = "B2"
        for i, _ in enumerate(header):
            sheet.column_dimensions[sheet.cell(1, i + 1).column_letter].width = 14
    s1 = wb.create_sheet("Rating Shapes")
    poss = list(pos_shape)
    table(s1, ["Rating"] + poss, [[k] + [pos_shape[p].get(k, "—") for p in poss] for k in TECH + MENTAL])
    s1.column_dimensions["A"].width = 16
    s2 = wb.create_sheet("Archetypes")
    cnt = Counter((r[col["Position"]], gen[r[col["Player ID"]]]["archetype"]) for r in rows)
    table(s2, ["Position", "Archetype", "Frequency", "Body fit", "Offsets", "Players"],
          [[a["position"], a["archetype"], a["frequency"], a["body_fit"], a["offsets"],
            cnt[(a["position"], a["archetype"])]] for a in shapes["archetypes"]])
    s2.column_dimensions["B"].width = 28
    s2.column_dimensions["E"].width = 60
    s3 = wb.create_sheet("Ratings Audit")
    body = []
    for k in TECH + MENTAL:
        v = [g["vals"][k] for g in gen.values() if g["vals"][k] is not None]
        body.append([k, len(v), round(st.mean(v), 1), round(st.pstdev(v), 1), min(v), max(v),
                     sum(1 for x in v if x == HI), round(100 * sum(1 for x in v if x == HI) / len(v), 1)])
    table(s3, ["Rating", "Players", "Mean", "SD", "Min", "Max", "At 99", "% at 99"], body)
    s3.column_dimensions["A"].width = 16

    mc = wb["Method & Canon"]
    for line in [
        ("Technical & mental ratings", f"{VERSION} DRAFT, generated from the Technical Ratings Spec (draft v0); NOT owner-approved"),
        ("Ratings formula", "Opening-day OVR (option A) + position shape + archetype offsets + noise sd 2, clamped 40-99"),
        ("Archetype draw", f"weight = frequency (30/20/5/1) x exp({FIT_GAIN} x body-fit z-score within legacy position)"),
        ("Specialists", "Keeping only for KPR; Archery only for ARC; Archers have no field technical skills"),
        ("Computed OVR", "PLACEHOLDER: equal weights per role set (specialist rating x5), rescaled to mean 78 sd 6; not measured"),
        ("Owner-locked", "Kamasi Sinella and Dante Sinella ratings generated as fill-ins; owner to set"),
        ("Engine use", "Not yet read by the simulator; Opening-day OVR remains authoritative until wiring is approved"),
    ]:
        mc.append(list(line))
    wb.save(out)
    print("players", len(gen))
    for b in body:
        print(b)
    print("archetype counts", sorted(cnt.items()))
    for n in OWNER_TO_SET | {"Julian Starhunter"}:
        r = next(r for r in rows if r[col["Player"]] == n)
        pid = r[col["Player ID"]]
        print(n, r[col["Position"]], r[col["Opening-day OVR"]], gen[pid]["archetype"], covr[pid], gen[pid]["vals"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
