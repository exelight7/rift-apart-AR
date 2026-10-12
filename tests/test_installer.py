# SPDX-License-Identifier: GPL-3.0-only
import unittest,tempfile,sys,json,struct as s,hashlib
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'installer'))
import engine
ROOT=Path(__file__).resolve().parents[1]
# A minimal synthetic game index, deliberately not a shipped game file.
def fixture(game):
    entries=[(int(p.parent.name),int(p.name,16)) for p in sorted((ROOT/'installer/payload/mod').glob('*/*')) if p.is_file()]
    ids=[];spans=[]
    for span in range(256):
        items=[asset for sn,asset in entries if sn==span];spans.append((len(ids),len(items)));ids+=items
    sec={0x506d7b8a:s.pack('<'+'Q'*len(ids),*ids),0xede8ada9:b''.join(s.pack('<II',*x) for x in spans),0x65bcf461:b''.join(s.pack('<IIIi',1,0,0,-1) for _ in ids),0x398abff0:b'\0'*66,0x654bded9:b''}
    b=bytearray(s.pack('<IIIHH',0x44415431,0,0,len(sec),0)+b'\0'*(12*len(sec)));table=[]
    for tag,data in sec.items():b.extend(b'\0'*((-len(b))%16));table.append((tag,len(b),len(data)));b.extend(data)
    for i,t in enumerate(table):s.pack_into('<III',b,16+12*i,*t)
    s.pack_into('<I',b,8,len(b));(game/'d').mkdir();toc=s.pack('<II',0x34e89035,len(b))+b;(game/'toc').write_bytes(toc);return bytes(toc)
class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.game=Path(self.temp.name);self.original=fixture(self.game);self.payload=ROOT/'installer/payload';self.proc=patch.object(engine,'running',return_value=False);self.proc.start()
    def tearDown(self):self.proc.stop();self.temp.cleanup()
    def test_install_update_restore(self):
        record=engine.install(self.game,self.payload);self.assertEqual(engine.sha(self.game/'toc'),record['installed_toc']);self.assertNotEqual((self.game/'toc').read_bytes(),self.original)
        engine.install(self.game,self.payload);engine.restore(self.game);self.assertEqual((self.game/'toc').read_bytes(),self.original);self.assertFalse((self.game/'d/mods/arabic_loc').exists())
    def test_reject_modified_game(self):
        engine.install(self.game,self.payload);(self.game/'toc').write_bytes(b'changed')
        with self.assertRaises(ValueError):engine.restore(self.game)
        with self.assertRaises(ValueError):engine.install(self.game,self.payload)
        self.assertEqual((self.game/'toc').read_bytes(),b'changed')
    def test_rollback(self):
        real=engine.atomic
        def fail(path,data):
            if Path(path).name=='state.json':raise OSError('simulated disk failure')
            return real(path,data)
        with patch.object(engine,'atomic',side_effect=fail):
            with self.assertRaises(OSError):engine.install(self.game,self.payload)
        self.assertEqual((self.game/'toc').read_bytes(),self.original);self.assertFalse((self.game/'d/mods/arabic_loc').exists())
    def test_bad_payload_and_running(self):
        with patch.object(engine,'running',return_value=True):
            with self.assertRaises(RuntimeError):engine.install(self.game,self.payload)
        self.assertEqual((self.game/'toc').read_bytes(),self.original)
    def test_lock(self):
        (self.game/'.rift-apart-ar.lock').touch()
        with self.assertRaises(RuntimeError):engine.install(self.game,self.payload)
    def test_missing_asset(self):
        with tempfile.TemporaryDirectory() as td:
            import shutil
            shutil.copytree(self.payload,Path(td)/'payload');p=next((Path(td)/'payload/mod').glob('*/*'));p.unlink()
            with self.assertRaises(ValueError):engine.install(self.game,Path(td)/'payload')
    def test_original_backup_tamper(self):
        record=engine.install(self.game,self.payload)
        (self.game/('.rift-apart-ar/toc.'+record['original_toc'])).write_bytes(b'bad')
        with self.assertRaises(ValueError):engine.restore(self.game)

    def make_legacy(self):
        toc,arc=engine.prepare(self.original,self.payload/'mod')
        (self.game/'toc').write_bytes(toc)
        archive=self.game/'d/mods/arabic_loc';archive.parent.mkdir(parents=True)
        archive.write_bytes(arc)
        return toc,arc

    def test_unknown_legacy_updates_and_requires_repair_to_remove(self):
        toc,arc=self.make_legacy()
        record=engine.install(self.game,self.payload)
        self.assertTrue(record['legacy_baseline'])
        self.assertEqual((self.game/('.rift-apart-ar/toc.'+hashlib.sha256(toc).hexdigest())).read_bytes(),toc)
        self.assertEqual((self.game/('.rift-apart-ar/archive.'+hashlib.sha256(arc).hexdigest())).read_bytes(),arc)
        engine.install(self.game,self.payload)
        with self.assertRaises(engine.RecoveryRequired):engine.restore(self.game)
        (self.game/'toc').write_bytes(self.original)
        engine.restore(self.game)
        self.assertEqual((self.game/'toc').read_bytes(),self.original)
        self.assertFalse((self.game/'d/mods/arabic_loc').exists())

    def test_clean_index_with_leftover_archive(self):
        self.make_legacy();(self.game/'toc').write_bytes(self.original)
        record=engine.install(self.game,self.payload)
        self.assertFalse(record['legacy_baseline'])
        engine.restore(self.game)
        self.assertEqual((self.game/'toc').read_bytes(),self.original)

    def test_clean_steam_update_rebases_stale_state(self):
        old=engine.install(self.game,self.payload)
        clean=bytearray(self.original);clean[12]^=1
        (self.game/'toc').write_bytes(clean)
        record=engine.install(self.game,self.payload)
        self.assertNotEqual(record['original_toc'],old['original_toc'])
        engine.restore(self.game)
        self.assertEqual((self.game/'toc').read_bytes(),clean)

    def test_legacy_backup_any_date(self):
        toc,arc=self.make_legacy()
        backup=self.game/'arabic_backup_20250101_120000';backup.mkdir()
        (backup/'toc').write_bytes(self.original)
        manifest={'legacy':[{'toc':hashlib.sha256(toc).hexdigest(),'archive':hashlib.sha256(arc).hexdigest(),'original':hashlib.sha256(self.original).hexdigest()}]}
        with patch.object(engine,'verify_payload',return_value=manifest):
            record=engine.install(self.game,self.payload)
        self.assertFalse(record['legacy_baseline'])
        engine.restore(self.game)
        self.assertEqual((self.game/'toc').read_bytes(),self.original)

    def test_legacy_rollback_restores_previous_files(self):
        toc,arc=self.make_legacy();real=engine.atomic
        def fail(path,data):
            if Path(path).name=='state.json':raise OSError('disk failure')
            return real(path,data)
        with patch.object(engine,'atomic',side_effect=fail):
            with self.assertRaises(OSError):engine.install(self.game,self.payload)
        self.assertEqual((self.game/'toc').read_bytes(),toc)
        self.assertEqual((self.game/'d/mods/arabic_loc').read_bytes(),arc)
        self.assertFalse((self.game/'.rift-apart-ar/state.json').exists())

    def test_unmanaged_legacy_removal_then_steam_cleanup(self):
        toc,arc=self.make_legacy()
        with self.assertRaises(engine.RecoveryRequired):engine.restore(self.game)
        self.assertEqual((self.game/'toc').read_bytes(),toc)
        (self.game/'toc').write_bytes(self.original)
        engine.restore(self.game)
        self.assertFalse((self.game/'d/mods/arabic_loc').exists())

    def test_repeated_install_keeps_one_archive(self):
        self.make_legacy()
        for _ in range(3):engine.install(self.game,self.payload)
        sec=engine.toc_sections((self.game/'toc').read_bytes())[2]
        self.assertEqual(len(sec[0x398abff0])//66,2)

    def test_index_with_unreferenced_trailing_bytes(self):
        original=self.original+b'legacy-padding'
        (self.game/'toc').write_bytes(original)
        engine.install(self.game,self.payload);engine.restore(self.game)
        self.assertEqual((self.game/'toc').read_bytes(),original)
if __name__=='__main__':unittest.main()
