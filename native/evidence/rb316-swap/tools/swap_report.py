"""Side-swap report. Reads result JSON only (no matches run).
python3 native/evidence/rb316-swap/tools/swap_report.py native/evidence/rb316-swap
Original orientation: Garvian Guardians = slot A, Ala Apex = slot B (RB-3.16 soak @ 409135f).
Swapped orientation: Ala Apex = slot A, Garvian Guardians = slot B (this run).
"""
import json, math, statistics as st, sys
from pathlib import Path

root = Path(sys.argv[1])
rows = []
for s in range(1, 11):
    o = json.loads((root / 'original/real' / f'real-seed{s:02d}.json').read_text())
    w = json.loads((root / 'real' / f'real-seed{s:02d}-swap.json').read_text())
    assert o['status'] == 'final' and w['status'] == 'final', s
    gar_o, ala_o = o['score']['A'], o['score']['B']
    ala_s, gar_s = w['score']['A'], w['score']['B']
    d_o, d_s = ala_o - gar_o, ala_s - gar_s
    rows.append(dict(seed=s, original_garvianA_alaB=f"{gar_o}-{ala_o}", swapped_alaA_garvianB=f"{ala_s}-{gar_s}",
                     ala_orig=ala_o, ala_swap=ala_s, gar_orig=gar_o, gar_swap=gar_s,
                     ala_won_orig=ala_o > gar_o, ala_won_swap=ala_s > gar_s,
                     team_effect=(d_o + d_s) / 2, slot_B_minus_A=(d_o - d_s) / 2,
                     trace_hash_swap=w['trace_hash'], state_hash_swap=w['state_hash'],
                     raw_swap=f'native/evidence/rb316-swap/real/raw-real-seed{s:02d}-swap.json.gz'))
ala_o = [r['ala_orig'] for r in rows]; ala_s = [r['ala_swap'] for r in rows]
gar_o = [r['gar_orig'] for r in rows]; gar_s = [r['gar_swap'] for r in rows]
slotB = ala_o + gar_s; slotA = gar_o + ala_s
team = [r['team_effect'] for r in rows]; side = [r['slot_B_minus_A'] for r in rows]
def t_stat(x):
    return st.mean(x), st.stdev(x), st.mean(x) / (st.stdev(x) / math.sqrt(len(x)))
summary = dict(
    ala_mean_slotB_orig=st.mean(ala_o), ala_mean_slotA_swap=st.mean(ala_s), ala_mean_pooled=st.mean(ala_o + ala_s),
    garvian_mean_slotA_orig=st.mean(gar_o), garvian_mean_slotB_swap=st.mean(gar_s), garvian_mean_pooled=st.mean(gar_o + gar_s),
    ala_wins_orig=sum(r['ala_won_orig'] for r in rows), ala_wins_swap=sum(r['ala_won_swap'] for r in rows),
    slotA_mean_points_20=st.mean(slotA), slotB_mean_points_20=st.mean(slotB), slotB_minus_slotA=st.mean(slotB) - st.mean(slotA),
    team_effect_mean_mean_sd_t=t_stat(team), slot_B_minus_A_per_seed_mean_sd_t=t_stat(side),
    team_effect_pooled=st.mean(ala_o + ala_s) - st.mean(gar_o + gar_s),
    ala_side_difference_B_minus_A=st.mean(ala_o) - st.mean(ala_s), garvian_side_difference_B_minus_A=st.mean(gar_s) - st.mean(gar_o),
)
ctl = []
for s in range(1, 4):
    c = json.loads((root / 'original/control' / f'control-seed{s:02d}.json').read_text())
    ctl.append(dict(seed=s, score=f"{c['score']['A']}-{c['score']['B']}", slot_B_minus_A=c['score']['B'] - c['score']['A']))
summary['control_identical_ratings_slot_B_minus_A_mean'] = st.mean(r['slot_B_minus_A'] for r in ctl)
(root / 'swap_table.json').write_text(json.dumps(dict(rows=rows, summary=summary, control_original=ctl), indent=1, default=str) + '\n')
L = ['# RB-3.16 side-swap test (TESTED; not ACCEPTED)', '',
     '| seed | original: Garvian A - Ala B | swapped: Ala A - Garvian B | Ala won orig | Ala won swap | team effect (Ala-Garv, avg) | slot B minus slot A |', '|---|---|---|---|---|---|---|']
for r in rows:
    L.append(f"| {r['seed']} | {r['original_garvianA_alaB']} | {r['swapped_alaA_garvianB']} | {'yes' if r['ala_won_orig'] else 'no'} | {'yes' if r['ala_won_swap'] else 'no'} | {r['team_effect']:+.1f} | {r['slot_B_minus_A']:+.1f} |")
L += ['', '## Summary', '| measure | value |', '|---|---|',
      f"| Ala Apex mean points, slot B (original, n=10) | {summary['ala_mean_slotB_orig']:.1f} |",
      f"| Ala Apex mean points, slot A (swapped, n=10) | {summary['ala_mean_slotA_swap']:.1f} |",
      f"| Ala Apex wins, original / swapped | {summary['ala_wins_orig']}/10 / {summary['ala_wins_swap']}/10 |",
      f"| Garvian Guardians mean points, slot A (original) | {summary['garvian_mean_slotA_orig']:.1f} |",
      f"| Garvian Guardians mean points, slot B (swapped) | {summary['garvian_mean_slotB_swap']:.1f} |",
      f"| slot A mean points, all 20 games | {summary['slotA_mean_points_20']:.1f} |",
      f"| slot B mean points, all 20 games | {summary['slotB_mean_points_20']:.1f} |",
      f"| slot B minus slot A, all 20 games | {summary['slotB_minus_slotA']:+.1f} |",
      f"| team effect Ala minus Garvian (average of both orientations, per seed): mean, sd, t | {summary['team_effect_mean_mean_sd_t'][0]:+.1f}, {summary['team_effect_mean_mean_sd_t'][1]:.1f}, t={summary['team_effect_mean_mean_sd_t'][2]:.2f} |",
      f"| side effect slot B minus slot A (per seed): mean, sd, t | {summary['slot_B_minus_A_per_seed_mean_sd_t'][0]:+.1f}, {summary['slot_B_minus_A_per_seed_mean_sd_t'][1]:.1f}, t={summary['slot_B_minus_A_per_seed_mean_sd_t'][2]:.2f} |",
      f"| Ala side difference (B minus A) | {summary['ala_side_difference_B_minus_A']:+.1f} |",
      f"| Garvian side difference (B minus A) | {summary['garvian_side_difference_B_minus_A']:+.1f} |",
      f"| control (identical ratings, original orientation, n=3) mean slot B minus slot A | {summary['control_identical_ratings_slot_B_minus_A_mean']:+.1f} |"]
(root / 'SWAP_TABLE.md').write_text('\n'.join(L) + '\n')
print(json.dumps(summary, indent=1, default=str))
