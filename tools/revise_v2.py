# SPDX-License-Identifier: GPL-3.0-only
"""Repeatable, audited layout and terminology pass. Does not claim prose review."""
from pathlib import Path
import json,re,collections
from text_layout import decode_legacy,wrap_text,shaped
R=Path(__file__).resolve().parents[1]
original={r['key']:r['text_raw'] for r in json.loads((R/'reference/all_original.json').read_text())}
terms=[
 (r'تتبع الأشعة\s*\(\s*(?:Ray Tracing|Tracing Ray)\s*\)', 'Ray Tracing'),
 (r'\(\s*(?:Ray Tracing|Tracing Ray)\s*\)\s*تتبع الأشعة', 'Ray Tracing'),
 (r'بتتبع الأشعة', 'بتقنية Ray Tracing'), (r'تتبع الأشعة','Ray Tracing'),
 (r'دي\s*إل\s*إس\s*إس','DLSS'),(r'دي\s*إل\s*إيه\s*إيه\s*إس','DLSS'),
 (r'إف\s*إس\s*آر','FSR'),(r'إكس\s*إي\s*إس','XeSS'),
 (r'دي\s*إل\s*إيه\s*إيه','DLAA'),(r'إنفيديا','NVIDIA'),
 (r'إيه\s*إم\s*دي','AMD'),(r'المزامنة العمودية','VSync')]
patch=[];counts=collections.Counter()
for p in sorted((R/'editable').rglob('*.json')):
 rows=json.loads(p.read_text());dirty=False
 for r in rows:
  raw=original[r['key']]
  if not raw or r['category'] in ('credits','audio_events'):continue
  old=r['arabic_edit'] or r['arabic_current'];logical=decode_legacy(raw)
  # Preserve previously reviewed prose. Only recover the legacy reading for todo.
  prior=bool(r['arabic_edit']);base=r['arabic_edit'] if prior else logical
  scope=['prose_batch1'] if prior else []
  if not prior and logical!=r['arabic_current']:
   r['arabic_current']=logical;dirty=True
  flat=re.sub(r'<br\s*/?>\s*<br\s*/?>','<PARAGRAPH>',base,flags=re.I)
  flat=re.sub(r'<br\s*/?>',' ',flat,flags=re.I)
  if r['category']!='dialogue':
   for pat,repl in terms:flat=re.sub(pat,repl,flat)
  # Unambiguous spelling/name fixes only; no global synonym replacements.
  flat=flat.replace('ريستشيت','راتشت').replace('راشتت','راتشت')
  if flat!=re.sub(r'<br\s*/?>',' ',base,flags=re.I):scope.append('terminology')
  # Reflow only long prose/dialogue, retain deliberate paragraphs and short labels.
  flat=flat.replace('<PARAGRAPH>','<br><br>')
  candidate=wrap_text(flat,42 if r['category']=='dialogue' else 34) if ('<br' in base or len(re.sub(r'<[^>]+>','',flat))>44) else flat
  if shaped(raw):scope.append('direction_and_punctuation')
  if candidate!=base and ('<br' in candidate or '<br' in base):scope.append('line_layout')
  if not scope:continue
  r['arabic_edit']=candidate;r['status']='reviewed' if prior else 'draft'
  r['review_scope']=sorted(set(scope));r['reading_needs_review']=not prior
  r['notes']='مراجعة صياغة سابقة؛ مع تحديث التقنيات والتنسيق.' if prior else 'تصحيح اتجاه وترقيم وتنسيق آلي؛ يحتاج مراجعة لغوية وسياق داخل اللعبة.'
  dirty=True
  patch.append({'key':r['key'],'scope':r['review_scope'],'before':old,'after':candidate})
  for c in set(scope):counts[c]+=1
 if dirty:p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(R/'patches/layout_terminology_v2.json').write_text(json.dumps(patch,ensure_ascii=False,indent=2)+'\n')
(R/'review/v2_editorial_scope.json').write_text(json.dumps({'eligible_nonempty_excluding_credits':15100,'candidates':len(patch),'scope_counts':dict(counts),'note':'Final percentage is computed from actual binary differences by build_release.py, not from setting draft status. Automated layout is separate from human prose review.'},indent=2)+'\n')
print(len(patch),dict(counts))
