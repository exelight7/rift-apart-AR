# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import argparse,hashlib,shutil,zipfile,os,sys
R=Path(__file__).resolve().parents[1];a=argparse.ArgumentParser();a.add_argument('--platform',required=True);a.add_argument('--metadata-only',action='store_true');args=a.parse_args()
p=R/'build/dist/RiftApartAR'
shutil.copytree(R/'installer/licenses',p/'licenses',dirs_exist_ok=True)
# Preserve license notices shipped by the exact wheels used for each platform.
from importlib.metadata import distribution, PackageNotFoundError
for name in ('PySide6','PySide6_Essentials','PySide6_Addons','shiboken6','psutil','pyinstaller'):
 try:
  dist=distribution(name)
  for entry in dist.files or []:
   if any(x in str(entry).lower() for x in ('license','copying')) and dist.locate_file(entry).is_file():
    dest=p/'licenses'/name/str(entry).replace('..','_')
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dist.locate_file(entry),dest)
 except PackageNotFoundError:pass
for name in ('NOTICE.md','RELEASE_NOTES.md'):shutil.copy2(R/name,p/name)
shutil.copy2(R/'tools/LICENSE',p/'LICENSE-GPL-3.0.txt')
(p/'READ-ME.txt').write_text('Rift Apart AR v1.0.2\n\nExtract the entire archive before launching RiftApartAR.\nLinux: chmod +x RiftApartAR && ./RiftApartAR\nWindows: run RiftApartAR.exe\nClose the game and launcher. Select the game folder, then Install.\nKeep the Steam game language set to English.\nThe Restore button restores the original game index.\n\nArabic documentation and editable source:\nhttps://github.com/exelight7/rift-apart-AR\n',encoding='utf-8')
out=R/'build/release';out.mkdir(parents=True,exist_ok=True)
if args.metadata_only:
 print('Application notices and licenses packaged');sys.exit(0)
dest=out/f'RiftApartAR-v1.0.2-{args.platform}.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in sorted(p.rglob('*')):
  if f.is_symlink():
   # Materialize PyInstaller library symlinks for ZIP extractors on all OSes.
   info=zipfile.ZipInfo(str(f.relative_to(p.parent)).replace('\\','/'));info.external_attr=(0o100755<<16);info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,f.read_bytes())
  elif f.is_file():z.write(f,f.relative_to(p.parent))
digest=hashlib.sha256(dest.read_bytes()).hexdigest();dest.with_suffix('.zip.sha256').write_text(digest+'  '+dest.name+'\n');print(dest.name,dest.stat().st_size)
