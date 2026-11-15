"""Reproducible workbook import. Primary sheet wins; no synthetic player identities."""
import sys,json,hashlib,collections,unicodedata,re
from pathlib import Path
import openpyxl
src=Path(sys.argv[1]); root=Path(__file__).resolve().parents[1]
w=openpyxl.load_workbook(src,data_only=True)
rows=list(w['All 712 Players'].values); headers=rows[0]
players=[dict(zip(headers,r)) for r in rows[1:] if r[0]]
assert len(players)==712
teams=[]; conflicts=[]
colors=['#2479ed','#e93849','#f58332','#bac857','#ff592f','#a673dd','#2ab4af','#edbf58','#48ba79','#8d91ed','#3cbbcc','#dd729e','#7387ef','#cd3f5d','#f2aa42','#d2ad42','#5dc1ce','#6b90a4','#b6a6da','#ad5353','#cf7740','#6baf92','#489fbd','#ff922d','#ddbf78','#47b7be']
for i,name in enumerate(dict.fromkeys(p['Franchise'] for p in players)):
 ps=[p for p in players if p['Franchise']==name]; starters=[p for p in ps if p['Opening-night role']=='Projected starter']
 assert len(starters)==12,(name,len(starters))
 assert sum(p['Position']=='KPR' for p in starters)==1
 assert sum(p['Position']=='ARC' for p in starters)==1
 slug=re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode().lower()).strip('-')
 teams.append({'id':slug,'name':name,'league':'NBL','color':colors[i],'accent':'#f3ead4','formation':starters[0]['Formation'],'players':ps,'starters':[p['Player ID'] for p in starters]})
 sheet=list(w[w.sheetnames[i+2]].values); sh=sheet[0]
 for row in sheet[1:]:
  d=dict(zip(sh,row)); p=next((p for p in ps if p['Player ID']==d['Player ID']),None)
  if p and p['Opening-day OVR']!=d['Opening-day OVR']:
   conflicts.append({'team':name,'playerId':p['Player ID'],'primary':p['Opening-day OVR'],'teamSheet':d['Opening-day OVR']})
assert len(teams)==26
out={'source':{'file':'NBL_2026-27_Opening_Night_Rosters_CANON_OVR.xlsx','sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sheet':'All 712 Players','players':len(players),'teams':len(teams),'note':'Primary sheet used verbatim. Team sheets disagree on some Opening-day OVR values. No jersey numbers provided; on-field bibs are temporary lineup labels.'},'teams':teams}
(root/'src/league.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(root/'evidence/roster-crosscheck.json').write_text(json.dumps({'conflicts':conflicts,'policy':'All 712 Players is authoritative for this import'},ensure_ascii=False,indent=2)+'\n')
print('Imported',len(players),'players,',len(teams),'teams;',len(conflicts),'rating differences recorded')
