"""Reproduce M1 tests, three samples, source provenance and portable packet."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import zipfile
from .preservation import canonical_hashes, verify_baseline

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'b1/evidence'
BASELINE=ROOT/'b1/baseline/B0_2abe497_GIT_BLOBS.json'


def source_hashes():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT/'b1').rglob('*')) if p.is_file()
            and '__pycache__' not in str(p) and 'evidence' not in p.parts}


def main():
    OUT.mkdir(exist_ok=True)
    verify_baseline(ROOT, BASELINE)
    subprocess.run([sys.executable,'-m','b1.m0_manifest'],cwd=ROOT,check=True)
    baseline=canonical_hashes(ROOT,BASELINE)
    r=subprocess.run([sys.executable,'-m','unittest','b1.test_m1','b1.test_g1','-v'],cwd=ROOT,capture_output=True,text=True,timeout=180)
    (OUT/'tests.txt').write_text(r.stdout+r.stderr)
    if r.returncode: raise RuntimeError(r.stderr)
    for case in ('pass','retain','interrupted'):
        subprocess.run([sys.executable,'-m','b1.run','--case',case,'--out',str(OUT/(case+'.json'))],cwd=ROOT,check=True,timeout=45)
    after=canonical_hashes(ROOT,BASELINE)
    if baseline != after: raise RuntimeError('B0 source changed')
    manifest={'baseline_commit':'2abe497ca82588cb2d8c871a7aab61daaae95c12',
              'python':platform.python_version(),'platform':platform.platform(),
              'profile':'m1-carrier-pass-or-carry-v2','test_exit_code':r.returncode,
              'b0_source_unchanged':True,'source':source_hashes(),
              'limitations':['M1 accepted at 4b19719; this packet preserves its scoped claims',
                             '37 matrix failures retain unknown attribution',
                             'conditional lane effect does not establish net defensive improvement',
                             'full T1 ten-case suite not rerun',
                             'general resource queues not integrated',
                             'receiver catch cognition and regulation excluded','RNG signatures cover discoverable direct generator attributes',
                             'field option evaluator is a limited provisional B1 policy'],
              'command':'python3 -m b1.evidence'}
    (OUT/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    with zipfile.ZipFile(ROOT/'HP-001_B1_M1_EVIDENCE_PACKET.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted((ROOT/'b1').rglob('*')):
            if p.is_file() and '__pycache__' not in str(p): z.write(p,p.relative_to(ROOT))


if __name__=='__main__': main()
