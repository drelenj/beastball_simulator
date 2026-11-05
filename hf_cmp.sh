cd /home/claude/work/p4
for hf in 0 1; do echo "HAND_FIGHT=$hf (CATCH_V2 PRISM_KEEPER PRISM_OFFBALL net5.5 10ft)"; HAND_FIGHT=$hf CATCH_V2=1 PRISM_KEEPER=1 KP_MINOBS=3 PRISM_OFFBALL=1 NGAMES=16 NPROC=2 NET_R=5.5 KEEPER_FT=10 THROW_SPLIT=1 python3 split_game_cmp.py 2>&1 | tail -2; done
