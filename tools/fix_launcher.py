# SPDX-License-Identifier: GPL-3.0-only
#!/usr/bin/env python3
from pathlib import Path
import struct as s,json,re,sys,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from extract import readable
src=ROOT/'source/mod_original/8/BE55D94F171BF8DE'
b=src.read_bytes();flags,hs,ts=s.unpack_from('<III',b,4)
header=bytearray(b[16:16+hs]);pos=(16+hs+15)//16*16;tex=b[pos:pos+ts];pos=(pos+ts+15)//16*16;dat=b[pos:]
n=s.unpack_from('<H',dat,12)[0];table=[s.unpack_from('<III',dat,16+i*12) for i in range(n)];sec={t:bytearray(dat[o:o+z]) for t,o,z in table}
def strings(ot,dt):
 block=sec[dt]
 return [block[o:block.index(0,o)].decode() for o, in s.iter_unpack('<I',sec[ot])]
keys=strings(0xA4EA55B2,0x4D73CEBD);values=strings(0xF80DEEB4,0x70A382B8)
overrides={
'LAUNCHER_OPTIONS_TITLE':'راتشت وكلانك — الإعدادات',
'PCDISPLAYSETTINGS_FSR':'AMD FSR 3',
'PCDISPLAYSETTINGS_FSRAA':'AMD FSR 3 Native AA',
'PCDISPLAYSETTINGS_FSRFRAMEGEN':'AMD FSR 3',
'PCDISPLAYSETTINGS_DLSS':'NVIDIA DLSS',
'PCDISPLAYSETTINGS_DLSSG':'NVIDIA DLSS',
'PCDISPLAYSETTINGS_XESS':'Intel XeSS',
'PCDISPLAYSETTINGS_HDR':'HDR',
'PCDISPLAYSETTINGS_HDRMAXNITS':'أقصى سطوع HDR',
'PCDISPLAYSETTINGS_HDRPAPERWHITE':'سطوع الورق الأبيض HDR',
'PCDISPLAYSETTINGS_NVIDIAREFLEX':'NVIDIA Reflex',
'PCDISPLAYSETTINGS_IGTI':'IGTI',
'PCDISPLAYSETTINGS_UPSCALEMETHOD':'طريقة رفع الدقة',
'PCDISPLAYSETTINGS_UPSCALEQUALITY':'جودة رفع الدقة',
'PCDISPLAYSETTINGS_UPSCALESHARPNESS':'حدة الصورة',
'PCDISPLAYSETTINGS_DRS':'الدقة الديناميكية',
'PCGRAPHICSSETTINGS_RTAO':'RTAO',
'PCGRAPHICSSETTINGS_SMAA':'SMAA',
'PCGRAPHICSSETTINGS_SSAO':'SSAO',
'PCGRAPHICSSETTINGS_TAA':'TAA',
'PCGRAPHICSSETTINGS_XEAA':'XeSS Native AA',
'PCGRAPHICSSETTINGS_XEGTAO':'XeGTAO',
}
changes=[]
for i,(k,v) in enumerate(zip(keys,values)):
 selected=(k.startswith(('PCDISPLAYSETTINGS_','PCGRAPHICSSETTINGS_','SETTINGSCATEGORY_')) or k.startswith('LAUNCHER_OPTIONS_')) and not k.endswith('_UPPERCASE')
 if not selected or not v:continue
 new=overrides.get(k,readable(v));new=re.sub(r'<br\s*/?>',' ',new,flags=re.I)
 if new!=v:values[i]=new;changes.append({'key':k,'before':v,'after':new})
# Untouched strings preserve their exact UTF8 contents; offsets are regenerated.
block=bytearray();offsets=bytearray()
for v in values:
 offsets.extend(s.pack('<I',len(block)));block.extend(v.encode()+b'\0')
sec[0x70A382B8]=block;sec[0xF80DEEB4]=offsets
first=min(o for t,o,z in table);out=bytearray(dat[:first]);offsetmap={}
for t,o,z in sorted(table,key=lambda x:x[1]):
 out.extend(b'\0'*((-len(out))%16));offsetmap[t]=(len(out),len(sec[t]));out.extend(sec[t])
for i,(t,o,z) in enumerate(table):s.pack_into('<III',out,16+i*12,t,*offsetmap[t])
s.pack_into('<I',out,8,len(out));s.pack_into('<I',header,4,len(out))
stage=bytearray(s.pack('<4I',0x00475453,flags,len(header),len(tex)));stage.extend(header);stage.extend(b'\0'*((-len(stage))%16));stage.extend(tex);stage.extend(b'\0'*((-len(stage))%16));stage.extend(out)
mod=ROOT/'build/launcher_fix_mod'
if not mod.exists():shutil.copytree(ROOT/'source/mod_original',mod)
(mod/'8/BE55D94F171BF8DE').write_bytes(stage)
(ROOT/'patches/launcher_direction_fix.json').write_text(json.dumps({'description':'Native launcher uses Unicode bidi/shaping. Restore logical Unicode for launcher and non-uppercase PC setting keys; uppercase game keys and all dialogue retained.','changes':changes},ensure_ascii=False,indent=2)+'\n')
# Validate every string and every unrelated section after rebuilding.
from extract import sections
parsed=sections(bytes(out));block=parsed[0x70A382B8]
actual=[block[o:block.index(0,o)].decode() for o, in s.iter_unpack('<I',parsed[0xF80DEEB4])]
assert actual==values
oldsecs=sections(dat)
for t in oldsecs:
 if t not in (0x70A382B8,0xF80DEEB4):assert parsed[t]==oldsecs[t]
changedkeys={x['key'] for x in changes}
original=json.loads((ROOT/'reference/all_original.json').read_text())
for r in original:
 if r['key'] not in changedkeys:assert actual[r['index']]==r['text_raw']
print('Patched',len(changes),'keys; verified all',len(values),'strings and unrelated sections.')
