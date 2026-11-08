#!/usr/bin/env python3
"""Build/verify audit/HP-002_SPEC_MANIFEST.json. Usage: build_manifest.py build|verify [--ext DIR_T2 DIR_T3]"""
import hashlib, json, sys, os, subprocess
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''):h.update(c)
    return h.hexdigest()
GOV=[("HP-002_B1_FINAL_APPROVAL_CANDIDATE_v1.0-rc1","audit/HP-002_B1_FINAL_APPROVAL_CANDIDATE_v1.0-rc1.md","governing candidate (self-contained)")]
SUPER=[("HP-002_B1_FINAL_CANDIDATE_SPEC","audit/HP-002_B1_FINAL_CANDIDATE_SPEC.md"),
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
def build(ext):
    m={"manifest_version":"1.0","spec":"HP-002 B1 Final Approval Candidate v1.0-rc1","status":"CANDIDATE - not accepted; B1 implementation NOT authorized",
       "base_repo_commit_before_this_change":subprocess.check_output(["git","-C",ROOT,"rev-parse","HEAD"]).decode().strip(),
       "b0_baseline":{"name":"B0-P4-DEFAULT","commit":"2abe497"},
       "governing":[{"id":i,"path":p,"role":r,"sha256":sha(os.path.join(ROOT,p))} for i,p,r in GOV],
       "superseded_non_governing":[{"id":i,"path":p,"sha256":sha(os.path.join(ROOT,p))} for i,p in SUPER],
       "claude_evidence":[{"id":i,"path":p,"sha256":sha(os.path.join(ROOT,p))} for i,p in EVID],
       "claude_tools":[{"path":f"tools/{t}.py","sha256":sha(os.path.join(ROOT,"tools",t+".py"))} for t in TOOLS],
       "codex_evidence":{
         "T1":{"status":"received, accepted","hash_source":"baseline/b0_claude_env/runs/*.json"},
         "T2":{"status":"received, read","file":"HP-001_T2_EVIDENCE_REPORT.md","sha256":ext.get("t2")},
         "T3":{"status":"received, read","file":"HP-001_T3_EVIDENCE_REPORT.md","sha256":ext.get("t3")},
         "T4":{"status":"NOT RECEIVED by Claude (not referenced as governing)"},
         "T5":{"status":"completed and accepted per DreLen; NOT RECEIVED by Claude; content not incorporated"},
         "T6":{"status":"completed and accepted per DreLen; NOT RECEIVED by Claude; content not incorporated"}},
       "note":"The repo commit that contains this manifest is the commit whose tree holds these hashes; verify with: tools/build_manifest.py verify"}
    json.dump(m,open(os.path.join(ROOT,"audit/HP-002_SPEC_MANIFEST.json"),"w"),indent=1)
def verify():
    m=json.load(open(os.path.join(ROOT,"audit/HP-002_SPEC_MANIFEST.json")));bad=0
    for sec in("governing","superseded_non_governing","claude_evidence","claude_tools"):
        for e in m[sec]:
            ok=sha(os.path.join(ROOT,e["path"]))==e["sha256"];bad+=not ok;print("OK  " if ok else "BAD ",e["path"])
    print("MANIFEST VERIFIED" if not bad else f"{bad} MISMATCH");return bad
if __name__=="__main__":
    if sys.argv[1]=="build":
        ext={}
        if len(sys.argv)>3:
            ext={"t2":sha(sys.argv[3]),"t3":sha(sys.argv[4])}
        build(ext)
    else:sys.exit(verify())
