# SPDX-License-Identifier: GPL-3.0-only
#!/usr/bin/env python3
"""Extract STG/DAT1 localization losslessly; readable Arabic is a review aid only."""
from pathlib import Path
import struct, json, re, unicodedata, collections, hashlib, shutil
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'source/mod_original'
def dump(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sections(b):
 assert struct.unpack_from('<I',b)[0]==0x44415431
 count=struct.unpack_from('<H',b,12)[0]
 result={}
 for i in range(count):
  tag,off,size=struct.unpack_from('<III',b,16+12*i)
  assert off+size<=len(b)
  result[tag]=b[off:off+size]
 return result

def readable(raw):
 # Reverse shaped display runs before expanding ligatures such as lam-alef.
 def line(text):
  if not any(0xFB50<=ord(c)<=0xFDFF or 0xFE70<=ord(c)<=0xFEFF for c in text):return text
  tokens=[]
  pattern=r'<[^>]+>|\{[^{}]*\}|\[[^\[\]]*\]|%[-+0-9.$]*[a-zA-Z]|[A-Za-z0-9][A-Za-z0-9_:/.,+%\-]*'
  def hold(m):
   tokens.append(m.group());return chr(0xE000+len(tokens)-1)
  text=re.sub(pattern,hold,text)[::-1]
  text=unicodedata.normalize('NFKC',text)
  for i,t in enumerate(tokens):text=text.replace(chr(0xE000+i),t)
  return text
 return ''.join(p if re.fullmatch(r'<[^>]+>|\r?\n',p,flags=re.I) else line(p) for p in re.split(r'(<[^>]+>|\r?\n)',raw,flags=re.I))

def main():
 assert not (ROOT/'editable').exists(),'Already extracted: refusing to overwrite work.'
 # Source assets are already included in source/mod_original.
 b=(SOURCE/'8/BE55D94F171BF8DE').read_bytes()
 assert b[:4]==b'STG\0'
 flags,hs,ts=struct.unpack_from('<III',b,4)
 pos=(16+hs+15)//16*16;pos=(pos+ts+15)//16*16
 dat=b[pos:];sec=sections(dat)
 def strings(ot,dt):
  block=sec[dt];result=[]
  for (o,) in struct.iter_unpack('<I',sec[ot]):
   end=block.find(b'\0',o);assert end>=o
   result.append(block[o:end].decode('utf-8',errors='strict'))
  return result
 keys=strings(0xA4EA55B2,0x4D73CEBD);values=strings(0xF80DEEB4,0x70A382B8)
 assert len(keys)==len(values)==struct.unpack('<I',sec[0xD540A903])[0]
 assert len(set(keys))==len(keys)
 known={'WAL','COM','GRP','ELSUP','SSAM','TUSUP','AMOE','HERO','SISUP','WALL','RATC','RIVE','CLANK','KIT','QWRK','SKIDD','PHAN','GLIT','MSZK','JRZK','DRNF','EPNF','FUNG','FUNGA','PROPH','PILF','MORT','ASSI','QUTM','CHEN','MRSZ','FIXER','STRAN','KLEM','CLEM','SJIM','BRAN','TRUD','MYVO','FAVI','SBOB','NEFCD','ZURK','PRVI','RTPT','LAMS','CIV'}
 groups=collections.defaultdict(list);allrows=[];issues=[]
 for i,(key,raw) in enumerate(zip(keys,values)):
  parts=key.split('_');prefix=parts[0]
  dialogue=(prefix in known or bool(re.fullmatch(r'(?:NEFT|NEFC|PIR|HPIR|HNEF|T4L|MORT|MEGM|MEGF|MON|VLRD|BARP|CHEF|CM|JUNB|SCIB|SQU)\d+',prefix))) and bool(re.search(r'_\d+$',key))
  if dialogue:
   category='dialogue';scene='_'.join(parts[1:-1]) or 'UNSORTED';group=scene
  elif prefix=='CREDITS':category='credits';scene='';group='credits'
  elif prefix in {'OBJ','MISSION','LOC','ACTIVITY'}:category='missions';scene='';group=prefix
  elif prefix in {'TUT','HELP'}:category='tutorials';scene='';group=prefix
  elif prefix in {'WEAPON','WPN','UPGRADE','GADGET','ARMOR','INV','NAME','DESC','BIO','CARD','TROPHY'}:category='items';scene='';group=prefix
  elif prefix in {'Play','Stop'}:category='audio_events';scene='';group=prefix
  else:category='ui_and_other';scene='';group=prefix
  arabic=any('\u0600'<=c<='\u06ff' or '\ufb50'<=c<='\ufdff' or '\ufe70'<=c<='\ufeff' for c in raw)
  shaped=any('\ufb50'<=c<='\ufdff' or '\ufe70'<=c<='\ufeff' for c in raw)
  row={'index':i,'key':key,'category':category,'speaker_code':prefix if dialogue else '', 'scene_code':scene,'arabic_current':readable(raw),'arabic_edit':'','status':'todo','notes':'','reading_needs_review':shaped}
  groups[(category,group)].append(row);allrows.append(row)
  if dialogue and (not raw or not arabic):issues.append({'key':key,'reason':'empty' if not raw else 'no_arabic','text':raw})
 dump(ROOT/'reference/all_original.json',[{'index':i,'key':k,'text_raw':v} for i,(k,v) in enumerate(zip(keys,values))])
 index=[]
 for (category,group),rows in sorted(groups.items()):
  safe=re.sub(r'[^A-Za-z0-9_.-]','_',group)
  rel=f'editable/{category}/{safe}.json'
  dump(ROOT/rel,rows);index.append({'file':rel,'entries':len(rows),'category':category})
 dump(ROOT/'reference/file_index.json',index)
 dump(ROOT/'review/dialogue_missing_arabic.json',issues)
 dump(ROOT/'reference/speakers.json',dict(sorted(collections.Counter(r['speaker_code'] for r in allrows if r['category']=='dialogue').items())))
 dump(ROOT/'reference/statistics.json',{'entries':len(keys),'files':len(index),'categories':dict(collections.Counter(r['category'] for r in allrows)),'dialogue_missing_arabic':len(issues),'source_sha256':hashlib.sha256(b).hexdigest(),'classification':'Inferred from keys; all entries retained, including uncertain categories.','readable_arabic':'Heuristic reversal and unshaping; mixed text and punctuation require review.'})
 assert sum(x['entries'] for x in index)==len(keys)
 print((ROOT/'reference/statistics.json').read_text())
if __name__=='__main__':main()
