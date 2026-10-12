# SPDX-License-Identifier: GPL-3.0-only
"""Rift Apart AR desktop installer."""
import sys,json,math
from pathlib import Path
from PySide6.QtCore import Qt,QThread,Signal,QTimer,QUrl,QRectF
from PySide6.QtGui import QPainter,QPainterPath,QColor,QImage,QFont,QLinearGradient,QIcon
from PySide6.QtWidgets import QApplication,QWidget,QFrame,QLabel,QPushButton,QVBoxLayout,QHBoxLayout,QLineEdit,QFileDialog,QProgressBar,QSlider,QMessageBox,QScrollArea
from PySide6.QtMultimedia import QMediaPlayer,QAudioOutput,QVideoSink
import engine
BASE=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))

def label(text,name='muted',wrap=False):
    w=QLabel(text);w.setObjectName(name);w.setWordWrap(wrap);return w

def button(text,name='secondary'):
    w=QPushButton(text);w.setObjectName(name);w.setCursor(Qt.PointingHandCursor);return w

class VideoCanvas(QWidget):
    def __init__(self):
        super().__init__();self.image=QImage(str(BASE/'assets/poster.jpg'));self.frames=0;self.setMinimumHeight(215)
    def frame(self,frame):
        if frame.isValid():
            image=frame.toImage()
            if not image.isNull():self.image=image;self.frames+=1;self.update()
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.setRenderHint(QPainter.SmoothPixmapTransform)
        path=QPainterPath();path.addRoundedRect(QRectF(self.rect()),19,19);p.setClipPath(path);p.fillRect(self.rect(),QColor('#151817'))
        if not self.image.isNull():
            iw,ih=self.image.width(),self.image.height();scale=max(self.width()/iw,self.height()/ih);w,h=self.width()/scale,self.height()/scale
            p.drawImage(QRectF(self.rect()),self.image,QRectF((iw-w)/2,(ih-h)/2,w,h))

class Worker(QThread):
    progress=Signal(int,str);done=Signal(bool,str,bool)
    def __init__(self,path,mode):super().__init__();self.path=path;self.mode=mode
    def run(self):
        try:
            if self.mode=='install':
                record=engine.install(self.path,BASE/'payload',self.progress.emit)
                message='اكتمل تحديث التعريب. النسخة السابقة محفوظة؛ الحذف الكامل يحتاج إصلاح Steam لعدم وجود أصل محفوظ.' if record.get('legacy_baseline') else 'اكتمل تثبيت التعريب. اجعل لغة اللعبة English في Steam ثم شغّلها.'
            else:
                engine.restore(self.path,self.progress.emit,payload=BASE/'payload')
                message='تم حذف التعريب وإرجاع ملفات اللعبة الأصلية.'
            self.done.emit(True,message,False)
        except PermissionError:
            self.done.emit(False,'لا توجد صلاحية للكتابة في مجلد اللعبة. أغلق اللعبة واللانشر، ثم شغّل المثبّت كمسؤول وأعد المحاولة.',False)
        except Exception as e:self.done.emit(False,str(e),isinstance(e,engine.RecoveryRequired))

class Header(QWidget):
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton and self.window().windowHandle():self.window().windowHandle().startSystemMove()

class Window(QWidget):
    def __init__(self):
        super().__init__();self.worker=None;self.setWindowTitle('Rift Apart AR — تثبيت التعريب');self.setWindowIcon(QIcon(str(BASE/'assets/icon.png')));self.setWindowFlags(Qt.Window|Qt.FramelessWindowHint);self.resize(1180,890);self.setMinimumSize(980,680);self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet('''
        QScrollArea{border:0;} QScrollBar:vertical{background:#171d16;width:6px;margin:0;} QScrollBar::handle:vertical{background:#526044;min-height:25px;border-radius:3px;} QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}
        QWidget{background:#101311;color:#f3f2e9;font-family:"Noto Sans Arabic","DejaVu Sans",sans-serif;font-size:14px;}
        QLabel{background:transparent;} QLabel#muted{color:#9da69b;font-size:12px;} QLabel#eyebrow{color:#fbab61;font-size:11px;font-weight:700;}
        QLabel#title{font-size:35px;font-weight:700;letter-spacing:-1px;} QLabel#mediaTitle{font-family:"DejaVu Sans";font-size:24px;font-weight:800;letter-spacing:2px;}
        QLabel#badge{background:#272d24;color:#d4deb9;border:1px solid #3c4731;border-radius:11px;padding:4px 11px;font-size:11px;}
        QFrame#media{background:#191e19;border:1px solid #30382e;border-radius:24px;}
        QFrame#card{background:#191f19;border:1px solid #333c30;border-radius:18px;}
        QFrame#stat{background:#1d241b;border:1px solid #323d2b;border-radius:14px;}
        QLabel#number{font-family:"DejaVu Sans";font-size:24px;font-weight:700;color:#e6ebd4;}
        QLineEdit{background:#101610;border:1px solid #3c4735;border-radius:10px;padding:13px;color:#e4e8dc;font-family:"DejaVu Sans";font-size:11px;}
        QLineEdit:focus{border-color:#f7a358;}
        QPushButton{background:#252d23;color:#e6eadb;border:1px solid #3b4832;border-radius:10px;padding:10px 15px;font-size:12px;font-weight:600;}
        QPushButton:hover{background:#333e2d;border-color:#70825b;}
        QPushButton:disabled{background:#20261e;color:#707b67;border-color:#30392b;}
        QPushButton#primary{background:#ffab63;color:#23170c;border:0;border-radius:13px;padding:17px;font-size:17px;font-weight:700;}
        QPushButton#primary:hover{background:#ffc18a;} QPushButton#primary:disabled{background:#63503b;color:#a89986;}
        QPushButton#quiet{background:transparent;border:0;color:#a3ad99;padding:7px;font-size:11px;}
        QPushButton#window{background:transparent;border:0;padding:0;font-family:"DejaVu Sans";font-size:22px;color:#aab09f;}
        QPushButton#window:hover{background:#333d2d;color:white;}
        QProgressBar{background:#30392c;border:0;border-radius:3px;height:5px;color:transparent;} QProgressBar::chunk{background:#ffab63;border-radius:3px;}
        QSlider::groove:horizontal{background:#343d30;height:3px;border-radius:1px;} QSlider::sub-page:horizontal{background:#f9ae72;border-radius:1px;} QSlider::handle:horizontal{background:#f5d0aa;width:9px;margin:-3px 0;border-radius:4px;}
        ''')
        root=QVBoxLayout(self);root.setContentsMargins(24,13,24,18);root.setSpacing(17)
        header=Header();h=QHBoxLayout(header);h.setContentsMargins(0,0,0,0);h.setDirection(QHBoxLayout.LeftToRight)
        brand=label('RIFT APART  /  ARABIC EDITION','eyebrow');brand.setLayoutDirection(Qt.LeftToRight);h.addWidget(brand);h.addStretch();h.addWidget(label('v'+engine.VERSION,'badge'))
        mini=button('−','window');mini.setFixedSize(32,30);mini.clicked.connect(self.showMinimized);h.addWidget(mini);close=button('×','window');close.setFixedSize(32,30);close.clicked.connect(self.close);h.addWidget(close);root.addWidget(header)
        row=QHBoxLayout();row.setDirection(QHBoxLayout.LeftToRight);row.setSpacing(27);root.addLayout(row,1)
        media=QFrame();media.setObjectName('media');media.setFixedWidth(490);self.mediaPanel=media;mv=QVBoxLayout(media);mv.setContentsMargins(16,17,16,16);mv.setSpacing(12)
        mediaHead=QHBoxLayout();mediaHead.setDirection(QHBoxLayout.LeftToRight);mediaHead.addWidget(label('A NEW\nDIMENSION.','mediaTitle'));mediaHead.addStretch();stamp=label('01 /  AR','eyebrow');stamp.setLayoutDirection(Qt.LeftToRight);mediaHead.addWidget(stamp);mv.addLayout(mediaHead)
        self.canvas=VideoCanvas();mv.addWidget(self.canvas,1)
        self.timeline=QSlider(Qt.Horizontal);self.timeline.setLayoutDirection(Qt.LeftToRight);self.timeline.sliderMoved.connect(lambda n:self.player.setPosition(n));mv.addWidget(self.timeline)
        controls=QHBoxLayout();controls.setDirection(QHBoxLayout.LeftToRight);self.play=button('إيقاف مؤقت','quiet');self.play.clicked.connect(self.togglePlay);controls.addWidget(self.play);self.sound=button('تشغيل الصوت','quiet');self.sound.clicked.connect(self.toggleSound);controls.addWidget(self.sound);controls.addStretch();self.time=label('00:00 / 00:16');self.time.setLayoutDirection(Qt.LeftToRight);controls.addWidget(self.time);mv.addLayout(controls)
        mv.addWidget(label('مغامرة واحدة. أبعاد بلا حدود.','eyebrow'));row.addWidget(media)
        body=QWidget();v=QVBoxLayout(body);v.setContentsMargins(0,8,0,0);v.setSpacing(7);body.setMinimumHeight(700);self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);self.scroll.setFrameShape(QFrame.NoFrame);self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);self.scroll.setWidget(body);row.addWidget(self.scroll,1)
        v.addWidget(label('RATCHET & CLANK: RIFT APART','eyebrow'));v.addWidget(label('جاهز لبُعد جديد؟','title'));v.addWidget(label('نصوص عربية محسّنة. كل كلمة أقرب للمغامرة.','muted',True))
        card=QFrame();card.setObjectName('card');card.setMinimumHeight(174);cv=QVBoxLayout(card);cv.setContentsMargins(19,16,19,16);cv.setSpacing(10)
        cr=QHBoxLayout();cr.addWidget(label('موقع اللعبة'));cr.addStretch();self.detect=label('اختيار المجلد','eyebrow');cr.addWidget(self.detect);cv.addLayout(cr)
        self.path=QLineEdit();self.path.setFixedHeight(48);self.path.setLayoutDirection(Qt.LeftToRight);self.path.setPlaceholderText('Steam / steamapps / common / Ratchet & Clank - Rift Apart');cv.addWidget(self.path)
        fr=QHBoxLayout();self.browse=button('اختيار مجلد');self.browse.setFixedHeight(48);self.browse.clicked.connect(self.choose);fr.addWidget(self.browse);fr.addStretch();self.location=label('اختر المجلد الذي يحتوي على toc','muted');fr.addWidget(self.location);cv.addLayout(fr);v.addWidget(card)
        detail=label('✓  حوارات وقوائم وإعدادات عربية\n✓  DLSS · FSR · XeSS · Ray Tracing بالإنجليزية\n✓  نسخة احتياطية واستعادة الأصل','muted',True);v.addWidget(detail)
        v.addStretch(1);self.status=label('جاهز للتثبيت. ملفات الحفظ لا تتغير.','muted',True);self.status.setMinimumHeight(34);v.addWidget(self.status);self.progress=QProgressBar();self.progress.setFixedHeight(5);self.progress.setValue(0);self.progress.setTextVisible(False);v.addWidget(self.progress)
        self.install=button('ثبّت التعريب  ←','primary');self.install.clicked.connect(lambda:self.start('install'));v.addWidget(self.install)
        actions=QHBoxLayout();self.restore=button('حذف التعريب','secondary');self.restore.setToolTip('يحذف التعريب ويرجع ملفات اللعبة الأصلية دون تغيير ملفات الحفظ');self.restore.clicked.connect(lambda:self.start('restore'));actions.addWidget(self.restore);self.repair=button('إصلاح عبر Steam','quiet');self.repair.clicked.connect(self.repairSteam);actions.addWidget(self.repair);actions.addStretch();actions.addWidget(label('WINDOWS  /  EXE' if sys.platform=='win32' else 'LINUX  /  APPIMAGE','eyebrow'));v.addLayout(actions)
        footer=QHBoxLayout();footer.addWidget(label('تعريب مجتمعي غير رسمي','muted'));footer.addStretch();credit=label('exelight7  /  RIFT APART AR','muted');credit.setLayoutDirection(Qt.LeftToRight);footer.addWidget(credit);root.addLayout(footer)
        self.player=QMediaPlayer(self);self.audio=QAudioOutput(self);self.audio.setMuted(True);self.player.setAudioOutput(self.audio);self.sink=QVideoSink(self);self.sink.videoFrameChanged.connect(self.canvas.frame);self.player.setVideoSink(self.sink);self.player.setLoops(QMediaPlayer.Infinite);self.player.durationChanged.connect(self.timeline.setMaximum);self.player.positionChanged.connect(self.position);self.player.errorOccurred.connect(self.videoError);self.player.setSource(QUrl.fromLocalFile(str(BASE/'assets/scene.webm')));self.player.play()
        found=engine.discover()
        if found:self.path.setText(found[0]);self.detect.setText('تم اكتشافها ✓');self.location.setText('تم العثور على مجلد اللعبة')
        else:self.detect.setText('اختيار يدوي')
    def resizeEvent(self,event):
        if hasattr(self,'mediaPanel'):self.mediaPanel.setFixedWidth(max(350,min(490,int(self.width()*.415))))
        super().resizeEvent(event)
    def position(self,n):
        if not self.timeline.isSliderDown():self.timeline.setValue(n)
        self.time.setText(f'00:{n//1000:02} / 00:{self.player.duration()//1000:02}')
    def togglePlay(self):
        if self.player.playbackState()==QMediaPlayer.PlayingState:self.player.pause();self.play.setText('تشغيل المقطع')
        else:self.player.play();self.play.setText('إيقاف مؤقت')
    def toggleSound(self):self.audio.setMuted(not self.audio.isMuted());self.sound.setText('تشغيل الصوت' if self.audio.isMuted() else 'كتم الصوت')
    def videoError(self,*args):self.play.setText('تعذر تشغيل المقطع');self.play.setToolTip(self.player.errorString())
    def choose(self):
        path=QFileDialog.getExistingDirectory(self,'اختر مجلد اللعبة',self.path.text())
        if path:self.path.setText(path);self.location.setText('سيُفحص المجلد قبل التثبيت')
    def start(self,mode):
        if self.worker and self.worker.isRunning():return
        path=self.path.text().strip().strip('"').strip()
        if not path:self.status.setText('اختر مجلد اللعبة أولًا.');return
        self.path.setText(path)
        for w in [self.install,self.restore,self.browse,self.path,self.repair]:w.setEnabled(False)
        self.progress.setValue(0);self.status.setText('جارٍ فحص الحزمة واللعبة…');self.worker=Worker(self.path.text(),mode);self.worker.progress.connect(self.updateProgress);self.worker.done.connect(self.finish);self.worker.start()
    def updateProgress(self,n,text):self.progress.setValue(n);self.status.setText(text)
    def finish(self,ok,text,repair=False):
        for w in [self.install,self.restore,self.browse,self.path,self.repair]:w.setEnabled(True)
        self.status.setText(text);self.status.setStyleSheet('color:#b7d297' if ok else 'color:#ffb5a0')
        if repair:
            box=QMessageBox(self);box.setWindowTitle('إصلاح ملفات اللعبة');box.setText(text)
            openSteam=box.addButton('فتح إصلاح Steam',QMessageBox.AcceptRole)
            box.addButton('إغلاق',QMessageBox.RejectRole);box.exec()
            if box.clickedButton()==openSteam:self.repairSteam()
        elif not ok:QMessageBox.warning(self,'تعذر إكمال العملية',text)

    def repairSteam(self):
        from PySide6.QtGui import QDesktopServices
        if QDesktopServices.openUrl(QUrl('steam://validate/1895880')):
            self.status.setText('انتظر انتهاء التحقق في Steam، ثم أغلق اللعبة وأعد الضغط على التثبيت أو الحذف. قد يعيد Steam تنزيل ملفات معدلة.')
        else:
            self.status.setText('افتح Steam ← خصائص اللعبة ← الملفات المثبتة ← التحقق من سلامة ملفات اللعبة، ثم أعد المحاولة.')
    def closeEvent(self,event):
        if self.worker and self.worker.isRunning():event.ignore();return
        self.player.stop();event.accept()

def main():
    app=QApplication(sys.argv);app.setStyle('Fusion');w=Window();screen=app.primaryScreen().availableGeometry();w.resize(min(1180,screen.width()-40),min(890,screen.height()-48));w.show()
    if '--screenshot' in sys.argv:
        w.resize(1180,890);target=sys.argv[sys.argv.index('--screenshot')+1];w.path.setText('Steam / steamapps / common / Ratchet & Clank - Rift Apart')
        def capture():
            w.grab().save(target);report={'video_frames':w.canvas.frames,'duration_ms':w.player.duration(),'position_ms':w.player.position(),'video_error':w.player.errorString(),'window':[w.width(),w.height()],'payload_assets':len(engine.verify_payload(BASE/'payload')['files']),'payload_files':engine.verify_payload(BASE/'payload')['files'],'payload_version':engine.VERSION};Path(target+'.json').write_text(json.dumps(report,indent=2));app.exit(0 if w.canvas.frames>3 and not w.player.errorString() else 2)
        QTimer.singleShot(3200,capture)
    sys.exit(app.exec())
if __name__=='__main__':main()
