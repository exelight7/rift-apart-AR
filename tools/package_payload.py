# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];p=R/'installer/payload'
if p.exists():shutil.rmtree(p)
shutil.copytree(R/'build/release_mod',p/'mod')
manifest={'version':'0.2.1','files':{str(f.relative_to(p/'mod')).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((p/'mod').glob('*/*')) if f.is_file()},'legacy':[]}
# Optional known previous local installation. Never include a user path or TOC.
legacy=R/'installer/legacy.json'
if legacy.exists():manifest['legacy']=json.loads(legacy.read_text())
(p/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Payload:',len(manifest['files']),'assets')
