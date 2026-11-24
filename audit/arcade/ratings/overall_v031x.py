"""Overall (OVR) formula trials on ratings 0.3 (owner, 24 Nov 2026).

Weighted average A of a player's ratings (physical ratings re-centred to 70 for this calculation only;
Durability left out: injuries inactive), then mapped to Overall:
  0.311 / 0.321  70 average: OVR = 70 + (99-70)/(95-70) x (A - 70)   (A 70 -> 70, A 95 -> 99)
  0.312 / 0.322  78 average: OVR = 78 + (99-78)/(95-70) x (A - 70)   (A 70 -> 78, A 95 -> 99)
  0.313 / 0.323  unanchored: OVR = A (no rescaling)
All clamped 40-99 and rounded.
Weights:
  0.31x Equal weight: field = 17 cognitive + 11 technique + 8 physical, all weight 1.
  0.32x Legacy role weight: as 0.31x, but every cognitive or technique rating with a positive offset in the
        player's legacy position shape counts double.
  Keepers and Archers use their role sets in both series: Keepers Goalkeeping x3 plus Reflex, Anticipation,
  Clarity, Reaction, Vision, Awareness, Focus, Instinct, Catching, Throw Accuracy, Touch, Passing, Jumping,
  Agility, Acceleration, Strength; Archers Archery Accuracy x3, Disruption x3 plus Vision, Awareness, Clarity,
  Focus, Reaction, Instinct, Anticipation, Reflex.
Usage: python overall_v031x.py <ratings.xlsx> <out.xlsx>
"""
import copy, statistics as st, sys
import openpyxl
from openpyxl.styles import PatternFill
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_ratings_v02 import COG, TECH, COG_SHAPE, TECH_SHAPE, HDR

PHYS = ["Speed", "Strength", "Jumping", "Acceleration", "Agility", "Balance", "Throw Power", "Stamina"]
KPR_SET = ["reflex", "anticipation", "clarity", "reaction", "vision", "awareness", "focus", "instinct",
           "catching", "throw_accuracy", "touch", "passing"]
KPR_PHYS = ["Jumping", "Agility", "Acceleration", "Strength"]
ARC_SET = ["vision", "awareness", "clarity", "focus", "reaction", "instinct", "anticipation", "reflex"]
MAPS = {"70": lambda a: 70 + 29 / 25 * (a - 70), "78": lambda a: 78 + 21 / 25 * (a - 70), "un": lambda a: a}
VERSIONS = [("0.311", "equal", "70"), ("0.312", "equal", "78"), ("0.313", "equal", "un"),
            ("0.321", "role", "70"), ("0.322", "role", "78"), ("0.323", "role", "un")]


def main(src, out):
    wb = openpyxl.load_workbook(src)
    ws = wb["All 712 Players"]
    head = [c.value for c in ws[1]]
    col = {h: i for i, h in enumerate(head)}
    rows = [list(r) for r in ws.iter_rows(min_row=2, values_only=True) if r[1]]
    pmean = {p: st.mean(float(r[col[p + " (rating)"]]) for r in rows) for p in PHYS}
    g = lambda r, k: float(r[col[HDR[k]]])
    ph = lambda r, p: float(r[col[p + " (rating)"]]) - pmean[p] + 70

    def average(r, weighting):
        pos = r[col["Position"]]
        if pos == "KPR":
            items = [(g(r, "goalkeeping"), 3)] + [(g(r, k), 1) for k in KPR_SET] + [(ph(r, p), 1) for p in KPR_PHYS]
        elif pos == "ARC":
            items = [(g(r, "archery_accuracy"), 3), (g(r, "disruption"), 3)] + [(g(r, k), 1) for k in ARC_SET]
        else:
            w = lambda shape, i: 2 if weighting == "role" and shape[pos][i] > 0 else 1
            items = [(g(r, k), w(COG_SHAPE, i)) for i, k in enumerate(COG)] + \
                    [(g(r, k), w(TECH_SHAPE, i)) for i, k in enumerate(TECH)] + [(ph(r, p), 1) for p in PHYS]
        return sum(v * wt for v, wt in items) / sum(wt for _, wt in items)

    # Labels follow the ratings version: ratings 0.4 -> 0.411 ... 0.423 (owner naming, 24 Nov).
    rv = str(rows[0][col["Ratings version"]]).replace("ratings-", "")
    major = rv.split(".")[0] + "." + rv.split(".")[1][0]
    global VERSIONS
    VERSIONS = [(major + v[3:].rjust(2, "0") if False else major + v[-2:], w, m) for v, w, m in VERSIONS]
    res = {}
    for r in rows:
        pid = r[col["Player ID"]]
        res[pid] = {}
        for ver, weighting, m in VERSIONS:
            res[pid][ver] = int(max(40, min(99, round(MAPS[m](average(r, weighting))))))

    fill = PatternFill("solid", fgColor="FF5E3A2E")
    hf = copy.copy(ws.cell(1, 1).font)

    def extend(sheet, id_idx):
        start = sheet.max_column + 1
        for j, (ver, weighting, m) in enumerate(VERSIONS):
            c = sheet.cell(1, start + j, f"OVR {ver}")
            c.font, c.fill = hf, fill
            sheet.column_dimensions[c.column_letter].width = 10
        for i in range(2, sheet.max_row + 1):
            pid = sheet.cell(i, id_idx).value
            if pid in res:
                for j, (ver, _, _) in enumerate(VERSIONS):
                    sheet.cell(i, start + j, res[pid][ver])

    extend(ws, col["Player ID"] + 1)
    for sh in wb.worksheets:
        if sh.title[:2].isdigit():
            h = [c.value for c in sh[1]]
            if "Player ID" in h:
                extend(sh, h.index("Player ID") + 1)

    s = wb.create_sheet("Overall Trials")
    s.append(["Version", "Weights", "Average player", "Group", "Players", "Mean", "SD", "Max", "99s", "90+",
              "55 or less", "Corr. with Opening-day OVR", "Top five"])
    for c in s[1]:
        c.font, c.fill = hf, copy.copy(ws.cell(1, 1).fill)
    lines = []
    for ver, weighting, m in VERSIONS:
        for grp in ("Field", "KPR", "ARC"):
            sel = [r for r in rows if (r[col["Position"]] not in ("KPR", "ARC") if grp == "Field" else r[col["Position"]] == grp)]
            o = [res[r[col["Player ID"]]][ver] for r in sel]
            old = [float(r[col["Opening-day OVR"]]) for r in sel]
            top = sorted(sel, key=lambda r: (-res[r[col["Player ID"]]][ver], r[col["Player"]]))[:5]
            line = [ver, "Equal" if weighting == "equal" else "Legacy role",
                    {"70": "70", "78": "78", "un": "Unanchored"}[m], grp, len(sel), round(st.mean(o), 1),
                    round(st.pstdev(o), 1), max(o), sum(x == 99 for x in o), sum(x >= 90 for x in o),
                    sum(x <= 55 for x in o), round(st.correlation(old, o), 2),
                    ", ".join(f"{r[col['Player']]} {res[r[col['Player ID']]][ver]}" for r in top)]
            s.append(line)
            lines.append(line)
    for i, w in enumerate([8, 12, 12, 7, 8, 7, 6, 6, 5, 5, 9, 12, 90]):
        s.column_dimensions[s.cell(1, i + 1).column_letter].width = w
    # Default view: one sortable Excel table of every player and rating, opened first.
    from openpyxl.worksheet.table import Table, TableStyleInfo
    tcols = ["Player", "Player ID", "Franchise", "Position", "Opening-day OVR"] + [f"OVR {v}" for v, _, _ in VERSIONS] + \
            ["Cognitive archetype", "Talent level T"] + [p + " (rating)" for p in PHYS + ["Durability"]] + \
            [HDR[k] for k in COG + TECH + ["goalkeeping", "disruption", "archery_accuracy"]]
    t = wb.create_sheet("Player Ratings", 0)
    t.append([h.replace(" (rating)", "") for h in tcols])
    for r in rows:
        pid = r[col["Player ID"]]
        t.append([res[pid][h[4:]] if h.startswith("OVR 0.") else r[col[h]] for h in tcols])
    last = t.cell(1, len(tcols)).column_letter
    tab = Table(displayName="PlayerRatings", ref=f"A1:{last}{len(rows) + 1}")
    tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    t.add_table(tab)
    t.freeze_panes = "B2"
    t.column_dimensions["A"].width = 22
    t.column_dimensions["C"].width = 20
    t.column_dimensions["L"].width = 16
    for i in range(4, len(tcols) + 1):
        if t.cell(1, i).column_letter not in ("C", "L"):
            t.column_dimensions[t.cell(1, i).column_letter].width = 11
    wb.active = 0
    for sh in wb.worksheets:
        sh.sheet_view.tabSelected = sh.title == "Player Ratings"
    wb["Method & Canon"].append(["Overall", f"Interim Overall = OVR {major}22 (legacy role weights, 78 average; owner adopted 24 Nov). Other OVR columns are trials; see sheet Overall Trials and overall_v031x.py"])
    wb.save(out)
    for l in lines:
        print(l)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
