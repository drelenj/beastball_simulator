#!/usr/bin/env python3
"""Applies owner-locked full profiles on top of the generated roster workbook (in place).
Locked 17 Nov 2026: Kamasi Sinella (final canonical profile). Usage: apply_profile_locks.py workbook.xlsx
Affinity labels (primary/secondary) come from the physical generator's ancestry slots for the locked ancestry (same per-athlete RNG stream); ratings are the locked values."""
import random, sys
import openpyxl
import physical_attributes as PA

LB_KG, IN_M = 0.45359237, 0.0254
LOCKS = {
    "NBL24-02-04": dict(
        player="Kamasi Sinella", ancestry="Ly’Kun/Shynän/Dryqona", cls="Tri", height_src="Dryqona", physique="Rangy",
        height_in=116.09, mass_lb=1018.0, span_in=127.7, reach_in=150.9, ovr=98,
        ratings=dict(Speed=94, Strength=96, Jumping=93, Acceleration=91, Agility=94, Balance=93, **{"Throw Power": 95}, Stamina=97, Durability=96)),
}

def cells(pid, L):
    h = L["height_in"]
    d = {"Ancestry": L["ancestry"], "Ancestry class": L["cls"], "Height source tribe": L["height_src"], "Physique": L["physique"],
         "Mass (lb)": round(L["mass_lb"], 1), "Mass (kg)": round(L["mass_lb"] * LB_KG, 1),
         "Arm span (in)": round(L["span_in"], 2), "Arm span (m)": round(L["span_in"] * IN_M, 3), "Arm-span ratio": round(L["span_in"] / h, 4),
         "Standing reach (in)": round(L["reach_in"], 2), "Standing reach (m)": round(L["reach_in"] * IN_M, 3),
         "Morphology locked": "YES (owner profile)", "Opening-day OVR": L["ovr"]}
    for a, v in L["ratings"].items(): d[f"{a} (rating)"] = v
    g = PA.generate_physical(h, L["physique"], L["ancestry"].split("/"), random.Random(f"20261116|phys-1.0|{pid}|attr"), 0, 0)
    d["Primary attributes"] = ", ".join(x for x in PA.ATTRS if g[x]["affinity"] == "P")
    d["Secondary attributes"] = ", ".join(x for x in PA.ATTRS if g[x]["affinity"] == "S")
    d["Secondary slot shortfall"] = g["_shortfall"] or None
    return d

def main(path):
    wb = openpyxl.load_workbook(path)
    for pid, L in LOCKS.items():
        d = cells(pid, L); n = 0
        for name in wb.sheetnames:
            sh = wb[name]; h = [c.value for c in sh[1]]
            if "Player ID" not in h: continue
            pi = h.index("Player ID")
            for r in range(2, sh.max_row + 1):
                if sh.cell(row=r, column=pi + 1).value == pid:
                    for k, v in d.items():
                        if k in h: sh.cell(row=r, column=h.index(k) + 1, value=v)
                    n += 1
        print(pid, L["player"], "rows patched:", n)
    wb.save(path)
if __name__ == "__main__": main(sys.argv[1])
