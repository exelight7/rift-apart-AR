# SPDX-License-Identifier: GPL-3.0-only
"""Check the actual payload used by both the launcher and in-game settings."""
import json,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from extract import sections

def strings(path):
    blob=path.read_bytes();hs,ts=struct.unpack_from('<II',blob,8)
    pos=(16+hs+15)//16*16;pos=(pos+ts+15)//16*16;sec=sections(blob[pos:])
    def read(ot,dt):
        b=sec[dt];return [b[o:b.index(0,o)].decode() for o, in struct.iter_unpack('<I',sec[ot])]
    return dict(zip(read(0xA4EA55B2,0x4D73CEBD),read(0xF80DEEB4,0x70A382B8)))

class AspectRatioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.values=strings(ROOT/'installer/payload/mod/8/BE55D94F171BF8DE')
    def test_shared_auto_is_safe_in_both_renderers(self):
        self.assertEqual(self.values['PCDISPLAYSETTINGS_AUTO'],'Auto')
        self.assertTrue(self.values['PCDISPLAYSETTINGS_AUTO'].isascii())
    def test_numeric_ratios_remain_left_to_right(self):
        for suffix,value in [('16_9','16:9'),('21_9','21:9'),('32_9','32:9')]:
            self.assertEqual(self.values['HUD_WIDESCREEN_SCALING_'+suffix],value)
    def test_ratio_titles_and_description_still_exist(self):
        for k in ('PCDISPLAYSETTINGS_ASPECTRATIO','PCDISPLAYSETTINGS_ASPECTRATIO_UPPERCASE','PCDISPLAYSETTINGS_ASPECTRATIO_DESC'):
            self.assertTrue(self.values[k]);self.assertNotIn('Auto',self.values[k])
