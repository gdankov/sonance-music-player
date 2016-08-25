from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QFrame, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5 import QtGui, QtCore



class CoverArt(QLabel):

    clicked = pyqtSignal()

    def __init__(self, clickable=False, parent=None):
        super(CoverArt, self).__init__(parent)
        self.setClickable(clickable)

        # self.setMinimumSize(180, 180)
        # self.setMaximumSize(300, 300)

        self.setScaledContents(False)

    def setClickable(self, clickable):
        if clickable:
            self._isClickable = True
            self.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        else:
            self.setCursor(QtGui.QCursor())

    def sizeHint(self):
        w = self.width()
        return QSize(w, self.heightForWidth(w))

    def heightForWidth(self, width):
        return self.width()

    def setPixmap(self, pixmap):
        self.pixmap = pixmap
        super(CoverArt, self).setPixmap(self.scaledPixmap())

    def setCoverArt(self, cover):
        if cover:
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(cover)
            self.pixmap = pixmap
            self.setPixmap(pixmap)
        else:
            self.setPixmap(QtGui.QPixmap(':/left_sidebar_icons/default_album_cover.png'))

    def scaledPixmap(self):
        return self.pixmap.scaled(self.size(), Qt.KeepAspectRatio,
                                  Qt.SmoothTransformation)

    def resizeEvent(self, event):
        if not self.pixmap.isNull():
            super(CoverArt, self).setPixmap(self.scaledPixmap())


class InformationLabel(QFrame):
    def __init__(self, songName='unknown', artistName='unknown', parent=None):
        super(InformationLabel, self).__init__(parent)

        self.songName = songName
        self.artistName = artistName
        self._renderUI()

    def _renderUI(self):
        self.songNameLabel = QLabel(self.songName)
        self.artistNameLabel = QLabel(self.artistName)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.songNameLabel, 0, Qt.AlignLeft)
        self.layout.addWidget(self.artistNameLabel, 0, Qt.AlignLeft)
        self.setLayout(self.layout)

    def setInformation(self, title, artist):
        self.songName = title
        self.artistName = artist
        self.songNameLabel.setText(self.songName)
        self.artistNameLabel.setText(self.artistName)


class CoverArtBox(QWidget):
    def __init__(self, parent=None):
        super(CoverArtBox, self).__init__(parent)
        self._renderUI()

    def _renderUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # self.setFlat(True)

        defaultAlbumCover = QtGui.QPixmap(':/left_sidebar_icons/default_album_cover.png')

        self.coverArt = CoverArt()
        self.coverArt.setPixmap(defaultAlbumCover)
        self.coverArt.setFrameShape(QFrame.Box)
        self.coverArt.setAlignment(Qt.AlignHCenter)
        self.coverArt.setSizePolicy(QSizePolicy.MinimumExpanding,
                                    QSizePolicy.MinimumExpanding)

        self.infoLabel = InformationLabel()
        self.coverArt.setSizePolicy(QSizePolicy.MinimumExpanding,
                                    QSizePolicy.Fixed)
        # self.coverArt.clicked.connect(self.)

        self.layout.addWidget(self.coverArt)
        self.layout.addWidget(self.infoLabel, 0, Qt.AlignBottom)

        self.setLayout(self.layout)

    @QtCore.pyqtSlot(str, str, bytes)
    def setCoverArtBox(self, title, artist, coverArt):
        self.coverArt.setCoverArt(coverArt)
        self.infoLabel.setInformation(title, artist)
