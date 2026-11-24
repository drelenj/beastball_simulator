"""Turn raw RB-3.27 rollout, benchmark and match evidence into report tables."""
import argparse
import csv
import json
from math import sqrt
from pathlib import Path
from statistics import mean, median, stdev


def get(source,name):
    return json.loads((source/name).read_text())


def match_row(name,row):
    return {'match':name,'teams':row.get('teams',()),'seed':row['seed'],
            'score':[row['score'][t] for t in ('A','B')],
            'possessions':[row['possessions'][t]['count'] for t in ('A','B')],
            'share_ending_in_attempt':[row['possessions'][t]['share_ending_in_attempt'] for t in ('A','B')],
            'shot_releases':[row['team_stats'][t].get('shots',0) for t in ('A','B')],
            'carry_attempts':[row['carry_attempts'][t]['attempts'] for t in ('A','B')],
            'margin_B_minus_A':row['score']['B']-row['score']['A'],
            'status':row['status'],'trace':row['trace_hash'],'state':row['state_hash'],
            'restart_completion':row['restart_completion_ratio']}


def summarise(rows):
    score = [s for row in rows for s in row['score']]
    possessions = [p for row in rows for p in row['possessions']]
    attempts = [p for row in rows for p in row['share_ending_in_attempt'] if p is not None]
    return {'matches':len(rows),'median_team_score':median(score),
            'median_team_possessions':median(possessions),'mean_team_possessions':mean(possessions),
            'possessions_range':[min(possessions),max(possessions)],
            'mean_terminal_attempt_share':mean(attempts) if attempts else None,
            'match_nonfinal':sum(row['status']!='final' for row in rows),
            'restart_completion':min(row['restart_completion'] for row in rows)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    source=args.directory
    all_rows={}
    summaries={}
    for label in ('anchor','soak-off','soak-on'):
        rows=[match_row(path.stem,get(path.parent,path.name)) for path in sorted((source/label).glob('*.json'))]
        if not rows:
            continue
        all_rows[label]=rows
        summaries[label]=summarise(rows)
        if label.startswith('soak'):
            main_rows=[row for row in rows if row['match'].startswith('0-')]
            margins=[row['margin_B_minus_A'] for row in main_rows]
            summaries[label]['ala_vs_garvian']=summarise(main_rows)|{
                'mean_margin':mean(margins),
                'margin_se':stdev(margins)/sqrt(len(margins)) if len(margins)>1 else None,
                'ala_wins':sum(m>0 for m in margins),'garvian_wins':sum(m<0 for m in margins),
                'ties':sum(m==0 for m in margins),
            }
        elif label=='anchor':
            for tag in ('real','control'):
                summaries[label][tag]=summarise([r for r in rows if r['match'].startswith(tag)])
    if (source/'bench-on-1-repeat.json').exists():
        base,core,learned=(median(get(source,f'bench-{mode}-{seed}.json')['cpu_ms_per_step']
                                  for seed in (1,3)) for mode in ('rb322','off','on'))
        repeat=get(source,'bench-on-1-repeat.json')
        first=get(source,'bench-on-1.json')
        summaries['performance']={'rb322':base,'core_off':core,'core_on':learned,
                                  'off_vs_rb322':core/base-1,'on_vs_rb322':learned/base-1,
                                  'on_vs_off':learned/core-1,
                                  'learned_repeat_matches':all(first[k]==repeat[k] for k in (
                                      'trace_hash','state_hash','config_digest','score','steps'))}
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'match-summary.json').write_text(json.dumps(summaries,sort_keys=True,indent=2)+'\n')
    with (args.out/'matches.csv').open('w',newline='') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(('mode','match','seed','team_A','team_B','score_A','score_B',
                         'possessions_A','possessions_B','terminal_attempt_share_A','terminal_attempt_share_B',
                         'shot_releases_A','shot_releases_B','carry_attempts_A','carry_attempts_B',
                         'margin_B_minus_A','status','restart_completion','trace','state'))
        for mode,rows in all_rows.items():
            for row in rows:
                writer.writerow((mode,row['match'],row['seed'],*(row['teams'] or ('A','B')),
                                 *row['score'],*row['possessions'],*row['share_ending_in_attempt'],
                                 *row['shot_releases'],*row['carry_attempts'],row['margin_B_minus_A'],
                                 row['status'],row['restart_completion'],row['trace'],row['state']))


if __name__=='__main__':
    main()
