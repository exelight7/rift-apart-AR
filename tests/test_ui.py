# SPDX-License-Identifier: GPL-3.0-only
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import sys,tempfile,unittest,json,time
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'installer'))
import app
from test_installer import fixture

class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.window=app.Window();self.window.show();self.proc=patch.object(app.engine,'running',return_value=False);self.proc.start();self.dialog=patch.object(app.QMessageBox,'warning');self.dialog.start()
    def tearDown(self):
        if self.window.worker:self.window.worker.wait(10000)
        self.window.close();self.qt.processEvents();self.proc.stop();self.dialog.stop()
    def wait_worker(self):
        end=time.monotonic()+10
        while self.window.worker.isRunning() and time.monotonic()<end:
            self.qt.processEvents();time.sleep(0.01)
        self.assertFalse(self.window.worker.isRunning());QTest.qWait(60)

    def test_steam_repair_opens_correct_game(self):
        with patch('PySide6.QtGui.QDesktopServices.openUrl',return_value=True) as opened:
            self.window.repairSteam()
        self.assertEqual(opened.call_args.args[0].toString(),'steam://validate/1895880')
        self.assertIn('انتظر',self.window.status.text())
    def test_install_and_restore_through_interface(self):
        with tempfile.TemporaryDirectory() as d:
            game=Path(d);original=fixture(game);self.window.path.setText(d);self.window.start('install');self.assertFalse(self.window.install.isEnabled());self.wait_worker();self.assertTrue(self.window.install.isEnabled());self.assertEqual(json.loads((game/'.rift-apart-ar/state.json').read_text())['version'],'1.9.9');self.assertNotEqual((game/'toc').read_bytes(),original)
            self.assertEqual(self.window.restore.text(),'حذف التعريب');self.window.start('restore');self.wait_worker();self.assertIn('حذف التعريب',self.window.status.text());self.assertEqual((game/'toc').read_bytes(),original);self.assertFalse((game/'d/mods/arabic_loc').exists());self.assertTrue(self.window.restore.isEnabled())
    def test_invalid_folder_recovers_controls(self):
        with tempfile.TemporaryDirectory() as d:
            self.window.path.setText(d);self.window.start('install');self.wait_worker();self.assertTrue(self.window.install.isEnabled());self.assertTrue(self.window.path.isEnabled());self.assertIn('toc',self.window.status.text())
    def test_empty_path_and_media_controls(self):
        end=time.monotonic()+10
        while self.window.player.playbackState()!=app.QMediaPlayer.PlayingState and time.monotonic()<end:QTest.qWait(30)
        self.assertEqual(self.window.player.playbackState(),app.QMediaPlayer.PlayingState)
        self.window.path.clear();self.window.start('install');self.assertIsNone(self.window.worker);self.assertIn('اختر',self.window.status.text());self.assertTrue(self.window.audio.isMuted());self.window.toggleSound();self.assertFalse(self.window.audio.isMuted());self.window.toggleSound();self.assertTrue(self.window.audio.isMuted());self.window.togglePlay();self.assertEqual(self.window.player.playbackState(),app.QMediaPlayer.PausedState);self.window.togglePlay();self.assertEqual(self.window.player.playbackState(),app.QMediaPlayer.PlayingState)
    def test_small_display_can_scroll(self):
        self.window.resize(1060,680);self.qt.processEvents();self.assertLessEqual(self.window.height(),700);self.assertGreater(self.window.scroll.verticalScrollBar().maximum(),0);self.window.scroll.ensureWidgetVisible(self.window.install);self.qt.processEvents();self.assertTrue(self.window.install.isVisible())
