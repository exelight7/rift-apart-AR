# SPDX-License-Identifier: GPL-3.0-only
"""Offline, reversible installer. Game saves and Steam settings are never touched."""
from pathlib import Path
import contextlib, hashlib, json, os, shutil, struct as s, tempfile
import psutil
VERSION='0.2.1'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def running():
    for p in psutil.process_iter(['name']):
        try:
            if (p.info['name'] or '').lower() in ('riftapart.exe','ratchetandclank.exe','ratchetandclanklauncher.exe'):return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):pass
    return False

def check_game(game):
    game=Path(game).expanduser().resolve()
    if not (game/'toc').is_file() or not (game/'d').is_dir():raise ValueError('اختر مجلد اللعبة الذي يحتوي على toc ومجلد d.')
    if (game/'toc').is_symlink() or (game/'d').is_symlink():raise ValueError('ملفات اللعبة المرتبطة رمزيًا غير مدعومة.')
    if running():raise RuntimeError('أغلق اللعبة واللانشر ثم أعد المحاولة.')
    return game

def prepare(toc, mod):
    orig=bytes(toc);b=orig[8:]
    if len(orig)<24 or s.unpack_from('<I',orig)[0]!=0x34e89035:raise ValueError('صيغة toc غير مدعومة.')
    magic,typ,size,n,u=s.unpack_from('<IIIHH',b)
    if magic!=0x44415431 or not 16<=size<=len(b) or not 1<=n<=64:raise ValueError('فهرس اللعبة غير صالح أو إصدار غير مدعوم.')
    table=[s.unpack_from('<III',b,16+i*12) for i in range(n)]
    if any(o+z>len(b) for t,o,z in table):raise ValueError('فهرس اللعبة تالف.')
    sec={t:bytearray(b[o:o+z]) for t,o,z in table}
    ids=list(s.unpack('<'+'Q'*(len(sec[0x506d7b8a])//8),sec[0x506d7b8a]));spans=list(s.iter_unpack('<II',sec[0xede8ada9]))
    arc=sec[0x398abff0];ai=len(arc)//66
    if len(arc)%66 or b'd\\mods\\arabic_loc' in arc:raise ValueError('توجد نسخة تعريب أو تعديلات أخرى؛ يلزم فهرس أصلي موثوق.')
    arc.extend(s.pack('<40sQQIHI',b'd\\mods\\arabic_loc',2678794514496,2678794514496,3844228203,32763,0))
    archive=bytearray(); assets=0
    for p in sorted(Path(mod).glob('*/*')):
        if not p.is_file():continue
        span=int(p.parent.name);asset=int(p.name,16)
        if not 0<=span<len(spans):raise ValueError('نطاق ملف التعريب غير صالح.')
        start,count=spans[span];matches=[i for i in range(start,start+count) if ids[i]==asset]
        if len(matches)!=1:raise ValueError('ملفات اللعبة لا تتوافق مع حزمة التعريب: '+p.name)
        i=matches[0];data=p.read_bytes();head=None
        if data[:4]==b'STG\0':
            _,flags,hs,ts=s.unpack_from('<4I',data)
            if ts or flags&2:raise ValueError('بيانات خامات غير مدعومة.')
            head=data[16:16+hs] if flags&1 else None;data=data[(16+hs+15)//16*16:]
        oldsize,oldai,oldoff,ho=s.unpack_from('<IIIi',sec[0x65bcf461],i*16)
        if head is not None:
            if len(head)!=36:raise ValueError('ترويسة أصل غير مدعومة.')
            if ho<0:ho=len(sec[0x654bded9]);sec[0x654bded9].extend(head)
            else:sec[0x654bded9][ho:ho+36]=head
        s.pack_into('<IIIi',sec[0x65bcf461],i*16,len(data),ai,len(archive),ho)
        archive.extend(data);assets+=1
    if assets!=25:raise ValueError('حزمة التعريب ناقصة.')
    first=min(o for t,o,z in table);res=bytearray(b[:first]);new={}
    for t,o,z in sorted(table,key=lambda x:x[1]):
        res.extend(b'\0'*((-len(res))%16));new[t]=(len(res),len(sec[t]));res.extend(sec[t])
    for j,(t,o,z) in enumerate(table):s.pack_into('<III',res,16+j*12,t,*new[t])
    s.pack_into('<I',res,8,len(res))
    return s.pack('<II',0x34e89035,len(res))+res,bytes(archive)

def verify_payload(payload):
    payload=Path(payload);manifest=json.loads((payload/'manifest.json').read_text(encoding='utf-8'))
    for name,digest in manifest['files'].items():
        p=payload/'mod'/name
        if p.resolve().is_relative_to((payload/'mod').resolve()) and p.is_file() and sha(p)==digest:continue
        raise ValueError('حزمة التثبيت تالفة: '+name)
    return manifest

def atomic(path,data):
    path=Path(path);fd,tmp=tempfile.mkstemp(prefix='.rift-ar-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

@contextlib.contextmanager
def lock(game):
    p=game/'.rift-apart-ar.lock'
    try:fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError:raise RuntimeError('توجد عملية تثبيت أخرى أو قفل متبقٍ. أغلق المثبت الآخر أولًا.')
    try:os.close(fd);yield
    finally:p.unlink(missing_ok=True)

def safe_state(game):
    state=game/'.rift-apart-ar';state.mkdir(exist_ok=True)
    if state.is_symlink():raise ValueError('مجلد النسخة الاحتياطية مرتبط رمزيًا.')
    return state

def install(game,payload,progress=lambda n,t:None):
    game=check_game(game);manifest=verify_payload(payload);state=safe_state(game)
    with lock(game):
        progress(10,'فحص ملفات اللعبة والحزمة…');current=(game/'toc').read_bytes();archive=game/'d/mods/arabic_loc'
        if (state/'state.json').exists():
            record=json.loads((state/'state.json').read_text());original=(state/'toc.original').read_bytes()
            if sha(game/'toc')!=record['installed_toc'] or not archive.exists() or sha(archive)!=record['installed_archive']:raise ValueError('تغيرت ملفات اللعبة منذ التثبيت. تحقق من ملفاتها عبر Steam قبل إعادة التثبيت.')
            if hashlib.sha256(original).hexdigest()!=record['original_toc']:raise ValueError('النسخة الاحتياطية تالفة.')
        else:
            original=current
            if archive.exists() or b'd\\mods\\arabic_loc' in current:
                match=next((x for x in manifest.get('legacy',[]) if hashlib.sha256(current).hexdigest()==x['toc'] and archive.exists() and sha(archive)==x['archive']),None)
                backup=game/'arabic_backup_2026-10-12/toc'
                if not match or not backup.exists() or sha(backup)!=match['original']:raise ValueError('توجد نسخة سابقة غير معروفة. استعد ملفات اللعبة عبر Steam أولًا؛ لن أستبدلها تلقائيًا.')
                original=backup.read_bytes()
        progress(30,'تجهيز التعريب وفحص الفهرس…');newtoc,newarc=prepare(original,Path(payload)/'mod')
        # Snapshot all replaced data before the first mutation. Existing backups
        # are validated above and remain immutable across updates.
        oldarc=archive.read_bytes() if archive.exists() else None
        oldrecord=(state/'state.json').read_bytes() if (state/'state.json').exists() else None
        if not (state/'toc.original').exists():atomic(state/'toc.original',original)
        elif sha(state/'toc.original')!=hashlib.sha256(original).hexdigest():raise ValueError('نسخة احتياطية مختلفة؛ أوقف التثبيت لحمايتها.')
        archive.parent.mkdir(parents=True,exist_ok=True)
        if archive.parent.is_symlink() or archive.is_symlink():raise ValueError('مسار التعريب مرتبط رمزيًا.')
        record={'version':VERSION,'original_toc':hashlib.sha256(original).hexdigest(),'installed_toc':hashlib.sha256(newtoc).hexdigest(),'installed_archive':hashlib.sha256(newarc).hexdigest()}
        progress(65,'تثبيت الملفات وحفظ النسخة الاحتياطية…')
        try:
            atomic(archive,newarc);atomic(game/'toc',newtoc);atomic(state/'state.json',json.dumps(record,indent=2).encode())
        except Exception:
            atomic(game/'toc',current)
            if oldarc is not None:atomic(archive,oldarc)
            else:archive.unlink(missing_ok=True)
            if oldrecord is not None:atomic(state/'state.json',oldrecord)
            else:(state/'state.json').unlink(missing_ok=True)
            raise
        progress(100,'اكتمل التثبيت. اختر English في Steam ثم شغّل اللعبة.');return record

def restore(game,progress=lambda n,t:None):
    game=check_game(game);state=game/'.rift-apart-ar';archive=game/'d/mods/arabic_loc'
    with lock(game):
        if not (state/'state.json').is_file():raise ValueError('لم أجد نسخة مثبتة بهذا التطبيق لاستعادتها.')
        record=json.loads((state/'state.json').read_text());original=state/'toc.original'
        if sha(original)!=record['original_toc']:raise ValueError('النسخة الاحتياطية غير سليمة.')
        if sha(game/'toc')!=record['installed_toc'] or not archive.exists() or sha(archive)!=record['installed_archive']:raise ValueError('تغيرت ملفات اللعبة. لن أستبدلها بنسخة قديمة؛ استخدم التحقق في Steam.')
        progress(40,'استعادة الفهرس الأصلي…');oldtoc=(game/'toc').read_bytes();oldarc=archive.read_bytes();oldrecord=(state/'state.json').read_bytes()
        try:atomic(game/'toc',original.read_bytes());archive.unlink();(state/'state.json').unlink()
        except Exception:
            atomic(archive,oldarc);atomic(game/'toc',oldtoc);atomic(state/'state.json',oldrecord);raise
        progress(100,'تمت استعادة ملفات اللعبة. النسخة الاحتياطية محفوظة.')

def discover():
    candidates=[];homes=[Path.home()/'.local/share/Steam',Path.home()/'.steam/steam',Path.home()/'.var/app/com.valvesoftware.Steam/.local/share/Steam']
    if os.name=='nt':
        homes += [Path(os.environ.get('PROGRAMFILES(X86)','C:/Program Files (x86)'))/'Steam',Path('C:/Steam')]
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Valve\Steam') as k:homes.append(Path(winreg.QueryValueEx(k,'SteamPath')[0]))
        except OSError:pass
    for root in list(homes):
        vdf=root/'steamapps/libraryfolders.vdf'
        if vdf.exists():
            import re
            homes.extend(Path(x.replace('\\\\','\\')) for x in re.findall(r'"path"\s*"([^"]+)"',vdf.read_text(errors='replace')))
    for root in homes:
        p=root/'steamapps/common/Ratchet & Clank - Rift Apart'
        if (p/'toc').is_file() and str(p) not in candidates:candidates.append(str(p))
    return candidates
