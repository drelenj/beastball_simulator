"""Locomotion 1.0 freeze: fails if any frozen file changes.  To change physics, make a new version and a new manifest."""
import hashlib, json, unittest
from pathlib import Path
R = Path(__file__).resolve().parent
class Freeze(unittest.TestCase):
    def test_files_match_manifest(self):
        man = json.load(open(R / 'LOCOMOTION_1_0_MANIFEST.json'))
        for f, h in man['files'].items(): self.assertEqual(hashlib.sha256((R / f).read_bytes()).hexdigest(), h, msg=f)
if __name__ == '__main__': unittest.main()
