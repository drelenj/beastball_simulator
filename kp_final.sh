cd /home/claude/work/p4
for ft in 9 12; do echo "FULL_PRISM_KEEPER NET_R=5.5 KEEPER_FT=$ft"; PRISM_KEEPER=1 KP_MINOBS=3 NGAMES=24 NPROC=2 NET_R=5.5 KEEPER_FT=$ft THROW_SPLIT=1 python3 split_game_cmp.py 2>&1 | tail -1; done
