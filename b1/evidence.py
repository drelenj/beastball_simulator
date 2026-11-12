"""Reproduce M1 tests, three samples, source provenance and portable packet."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import zipfile
from .preservation import historical_hashes

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'b1/evidence'


def source_hashes():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT/'b1').rglob('*')) if p.is_file()
            and '__pycache__' not in str(p) and 'evidence' not in p.parts}


def main():
    OUT.mkdir(exist_ok=True)
    subprocess.run([sys.executable,'-m','b1.m0_manifest'],cwd=ROOT,check=True)
    baseline=historical_hashes(ROOT)
    r=subprocess.run([sys.executable,'-m','unittest','b1.test_m1','-v'],cwd=ROOT,capture_output=True,text=True,timeout=120)
    (OUT/'tests.txt').write_text(r.stdout+r.stderr)
    if r.returncode: raise RuntimeError(r.stderr)
    for case in ('pass','retain','interrupted'):
        subprocess.run([sys.executable,'-m','b1.run','--case',case,'--out',str(OUT/(case+'.json'))],cwd=ROOT,check=True,timeout=45)
    after=historical_hashes(ROOT)
    if baseline != after: raise RuntimeError('B0 source changed')
    (OUT/'b0_source_hashes.json').write_text(json.dumps(baseline,sort_keys=True,indent=2)+'\n')
    manifest={'baseline_commit':'2abe497ca82588cb2d8c871a7aab61daaae95c12',
              'python':platform.python_version(),'platform':platform.platform(),
              'profile':'m1-pass-flight-v1','test_exit_code':r.returncode,
              'b0_source_unchanged':True,'source':source_hashes(),
              'limitations':['Claude behavioral acceptance pending','full T1 ten-case suite not rerun',
                             'general resource queues and locomotion not integrated',
                             'catch cognition and regulation excluded','RNG signatures cover discoverable direct generator attributes',
                             'field option evaluator is a limited provisional B1 policy'],
              'command':'python3 -m b1.evidence'}
    (OUT/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    with zipfile.ZipFile(ROOT/'HP-001_B1_M1_EVIDENCE_PACKET.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted((ROOT/'b1').rglob('*')):
            if p.is_file() and '__pycache__' not in str(p): z.write(p,p.relative_to(ROOT))


if __name__=='__main__': main()
