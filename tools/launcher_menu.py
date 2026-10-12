# SPDX-License-Identifier: GPL-3.0-only
"""Windows launcher main menu uses native Unicode; Wine keeps the legacy renderer."""
import json,struct
from pathlib import Path
from extract import sections
MAIN_KEYS=('LAUNCHER_PLAY','LAUNCHER_OPTIONS','LAUNCHER_QUIT','LAUNCHER_ENABLED')

def native_menu(blob,translations):
    flags,hs,ts=struct.unpack_from('<III',blob,4)
    header=bytearray(blob[16:16+hs]);pos=(16+hs+15)//16*16
    tex=blob[pos:pos+ts];pos=(pos+ts+15)//16*16;data=blob[pos:]
    sec=sections(data);count=struct.unpack_from('<H',data,12)[0]
    table=[struct.unpack_from('<III',data,16+i*12) for i in range(count)]
    def read(ot,dt):
        b=sec[dt];return [b[o:b.index(0,o)].decode() for o, in struct.iter_unpack('<I',sec[ot])]
    keys=read(0xA4EA55B2,0x4D73CEBD);values=read(0xF80DEEB4,0x70A382B8)
    for i,key in enumerate(keys):
        if key in MAIN_KEYS:values[i]=translations[key]
    block=bytearray();offsets=bytearray()
    for value in values:offsets.extend(struct.pack('<I',len(block)));block.extend(value.encode()+b'\0')
    sec[0x70A382B8]=block;sec[0xF80DEEB4]=offsets
    out=bytearray(data[:min(o for _,o,_ in table)]);new={}
    for tag,offset,size in sorted(table,key=lambda x:x[1]):
        out.extend(b'\0'*((-len(out))%16));new[tag]=(len(out),len(sec[tag]));out.extend(sec[tag])
    for i,(tag,_,_) in enumerate(table):struct.pack_into('<III',out,16+i*12,tag,*new[tag])
    struct.pack_into('<I',out,8,len(out));struct.pack_into('<I',header,4,len(out))
    result=bytearray(struct.pack('<4I',0x00475453,flags,len(header),len(tex)));result.extend(header);result.extend(b'\0'*((-len(result))%16));result.extend(tex);result.extend(b'\0'*((-len(result))%16));result.extend(out)
    return bytes(result)

def main_translations(root):
    return {r['key']:r['arabic_edit'] or r['arabic_current'] for p in (Path(root)/'editable').rglob('*.json') for r in json.loads(p.read_text(encoding='utf-8')) if r['key'] in MAIN_KEYS}
