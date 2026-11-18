"""Writes DIAGNOSIS_DATA.md from offense_diagnosis.json, pass_aim.json and restart_lane.json."""
import json, sys
from pathlib import Path
root = Path(sys.argv[1] if len(sys.argv) > 1 else 'native/evidence/rb37')
d = json.loads((root/'offense_diagnosis.json').read_text()); R, K = d['real'], d['control']
la = json.loads((root/'restart_lane.json').read_text()); pa = json.loads((root/'pass_aim.json').read_text())
def pct(x): return f"{100*x:.1f}%"
def q(x): return f"{x['min']} / {x['q1']} / {x['median']} / {x['q3']} / {x['max']}" if x else '-'
def causes(r):
    out = ['| End cause | Possessions | Share | Median live s |', '|---|---|---|---|']
    for c in r['q1_end_causes']: out.append(f"| {c['cause']} | {c['count']} | {pct(c['share'])} | {c['median_live_s']} |")
    return out
r3, k3, c4, k4 = R['q3'], K['q3'], R['q4'], K['q4']
scrim_n = la['real/scrim/intercepted/distance']['n'] + la['real/scrim/ok/distance']['n'] + la['real/scrim/out_or_dead/distance']['n']
toss_n = la['real/toss/intercepted/distance']['n'] + la['real/toss/ok/distance']['n'] + la['real/toss/out_or_dead/distance']['n']
snap_n = la['real/snap40/ok/distance']['n'] + la['real/snap40/out_or_dead/distance']['n']
P, PK = R['possessions'], K['possessions']
L = ['# RB-3.7 offense diagnosis: data (answers to questions 1-8)', '',
 'Possession = the soak definition: it starts when passive possession changes. Distances are to the centre of the goal the possessing team attacks. Distributions are min / q1 / median / q3 / max.', '',
 '## 1. How possessions end', '',
 f"Real rosters: {P} possessions in 10 matches = {R['possessions_per_team_per_match']} per team per match; median live time {R['median_possession_live_s']} s. Control: {K['possessions_per_team_per_match']} per team per match, median {K['median_possession_live_s']} s.", '',
 'Real (10 matches):', ''] + causes(R) + ['', 'Control (3 matches):', ''] + causes(K) + ['',
 f"A first tackle never changes passive possession (the tackled team keeps the ball and snaps), so it is never itself an end cause; its effect appears as 'restart throw intercepted or loose' (sections 3 and 7). Shot and carry attempts are actions, not end events: possessions containing a shot {R['q1_possessions_with_shot']} of {P} ({pct(R['q1_possessions_with_shot']/P)}). Clock expiry (possession_expiry): 0.1 per match.", '',
 '## 2. Where the ball goes', '', '| | Real | Control |', '|---|---|---|',
 f"| Ball at possession start (m) | {q(R['q2']['start_distance'])} | {q(K['q2']['start_distance'])} |",
 f"| Ball at possession end (m) | {q(R['q2']['end_distance'])} | {q(K['q2']['end_distance'])} |",
 f"| Furthest advance, ball or carrier (m) | {q(R['q2']['furthest_advance_distance'])} | {q(K['q2']['furthest_advance_distance'])} |",
 f"| Reached the opposing 40 | {R['q2']['reached_opposing_40']} ({pct(R['q2']['reached_opposing_40']/P)}) | {K['q2']['reached_opposing_40']} ({pct(K['q2']['reached_opposing_40']/PK)}) |",
 f"| Reached 32 m (cognition shot range) | {R['q2']['reached_cognition_shot_range_32m']} ({pct(R['q2']['reached_cognition_shot_range_32m']/P)}) | {K['q2']['reached_cognition_shot_range_32m']} ({pct(K['q2']['reached_cognition_shot_range_32m']/PK)}) |",
 f"| Reached the Keeper Zone edge (20 m) | {R['q2']['reached_keeper_zone_edge_20m']} ({pct(R['q2']['reached_keeper_zone_edge_20m']/P)}) | {K['q2']['reached_keeper_zone_edge_20m']} ({pct(K['q2']['reached_keeper_zone_edge_20m']/PK)}) |", '',
 '## 3. Passing', '',
 f"Real: {r3['passes_per_possession']} open-play passes per possession; completion {pct(r3['completion_rate'])}: {r3['open_play_pass_results']}. Restart throws: {r3['restart_throw_results']}. Failures (intercepted or out) within 5 s of a restart: open-play passes {r3['failures_within_5s_of_restart']['pass']}, restart throws {r3['failures_within_5s_of_restart']['restart_pass']}. Control completion {pct(k3['completion_rate'])}.", '',
 f"Release speed (m/s), all passes and restart throws: real {q(r3['speed'])}; control {k3['speed']['median']} for every throw. Pass distance (m): {q(r3['pass_distance'])}. Passes leave at 50-64 m/s whatever their length.", '',
 'Open-play failure rate by distance (real): ' + ', '.join(f"{k} {pct(v['fail_rate'])}" for k, v in r3['fail_rate_by_distance_open_play'].items()) + '. Restart throws: ' + ', '.join(f"{k} {pct(v['fail_rate'])}" for k, v in r3['fail_rate_by_distance_restart'].items()) + '.', '',
 f"Reachable and legal at release ({r3['with_geometry']} passes with positions): lane clearance {q(r3['lane_clearance'])} m; nearest defender to the receiver {q(r3['nearest_defender_to_target'])} m; receiver frozen at release {r3['target_frozen']}; receiver in his own Keeper Zone {r3['target_in_own_zone']}; in the attacked zone {r3['target_in_attacked_zone']}.", '',
 f"Why open-play passes fail (`pass_aim.json`): failed passes leave with the receiver {pa['real/pass/fail']['lateral_offset_at_release_m']['median']} m off the line of flight (median) against {pa['real/pass/ok']['lateral_offset_at_release_m']['median']} m for completed ones; {pct(pa['real/pass/fail']['behind_passer_share'])} of failed passes are thrown with the receiver behind the direction of the throw (completed {pct(pa['real/pass/ok']['behind_passer_share'])}); the receiver does not move during the flight (median 0 m) and the ball passes him at a median {pa['real/pass/fail']['closest_ball_to_receiver_m']['median']} m (completed {pa['real/pass/ok']['closest_ball_to_receiver_m']['median']} m, sampled every step); failures almost never involve a touch by the passing team. Cognition leads a moving receiver by his velocity x distance / 27 m/s (`native/cognition.py:351`) while RB/3 releases at min(80, 0.5 x max throw speed), 50-64 m/s (`native/cognition.py:577`). Isolated catch test (forced scenario, stationary receiver, nobody else nearby): at 58 m/s passes of 6 m or less are not caught (hands not set in time, `core_src/match.py:2176`), 7 m and over are; at 40 m/s and below everything from 4 m is caught.", '',
 '## 4. Carries', '',
 f"A carry attempt = the carrier enters the 20 m Keeper Zone he attacks. Real: {c4['carries']}; control {k4['carries']}.", '', '| Real | min / q1 / median / q3 / max |', '|---|---|',
 f"| Start distance (m) | {q(c4['start_distance'])} |", f"| Closest approach (m) | {q(c4['closest_approach'])} |",
 f"| Distance covered (m) | {q(c4['distance_covered'])} |", f"| Time held (s) | {q(c4['held_s'])} |",
 f"| Defenders within 5 m at start | {q(c4['defenders_within_5m_at_start'])} |", f"| Keeper distance at start (m) | {q(c4['keeper_distance_at_start'])} |", '',
 f"Outcomes: {c4['outcomes']}; ended by {c4['ended_by']}. Closest approach of any carry: real {c4['closest_approach_any']} m, control {k4['closest_approach_any']} m. Zero carry goals.", '',
 'Carrier decisions by distance to the goal he attacks (real): ' + '; '.join(f"{k}: {v}" for k, v in R['q4_carrier_choices'].items()) + '.', '',
 'Forced scenario (no defenders): a carrier who keeps running at the goal scores 5, so the engine allows carry goals.', '',
 '## 5. Shots', '',
 f"Real: {R['q5']['shots']} shots; bands {R['q5']['bands']}; distance {q(R['q5']['distance'])} m; defenders within 5 m {q(R['q5']['defenders_within_5m'])}; outcomes {R['q5']['outcomes']}. Control: {K['q5']['shots']} shots, {K['q5']['outcomes']}.", '',
 '## 6. Archers', '',
 f"Real: {R['q6']['arrows']} arrows, {R['q6']['freezes']} freezes ({R['q6']['arrows_per_possession']} arrows, {R['q6']['freezes_per_possession']} freezes per possession); carrier frozen {R['q6']['carrier_freezes']}; receiver frozen in flight {R['q6']['receiver_freezes']}; possessions ended by a carrier freeze {R['q6']['possessions_ended_by_carrier_freeze']} ({pct(R['q6']['possessions_ended_by_carrier_freeze']/P)}).", '',
 '## 7. Restarts', '',
 'Released per match (real): ' + ', '.join(f"{k} {v}" for k, v in sorted(R['q7']['per_match'].items(), key=lambda x: -x[1])) + '.', '',
 'Possession lost within 5 s of the release, per match (real): ' + ', '.join(f"{k} {v}" for k, v in sorted(R['q7']['lost_within_5s_per_match'].items(), key=lambda x: -x[1])) + '.', '',
 f"Restart-throw geometry (`restart_lane.json`, real). Scrimmage snaps: intercepted {la['real/scrim/intercepted/distance']['n']} of {scrim_n} ({pct(la['real/scrim/intercepted/distance']['n']/scrim_n)}), a median {la['real/scrim/intercept_point_from_spot']['median']} m from the spot; nearest defender to the throw line {la['real/scrim/intercepted/lane']['median']} m (intercepted) and {la['real/scrim/ok/lane']['median']} m (completed); opponents within 5 m of the spot {la['real/scrim/intercepted/opp_within_5m_of_spot']['median']} (intercepted) vs {la['real/scrim/ok/opp_within_5m_of_spot']['median']} (completed). Own-40 snaps (defenders behind their own 40; lane {la['real/snap40/ok/lane']['median']} m): {la['real/snap40/ok/distance']['n']} of {snap_n} completed. Tosses (3 m clearance): intercepted {la['real/toss/intercepted/distance']['n']} of {toss_n}, a median {la['real/toss/intercept_point_from_spot']['median']} m from the spot. Interceptors: {la['interceptor_origin']}.", '',
 '## 8. Defence at the end of possessions (field players within 5 m / 25 m of the ball)', '', '| | Real | Control |', '|---|---|---|',
 f"| At a tackle: defenders within 5 m | {q(R['q8']['at_tackle']['defenders_within_5m'])} | {q(K['q8']['at_tackle']['defenders_within_5m'])} |",
 f"| At a tackle: defenders within 25 m | {q(R['q8']['at_tackle']['defenders_within_25m'])} | {q(K['q8']['at_tackle']['defenders_within_25m'])} |",
 f"| At a tackle: attackers within 5 m | {q(R['q8']['at_tackle']['attackers_within_5m'])} | {q(K['q8']['at_tackle']['attackers_within_5m'])} |",
 f"| At an in-play turnover: defenders within 5 m | {q(R['q8']['at_turnover']['defenders_within_5m'])} | {q(K['q8']['at_turnover']['defenders_within_5m'])} |",
 f"| At an in-play turnover: defenders within 25 m | {q(R['q8']['at_turnover']['defenders_within_25m'])} | {q(K['q8']['at_turnover']['defenders_within_25m'])} |"]
(root/'DIAGNOSIS_DATA.md').write_text('\n'.join(L) + '\n')
