cd /home/claude/work/p4
for ft in 9 12; do echo "NET_R=5.5 KEEPER_FT=$ft"; NGAMES=24 NPROC=2 NET_R=5.5 KEEPER_FT=$ft THROW_SPLIT=1 python3 split_game_cmp.py 2>&1 | tail -1; done > net55_out.txt 2>&1
python3 keeper_height_drill.py > keeper_height_drill_out.txt 2>&1
