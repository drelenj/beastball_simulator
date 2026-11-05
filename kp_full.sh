cd /home/claude/work/p4
BEST='{"vision":0.98,"awareness":0.98,"clarity":0.98,"reaction":0.98,"focus":0.98,"instinct":0.98,"anticipation":0.98,"judgment":0.98}'
echo DRILL_FULL_BEST; KP_MINOBS=3 NETR=5.5 KFT=12 PRISM_KEEPER=1 PRISM_KEEPER_RATINGS="$BEST" python3 kp_probe7.py 2>&1 | tail -3
echo DRILL_NOJUD_NOINS; KP_JUD=0 KP_INS=0 KP_MINOBS=3 NETR=5.5 KFT=12 PRISM_KEEPER=1 PRISM_KEEPER_RATINGS="$BEST" python3 kp_probe7.py 2>&1 | tail -3
for ft in 9 12; do echo "FULL_SUITE NET_R=5.5 KEEPER_FT=$ft"; PRISM_KEEPER=1 KP_MINOBS=3 NGAMES=24 NPROC=2 NET_R=5.5 KEEPER_FT=$ft THROW_SPLIT=1 python3 split_game_cmp.py 2>&1 | tail -1; done
