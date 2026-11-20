"""Score distributions from the NBL 25-26 (men) and MBL 2026 (women) season logs (owner's Drive)."""
import openpyxl, statistics as st, json, sys
def games(f, hs_col, as_col):
    ws=openpyxl.load_workbook(f,read_only=True,data_only=True)['Schedule']; out=[]
    for r in ws.iter_rows(values_only=True):
        r=list(r)
        try: h=int(r[hs_col]); a=int(r[as_col])
        except (TypeError,ValueError,IndexError): continue
        out.append((h,a))
    return out
def pct(x,p): x=sorted(x); return x[min(len(x)-1,int(p/100*len(x)))]
res={}
for name,f,hc,ac in [('NBL men 25-26','NBL_25-26.xlsx',4,5),('MBL women 2026','MBL_2026.xlsx',4,5)]:
    g=games(f,hc,ac); team=[s for p in g for s in p]; tot=[h+a for h,a in g]; mar=[abs(h-a) for h,a in g]
    r=dict(games=len(g), team_ppg_mean=round(st.mean(team),1), team_ppg_sd=round(st.pstdev(team),1),
      team_p5=pct(team,5), team_p25=pct(team,25), team_median=pct(team,50), team_p75=pct(team,75), team_p95=pct(team,95), team_min=min(team), team_max=max(team),
      total_mean=round(st.mean(tot),1), total_sd=round(st.pstdev(tot),1), total_p5=pct(tot,5), total_median=pct(tot,50), total_p95=pct(tot,95),
      margin_mean=round(st.mean(mar),1), margin_median=pct(mar,50), margin_p90=pct(mar,90), one_score_games_share_le5=round(sum(m<=5 for m in mar)/len(mar),3),
      home_win_share=round(sum(h>a for h,a in g)/len(g),3), home_minus_away_mean=round(st.mean([h-a for h,a in g]),2), ties=sum(h==a for h,a in g),
      score_parity_odd_share=round(sum(s%2 for s in team)/len(team),3))
    res[name]=r
print(json.dumps(res,indent=1))
