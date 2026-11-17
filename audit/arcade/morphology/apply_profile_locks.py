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
    "NBL24-11-12": dict(  # Dante Sinella, Kasuf Bloodravens: league MVP + Archer of the Year, title winner (owner, 17 Nov 2026). Morphology unchanged.
        player="Dante Sinella", ancestry="Yubu/Shynän", cls="Dual", height_src="Yubu", physique="Powerful",
        height_in=81.07, mass_lb=388.5, span_in=84.31, reach_in=102.96, ovr=99, keep_locked_label=True,
        ratings=dict(Speed=80, Strength=95, Jumping=99, Acceleration=95, Agility=87, Balance=93, **{"Throw Power": 86}, Stamina=100, Durability=91)),
}

def cells(pid, L):
    h = L["height_in"]
    d = {"Ancestry": L["ancestry"], "Ancestry class": L["cls"], "Height source tribe": L["height_src"], "Physique": L["physique"],
         "Mass (lb)": round(L["mass_lb"], 1), "Mass (kg)": round(L["mass_lb"] * LB_KG, 1),
         "Arm span (in)": round(L["span_in"], 2), "Arm span (m)": round(L["span_in"] * IN_M, 3), "Arm-span ratio": round(L["span_in"] / h, 4),
         "Standing reach (in)": round(L["reach_in"], 2), "Standing reach (m)": round(L["reach_in"] * IN_M, 3),
         "Opening-day OVR": L["ovr"]}
    if not L.get("keep_locked_label"): d["Morphology locked"] = "YES (owner profile)"
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
