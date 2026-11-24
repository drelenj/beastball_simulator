"""Make the workbook sortable: an 'Overall Board' Excel table as the first (default) sheet, and the
'All 712 Players' sheet as an Excel table. Usage: python make_tables.py <in.xlsx> <out.xlsx>"""
import sys
import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

src, out = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(src)
ws = wb["All 712 Players"]
head = [c.value for c in ws[1]]
col = {h: i for i, h in enumerate(head)}
rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[1]]

keep = ["Player", "Franchise", "Position", "Cognitive archetype", "Age", "Opening-day OVR",
        "OVR 0.311", "OVR 0.312", "OVR 0.313", "OVR 0.321", "OVR 0.322", "OVR 0.323", "Talent level T"]
ratings = [h for h in head if h and h.endswith("(rating)")]
board = wb.create_sheet("Overall Board", 0)
board.append(keep + ratings)
for r in rows:
    board.append([r[col[h]] for h in keep + ratings])
last = get_column_letter(len(keep) + len(ratings))
style = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
t = Table(displayName="OverallBoard", ref=f"A1:{last}{len(rows) + 1}")
t.tableStyleInfo = style
board.add_table(t)
board.freeze_panes = "B2"
for i, h in enumerate(keep + ratings, start=1):
    board.column_dimensions[get_column_letter(i)].width = 24 if h in ("Player", "Franchise", "Cognitive archetype") else 11
for c in board[1]:
    c.alignment = openpyxl.styles.Alignment(wrap_text=True, vertical="center")
board.row_dimensions[1].height = 45

ws.auto_filter.ref = None
seen = set()
for i, h in enumerate(head, start=1):       # table headers must be unique text
    name = str(h) if h is not None else f"Column {i}"
    while name in seen:
        name += " (2)"
    seen.add(name)
    ws.cell(1, i, name)
t2 = Table(displayName="AllPlayers", ref=f"A1:{get_column_letter(len(head))}{len(rows) + 1}")
t2.tableStyleInfo = TableStyleInfo(name="TableStyleLight9", showRowStripes=True)
ws.add_table(t2)
wb.active = 0
wb.save(out)
print("board rows", len(rows), "columns", len(keep) + len(ratings))
