"""Generate the reproducible M0 contract and preservation input hash manifest."""
import hashlib
import json
from pathlib import Path
from .preservation import load_inventory

ROOT=Path(__file__).resolve().parents[1]
BASELINE_INVENTORY=ROOT/'b1/baseline/B0_2abe497_GIT_BLOBS.json'
INPUTS={
    'readiness_plan':('coordination_review/HP-001_HP-002_B1_IMPLEMENTATION_READINESS_AND_MILESTONE_PLAN.md','44f55b0a4b7439fbbef254bcf1b9ce7fd5ab8e3cfe030c94c35bca91b54bbd47'),
    'o4_v3_5':('upload/HP-002_T6-O4_v3.5_DRAFT.md','0acaa65488fa2786981f8b81ef35f3d1644e5e21c91e9c13bc061d1ce15c2596'),
    'o5_v3_5':('upload/HP-002_T6-O5_v3.5_DRAFT.md','904c6bd0dce8ab82abffe0ff970df8c6216dee6b0c6fb3a6eac2fab76ea40572'),
    'v3_5_review_disposition':('upload/HP-002_V3.5_CODEX_REVIEW_DISPOSITION.md','7412c985f9d59aed8d5a7ce50990771ba17608daac722da63f218ccf832109b9'),
    't1_closure':('T1_closure_evidence/T1_CLOSURE_REPORT.md','687cbefd47e233d123d52eaa2fccd4a1f2e207ed717786dc3f2dde143ef11eb6'),
    't1_cross_environment':('T1_closure_evidence/T1_CROSS_ENV_COMPARISON.json','af989e65a1e748d2773d75d2bc77365dcb935fb8ca2cd1b8c487a6bf20087cc0'),
    't1_packet':('T1_CLOSURE_EVIDENCE.zip','2ab7c5581681b10c90aa461b2dd07d0a761aa42d8b3e05b93ed738c524e5c3b0'),
    't2_evidence_report':('HP-001_T2_EVIDENCE_REPORT.md','fd2cf9eeba67081d8c087123ee1dd6bb2aa9a7153b9fb07a71fce35a9c160eee'),
    't2_packet':('HP-001_T2_EVIDENCE_PACKET.zip','a40744b655f5783865434ba1f62da1162fde4ce1404514611a2035339d6b4982'),
    't3_manifest':('HP-001_T3_FINAL_PACKET/MANIFEST.json','a28ae50e8fc46d00f0712dbdbc9a668d04310aadb92343847acc1a8e6182063e'),
    't3_packet':('HP-001_T3_EVIDENCE_PACKET.zip','8d9f93436eec5ef19ba6562ec3eb09d9f37ef1f3e7dc8516c92ddb72d09ee61c'),
    't4_manifest':('HP-001_T4_EVIDENCE_PACKET/MANIFEST.json','a5f3dc8e4b122c192df61d23979cc02bd49363aa071a00f7ba90c4ee0e496a99'),
    't4_packet':('HP-001_T4_EVIDENCE_PACKET.zip','634ac16eb6a5c2e4cfa806bc8bab721e510a9c3725ce13759ab64e9630380b82'),
    't5_manifest':('HP-001_T5_EVIDENCE_PACKET/MANIFEST.json','551c4709cdd3cf8ab7a49257ab1961ea7cc32eba6dd529d54c03aa115283effd'),
    't5_packet':('HP-001_T5_EVIDENCE_PACKET.zip','824b83c1591fc22e6358e76d9d1ef122959547a1c67ecc9f00dccb11461583bb'),
}

def main():
    records={}
    for name,(relative,expected) in INPUTS.items():
        path=ROOT/relative
        if not path.is_file():
            records[name]={'path':relative,'available':False,'sha256':expected}
        else:
            actual=hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != expected:
                raise RuntimeError(f'frozen input mismatch: {relative}')
            records[name]={'path':relative,'available':True,'sha256':actual}
    algorithm,source_files,inventory_meta=load_inventory(BASELINE_INVENTORY)
    source_inventory=json.dumps(source_files,sort_keys=True,separators=(',',':')).encode()
    obj={'manifest_schema':'b1-m0-freeze-manifest-v1',
         'baseline':{'profile':'B0-P4-DEFAULT',
                     'accepted_commit':'2abe497ca82588cb2d8c871a7aab61daaae95c12'},
         'contract_freeze':'B1 Core Slice v1 plus IMPL-01..10 in M0_CLOSURE.md',
         'm1_authorized':True,'m1_accepted':True,'m2_authorized':False,
         'canonical_b0_source_inventory':{'file_count':len(source_files),
               'inventory_sha256':hashlib.sha256(source_inventory).hexdigest(),
               'algorithm':algorithm,'commit':inventory_meta.get('commit'),
               'note':'Canonical committed blob inventory; untracked workspace files are excluded.'},
         'inputs':records}
    out=ROOT/'b1'/'M0_FREEZE_MANIFEST.json'
    out.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
    print(out)

if __name__=='__main__': main()
