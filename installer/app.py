# SPDX-License-Identifier: GPL-3.0-only
"""Rift Apart AR — desktop installer for Linux and Windows."""
from pathlib import Path
import sys, math, random
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QRectF, QUrl
from PySide6.QtGui import QColor, QPainter, QPen, QLinearGradient, QRadialGradient, QFont, QDesktopServices
from PySide6.QtWidgets import QApplication,QWidget,QLabel,QPushButton,QVBoxLayout,QHBoxLayout,QLineEdit,QFileDialog,QFrame,QProgressBar,QMessageBox
import engine

def payload_path():return Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))/'payload'

class Portal(QWidget):
    def __init__(self):
        super().__init__();self.setMinimumWidth(330);self.setMaximumWidth(370);self.setMinimumHeight(620)
        self.setLayoutDirection(Qt.LeftToRight)
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);w=self.width();h=self.height()
        g=QLinearGradient(0,0,w,h);g.setColorAt(0,QColor('#16183c'));g.setColorAt(.6,QColor('#12152c'));g.setColorAt(1,QColor('#090e1d'));p.fillRect(self.rect(),g)
        rng=random.Random(42)
        for i in range(100):
            p.setPen(QColor(149,166,218,rng.randrange(35,150)));p.drawPoint(rng.randrange(w),rng.randrange(h))
        cx=w*.50;cy=h*.48
        glow=QRadialGradient(cx,cy,180);glow.setColorAt(0,QColor(89,57,173,95));glow.setColorAt(.7,QColor(85,59,156,55));glow.setColorAt(1,QColor(85,59,156,0));p.fillRect(self.rect(),glow)
        p.save();p.translate(cx,cy);p.rotate(-24)
        for i in range(16,0,-1):
            p.setPen(QPen(QColor(114,83,255,max(5,60-i*3)),i*2));p.drawEllipse(QRectF(-91,-126,182,252))
        ring=QLinearGradient(-100,-126,100,126);ring.setColorAt(0,QColor('#5ce7e8'));ring.setColorAt(.44,QColor('#bba7ff'));ring.setColorAt(1,QColor('#e18be5'))
        p.setPen(QPen(ring,3));p.setBrush(QColor('#0f1429'));p.drawEllipse(QRectF(-91,-126,182,252))
        for i in range(3):
            p.setPen(QPen(QColor(139,111,250,60-i*15),1));p.drawEllipse(QRectF(-80+i*9,-114+i*12,160-i*18,228-i*24))
        p.restore()
        p.setPen(QColor('#f1f3ff'));p.setFont(QFont('DejaVu Sans',20,QFont.Bold));p.drawText(QRectF(32,38,w-64,40),Qt.AlignLeft,'RIFT APART')
        p.setPen(QColor('#73e4e5'));p.setFont(QFont('DejaVu Sans',10,QFont.Medium));p.drawText(QRectF(33,78,w-64,30),Qt.AlignLeft,'ARABIC • COMMUNITY EDITION')
        p.setPen(QColor('#ffffff'));p.setFont(QFont('Noto Sans Arabic',46,QFont.Bold));p.drawText(QRectF(35,cy-47,w-70,95),Qt.AlignCenter,'عربي')
        p.setPen(QColor('#a1accb'));p.setFont(QFont('DejaVu Sans',9));p.drawText(QRectF(32,h-110,w-64,30),Qt.AlignLeft,'BUILT BY THE COMMUNITY')
        p.setPen(QColor('#d7def5'));p.setFont(QFont('Noto Sans Arabic',12));p.drawText(QRectF(32,h-76,w-64,30),Qt.AlignRight,'مغامرة واحدة. أبعاد بلا حدود.')
        p.setPen(QColor('#697899'));p.setFont(QFont('DejaVu Sans',9));p.drawText(QRectF(32,h-39,w-64,20),Qt.AlignLeft,'exelight7 / rift-apart-AR')

class Worker(QThread):
    progress=Signal(int,str);done=Signal(bool,str)
    def __init__(self,path,mode):super().__init__();self.path=path;self.mode=mode
    def run(self):
        try:
            if self.mode=='install':engine.install(self.path,payload_path(),self.progress.emit)
            else:engine.restore(self.path,self.progress.emit)
            self.done.emit(True,'اكتمل التثبيت. اختر English في لغة اللعبة على Steam، ثم شغّلها.' if self.mode=='install' else 'تمت استعادة ملفات اللعبة الأصلية.')
        except Exception as e:self.done.emit(False,str(e))

class Window(QWidget):
    def __init__(self):
        super().__init__();self.worker=None;self.setWindowTitle('Rift Apart AR • تثبيت التعريب');self.resize(1100,850);self.setMinimumSize(1020,820)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet('''
        QWidget{background:#0d1222;color:#eef2ff;font-family:"Noto Sans Arabic","Segoe UI",sans-serif;font-size:14px;}
        QLabel{background:transparent;}
        QLabel#muted{color:#8d9bb7;font-size:13px;}
        QLabel#eyebrow{color:#79dfde;font-size:12px;font-weight:600;}
        QLabel#title{font-size:29px;font-weight:700;}
        QLabel#badge{background:#23203f;color:#c4b5fd;border:1px solid #3b325c;border-radius:12px;padding:5px 13px;font-size:11px;}
        QFrame#card{background:#141c2f;border:1px solid #263047;border-radius:16px;}
        QLineEdit{background:#0e1525;border:1px solid #303c56;border-radius:10px;padding:13px;color:#dfe8ff;font-size:12px;}
        QLineEdit:focus{border:1px solid #7d70ef;}
        QPushButton{background:#222c43;border:1px solid #34405a;border-radius:10px;padding:11px 18px;color:#dfe7fa;font-weight:600;}
        QPushButton:hover{background:#2b3652;border-color:#67769c;}
        QPushButton:disabled{background:#1b2233;color:#5d6881;border-color:#252e43;}
        QPushButton#primary{background:#9c87fa;color:#12152b;border:0;font-size:16px;padding:15px 24px;}
        QPushButton#primary:hover{background:#b4a2ff;}
        QPushButton#primary:disabled{background:#3a345c;color:#827b9c;}
        QPushButton#link{background:transparent;border:0;color:#a7b6d3;font-size:12px;padding:6px;}
        QProgressBar{background:#252e43;border:0;border-radius:3px;height:6px;color:transparent;}
        QProgressBar::chunk{background:#75dedb;border-radius:3px;}
        ''')
        outer=QHBoxLayout(self);outer.setContentsMargins(0,0,0,0);outer.setSpacing(0);outer.setDirection(QHBoxLayout.LeftToRight);outer.addWidget(Portal())
        body=QWidget();outer.addWidget(body,1);v=QVBoxLayout(body);v.setContentsMargins(32,24,32,22);v.setSpacing(12)
        top=QHBoxLayout();ey=QLabel('مجتمع التعريب  /  RIFT APART AR');ey.setObjectName('eyebrow');top.addWidget(ey);top.addStretch();badge=QLabel('v0.2.0 • تجريبية');badge.setObjectName('badge');top.addWidget(badge);v.addLayout(top)
        title=QLabel('افتح بوابة المغامرة.');title.setObjectName('title');v.addWidget(title)
        desc=QLabel('تعريب راتشت وكلانك، بخط واضح ونصوص محسّنة.\nثبّت الحزمة بخطوة واحدة واحتفظ بنسخة للعودة.');desc.setObjectName('muted');desc.setWordWrap(True);v.addWidget(desc)
        card=QFrame();card.setObjectName('card');card.setMinimumHeight(170);cv=QVBoxLayout(card);cv.setContentsMargins(20,18,20,20);cv.setSpacing(12)
        row=QHBoxLayout();row.addWidget(QLabel('01   موقع اللعبة'));row.addStretch();self.detect=QLabel('اكتشاف تلقائي');self.detect.setObjectName('eyebrow');row.addWidget(self.detect);cv.addLayout(row)
        self.path=QLineEdit();self.path.setLayoutDirection(Qt.LeftToRight);self.path.setPlaceholderText('Steam / steamapps / common / Ratchet & Clank - Rift Apart');cv.addWidget(self.path)
        pr=QHBoxLayout();self.browse=QPushButton('اختيار مجلد');self.browse.clicked.connect(self.choose);pr.addWidget(self.browse);pr.addStretch();self.location=QLabel('اختر المجلد الذي يحتوي على toc');self.location.setObjectName('muted');pr.addWidget(self.location);cv.addLayout(pr);v.addWidget(card)
        card2=QFrame();card2.setObjectName('card');card2.setMinimumHeight(152);cv2=QVBoxLayout(card2);cv2.setContentsMargins(20,15,20,15);cv2.setSpacing(9);cv2.addWidget(QLabel('02   جاهز لعبور البوابة'))
        for text in ['✓  حوارات وواجهة مع تصحيح اتجاه النص وتنسيق السطور','✓  DLSS · FSR · XeSS · Ray Tracing تبقى بالإنجليزية','✓  تثبيت دون إنترنت، مع فحص سلامة ونسخة احتياطية']:
            l=QLabel(text);l.setObjectName('muted');l.setWordWrap(True);cv2.addWidget(l)
        v.addWidget(card2)
        notice=QLabel('إصدار تجريبي: تصحيح التنسيق أوسع من المراجعة اللغوية.\nأغلق اللعبة واللانشر قبل التثبيت أو الاستعادة.');notice.setObjectName('muted');notice.setWordWrap(True);v.addWidget(notice)
        v.addStretch(1);self.status=QLabel('جاهز. ملفات الحفظ لا تتغير.');self.status.setObjectName('muted');self.status.setWordWrap(True);v.addWidget(self.status)
        self.progress=QProgressBar();self.progress.setFixedHeight(6);self.progress.setRange(0,100);self.progress.setValue(0);self.progress.setTextVisible(False);v.addWidget(self.progress)
        actions=QHBoxLayout();self.install_btn=QPushButton('تثبيت التعريب  ←');self.install_btn.setObjectName('primary');self.install_btn.clicked.connect(lambda:self.start('install'));actions.addWidget(self.install_btn,2);self.restore_btn=QPushButton('استعادة الأصل');self.restore_btn.clicked.connect(lambda:self.start('restore'));actions.addWidget(self.restore_btn,1);v.addLayout(actions)
        foot=QHBoxLayout();source=QPushButton('المصدر والتحديثات ↗');source.setObjectName('link');source.clicked.connect(lambda:QDesktopServices.openUrl(QUrl('https://github.com/exelight7/rift-apart-AR')));foot.addWidget(source);foot.addStretch();fine=QLabel('Linux + Windows  •  تطبيق مجتمعي غير رسمي');fine.setObjectName('muted');foot.addWidget(fine);v.addLayout(foot)
        found=engine.discover()
        if found:self.path.setText(found[0]);self.location.setText('تم العثور على اللعبة ✓')
        else:self.detect.setText('اختيار يدوي')
    def choose(self):
        path=QFileDialog.getExistingDirectory(self,'اختر مجلد اللعبة',self.path.text())
        if path:self.path.setText(path);self.location.setText('تحقق من المجلد عند التثبيت')
    def start(self,mode):
        if self.worker and self.worker.isRunning():return
        if not self.path.text().strip():self.status.setText('اختر مجلد اللعبة أولًا.');return
        for w in [self.install_btn,self.restore_btn,self.browse,self.path]:w.setEnabled(False)
        self.progress.setValue(0);self.status.setText('بدء الفحص…');self.worker=Worker(self.path.text(),mode);self.worker.progress.connect(self.update);self.worker.done.connect(self.finish);self.worker.start()
    def update(self,n,text):self.progress.setValue(n);self.status.setText(text)
    def finish(self,ok,text):
        for w in [self.install_btn,self.restore_btn,self.browse,self.path]:w.setEnabled(True)
        self.status.setText(text);self.status.setStyleSheet('color:#79dfb9;' if ok else 'color:#ffacb7;')
        if not ok:QMessageBox.warning(self,'تعذر إكمال العملية',text)
    def closeEvent(self,event):
        if self.worker and self.worker.isRunning():event.ignore();return
        event.accept()

def main():
    app=QApplication(sys.argv);app.setApplicationName('Rift Apart AR');app.setStyle('Fusion');window=Window();window.show()
    if '--screenshot' in sys.argv:
        window.path.setText('Steam / steamapps / common / Ratchet & Clank - Rift Apart')
        target=sys.argv[sys.argv.index('--screenshot')+1]
        QTimer.singleShot(700,lambda:(window.grab().save(target),app.quit()))
    sys.exit(app.exec())
if __name__=='__main__':main()
