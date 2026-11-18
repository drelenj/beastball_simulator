# RB-3.7 offense diagnosis: data (answers to questions 1-8)

Possession = the soak definition: it starts when passive possession changes. Distances are to the centre of the goal the possessing team attacks. Distributions are min / q1 / median / q3 / max.

## 1. How possessions end

Real rosters: 6817 possessions in 10 matches = 340.9 per team per match; median live time 2.38 s. Control: 318.0 per team per match, median 2.66 s.

Real (10 matches):

| End cause | Possessions | Share | Median live s |
|---|---|---|---|
| lost in play: restart throw intercepted or loose | 1726 | 25.3% | 1.18 |
| boundary: pass went out (last touch own) | 1581 | 23.2% | 3.48 |
| lost in play: pass intercepted or loose after pass | 1070 | 15.7% | 3.47 |
| boundary: other out (last touch own) | 428 | 6.3% | 2.54 |
| award: turnover | 419 | 6.2% | 0.0 |
| second tackle | 302 | 4.4% | 6.51 |
| lost in play: carrier frozen by arrow (ball loose) | 299 | 4.4% | 3.43 |
| boundary: restart throw went out (last touch own) | 286 | 4.2% | 2.11 |
| boundary: carrier stepped out | 177 | 2.6% | 1.2 |
| lost in play: shot saved/recovered by defence | 136 | 2.0% | 3.25 |
| zone rule (ZR-*/zone_residence) | 130 | 1.9% | 5.0 |
| goal scored | 112 | 1.6% | 3.39 |
| lost in play: strip | 86 | 1.3% | 3.46 |
| period/match end | 29 | 0.4% | 3.26 |
| boundary: shot missed out | 27 | 0.4% | 2.96 |
| award: first_tackle | 5 | 0.1% | 4.92 |
| award: held_ball | 3 | 0.0% | 2.35 |
| award: possession_expiry | 1 | 0.0% | 30.0 |

Control (3 matches):

| End cause | Possessions | Share | Median live s |
|---|---|---|---|
| boundary: pass went out (last touch own) | 474 | 24.8% | 3.63 |
| lost in play: restart throw intercepted or loose | 392 | 20.5% | 1.18 |
| lost in play: pass intercepted or loose after pass | 294 | 15.4% | 4.11 |
| award: turnover | 188 | 9.8% | 0.0 |
| second tackle | 145 | 7.6% | 6.56 |
| boundary: restart throw went out (last touch own) | 132 | 6.9% | 2.6 |
| lost in play: carrier frozen by arrow (ball loose) | 78 | 4.1% | 4.21 |
| boundary: other out (last touch own) | 75 | 3.9% | 3.37 |
| zone rule (ZR-*/zone_residence) | 38 | 2.0% | 5.08 |
| lost in play: strip | 26 | 1.4% | 2.93 |
| boundary: carrier stepped out | 18 | 0.9% | 1.38 |
| goal scored | 16 | 0.8% | 2.9 |
| lost in play: shot saved/recovered by defence | 15 | 0.8% | 2.13 |
| boundary: shot missed out | 8 | 0.4% | 3.08 |
| period/match end | 7 | 0.4% | 1.62 |
| award: possession_expiry | 1 | 0.1% | 25.6 |
| lost in play: ball loose at tackle/grounding | 1 | 0.1% | 3.99 |

A first tackle never changes passive possession (the tackled team keeps the ball and snaps), so it is never itself an end cause; its effect appears as 'restart throw intercepted or loose' (sections 3 and 7). Shot and carry attempts are actions, not end events: possessions containing a shot 327 of 6817 (4.8%). Clock expiry (possession_expiry): 0.1 per match.

## 2. Where the ball goes

| | Real | Control |
|---|---|---|
| Ball at possession start (m) | 1.24 / 42.68 / 62.96 / 85.94 / 111.8 | 4.63 / 42.84 / 61.15 / 79.0 / 111.79 |
| Ball at possession end (m) | 0.24 / 35.69 / 58.96 / 84.2 / 111.96 | 0.43 / 38.33 / 60.36 / 87.11 / 111.92 |
| Furthest advance, ball or carrier (m) | 0.24 / 27.38 / 48.21 / 70.47 / 109.21 | 0.43 / 27.96 / 48.2 / 67.4 / 103.89 |
| Reached the opposing 40 | 3404 (49.9%) | 901 (47.2%) |
| Reached 32 m (cognition shot range) | 1886 (27.7%) | 492 (25.8%) |
| Reached the Keeper Zone edge (20 m) | 1062 (15.6%) | 239 (12.5%) |

## 3. Passing

Real: 1.39 open-play passes per possession; completion 71.0%: {'complete_other': 2201, 'complete_to_target': 4653, 'dead_before_control': 31, 'intercepted': 1145, 'out_of_bounds': 1625, 'unresolved': 3}. Restart throws: {'complete_other': 869, 'complete_to_target': 2202, 'dead_before_control': 18, 'intercepted': 1792, 'out_of_bounds': 308, 'unresolved': 1}. Failures (intercepted or out) within 5 s of a restart: open-play passes 1920, restart throws 2100. Control completion 68.2%.

Release speed (m/s), all passes and restart throws: real 50.29 / 54.2 / 58.11 / 59.79 / 63.7; control 50.29 for every throw. Pass distance (m): 0.09 / 5.44 / 8.52 / 12.18 / 39.81. Passes leave at 50-64 m/s whatever their length.

Open-play failure rate by distance (real): 12-20 m 27.7%, 20+ m 27.1%, 6-8 m 27.9%, 8-12 m 29.7%, <6 m 26.1%. Restart throws: 12-20 m 38.6%, 20+ m 42.3%, 6-8 m 44.1%, 8-12 m 33.7%, <6 m 51.6%.

Reachable and legal at release (9483 passes with positions): lane clearance 0.0 / 3.83 / 6.22 / 9.5 / 65.45 m; nearest defender to the receiver 0.06 / 5.82 / 9.03 / 13.68 / 76.15 m; receiver frozen at release 196; receiver in his own Keeper Zone 322; in the attacked zone 299.

Why open-play passes fail (`pass_aim.json`): failed passes leave with the receiver 1.97 m off the line of flight (median) against 0.84 m for completed ones; 26.3% of failed passes are thrown with the receiver behind the direction of the throw (completed 10.1%); the receiver does not move during the flight (median 0 m) and the ball passes him at a median 3.53 m (completed 2.52 m, sampled every step); failures almost never involve a touch by the passing team. Cognition leads a moving receiver by his velocity x distance / 27 m/s (`native/cognition.py:351`) while RB/3 releases at min(80, 0.5 x max throw speed), 50-64 m/s (`native/cognition.py:577`). Isolated catch test (forced scenario, stationary receiver, nobody else nearby): at 58 m/s passes of 6 m or less are not caught (hands not set in time, `core_src/match.py:2176`), 7 m and over are; at 40 m/s and below everything from 4 m is caught.

## 4. Carries

A carry attempt = the carrier enters the 20 m Keeper Zone he attacks. Real: 1098; control 223.

| Real | min / q1 / median / q3 / max |
|---|---|
| Start distance (m) | 3.43 / 16.4 / 19.43 / 19.79 / 20.0 |
| Closest approach (m) | 2.56 / 13.13 / 15.64 / 18.33 / 20.0 |
| Distance covered (m) | 0 / 0.87 / 2.67 / 6.3 / 26.47 |
| Time held (s) | 0.0 / 0.4 / 0.6 / 0.9 / 3.6 |
| Defenders within 5 m at start | 0 / 0 / 0 / 1 / 10 |
| Keeper distance at start (m) | 0.9 / 13.31 / 15.19 / 15.91 / 21.34 |

Outcomes: {'grounded': 73, 'stopped_short': 894, 'turnover': 131}; ended by {'boundary': 110, 'c3_grounding': 73, 'freeze': 33, 'new_attempt': 31, 'period_end': 1, 'rb_discipline': 18, 'release': 811, 'restart_awarded': 21}. Closest approach of any carry: real 2.56 m, control 4.92 m. Zero carry goals.

Carrier decisions by distance to the goal he attacks (real): 20-32: {'carry': 2980, 'dribble': 34, 'pass': 1351, 'shoot': 3}; 32-50: {'carry': 5267, 'dribble': 85, 'pass': 2062}; 50+: {'carry': 13353, 'dribble': 75, 'pass': 5898, 'retain': 908}; under 20: {'carry': 414, 'dribble': 16, 'pass': 380, 'position': 59, 'shoot': 426}; under 20 & zone timer >= 3 s: {'position': 59}.

Forced scenario (no defenders): a carrier who keeps running at the goal scores 5, so the engine allows carry goals.

## 5. Shots

Real: 385 shots; bands {'10_to20': 298, '20plus': 2, 'under10': 85}; distance 2.47 / 10.36 / 12.97 / 14.5 / 21.9 m; defenders within 5 m 0 / 0 / 1 / 1 / 8; outcomes {'blocked/recovered by defence': 158, 'blocked/recovered by own': 26, 'deflected': 76, 'hit frame': 3, 'missed (out)': 24, 'scored': 98}. Control: 51 shots, {'blocked/recovered by defence': 20, 'blocked/recovered by own': 2, 'deflected': 7, 'hit frame': 1, 'missed (out)': 6, 'scored': 15}.

## 6. Archers

Real: 5425 arrows, 1821 freezes (0.796 arrows, 0.267 freezes per possession); carrier frozen 437; receiver frozen in flight 33; possessions ended by a carrier freeze 299 (4.4%).

## 7. Restarts

Released per match (real): boundary 224.1, first_tackle 178.5, turnover 41.9, second_tackle 30.3, goal 13.0, minor_count_plus 9.6, zone_residence 4.7, period_start 4.0, ZR-T 3.8, defence_minor 3.8, ZR-C 2.8, ZR-1 1.7, held_ball 0.7, possession_expiry 0.1.

Possession lost within 5 s of the release, per match (real): boundary 187.1, first_tackle 156.0, turnover 31.9, second_tackle 22.5, goal 8.6, minor_count_plus 7.5, zone_residence 4.0, ZR-T 3.0, defence_minor 2.6, ZR-C 2.4, period_start 2.1, ZR-1 1.4, held_ball 0.7.

Restart-throw geometry (`restart_lane.json`, real). Scrimmage snaps: intercepted 1209 of 2624 (46.1%), a median 2.3 m from the spot; nearest defender to the throw line 2.12 m (intercepted) and 2.26 m (completed); opponents within 5 m of the spot 4 (intercepted) vs 2 (completed). Own-40 snaps (defenders behind their own 40; lane 21.43 m): 131 of 138 completed. Tosses (3 m clearance): intercepted 406 of 1971, a median 5.73 m from the spot. Interceptors: {'interceptor came from elsewhere': 1402, 'interceptor was in the lane (<2 m) at release': 582}.

## 8. Defence at the end of possessions (field players within 5 m / 25 m of the ball)

| | Real | Control |
|---|---|---|
| At a tackle: defenders within 5 m | 0 / 1 / 2 / 4 / 10 | 0 / 1 / 2 / 4 / 10 |
| At a tackle: defenders within 25 m | 0 / 7 / 10 / 11 / 11 | 0 / 7 / 10 / 11 / 11 |
| At a tackle: attackers within 5 m | 0 / 1 / 2 / 3 / 9 | 0 / 1 / 2 / 3 / 10 |
| At an in-play turnover: defenders within 5 m | 0 / 0 / 0 / 0 / 4 | 0 / 0 / 0 / 0 / 4 |
| At an in-play turnover: defenders within 25 m | 0 / 4 / 7 / 10 / 11 | 0 / 4 / 8 / 10 / 11 |
