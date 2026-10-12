# SPDX-License-Identifier: GPL-3.0-only
"""Explicit, source-compared editorial batches with stale-input protection."""
import argparse,collections,hashlib,json,re,sys,os
from pathlib import Path
from text_layout import wrap_text
R=Path(__file__).resolve().parents[1]
EN=Path(os.environ.get('RIFT_ENGLISH_REFERENCE', str(R/'review/linguistic/english_reference.json')))
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def load():
 rows={};files={}
 for p in sorted((R/'editable').rglob('*.json')):
  data=json.loads(p.read_text())
  for r in data:rows[r['index']]=r;files[r['index']]=p
 return rows,files,json.loads(EN.read_text())
def eligible(r):return bool(r['arabic_current']) and r['category'] not in ('credits','audio_events')
def reviewed(r):
 if r.get('linguistic_review'):return r['linguistic_review'].get('candidate_sha256')==digest(r['arabic_edit'] or r['arabic_current'])
 return r['status']=='reviewed' and any(x.startswith('prose_') for x in r.get('review_scope',[]))
def export(args):
 rows,files,en=load();selected=[r for i,r in sorted(rows.items()) if eligible(r) and (r['index'] in set(map(int,args.indices.split(','))) if args.indices else not reviewed(r)) and (not args.category or r['category']==args.category) and (not args.prefix or r['key'].startswith(args.prefix))]
 batch=selected[:args.limit];out=[]
 for r in batch:
  s=en.get(r['key'],'');a=r['arabic_edit'] or r['arabic_current'];out.append({'index':r['index'],'key':r['key'],'source_sha256':digest(s),'candidate_sha256':digest(a)})
  def compact(t):return re.sub(r'<ts[^>]*>',' § ',t).replace('<br>',' / ').strip()
  print(f"{r['index']} {r['key']}\nE: {compact(s)}\nA: {compact(a)}")
 (R/'review/linguistic'/f'{args.batch}.input.json').write_text(json.dumps(out,indent=2)+'\n');print('BATCH',args.batch,'ENTRIES',len(batch),'QUEUE',len(selected))
def apply(args):
 rows,files,en=load();inp=json.loads((R/'review/linguistic'/f'{args.batch}.input.json').read_text());patch=json.loads(Path(args.patch).read_text());keep=set(patch.get('keep',[]));changes={int(k):v for k,v in patch.get('changes',{}).items()};defer={int(k):v for k,v in patch.get('defer',{}).items()};expected={r['index'] for r in inp}
 if keep|set(changes)|set(defer)!=expected or keep&set(changes):raise ValueError('Every input must be accounted for exactly once')
 outputs=[];dirty=set()
 for item in inp:
  i=item['index'];r=rows[i];source=en.get(r['key'],'');old=r['arabic_edit'] or r['arabic_current']
  if digest(source)!=item['source_sha256'] or digest(old)!=item['candidate_sha256']:raise ValueError('Stale input '+str(i))
  if i in defer:r['notes']=defer[i];r['status']='draft';dirty.add(files[i]);continue
  text=changes.get(i,old)
  if isinstance(text,list):
   ts=re.findall(r'<ts[^>]*>',source)
   if len(ts)!=len(text):raise ValueError('Segment count '+str(i))
   leading=source[:source.index(ts[0])] if ts else ''
   text=leading+''.join(t+v for t,v in zip(ts,text))
  elif i in changes and '<ts' in source and '<ts' not in text:
   ts=re.findall(r'<ts[^>]*>',source)
   if len(ts)!=1:raise ValueError('Multiple timed segments require array '+str(i))
   text=source[:source.index(ts[0])]+ts[0]+text
  if i in changes:
   text='<br>'.join(wrap_text(part,42) for part in text.split('<br>')) if r['category'] in ('tutorials','ui_and_other') else wrap_text(text,42 if r['category']=='dialogue' or '<ts' in source else 34)
  pattern=r'<[/A-Za-z][^<>]*>|\{[^{}]*\}|\[[A-Za-z0-9_:=+ .-]+\]|%[-+0-9.$]*[a-zA-Z]|&[A-Za-z#0-9]+;'
  def tokens(v):return collections.Counter(re.findall(pattern,re.sub(r'<br\s*/?>','',v,flags=re.I)))
  if tokens(text)!=tokens(r['arabic_current']):raise ValueError('Tags/placeholders changed '+str(i))
  if re.findall(r'<ts[^>]*>',text)!=re.findall(r'<ts[^>]*>',r['arabic_current']):raise ValueError('Timing order changed '+str(i))
  r['arabic_edit']=text;r['status']='reviewed';r['reading_needs_review']=False
  r['review_scope']=sorted(set(r.get('review_scope',[])+['prose_full_review']))
  r['linguistic_review']={'batch':args.batch,'source_sha256':digest(source),'candidate_sha256':digest(text),'method':'Source-compared linguistic review; kept or explicitly rewritten by reviewer','visual_approval':'pending'}
  r['notes']='مراجعة لغوية بمقارنة الأصل الإنجليزي؛ اعتماد العرض داخل اللعبة معلق.'
  outputs.append({'index':i,'key':r['key'],'source_sha256':digest(source),'before':old,'after':text,'decision':'rewrite' if i in changes else 'keep'})
  dirty.add(files[i])
 for p in dirty:
  data=json.loads(p.read_text());data=[rows[x['index']] for x in data];p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 (R/'review/linguistic'/f'{args.batch}.review.json').write_text(json.dumps(outputs,ensure_ascii=False,indent=2)+'\n')
 print('Reviewed',len(outputs),'rewritten',len(changes),'deferred',len(defer));summary(args)
def summary(args):
 rows,files,en=load();allr=[r for r in rows.values() if eligible(r)];done=[r for r in allr if reviewed(r)];report={'eligible':len(allr),'linguistically_reviewed':len(done),'coverage_percent':round(100*len(done)/len(allr),2),'reviewed_by_category':dict(collections.Counter(r['category'] for r in done)),'remaining_by_category':dict(collections.Counter(r['category'] for r in allr if not reviewed(r))),'visual_approval':'pending'}
 (R/'review/linguistic/progress.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
p=argparse.ArgumentParser();p.add_argument('mode',choices=['export','apply','summary']);p.add_argument('--category');p.add_argument('--prefix');p.add_argument('--indices');p.add_argument('--limit',type=int,default=100);p.add_argument('--batch');p.add_argument('--patch');args=p.parse_args();globals()[args.mode](args)
