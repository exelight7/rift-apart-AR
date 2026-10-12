# SPDX-License-Identifier: GPL-3.0-only
#!/usr/bin/env python3
from pathlib import Path
import json,re,collections,sys
ROOT=Path(__file__).resolve().parents[1]
def main():
 originals=json.loads((ROOT/'reference/all_original.json').read_text())
 original={r['key']:r for r in originals};seen=collections.Counter();errors=[];warnings=[];changed=0
 for p in sorted((ROOT/'editable').rglob('*.json')):
  try:rows=json.loads(p.read_text(encoding='utf-8'))
  except Exception as e:errors.append(f'{p}: {e}');continue
  for r in rows:
   k=r.get('key');seen[k]+=1
   if k not in original:errors.append(f'Unknown key: {k}');continue
   if r.get('index')!=original[k]['index']:errors.append(f'Index changed: {k}')
   if r.get('status') not in ['todo','draft','reviewed','approved']:errors.append(f'Invalid status: {k}')
   text=r.get('arabic_edit')
   if not isinstance(text,str):errors.append(f'Edit must be string: {k}');continue
   if not text:continue
   changed+=1
   raw=original[k]['text_raw']
   # Tags, variables, entities and printf substitutions must survive exactly.
   pattern=r'<[/A-Za-z][^<>]*>|\{[^{}]*\}|\[[A-Za-z0-9_:=+ .-]+\]|%[-+0-9.$]*[a-zA-Z]|&[A-Za-z#0-9]+;'
   if collections.Counter(re.findall(pattern,re.sub(r'<br\s*/?>','',raw,flags=re.I)))!=collections.Counter(re.findall(pattern,re.sub(r'<br\s*/?>','',text,flags=re.I))):
    errors.append(f'Tags/placeholders changed: {k}')
   if re.findall(r'<ts[^>]*>',raw)!=re.findall(r'<ts[^>]*>',text):errors.append(f'Timing order changed: {k}')
   if '\0' in text:errors.append(f'NUL in text: {k}')
   if any('\ufb50'<=c<='\ufdff' or '\ufe70'<=c<='\ufeff' for c in text):warnings.append(f'Shaped characters in edit: {k}')
 for k in original:
  if seen[k]!=1:errors.append(f'Key count {seen[k]}: {k}')
 report={'total_original':len(original),'total_editable':sum(seen.values()),'edited':changed,'errors':errors,'warnings':warnings}
 (ROOT/'review/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False,indent=2));return bool(errors)
if __name__=='__main__':sys.exit(main())
