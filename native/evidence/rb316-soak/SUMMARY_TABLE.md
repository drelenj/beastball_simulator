# RB-3.16 soak: per-match and summary (TESTED measurements; not ACCEPTED)

## Per match
| match | status | score A-B | play pts A/B | award pts A/B | points by method | possessions A/B | % poss ending in attempt A/B | shots A/B | shot outcome % (scored/keeper/field/own/out-award) | passes | pass intercepted % | intercepted <=3 m | tackles | carry att A/B | carry goals A/B | fouls by reason | DQs A/B | legal-arrow A/B | restart TO | restart compl. | zone_unmarked | runtime s | trace_hash | state_hash |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| real-seed01 | final | 74-92 | 66/91 | 8/1 | A|award=6, A|half=2, A|release=66, B|carry=20, B|half=1, B|own=2, B|release=69 | 228/226 | 23.7 / 20.4 | 36/28 | 54.7/25.0/1.6/7.8/10.9 | 334 | 13.8 | 6 | 82 | 66/52 | 0/4 | archery_target=9, zone_unmarked=1 | 0/1 | 98.3/98.2 | 17 | 1.0 | 1 | 177.85 | `93b1f57e268ee6c436fae47109e4e2987cfdf7024df5575b6405e119c5ed32d7` | `b9962ddfb23dbc96551258ea6c2132565804d22ec1b0c87295e3f3ff37d59854` |
| real-seed02 | final | 71-104 | 69/99 | 2/5 | A|carry=10, A|half=2, A|release=59, B|award=3, B|carry=15, B|half=2, B|release=84 | 209/209 | 23.4 / 24.4 | 27/32 | 61.0/27.1/3.4/3.4/5.1 | 335 | 19.7 | 8 | 83 | 60/58 | 2/3 | archery_target=11 | 1/1 | 98.2/97.6 | 14 | 1.0 | 0 | 175.64 | `711e24c6242fb8101f7c06e296c363460e11c6dbfdc9b8510022aab8786a7e1b` | `b753afa1bbaf35ad947b498f4e7c19eebfbd482b11707ee7280265837e2a5842` |
| real-seed03 | final | 42-92 | 39/85 | 3/7 | A|award=3, A|carry=5, A|release=34, B|award=6, B|carry=5, B|half=1, B|release=80 | 217/217 | 16.6 / 24.9 | 29/41 | 44.3/28.6/5.7/11.4/10.0 | 309 | 19.1 | 10 | 68 | 40/59 | 1/1 | archery_target=4, zone_unmarked=2 | 0/0 | 99.3/99.3 | 23 | 1.0 | 2 | 176.07 | `7ebf8e03e627e9dc09e4851ff168822faa245e58f100a40f8b694003307bf816` | `835f70477706159b0a68959e56c35d04a4c529ebc45b8dea73f51d2f29e4ce71` |
| real-seed04 | final | 68-76 | 68/71 | 0/5 | A|release=68, B|award=3, B|carry=5, B|half=2, B|release=66 | 211/212 | 24.2 / 22.6 | 36/32 | 52.9/32.4/2.9/1.5/10.3 | 333 | 16.2 | 10 | 58 | 49/53 | 0/1 | archery_target=7 | 1/0 | 98.1/99.3 | 16 | 1.0 | 0 | 172.07 | `f7b16b77060cdcbe5eeaa9f3a7029d7c0dd26c732e98ef901f3d673b72227092` | `27ca2f397e4b529d948d6035d8459ac9e4505b0666fedcdcc5312900f2487329` |
| real-seed05 | final | 84-60 | 69/58 | 15/2 | A|award=12, A|carry=5, A|half=3, A|release=64, B|half=2, B|own=2, B|release=56 | 201/201 | 26.4 / 19.9 | 34/28 | 51.6/29.0/3.2/11.3/4.8 | 311 | 14.1 | 11 | 88 | 59/52 | 1/0 | archery_target=13 | 0/1 | 98.6/96.4 | 20 | 1.0 | 0 | 174.38 | `ceaf966728aea1fa5fbd3761adbeb02c6fe596196821ea5a681c3fe40535907c` | `52c4c25e08f6c13373a019a10e981eb76842d710c968ce2fc39e58c1e00f151e` |
| real-seed06 | final | 58-82 | 52/80 | 6/2 | A|award=3, A|half=3, A|release=52, B|carry=10, B|half=2, B|release=70 | 228/227 | 14.5 / 22.0 | 26/35 | 55.7/23.0/0/11.5/9.8 | 356 | 19.4 | 7 | 65 | 37/59 | 0/2 | archery_target=11, zone_unmarked=1 | 1/1 | 97.8/98.1 | 15 | 1.0 | 1 | 177.53 | `cfadd324010c9af4fbc9f0b94a1f9940c6c5721c05131feb424d5222f63c4936` | `f3edc40c77e887b48c5710fdb0dc5c61c87efef4e729a9ee4d95c7b75d139e7e` |
| real-seed07 | final | 67-104 | 64/101 | 3/3 | A|award=3, A|carry=15, A|release=49, B|carry=15, B|half=3, B|release=86 | 215/216 | 23.3 / 26.9 | 34/48 | 42.7/35.4/6.1/8.5/7.3 | 346 | 20.2 | 4 | 80 | 57/68 | 3/3 | archery_target=10 | 1/1 | 98.1/98.1 | 20 | 1.0 | 0 | 174.11 | `c222ff83eafc9896b6f3079d8a1f4b769c3a2197a99c05abbbf15528d3ce28e7` | `0751281eef8540aa0775f8b5fe68a17e2bf2345310a546f9f9a726c34b64be56` |
| real-seed08 | final | 55-101 | 52/100 | 3/1 | A|half=3, A|release=52, B|carry=10, B|half=1, B|release=90 | 213/213 | 19.2 / 23.5 | 24/43 | 55.2/29.9/9.0/3.0/3.0 | 348 | 17.8 | 12 | 85 | 47/54 | 0/2 | archery_target=8, protected_keeper=1, zone_unmarked=1 | 0/1 | 99.6/97.4 | 26 | 1.0 | 1 | 183.7 | `ba84dcb8a434dfb7929a995abedaf50a232a0af60ed75f9edda452be1a16ceb6` | `b0a4a4bff61db105c7fbbb5064471709fc5cd60278c691b2efca22cd7fde6bc1` |
| real-seed09 | final | 74-94 | 73/88 | 1/6 | A|carry=5, A|half=1, A|release=68, B|award=3, B|carry=10, B|half=3, B|release=78 | 223/223 | 23.3 / 22.4 | 38/29 | 55.2/20.9/3.0/10.4/10.4 | 344 | 12.8 | 5 | 71 | 60/55 | 1/2 | archery_target=9, zone_unmarked=1 | 1/0 | 97.2/99.6 | 21 | 1.0 | 1 | 183.67 | `266ec725b258e22e29f9008ccab75c3c213020558df855804af761d521c8f984` | `1a584f481a211ba33913f55bc3805519be2516c867a53396ef928f7dc078bed7` |
| real-seed10 | final | 51-80 | 48/75 | 3/5 | A|award=3, A|carry=5, A|release=43, B|award=3, B|carry=15, B|half=2, B|release=60 | 218/219 | 17.4 / 23.3 | 27/38 | 50.8/26.2/7.7/9.2/6.2 | 346 | 17.6 | 3 | 76 | 45/63 | 1/3 | archery_target=3, zone_unmarked=2 | 0/0 | 99.3/99.6 | 27 | 1.0 | 2 | 182.74 | `588c4cfbc65a7ccde424cce91ab5df6238ecac60c50eaf8bc5090f36df3630d5` | `f0f328390815af1b4ce82d1e7bf383b3d15185c22e3708e95a5695dad09787db` |
| control-seed01 | final | 68-55 | 67/54 | 1/1 | A|half=1, A|release=67, B|carry=10, B|half=1, B|release=44 | 206/206 | 17.0 / 16.0 | 37/24 | 44.3/26.2/3.3/14.8/11.5 | 292 | 19.2 | 4 | 75 | 46/46 | 0/2 | archery_target=9, zone_unmarked=4 | 1/0 | 98.2/98.5 | 27 | 1.0 | 4 | 178.45 | `c251c06f90ae4236b201af6a3e94ce587fce66d6ef8e630e95bcaefde84b7446` | `4a3cbc5c7c98d1c4e4b5b3fcf8db7278e5804c8d363c92ad9c0e7977ab76e3c4` |
| control-seed02 | final | 56-97 | 51/89 | 5/8 | A|half=5, A|release=51, B|award=6, B|carry=10, B|half=2, B|own=2, B|release=77 | 202/203 | 17.8 / 21.2 | 24/30 | 55.6/25.9/3.7/3.7/11.1 | 322 | 16.5 | 2 | 78 | 46/50 | 0/2 | archery_target=14, zone_unmarked=4 | 1/1 | 97.6/97.2 | 28 | 1.0 | 4 | 187.3 | `13fc440406aeb432035bc6adff29ad3b29498a45250948adf91c982f528fd6df` | `3aeb10e9c981db5ef5e25f50c7471fb643d945592361cd94f17f6fa5fcd9193a` |
| control-seed03 | final | 40-74 | 38/68 | 2/6 | A|half=2, A|release=38, B|award=3, B|carry=5, B|half=3, B|release=63 | 206/206 | 20.4 / 19.9 | 26/35 | 42.6/37.7/8.2/6.6/4.9 | 309 | 15.9 | 5 | 85 | 51/46 | 0/1 | archery_target=8, zone_unmarked=3 | 1/0 | 97.2/99.6 | 25 | 1.0 | 3 | 187.21 | `11ab900634e5916b7a44edf80385760afabb1b606aa9188574f1db74e364d784` | `d6bd850ec854f53b36603623b17b0afa2175c88a33e5fc9aa613d5f366f1f906` |

## Real-roster team scores vs owner target (20 team-games)
| statistic | this soak (real, n=20) | owner target (canon) |
|---|---|---|
| median | 75.0 | 76 |
| mean | 76.45 | — |
| sd (sample) | 17.95 | 12.7 |
| p5 / p95 | 50.5 / 104.0 | 59 / 102 |
| min / max | 42 / 104 | — |

## Summary: real roster (n = 10; min / median / max across seeds)
| measure | min | median | max |
|---|---|---|---|
| team score A | 42 | 67.5 | 84 |
| team score B | 60 | 92.0 | 104 |
| play points A | 39 | 65.0 | 73 |
| play points B | 58 | 86.5 | 101 |
| award points A | 0 | 3.0 | 15 |
| award points B | 1 | 4.0 | 7 |
| possessions A | 201 | 216.0 | 228 |
| possessions B | 201 | 216.5 | 227 |
| % possessions ending in attempt A | 14.474 | 23.287 | 26.368 |
| % possessions ending in attempt B | 19.9 | 22.965 | 26.852 |
| shots A | 24 | 31.5 | 38 |
| shots B | 28 | 33.5 | 48 |
| shot outcome % scored | 42.7 | 53.8 | 61.0 |
| shot outcome % keeper | 20.9 | 27.85 | 35.4 |
| shot outcome % field | 0 | 3.3 | 9.0 |
| shot outcome % own | 1.5 | 8.85 | 11.5 |
| shot outcome % out/award | 3.0 | 8.55 | 10.9 |
| pass interception % | 12.8 | 17.7 | 20.2 |
| interceptions within 3 m | 3 | 7.5 | 12 |
| tackles per match | 58 | 78.0 | 88 |
| carry attempts A | 37 | 53.0 | 66 |
| carry attempts B | 52 | 56.5 | 68 |
| carry goals A | 0 | 1.0 | 3 |
| carry goals B | 0 | 2.0 | 4 |
| DQs A | 0 | 0.5 | 1 |
| DQs B | 0 | 1.0 | 1 |
| legal-arrow rate A % | 97.203 | 98.275 | 99.643 |
| legal-arrow rate B % | 96.429 | 98.161 | 99.642 |
| restart timeouts | 14 | 20.0 | 27 |
| restart completion ratio | 1.0 | 1.0 | 1.0 |
| zone_unmarked calls | 0 | 1.0 | 2 |
| zone_residence events | 0 | 0.0 | 0 |
| runtime s | 172.07 | 176.8 | 183.7 |

## Summary: control (n = 3; min / median / max across seeds)
| measure | min | median | max |
|---|---|---|---|
| team score A | 40 | 56 | 68 |
| team score B | 55 | 74 | 97 |
| play points A | 38 | 51 | 67 |
| play points B | 54 | 68 | 89 |
| award points A | 1 | 2 | 5 |
| award points B | 1 | 6 | 8 |
| possessions A | 202 | 206 | 206 |
| possessions B | 203 | 206 | 206 |
| % possessions ending in attempt A | 16.99 | 17.822 | 20.388 |
| % possessions ending in attempt B | 16.019 | 19.903 | 21.182 |
| shots A | 24 | 26 | 37 |
| shots B | 24 | 30 | 35 |
| shot outcome % scored | 42.6 | 44.3 | 55.6 |
| shot outcome % keeper | 25.9 | 26.2 | 37.7 |
| shot outcome % field | 3.3 | 3.7 | 8.2 |
| shot outcome % own | 3.7 | 6.6 | 14.8 |
| shot outcome % out/award | 4.9 | 11.1 | 11.5 |
| pass interception % | 15.9 | 16.5 | 19.2 |
| interceptions within 3 m | 2 | 4 | 5 |
| tackles per match | 75 | 78 | 85 |
| carry attempts A | 46 | 46 | 51 |
| carry attempts B | 46 | 46 | 50 |
| carry goals A | 0 | 0 | 0 |
| carry goals B | 1 | 2 | 2 |
| DQs A | 1 | 1 | 1 |
| DQs B | 0 | 0 | 1 |
| legal-arrow rate A % | 97.244 | 97.551 | 98.221 |
| legal-arrow rate B % | 97.163 | 98.456 | 99.643 |
| restart timeouts | 25 | 27 | 28 |
| restart completion ratio | 1.0 | 1.0 | 1.0 |
| zone_unmarked calls | 3 | 4 | 4 |
| zone_residence events | 0 | 0 | 0 |
| runtime s | 178.45 | 187.21 | 187.3 |

## Foul reasons, all matches
| match | archery_target | protected_keeper | zone_unmarked |
|---|---|---|---|
| real-seed01 | 9 | 0 | 1 |
| real-seed02 | 11 | 0 | 0 |
| real-seed03 | 4 | 0 | 2 |
| real-seed04 | 7 | 0 | 0 |
| real-seed05 | 13 | 0 | 0 |
| real-seed06 | 11 | 0 | 1 |
| real-seed07 | 10 | 0 | 0 |
| real-seed08 | 8 | 1 | 1 |
| real-seed09 | 9 | 0 | 1 |
| real-seed10 | 3 | 0 | 2 |
| control-seed01 | 9 | 0 | 4 |
| control-seed02 | 14 | 0 | 4 |
| control-seed03 | 8 | 0 | 3 |
