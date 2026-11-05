#!/bin/bash
export PLAT=1 PLAT_H=15 PLAT_SET=5 RULESET=1.0.2 ARROW_V=250 QUIVER_POSS=1 PRISM=1 PRISM_DRIVE=1 PRISM_SOFT=1 PRISM_TRACKID=1
S=1,2,3,4,5,6,7,8,9,10
cfgs=("base:{}")
for r in vision awareness clarity reaction focus; do for v in 0.1 0.9; do cfgs+=("${r}_${v}:{\"$r\":$v}"); done; done
printf '%s\n' "${cfgs[@]}" | xargs -P 2 -I{} bash -c 'c="{}"; tag=${c%%:*}; js=${c#*:}; PRISM_RATINGS="$js" python3 plat_study.py sw_$tag '$S' > sw_$tag.log 2>&1'
echo done > sweep_done
