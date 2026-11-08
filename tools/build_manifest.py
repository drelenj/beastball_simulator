#!/usr/bin/env python3
"""Build/verify audit/HP-002_SPEC_MANIFEST.json. Usage: build_manifest.py build|verify [--ext DIR_T2 DIR_T3]"""
import hashlib, json, sys, os, subprocess
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''):h.update(c)
    return h.hexdigest()
GOV=[("HP-002_B1_FINAL_APPROVAL_CANDIDATE_v1.0-rc2","audit/HP-002_B1_FINAL_APPROVAL_CANDIDATE_v1.0-rc2.md","governing candidate (self-contained); contains the T5/T6 conflict register")]
SUPER=[("HP-002_B1_FINAL_APPROVAL_CANDIDATE_v1.0-rc1","audit/HP-002_B1_FINAL_APPROVAL_CANDIDATE_v1.0-rc1.md"),
 ("HP-002_B1_FINAL_CANDIDATE_SPEC","audit/HP-002_B1_FINAL_CANDIDATE_SPEC.md"),
 ("HP-002_reconciliation_spec_DRAFT_r1","audit/HP-002_reconciliation_spec_DRAFT_r1.md"),
 ("HP-002_reconciliation_spec_DRAFT_r2","audit/HP-002_reconciliation_spec_DRAFT_r2.md"),
 ("HP-002_reconciliation_spec_DRAFT_r3","audit/HP-002_reconciliation_spec_DRAFT_r3.md")]
EVID=[("HP-002_stageA_decision_ownership","audit/HP-002_stageA_decision_ownership.md"),
 ("HP-002_stageB_report","audit/HP-002_stageB_report.md"),
 ("T1_EVIDENCE_PACKET","baseline/b0_claude_env/T1_EVIDENCE_PACKET.md"),
 ("T1_COMPLETION_ADDENDUM","baseline/b0_claude_env/T1_COMPLETION_ADDENDUM.md"),
 ("T1_MANIFEST","baseline/b0_claude_env/MANIFEST.json"),
 ("NI4_SUMMARY","audit/ni4/NI4_SUMMARY.json")]
TOOLS=["audit_fields","audit_probes","audit_update_jumps","audit_archer","audit_cadence","audit_neutrality","audit_canary","audit_trace","ni4_capture"]
import glob, re
SPEC="audit/HP-002_B1_FINAL_APPROVAL_CANDIDATE_v1.0-rc2.md"
EXT_ZIPS={"HP-001_T5_EVIDENCE_PACKET.zip":"824b83c1591fc22e6358e76d9d1ef122959547a1c67ecc9f00dccb11461583bb",
          "HP-001_T6_DESIGN_PACKET.zip":"9c04c1b1c697d22fedef550ef581eab395a0904929c2934cc53aa3048040b6f7"}
def files_under(*dirs):
    out=[]
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(ROOT,d,"**","*"),recursive=True)):
            if os.path.isfile(f): out.append(os.path.relpath(f,ROOT))
    return out
def register():
    rows=[]
    for l in open(os.path.join(ROOT,SPEC),encoding="utf-8"):
        m=re.match(r"\| ((?:TI|CT|CS|PO|RN|VG|SQ)-\d+) \|",l)
        if m:
            cells=[c.strip() for c in l.strip().strip("|").split(" | ")]
            code=re.match(r"(RES-A|RES-P|OPEN-D|OPEN-C|INFO)",cells[-1]).group(1)
            rows.append({"id":m.group(1),"topic":cells[1],"verdict":cells[-2],"disposition":code})
    return rows
UNRESOLVED=[{"id":"U-1","what":"Keeper protection cells KP-01..KP-14","state":"UNRESOLVED"},
 {"id":"U-2","what":"zone-clock reset rule (PA basis direction recorded); Keeper phase basis KP-12","state":"UNRESOLVED"},
 {"id":"U-3","what":"zone geometry G-1..G-6, separate ball and athlete predicates","state":"UNRESOLVED"},
 {"id":"U-4","what":"rules-state transition table; scenarios U4-01..U4-13 incl. bounce-pass and control-at-release","state":"UNRESOLVED"},
 {"id":"SELF-1","what":"exactness of an athlete's knowledge of own capabilities","state":"needs DreLen"},
 {"id":"R-RS","what":"ruleset 1.0.1 vs 1.0.2 for Archer freeze eligibility","state":"needs DreLen"},
 {"id":"T6-O4","what":"supersession priority among simultaneous commands","state":"needs approval"},
 {"id":"T6-O5","what":"causal-ID encoding and telemetry schema version","state":"needs approval"},
 {"id":"A-1","what":"approve refined dependency order and measurement-first Gate C","state":"needs DreLen"},
 {"id":"T6-O3","what":"Keeper arbitration policy","state":"deferred (before Keeper migration)"},
 {"id":"T6-O6","what":"native numeric tolerances","state":"deferred (native track)"}]
RESOLVED_FIXED=["RST-1","IA-001","C-7","O1-O10","R1","ARC-1","KP-A","ZR-1","ZR-2"]
def build(ext):
    reg=register()
    m={"manifest_version":"2.0","spec":"HP-002 B1 Final Approval Candidate v1.0-rc2","spec_version":"1.0-rc2",
       "status":"CANDIDATE - not accepted; B1 implementation NOT authorized",
       "base_repo_commit_before_this_change":subprocess.check_output(["git","-C",ROOT,"rev-parse","HEAD"]).decode().strip(),
       "b0_baseline":{"name":"B0-P4-DEFAULT","commit":"2abe497"},
       "contract_v1":{"status":"NOT FROZEN","requires":["U-1","U-2","U-3","U-4","SELF-1","R-RS","T6-O4","T6-O5"]},
       "governing":[{"id":i,"path":p,"role":r,"sha256":sha(os.path.join(ROOT,p))} for i,p,r in GOV],
       "superseded_non_governing":[{"id":i,"path":p,"sha256":sha(os.path.join(ROOT,p))} for i,p in SUPER],
       "claude_evidence":[{"id":i,"path":p,"sha256":sha(os.path.join(ROOT,p))} for i,p in EVID]+
            [{"id":"t5_replication","path":p,"sha256":sha(os.path.join(ROOT,p))} for p in files_under("audit/t5_replication")],
       "claude_tools":[{"path":f"tools/{t}.py","sha256":sha(os.path.join(ROOT,"tools",t+".py"))} for t in TOOLS+["build_manifest"]],
       "codex_evidence":{
         "T1":{"status":"received, accepted","hash_source":"baseline/b0_claude_env/runs/*.json"},
         "T2":{"status":"received, read"},"T3":{"status":"received, read"},
         "T4":{"status":"NOT RECEIVED by Claude; not governing; referenced by T5/T6 (report 606e7a79..., packet 634ac16e...)"},
         "T5":{"status":"received 2026-11-08, read; unit suite and short seed-1 equivalence replicated","packet_zip_sha256":EXT_ZIPS["HP-001_T5_EVIDENCE_PACKET.zip"]},
         "T6":{"status":"received 2026-11-08, read; packet manifest verified","packet_zip_sha256":EXT_ZIPS["HP-001_T6_DESIGN_PACKET.zip"]},
         "copies_read_only":[{"path":p,"sha256":sha(os.path.join(ROOT,p))} for p in files_under("baseline/codex_evidence")]},
       "decisions":{"resolved_fixed":RESOLVED_FIXED,"unresolved":UNRESOLVED},
       "conflict_register":{"source":SPEC,"rows":reg,
            "counts":{k:sum(1 for r in reg if r["disposition"]==k) for k in("RES-A","RES-P","OPEN-D","OPEN-C","INFO")}},
       "note":"Verify with: python3 tools/build_manifest.py verify"}
    json.dump(m,open(os.path.join(ROOT,"audit/HP-002_SPEC_MANIFEST.json"),"w"),indent=1)
def verify():
    m=json.load(open(os.path.join(ROOT,"audit/HP-002_SPEC_MANIFEST.json")));bad=0
    lists=[m["governing"],m["superseded_non_governing"],m["claude_evidence"],m["claude_tools"],m["codex_evidence"]["copies_read_only"]]
    for sec in lists:
        for e in sec:
            ok=sha(os.path.join(ROOT,e["path"]))==e["sha256"];bad+=not ok;print("OK  " if ok else "BAD ",e["path"])
    reg=register();ok=reg==m["conflict_register"]["rows"];bad+=not ok;print("OK  " if ok else "BAD ","conflict register matches spec (%d rows)"%len(reg))
    print("MANIFEST VERIFIED" if not bad else f"{bad} MISMATCH");return bad
if __name__=="__main__":
    if sys.argv[1]=="build":build({})
    else:sys.exit(verify())
