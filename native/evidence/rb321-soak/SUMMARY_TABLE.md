# RB-3.21 soak: per-match and summary (TESTED measurements; not ACCEPTED)

## Per match
| match | score A-B | play A/B | award A/B | possessions A/B (metrics) | control-change spans | end causes (n) | shots A/B | scored A/B | conv % | points by method | handoffs done/started | blocks engaged/shed | trucks att/broken | stiff arms | stretch goals | DQs A/B | legal-arrow % A/B | restart TO | restart throw lost ≤5 s | runtime s | trace_hash | state_hash |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| real-seed01 | 57-76 | 53/73 | 4/3 | 145/144 | 146 | first tackle 33; carrier frozen 28; carrier stopped short 18; intercepted/loose 18; unclassified 15; pass out of bounds 10; other out 9; goal 8; restart (other) 7 | 42/38 | 15/17 | 40.0 | award 3, carry 10, half 4, release 116 | 257/348 | 62/62 | 60/8 | 166 | 2 | 1/1 | 98.1/97.9 | 2 | 90 | 150.57 | `44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072` | `046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d` |
| real-seed02 | 77-120 | 71/113 | 6/7 | 157/155 | 158 | first tackle 34; intercepted/loose 23; carrier frozen 20; unclassified 20; carrier stopped short 16; goal 14; pass out of bounds 12; restart (other) 11; other out 8 | 31/42 | 15/26 | 56.2 | award 12, carry 25, half 1, release 159 | 228/305 | 59/59 | 54/8 | 120 | 5 | 1/1 | 97.8/97.0 | 3 | 110 | 160.38 | `82c156ac0e6739fc2f3ea66a58094269984cb47071816c9d089bd3525a117019` | `0338211648ea59f4e8d782defd3a20b782202b22058a2ff9c2c2c7d33cf333de` |
| real-seed03 | 64-117 | 59/116 | 5/1 | 150/151 | 168 | carrier frozen 33; first tackle 28; intercepted/loose 27; unclassified 22; goal 17; carrier stopped short 16; pass out of bounds 15; other out 9; restart (other) 1 | 40/39 | 14/26 | 50.6 | award 3, carry 25, half 3, release 150 | 258/335 | 53/53 | 69/12 | 126 | 5 | 0/0 | 99.7/98.4 | 0 | 76 | 158.73 | `4ae3525dadd2f463c9337f7f76f879fae3d6298f740baf6f023dd95698ec6db9` | `19dc3a43d6be47264b57d0eab25948cfe43903165c85dc5c8575c50e0f730565` |
| real-seed04 | 84-106 | 80/96 | 4/10 | 146/147 | 155 | intercepted/loose 27; unclassified 24; carrier frozen 23; first tackle 21; carrier stopped short 19; other out 13; goal 11; restart (other) 10; pass out of bounds 7 | 40/44 | 19/22 | 48.8 | award 9, carry 20, half 5, own 2, release 154 | 237/317 | 73/73 | 70/10 | 141 | 3 | 1/1 | 97.2/97.6 | 3 | 77 | 148.04 | `489cf0b702f7f1015f6a62e39a4f6a54d50ec421ee92c9e5b3a88d9651a23ab9` | `3c6e3085b36b9239fcdd74852fe4dbecfa9a1c4fb51f022ffe8cfca83625bb71` |
| real-seed05 | 99-95 | 91/94 | 8/1 | 163/163 | 168 | carrier frozen 31; first tackle 30; unclassified 25; intercepted/loose 24; carrier stopped short 23; other out 11; pass out of bounds 11; restart (other) 7; goal 6 | 41/32 | 21/21 | 57.5 | award 6, carry 35, half 3, release 150 | 254/366 | 75/75 | 60/7 | 150 | 7 | 0/1 | 98.5/97.3 | 0 | 92 | 154.28 | `953c2c79f7283c9fca4de4c2538f372d1627555e6a04018935559effbef4e74d` | `8f78544774717c46aec571fa37f054b9ab0f9dfa5419248b0bb250e4c0460160` |
| real-seed06 | 84-85 | 79/84 | 5/1 | 159/159 | 162 | carrier frozen 37; intercepted/loose 28; carrier stopped short 19; first tackle 19; other out 17; pass out of bounds 15; unclassified 12; goal 9; restart (other) 5; second tackle 1 | 42/37 | 15/20 | 44.3 | award 3, carry 15, half 3, release 148 | 198/265 | 45/45 | 49/8 | 100 | 3 | 0/1 | 99.3/97.7 | 1 | 107 | 167.39 | `217276ecea000ef10c0f5254c7a69ea200a300fd2c7de8283380260f26a4c479` | `be5aad1e447d045b2f244e9de7b49e86d1f113cbe79cedd7d841de6abdd4ed0e` |
| real-seed07 | 62-95 | 62/94 | 0/1 | 158/158 | 169 | first tackle 32; carrier frozen 30; intercepted/loose 24; unclassified 21; pass out of bounds 17; carrier stopped short 14; restart (other) 14; goal 9; other out 8 | 40/43 | 13/23 | 43.4 | carry 20, half 1, release 136 | 296/390 | 90/90 | 72/12 | 133 | 2 | 1/0 | 97.6/98.4 | 2 | 99 | 164.65 | `02f5f4b6c7d244fad1b5ed897dde375be937a5d24ebb2cd93d24a93cb2c0da69` | `7e742c65b52f48370be89e9f6689a36a3b279d786d5982709d0cf31ad1de4a6f` |
| real-seed08 | 70-125 | 69/119 | 1/6 | 148/148 | 147 | first tackle 37; intercepted/loose 25; carrier frozen 22; unclassified 14; carrier stopped short 13; goal 11; pass out of bounds 10; restart (other) 9; other out 6 | 43/41 | 20/27 | 56.0 | award 6, carry 20, half 1, release 168 | 218/317 | 44/44 | 46/7 | 88 | 4 | 1/1 | 97.5/98.0 | 2 | 97 | 155.26 | `459f007b90ad293e07105fa1f289c61fb81f2d87bf3875aba15c57c0339eadfc` | `838364330b8bd651e9dada35c5d61f373db1aba377ccdc052dd88c7821b18ea3` |
| real-seed09 | 66-111 | 62/107 | 4/4 | 152/150 | 144 | first tackle 41; carrier frozen 25; unclassified 19; intercepted/loose 16; restart (other) 14; goal 11; pass out of bounds 11; carrier stopped short 5; other out 1; second tackle 1 | 35/38 | 18/24 | 57.5 | carry 25, half 8, release 144 | 251/335 | 53/53 | 57/5 | 131 | 5 | 2/1 | 96.2/97.3 | 2 | 102 | 164.09 | `6309c26cb1d9cb29a363eb5092d17624fdae09a353987d621acba23bd5ad1c32` | `40c6232628e7c327d2322c589ed14f58dce3f010d4a9990ee5fbf578dd55d5f7` |
| real-seed10 | 67-121 | 60/115 | 7/6 | 143/143 | 133 | first tackle 28; carrier frozen 20; unclassified 18; carrier stopped short 16; intercepted/loose 15; other out 12; pass out of bounds 9; restart (other) 8; goal 7 | 35/41 | 14/22 | 47.4 | award 9, carry 40, half 4, release 135 | 229/318 | 80/80 | 65/9 | 139 | 7 | 1/1 | 96.9/98.0 | 2 | 98 | 157.48 | `770cdd1b1ba3547251c29b683ddd147d2b3fa09f95452c70709a76cd934c87dc` | `f92d3b0f6b59bf3e5129e6e40099c5761152e0391c55f46d3762c52be291fedd` |
| control-seed01 | 55-79 | 52/76 | 3/3 | 144/144 | 140 | first tackle 35; carrier frozen 28; intercepted/loose 17; carrier stopped short 15; restart (other) 14; unclassified 14; pass out of bounds 8; goal 5; other out 4 | 35/31 | 16/12 | 42.4 | award 6, carry 20, release 108 | 238/335 | 45/45 | 64/3 | 159 | 3 | 1/0 | 97.0/98.5 | 4 | 95 | 154.61 | `b4f5ed690665f894ad06560b1108a83f9b556b9cfe50e56463fdc39adb9f523b` | `b28b5ba40f82c6d0d601af8dc6a8a86e0b3dcad763df14b6c75da83cd6645676` |
| control-seed02 | 97-65 | 95/65 | 2/0 | 148/149 | 148 | first tackle 36; unclassified 22; carrier frozen 20; intercepted/loose 17; carrier stopped short 15; restart (other) 14; pass out of bounds 13; other out 6; goal 5 | 53/30 | 24/11 | 42.2 | carry 20, half 2, release 140 | 244/338 | 70/70 | 38/6 | 108 | 4 | 0/1 | 99.2/96.5 | 5 | 102 | 157.33 | `8dc8b1747d389ffd52df09f75771b5dada6c6d8375a9286c2cb9d9ad88d2c0b9` | `08fc71327268707c1363483d9ec900ae4a39432226cd2252836f43a3e8cea5f1` |
| control-seed03 | 96-92 | 88/90 | 8/2 | 149/149 | 141 | first tackle 34; carrier frozen 30; unclassified 18; carrier stopped short 17; intercepted/loose 15; pass out of bounds 11; restart (other) 8; goal 6; other out 2 | 32/49 | 16/21 | 45.7 | award 6, carry 30, half 4, own 2, release 146 | 236/339 | 56/56 | 59/8 | 100 | 5 | 0/1 | 98.6/97.6 | 4 | 96 | 152.67 | `51734836cd9bcfe787be86a34a0511f950945b9c845250574b72c21c8fb08de2` | `86eaa91da1cbfbafd1864ffc89a4e6f44536edc676dd7ab1b0b2745334e1e6ad` |

## Summary vs owner ranges (real roster, 20 team-games)
| measure | this soak | owner range / reference |
|---|---|---|
| median team score | 84.5 | 75-90 (pro NBL median 76) |
| mean team score | 89.05 | — |
| team-score sd (sample) | 21.93 | pro reference 12.7 |
| team-score p5 / p95 | 61.8 / 121.2 | — |
| possessions per team, mean | 151.9 | 100-150 |
| possessions per team, median | 150.5 | 100-150 |
| possessions per team, min / max | 143 / 163 | 100-150 |
| team-matches with possessions > 150 | 10 of 20 |
| matches where any team exceeds 150 | 6 of 10 |

## Summary: real roster (n = 10; min / median / max across matches)
| measure | min | median | max |
|---|---|---|---|
| score A | 57 | 68.5 | 99 |
| score B | 76 | 108.5 | 125 |
| possessions A | 143 | 151.0 | 163 |
| possessions B | 143 | 150.5 | 163 |
| control-change spans | 133 | 156.5 | 169 |
| end cause: goal | 6 | 10.0 | 17 |
| end cause: pass out of bounds | 7 | 11.0 | 17 |
| end cause: other out | 1 | 9.0 | 17 |
| end cause: intercepted/loose | 15 | 24.0 | 28 |
| end cause: carrier frozen | 20 | 26.5 | 37 |
| end cause: carrier stopped short | 5 | 16.0 | 23 |
| end cause: first tackle | 19 | 31.0 | 41 |
| end cause: second tackle | 0 | 0.0 | 1 |
| end cause: restart (other) | 1 | 8.5 | 14 |
| end cause: unclassified | 12 | 19.5 | 25 |
| shots A | 31 | 40.0 | 43 |
| shots B | 32 | 40.0 | 44 |
| shot conversion % | 40.0 | 49.7 | 57.5 |
| points release (both teams) | 116 | 149.0 | 168 |
| points carry (both teams) | 10 | 22.5 | 40 |
| points half (both teams) | 1 | 3.0 | 8 |
| points award (both teams) | 0 | 4.5 | 12 |
| points own (both teams) | 0 | 0.0 | 2 |
| handoffs completed | 198 | 244.0 | 296 |
| handoffs started | 265 | 326.5 | 390 |
| blocks engaged | 44 | 60.5 | 90 |
| blocks shed | 44 | 60.5 | 90 |
| trucks attempted | 46 | 60.0 | 72 |
| trucks broken | 5 | 8.0 | 12 |
| stiff arms | 88 | 132.0 | 166 |
| stretch goals | 2 | 4.5 | 7 |
| DQs A | 0 | 1.0 | 2 |
| DQs B | 0 | 1.0 | 1 |
| legal-arrow % A | 96.21 | 97.66 | 99.65 |
| legal-arrow % B | 96.99 | 97.81 | 98.44 |
| restart timeouts | 0 | 2.0 | 3 |
| restart throw lost ≤5 s | 76 | 97.5 | 110 |
| zone_unmarked calls | 0 | 1.0 | 2 |

## Summary: control (n = 3; min / median / max across matches)
| measure | min | median | max |
|---|---|---|---|
| score A | 55 | 96 | 97 |
| score B | 65 | 79 | 92 |
| possessions A | 144 | 148 | 149 |
| possessions B | 144 | 149 | 149 |
| control-change spans | 140 | 141 | 148 |
| end cause: goal | 5 | 5 | 6 |
| end cause: pass out of bounds | 8 | 11 | 13 |
| end cause: other out | 2 | 4 | 6 |
| end cause: intercepted/loose | 15 | 17 | 17 |
| end cause: carrier frozen | 20 | 28 | 30 |
| end cause: carrier stopped short | 15 | 15 | 17 |
| end cause: first tackle | 34 | 35 | 36 |
| end cause: second tackle | 0 | 0 | 0 |
| end cause: restart (other) | 8 | 14 | 14 |
| end cause: unclassified | 14 | 18 | 22 |
| shots A | 32 | 35 | 53 |
| shots B | 30 | 31 | 49 |
| shot conversion % | 42.2 | 42.4 | 45.7 |
| points release (both teams) | 108 | 140 | 146 |
| points carry (both teams) | 20 | 20 | 30 |
| points half (both teams) | 0 | 2 | 4 |
| points award (both teams) | 0 | 6 | 6 |
| points own (both teams) | 0 | 0 | 2 |
| handoffs completed | 236 | 238 | 244 |
| handoffs started | 335 | 338 | 339 |
| blocks engaged | 45 | 56 | 70 |
| blocks shed | 45 | 56 | 70 |
| trucks attempted | 38 | 59 | 64 |
| trucks broken | 3 | 6 | 8 |
| stiff arms | 100 | 108 | 159 |
| stretch goals | 3 | 4 | 5 |
| DQs A | 0 | 0 | 1 |
| DQs B | 0 | 1 | 1 |
| legal-arrow % A | 97.0 | 98.59 | 99.23 |
| legal-arrow % B | 96.53 | 97.56 | 98.52 |
| restart timeouts | 4 | 4 | 5 |
| restart throw lost ≤5 s | 95 | 96 | 102 |
| zone_unmarked calls | 0 | 0 | 4 |

