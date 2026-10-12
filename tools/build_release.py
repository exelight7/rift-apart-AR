# SPDX-License-Identifier: GPL-3.0-only
#!/usr/bin/env python3
from pathlib import Path
import struct as s,json,re,shutil
import arabic_reshaper
from bidi.algorithm import get_display
R=Path(__file__).resolve().parents[1]
from extract import sections
source=R/'build/launcher_fix_mod';target=R/'build/release_mod'
if target.exists():raise RuntimeError('Build exists: preserve it before rebuilding')
shutil.copytree(source,target)
path=target/'8/BE55D94F171BF8DE';blob=path.read_bytes();_,flags,hs,ts=s.unpack_from('<4I',blob)
header=bytearray(blob[16:16+hs]);pos=(16+hs+15)//16*16;tex=blob[pos:pos+ts];pos=(pos+ts+15)//16*16;data=blob[pos:]
n=s.unpack_from('<H',data,12)[0];table=[s.unpack_from('<III',data,16+i*12) for i in range(n)];sec=sections(data)
def readstrings(ot,dt):
 block=sec[dt];return [block[o:block.index(0,o)].decode() for o, in s.iter_unpack('<I',sec[ot])]
keys=readstrings(0xA4EA55B2,0x4D73CEBD);old=readstrings(0xF80DEEB4,0x70A382B8);values=list(old)
changes={r['key']:r['arabic_edit'] for p in (R/'editable').rglob('*.json') for r in json.loads(p.read_text()) if r['arabic_edit']}
reshaper=arabic_reshaper.ArabicReshaper(configuration={'delete_harakat':True})
def visual(text):
 # Markup stays at its existing logical boundary; only visible text is reordered.
 def fragment(v):
  tokens=[]
  def hold(m):tokens.append(m.group());return chr(0xE000+len(tokens)-1)
  v=re.sub(r'\[[A-Za-z0-9_:=+ .-]+\]|\{[^}]+\}|%[-+0-9.$]*[a-zA-Z]|&[A-Za-z#0-9]+;',hold,v)
  v=get_display(reshaper.reshape(v),base_dir='R')
  for i,t in enumerate(tokens):v=v.replace(chr(0xE000+i),t)
  return v
 return ''.join(p if p.startswith('<') else fragment(p) for p in re.split(r'(<[/A-Za-z][^<>]*>)',text))
report=[]
for i,k in enumerate(keys):
 if k not in changes or (k.startswith('LAUNCHER_') and not k.startswith('LAUNCHER_OPTIONS_')):continue
 logical=changes[k]
 native=k.startswith('LAUNCHER_OPTIONS_') or (k.startswith(('PCDISPLAYSETTINGS_','PCGRAPHICSSETTINGS_','SETTINGSCATEGORY_')) and not k.endswith(('_UPPERCASE','_DESC')))
 new=re.sub(r'<br\s*/?>',' ',logical,flags=re.I) if native else visual(logical)
 values[i]=new;report.append({'key':k,'renderer':'native_unicode' if native else 'game_visual_arabic','logical':logical,'before':old[i],'after':new})
block=bytearray();offsets=bytearray()
for v in values:offsets.extend(s.pack('<I',len(block)));block.extend(v.encode()+b'\0')
sec[0x70A382B8]=block;sec[0xF80DEEB4]=offsets
first=min(o for t,o,z in table);out=bytearray(data[:first]);omap={}
for t,o,z in sorted(table,key=lambda x:x[1]):
 out.extend(b'\0'*((-len(out))%16));omap[t]=(len(out),len(sec[t]));out.extend(sec[t])
for i,(t,o,z) in enumerate(table):s.pack_into('<III',out,16+i*12,t,*omap[t])
s.pack_into('<I',out,8,len(out));s.pack_into('<I',header,4,len(out))
stage=bytearray(s.pack('<4I',0x00475453,flags,len(header),len(tex)));stage.extend(header);stage.extend(b'\0'*((-len(stage))%16));stage.extend(tex);stage.extend(b'\0'*((-len(stage))%16));stage.extend(out)
path.write_bytes(stage)
check=sections(bytes(out));vb=check[0x70A382B8];got=[vb[o:vb.index(0,o)].decode() for o, in s.iter_unpack('<I',check[0xF80DEEB4])];assert got==values
for i,k in enumerate(keys):
 if k not in changes or (k.startswith('LAUNCHER_') and not k.startswith('LAUNCHER_OPTIONS_')):assert got[i]==old[i]
for t,v in sections(data).items():
 if t not in (0x70A382B8,0xF80DEEB4):assert check[t]==v
for p in source.rglob('*'):
 if p.is_file() and p.relative_to(source).as_posix()!='8/BE55D94F171BF8DE':assert p.read_bytes()==(target/p.relative_to(source)).read_bytes()
(R/'review/release_build.json').write_text(json.dumps({'changed':sum(old[i]!=values[i] for i in range(len(old))), 'eligible_nonempty_excluding_credits':15100, 'actual_changed_eligible':sum(old[i]!=values[i] and not k.startswith('CREDITS_') and bool(old[i]) for i,k in enumerate(keys)),'entries_verified':len(keys),'visual_test':'pending','shared_keys_note':'Native launcher labels remain logical Unicode; in-game uppercase labels and all descriptions use visual Arabic. Shared labels still need in-game verification.','changes':report},ensure_ascii=False,indent=2)+'\n')
print('Built and round-trip verified',len(report),'changes;',len(keys),'total entries.')
