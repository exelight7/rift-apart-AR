# SPDX-License-Identifier: GPL-3.0-only
import unittest,sys,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from text_layout import decode_legacy,wrap_text
class TextTests(unittest.TestCase):
    def test_sentence_order(self):
        self.assertEqual(decode_legacy('ﻚﻧﻼﻛ! ﻮﺘﻠﻟ ﺖﺸﺗﺍﺭ ﺖﻳﺃﺭ!'),'كلانك! رأيت راتشت للتو!')
        self.assertEqual(decode_legacy('؟ﺍﺫﺎﻣ ﻡﺃ ﺐﺴﺤﻓ ﺢﻔﺼﺘﺗ ﺖﻧﺃ'),'أنت تتصفح فحسب أم ماذا؟')
    def test_control_tags(self):
        text='<ts=&quot;0;1&quot;>[GAMEPAD_X] ﻚﻧﻼﻛ!<ts=&quot;2;3&quot;>ﻚﻧﻼﻛ!'
        result=wrap_text(decode_legacy(text),12)
        self.assertEqual(re.findall(r'<ts[^>]*>',text),re.findall(r'<ts[^>]*>',result))
        self.assertIn('[GAMEPAD_X]',result)
    def test_paragraphs(self):
        self.assertIn('<br><br>',wrap_text('نص أول<br><br>نص ثان',20))
if __name__=='__main__':unittest.main()
