# SPDX-License-Identifier: GPL-3.0-only
import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from launcher_menu import native_menu,main_translations,MAIN_KEYS
from test_aspect_ratio import strings
class LauncherMenuTests(unittest.TestCase):
    def test_windows_main_menu_changes_only_four_keys(self):
        # The common reviewed build is independent of the target OS payload.
        source=ROOT/'build/release_mod/8/BE55D94F171BF8DE';before=strings(source);translations=main_translations(ROOT)
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/'menu.stg';dest.write_bytes(native_menu(source.read_bytes(),translations));after=strings(dest)
        self.assertEqual(set(before),set(after));self.assertEqual({k for k in before if before[k]!=after[k]},set(MAIN_KEYS))
        for key in MAIN_KEYS:self.assertEqual(after[key],translations[key])
        for key in before:
            if key not in MAIN_KEYS:self.assertEqual(before[key],after[key],key)
    def test_packaged_main_menu_matches_target_renderer(self):
        values=strings(ROOT/'installer/payload/mod/8/BE55D94F171BF8DE')
        expected=main_translations(ROOT) if sys.platform=='win32' else strings(ROOT/'build/release_mod/8/BE55D94F171BF8DE')
        for key in MAIN_KEYS:self.assertEqual(values[key],expected[key])
