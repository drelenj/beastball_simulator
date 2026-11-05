cd /home/claude/work/p4
for cfg in "6 0" "3 9" "3 10" "3 11" "3 12"; do set -- $cfg
 echo "NET_R=$1 KEEPER_FT=$2"; NET_R=$1 KEEPER_FT=$2 THROW_SPLIT=1 python3 split_game_cmp.py 2>&1 | tail -1
done
