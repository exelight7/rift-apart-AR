# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import struct,json,collections,hashlib
from extract import sections
R=Path(__file__).resolve().parents[1];blob=(R/'build/release_mod/8/BE55D94F171BF8DE').read_bytes();hs,ts=struct.unpack_from('<II',blob,8);p=(16+hs+15)//16*16;p=(p+ts+15)//16*16;sec=sections(blob[p:]);block=sec[0x70A382B8];values=[block[o:block.index(0,o)].decode() for o, in struct.iter_unpack('<I',sec[0xF80DEEB4])]
orig=json.loads((R/'reference/all_original.json').read_text());rows=[x for f in (R/'editable').rglob('*.json') for x in json.loads(f.read_text())];rows.sort(key=lambda x:x['index']);changed=[];eligible=[];prose=[]
assert len(rows)==len(orig)==len(values), 'Packaged string count differs from the source'
for r,o,v in zip(rows,orig,values):
 assert r['key']==o['key'] and r['index']==o['index']
 if o['text_raw'] and r['category'] not in ('credits','audio_events'):
  eligible.append(r)
  if v!=o['text_raw']:changed.append(r)
  review=r.get('linguistic_review',{})
  candidate=r['arabic_edit'] or r['arabic_current']
  if review.get('candidate_sha256')==hashlib.sha256(candidate.encode()).hexdigest() and review.get('source_sha256'):prose.append(r)
report={'version':'1.0.1','all_entries':len(rows),'eligible_nonempty_excluding_credits':len(eligible),'actual_binary_changed':len(changed),'actual_changed_percent':round(len(changed)/len(eligible)*100,2),'human_prose_reviewed_unique':len(prose),'human_prose_percent':round(len(prose)/len(eligible)*100,2),'changed_by_category':dict(collections.Counter(x['category'] for x in changed)),'human_prose_by_category':dict(collections.Counter(x['category'] for x in prose)),'in_game_visual_approval':'pending','counting_method':'Distinct keys whose final packaged bytes differ from source/mod_original. Empty entries, credits and audio-event identifiers excluded. Direction/typography/reflow counted separately from human prose review.'}
(R/'review/progress_v2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
