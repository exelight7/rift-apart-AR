# SPDX-License-Identifier: GPL-3.0-only
"""Build the Linux AppImage from the tested PyInstaller directory."""
from pathlib import Path
import hashlib,os,shutil,subprocess,urllib.request
ROOT=Path(__file__).resolve().parents[1];appdir=ROOT/'build/AppDir';appdir.mkdir(parents=True,exist_ok=True)
shutil.copytree(ROOT/'build/dist/RiftApartAR',appdir/'usr/bin',dirs_exist_ok=True,symlinks=True)
for name in ['NOTICE.md','RELEASE_NOTES.md','LICENSE-GPL-3.0.txt','READ-ME.txt']:
    shutil.copy2(ROOT/'build/dist/RiftApartAR'/name,appdir/name)
shutil.copytree(ROOT/'build/dist/RiftApartAR/licenses',appdir/'licenses',dirs_exist_ok=True)
for name in ['rift-apart-ar.png','.DirIcon']:shutil.copy2(ROOT/'installer/assets/icon.png',appdir/name)
(appdir/'AppRun').write_text('#!/bin/sh\nset -eu\nRIFT_APPDIR=${APPDIR:-$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)}\nexport QT_MEDIA_BACKEND=ffmpeg\nexec "$RIFT_APPDIR/usr/bin/RiftApartAR" "$@"\n',encoding='utf-8');(appdir/'AppRun').chmod(0o755)
(appdir/'rift-apart-ar.desktop').write_text('[Desktop Entry]\nType=Application\nName=Rift Apart AR\nName[ar]=مثبت تعريب راتشت وكلانك\nExec=RiftApartAR\nIcon=rift-apart-ar\nCategories=Game;Utility;\nTerminal=false\n',encoding='utf-8')
tool=ROOT/'build/appimagetool.AppImage'
expected='95cbe7cce9717fce90c484e34052ee7c7f1d7635b33c12525b4776826a7d29b6'
if not tool.exists():
    with urllib.request.urlopen('https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage',timeout=90) as r:tool.write_bytes(r.read())
assert hashlib.sha256(tool.read_bytes()).hexdigest()==expected,'AppImage build tool changed; review its new release before updating the checksum'
tool.chmod(0o755);out=ROOT/'build/release/RiftApartAR-v1.0.0-Linux-x86_64.AppImage'
subprocess.run([str(tool),'--no-appstream',str(appdir),str(out)],check=True,env=dict(os.environ,ARCH='x86_64',APPIMAGE_EXTRACT_AND_RUN='1'))
out.with_suffix('.AppImage.sha256').write_text(hashlib.sha256(out.read_bytes()).hexdigest()+'  '+out.name+'\n',encoding='utf-8');print(out.name,out.stat().st_size)
