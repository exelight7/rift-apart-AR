# SPDX-License-Identifier: GPL-3.0-only
"""Install a locally prepared archive, with hashes and rollback backups."""
from pathlib import Path
import argparse,json,hashlib,shutil,datetime,os
p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);p.add_argument('--prepared',type=Path,required=True);a=p.parse_args()
g=a.game;prepared=a.prepared
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((prepared/'manifest.json').read_text())
assert h(g/'toc')==m['original_sha256'],'Game index differs: do not overwrite other mods'
assert h(prepared/'toc')==m['toc_sha256'];assert h(prepared/'arabic_loc')==m['archive_sha256']
assert h(prepared/'toc.original')==m['original_sha256']
if Path('/proc').exists():
 for f in Path('/proc').glob('[0-9]*/comm'):
  try:assert 'riftapart' not in f.read_text().lower(),'Close game/launcher first'
  except OSError:pass
mods=g/'d/mods';mods.mkdir(exist_ok=True)
archive=mods/'arabic_loc';assert not archive.exists(),'Existing Arabic archive; restore clean game or manage previous installation first'
backup=g/('arabic_backup_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir()
shutil.copy2(g/'toc',backup/'toc');shutil.copy2(prepared/'manifest.json',backup/'manifest.json')
try:
 shutil.copy2(prepared/'arabic_loc',archive)
 shutil.copy2(prepared/'toc',g/'toc.arabic.tmp')
 assert h(archive)==m['archive_sha256'] and h(g/'toc.arabic.tmp')==m['toc_sha256']
 os.replace(g/'toc.arabic.tmp',g/'toc')
 assert h(g/'toc')==m['toc_sha256']
except BaseException:
 shutil.copy2(backup/'toc',g/'toc')
 if archive.exists():archive.unlink()
 tmp=g/'toc.arabic.tmp'
 if tmp.exists():tmp.unlink()
 raise
print('Installed. Original index backup:',backup)
