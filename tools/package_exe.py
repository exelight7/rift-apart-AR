# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import shutil,hashlib
ROOT=Path(__file__).resolve().parents[1];src=ROOT/'build/standalone/RiftApartAR.exe';out=ROOT/'build/release/RiftApartAR-v1.0.1-Windows-x64.exe';shutil.copy2(src,out);out.with_suffix('.exe.sha256').write_text(hashlib.sha256(out.read_bytes()).hexdigest()+'  '+out.name+'\n',encoding='utf-8');print(out.name,out.stat().st_size)
