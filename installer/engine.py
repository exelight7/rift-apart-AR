# SPDX-License-Identifier: GPL-3.0-only
"""Offline, reversible installer. Game saves and Steam settings are never touched."""
from pathlib import Path
import contextlib, hashlib, json, os, shutil, struct as s, tempfile
import psutil
VERSION='1.9.9'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class RecoveryRequired(ValueError):
    """A clean game index must be recovered by Steam before removal."""

def toc_sections(toc):
    if len(toc)<24 or s.unpack_from('<I',toc)[0]!=0x34e89035:
        raise ValueError('صيغة toc غير مدعومة.')
    b=toc[8:]
    magic,typ,size,n,u=s.unpack_from('<IIIHH',b)
    if magic!=0x44415431 or not 16<=size<=len(b) or not 1<=n<=64 or 16+n*12>len(b):
        raise ValueError('فهرس اللعبة تالف أو غير مدعوم.')
    table=[s.unpack_from('<III',b,16+i*12) for i in range(n)]
    if any(o<16+n*12 or o+z>len(b) for t,o,z in table):
        raise ValueError('فهرس اللعبة تالف.')
    sec={t:bytearray(b[o:o+z]) for t,o,z in table}
    if len(sec)!=n or not {0x506d7b8a,0xede8ada9,0x65bcf461,0x398abff0,0x654bded9}<=sec.keys():
        raise ValueError('أقسام فهرس اللعبة غير صالحة.')
    return b,table,sec

def arabic_indices(arc):
    if len(arc)%66:raise ValueError('جدول الأرشيفات تالف.')
    paths=[bytes(arc[i:i+40]).split(b'\0')[0].lower().replace(b'/',b'\\').replace(b'\\\\',b'\\') for i in range(0,len(arc),66)]
    indices=[i for i,p in enumerate(paths) if p==b'd\\mods\\arabic_loc']
    if len(indices)>1:raise RecoveryRequired('توجد أرشيفات تعريب مكررة. أصلح ملفات اللعبة عبر Steam ثم أعد المحاولة.')
    return indices

def is_localized(toc):
    return bool(arabic_indices(toc_sections(toc)[2][0x398abff0]))

def legacy_original(game,current,archive,manifest):
    if not archive.is_file():return None
    match=next((x for x in manifest.get('legacy',[]) if hashlib.sha256(current).hexdigest()==x['toc'] and sha(archive)==x['archive']),None)
    if not match:return None
    candidates=[game/'.rift-apart-ar/toc.original',game/'toc.original',game/'toc.bak',game/'toc.backup']
    candidates.extend(sorted(game.glob('arabic_backup*/toc')))
    for p in candidates:
        if p.is_file() and not p.is_symlink() and sha(p)==match['original']:
            original=p.read_bytes()
            if not is_localized(original):return original
    return None

def saved_original(state,record):
    digest=record['original_toc']
    if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('سجل النسخة الاحتياطية غير صالح.')
    p=state/('toc.'+digest if record.get('backup_format')==2 else 'toc.original')
    if p.is_symlink() or sha(p)!=digest:raise ValueError('النسخة الاحتياطية غير سليمة.')
    return p.read_bytes()

def snapshot(state,name,data):
    p=state/(name+'.'+hashlib.sha256(data).hexdigest())
    if p.is_symlink():raise ValueError('مسار النسخة الاحتياطية مرتبط رمزيًا.')
    if p.exists():
        if p.read_bytes()!=data:raise ValueError('النسخة الاحتياطية غير سليمة.')
    else:atomic(p,data)
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

def prepare(toc, mod, replace_existing=False):
    orig=bytes(toc);b,table,sec=toc_sections(orig)
    ids=list(s.unpack('<'+'Q'*(len(sec[0x506d7b8a])//8),sec[0x506d7b8a]));spans=list(s.iter_unpack('<II',sec[0xede8ada9]))
    arc=sec[0x398abff0];indices=arabic_indices(arc)
    if indices and not replace_existing:raise ValueError('يوجد تعريب بالفعل في الفهرس.')
    ai=indices[0] if indices else len(arc)//66
    if not indices:
        arc.extend(s.pack('<40sQQIHI',b'd\\mods\\arabic_loc',2678794514496,2678794514496,3844228203,32763,0))
    archive=bytearray(); assets=0;replaced=set()
    for p in sorted(Path(mod).glob('*/*')):
        if not p.is_file():continue
        span=int(p.parent.name);asset=int(p.name,16)
        if not 0<=span<len(spans):raise ValueError('نطاق ملف التعريب غير صالح.')
        start,count=spans[span];matches=[i for i in range(start,start+count) if ids[i]==asset]
        if len(matches)!=1:raise ValueError('ملفات اللعبة لا تتوافق مع حزمة التعريب: '+p.name)
        i=matches[0];replaced.add(i);data=p.read_bytes();head=None
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
    if indices and any(oldai==ai and i not in replaced for i,(_,oldai,_,_) in enumerate(s.iter_unpack('<IIIi',sec[0x65bcf461]))):
        raise RecoveryRequired('التعريب السابق يحتوي ملفات إضافية غير متوافقة. أصلح اللعبة عبر Steam ثم أعد المحاولة.')
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
        progress(10,'فحص ملفات اللعبة والحزمة…')
        current=(game/'toc').read_bytes();archive=game/'d/mods/arabic_loc'
        archive.parent.mkdir(parents=True,exist_ok=True)
        if archive.parent.is_symlink() or archive.is_symlink():raise ValueError('مسار التعريب مرتبط رمزيًا.')
        oldarc=archive.read_bytes() if archive.exists() else None
        oldrecord=(state/'state.json').read_bytes() if (state/'state.json').exists() else None
        localized=is_localized(current);legacy=False;original=current
        if oldrecord is not None and localized:
            previous=json.loads(oldrecord)
            if hashlib.sha256(current).hexdigest()!=previous['installed_toc'] or (oldarc is not None and hashlib.sha256(oldarc).hexdigest()!=previous['installed_archive']):
                raise RecoveryRequired('تغيرت ملفات التعريب منذ التثبيت. أصلح اللعبة عبر Steam ثم أعد المحاولة.')
            original=saved_original(state,previous);legacy=previous.get('legacy_baseline',False)
        elif localized:
            original=legacy_original(game,current,archive,manifest)
            legacy=original is None
            if legacy:original=current
        progress(30,'تجهيز التحديث وحفظ حالة التثبيت السابق…' if localized else 'تجهيز التعريب…')
        newtoc,newarc=prepare(current if legacy else original,Path(payload)/'mod',replace_existing=legacy)
        snapshot(state,'toc',original)
        snapshot(state,'toc',current)
        if oldarc is not None:snapshot(state,'archive',oldarc)
        if oldrecord is not None:snapshot(state,'record',oldrecord)
        record={'version':VERSION,'backup_format':2,'legacy_baseline':legacy,'original_toc':hashlib.sha256(original).hexdigest(),'installed_toc':hashlib.sha256(newtoc).hexdigest(),'installed_archive':hashlib.sha256(newarc).hexdigest()}
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
        progress(100,'اكتمل تحديث التعريب. لا توجد نسخة أصلية محفوظة؛ الحذف الكامل متاح عبر إصلاح Steam.' if legacy else 'اكتمل التثبيت. اختر English في Steam ثم شغّل اللعبة.')
        return record

def restore(game,progress=lambda n,t:None,payload=None):
    game=check_game(game);state=safe_state(game);archive=game/'d/mods/arabic_loc'
    with lock(game):
        if archive.parent.is_symlink() or archive.is_symlink():raise ValueError('مسار التعريب مرتبط رمزيًا.')
        oldtoc=(game/'toc').read_bytes();oldarc=archive.read_bytes() if archive.exists() else None
        oldrecord=(state/'state.json').read_bytes() if (state/'state.json').exists() else None
        original=oldtoc
        if is_localized(oldtoc):
            if oldrecord is not None:
                record=json.loads(oldrecord)
                if hashlib.sha256(oldtoc).hexdigest()!=record['installed_toc'] or (oldarc is not None and hashlib.sha256(oldarc).hexdigest()!=record['installed_archive']):
                    raise RecoveryRequired('تغيرت ملفات التعريب. أصلح اللعبة عبر Steam ثم اضغط حذف التعريب مجددًا.')
                if record.get('legacy_baseline'):
                    raise RecoveryRequired('التعريب السابق لم يحفظ فهرس اللعبة الأصلي. افتح إصلاح Steam، وبعد اكتماله اضغط حذف التعريب مجددًا.')
                original=saved_original(state,record)
            else:
                manifest=verify_payload(payload) if payload is not None else {}
                original=legacy_original(game,oldtoc,archive,manifest)
                if original is None:raise RecoveryRequired('لم أجد نسخة أصلية موثوقة للتعريب القديم. افتح إصلاح Steam، وبعد اكتماله اضغط حذف التعريب مجددًا.')
            if is_localized(original):raise ValueError('النسخة الاحتياطية ليست أصلية.')
        # Steam may already have restored the index while leaving the mod archive.
        snapshot(state,'toc',oldtoc)
        if oldarc is not None:snapshot(state,'archive',oldarc)
        if oldrecord is not None:snapshot(state,'record',oldrecord)
        progress(40,'استعادة الفهرس الأصلي وإزالة بقايا التعريب…')
        try:
            atomic(game/'toc',original);archive.unlink(missing_ok=True);(state/'state.json').unlink(missing_ok=True)
        except Exception:
            if oldarc is not None:atomic(archive,oldarc)
            atomic(game/'toc',oldtoc)
            if oldrecord is not None:atomic(state/'state.json',oldrecord)
            raise
        progress(100,'تم حذف التعريب. النسخ الاحتياطية محفوظة.')

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
