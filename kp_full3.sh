cd /home/claude/work/p4
echo "FULL_SUITE NET_R=5.5 KEEPER_FT=12"; PRISM_KEEPER=1 KP_MINOBS=3 NGAMES=24 NPROC=2 NET_R=5.5 KEEPER_FT=12 THROW_SPLIT=1 python3 split_game_cmp.py 2>&1 | tail -1
for ft in 9 12; do echo "PERCEPTION_ONLY NET_R=5.5 KEEPER_FT=$ft"; KP_ANT=0 KP_INS=0 KP_JUD=0 PRISM_KEEPER=1 KP_MINOBS=3 NGAMES=24 NPROC=2 NET_R=5.5 KEEPER_FT=$ft THROW_SPLIT=1 python3 split_game_cmp.py 2>&1 | tail -1; done
