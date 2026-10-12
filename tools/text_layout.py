# SPDX-License-Identifier: GPL-3.0-only
"""Recover legacy display text and wrap Arabic without moving game control tags."""
import re, unicodedata, textwrap
from bidi.algorithm import get_display
TAG = r'<[/A-Za-z][^<>]*>'
PROTECTED = r'\{[^{}]*\}|\[[A-Za-z0-9_:=+ .-]+\]|%[-+0-9.$]*[a-zA-Z]|&[A-Za-z#0-9]+;'
def shaped(text):
    return any(0xfb50 <= ord(c) <= 0xfdff or 0xfe70 <= ord(c) <= 0xfeff for c in text)
def decode_legacy(raw):
    def fragment(text):
        if not shaped(text): return text
        # The old generator treated ASCII punctuation as LTR boundaries, but
        # Arabic comma/question-mark as part of the RTL run. Whole-line reversal
        # consequently swaps sentences around exclamation marks and emphasis.
        parts = re.split('('+PROTECTED+r'|[.!?;:*<>«»“”]+)', text)
        return ''.join(p if re.fullmatch(PROTECTED+r'|[.!?;:*<>«»“”]+',p) else
                       ''.join(unicodedata.normalize('NFKC',c) if shaped(c) else c for c in get_display(p,base_dir='L')) for p in parts)
    return ''.join(p if p.startswith('<') else fragment(p) for p in re.split('('+TAG+')',raw))
def wrap_text(text, width=42):
    # Timing/name/style tags remain in their exact sequence. A double break is
    # a paragraph boundary. Never wrap inside a button, variable or a tag.
    text = re.sub(r'<br\s*/?>\s*<br\s*/?>','<PARAGRAPH>',text,flags=re.I)
    text = re.sub(r'<br\s*/?>',' ',text,flags=re.I)
    parts = re.split('('+TAG+')',text)
    out=[]
    for p in parts:
        if p.startswith('<'): out.append('<br><br>' if p=='<PARAGRAPH>' else p); continue
        # Spaces at inline style boundaries separate words across fragments.
        # textwrap strips them, so restore those supplied by the editor.
        leading = ' ' if p[:1].isspace() else ''
        trailing = ' ' if p[-1:].isspace() else ''
        tokens=[]
        def hold(m): tokens.append(m.group());return chr(0xe000+len(tokens)-1)
        p = re.sub(PROTECTED,hold,p)
        p = re.sub(r'[ \t]+',' ',p).strip()
        p = '<br>'.join(textwrap.wrap(p,width,break_long_words=False,break_on_hyphens=False))
        for i,t in enumerate(tokens):p=p.replace(chr(0xe000+i),t)
        out.append(leading+p+trailing if p else leading or trailing)
    return ''.join(out)
