# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import struct as s, hashlib,json
import argparse
parser=argparse.ArgumentParser(description='Prepare a local game index and Arabic archive. Does not modify the game.')
parser.add_argument('--game',type=Path,required=True)
parser.add_argument('--toc',type=Path,help='Clean original toc; defaults to GAME/toc')
parser.add_argument('--mod',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
G=args.game;M=args.mod;out=args.output
out.mkdir(parents=True,exist_ok=False)
orig=(args.toc or G/'toc').read_bytes(); b=orig[8:]
assert s.unpack_from('<I',orig)[0]==0x34e89035
magic,typ,sz,n,u=s.unpack_from('<IIIHH',b)
assert magic==0x44415431 and sz<=len(b)
table=[s.unpack_from('<III',b,16+i*12) for i in range(n)]
sec={t:bytearray(b[o:o+z]) for t,o,z in table}
ids=list(s.unpack('<'+'Q'*(len(sec[0x506d7b8a])//8),sec[0x506d7b8a]))
spans=list(s.iter_unpack('<II',sec[0xede8ada9]))
arc=sec[0x398abff0]; ai=len(arc)//66
assert len(arc)%66==0
name=b'd\\mods\\arabic_loc';assert name not in arc
arc.extend(s.pack('<40sQQIHI',name,2678794514496,2678794514496,3844228203,32763,0))
print('sections',[(hex(t),len(v)) for t,v in sec.items()])
archive=bytearray(); report=[]
for p in sorted(M.glob('*/*')):
 span=int(p.parent.name);asset=int(p.name,16); start,count=spans[span]
 matches=[i for i in range(start,start+count) if ids[i]==asset];assert len(matches)==1,(p,matches)
 i=matches[0];data=p.read_bytes();head=None;meta=None
 if data[:4]==b'STG\0':
  _,flags,hs,ts=s.unpack_from('<4I',data);pos=16
  head=data[pos:pos+hs] if flags&1 else None;pos=(pos+hs+15)//16*16
  meta=data[pos:pos+ts] if flags&2 else None;pos=(pos+ts+15)//16*16
  data=data[pos:]
 assert meta is None,('texture meta needs handling',p)
 oldsize,oldai,oldoff,ho=s.unpack_from('<IIIi',sec[0x65bcf461],i*16)
 if head is not None:
  assert len(head)==36
  if ho<0:ho=len(sec[0x654bded9]);sec[0x654bded9].extend(head)
  else:sec[0x654bded9][ho:ho+36]=head
 s.pack_into('<IIIi',sec[0x65bcf461],i*16,len(data),ai,len(archive),ho)
 archive.extend(data);report.append({'asset':str(p.relative_to(M)),'size':len(data)})
first=min(o for t,o,z in table);res=bytearray(b[:first]);newtable={}
for t,o,z in sorted(table,key=lambda x:x[1]):
 res.extend(b'\0'*((-len(res))%16));newtable[t]=(len(res),len(sec[t]));res.extend(sec[t])
for j,(t,o,z) in enumerate(table):s.pack_into('<III',res,16+j*12,t,*newtable[t])
s.pack_into('<I',res,8,len(res));toc=s.pack('<II',0x34e89035,len(res))+res
(out/'toc').write_bytes(toc);(out/'arabic_loc').write_bytes(archive);(out/'toc.original').write_bytes(orig)
(out/'manifest.json').write_text(json.dumps({'original_sha256':hashlib.sha256(orig).hexdigest(),'toc_sha256':hashlib.sha256(toc).hexdigest(),'archive_sha256':hashlib.sha256(archive).hexdigest(),'assets':report},indent=2))
print('Prepared',len(report),'assets',len(archive),'bytes')
