"""Optimize authenticated local originals; never remove alpha or change aspect ratio."""
from pathlib import Path
import json,hashlib
from PIL import Image
root=Path(__file__).resolve().parents[1]
p=root/'src/logos.json'; manifest=json.loads(p.read_text())
for a in manifest['assets']:
 if a['status'].startswith('unmapped'): continue
 src=Path(a['sourcePath'])
 im=Image.open(src)
 a['sourceSha256']=hashlib.sha256(src.read_bytes()).hexdigest()
 a['sourceDimensions']=list(im.size)
 a['hasAlpha']='A' in im.getbands() or 'transparency' in im.info
 im.thumbnail((512,512),Image.Resampling.LANCZOS)
 im.save(root/'public'/a['localPath'].lstrip('/'),quality=90,method=6)
 a['optimizedDimensions']=list(im.size)
 a['optimizedSha256']=hashlib.sha256((root/'public'/a['localPath'].lstrip('/')).read_bytes()).hexdigest()
print('Optimized',sum(not a['status'].startswith('unmapped') for a in manifest['assets']),'verified logo mappings')
p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
