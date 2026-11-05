cd /home/claude/work/p4
for ob in 0 1; do echo "CATCH_V2=1 PRISM_KEEPER=1 PRISM_OFFBALL=$ob NET_R=5.5 KEEPER_FT=10"; CATCH_V2=1 PRISM_KEEPER=1 KP_MINOBS=3 PRISM_OFFBALL=$ob NGAMES=8 NPROC=2 NET_R=5.5 KEEPER_FT=10 THROW_SPLIT=1 python3 split_game_cmp.py 2>&1 | tail -2; done
