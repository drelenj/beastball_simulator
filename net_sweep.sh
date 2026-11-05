cd /home/claude/work/p4
for r in 4 4.5 5; do for ft in 9 12; do echo "NET_R=$r KEEPER_FT=$ft"; NGAMES=24 NPROC=$(nproc) NET_R=$r KEEPER_FT=$ft THROW_SPLIT=1 python3 split_game_cmp.py 2>&1 | tail -1; done; done
