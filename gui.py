#!/usr/bin/env python3
import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtWidgets import(QTableView, QHBoxLayout, QVBoxLayout, QWidget,
                            QApplication, QMainWindow, QAction, QFileDialog,
                            QTextEdit, QAbstractItemView, QHeaderView,
                            QToolButton, QStyle, QSlider, QToolBar,
                            QGridLayout, QPushButton)
from models.playlist_models import DirectoryPlaylist


class PlaylistModel(QtCore.QAbstractTableModel):
    COLUMN_COUNT = 5
    HEADERS = ['title', 'artist', 'album', 'genre', 'file name']

    def __init__(self, parent=None):
        super(PlaylistModel, self).__init__(parent)
        self.playlist = None
        self.urlSongMappings = {}

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self.playlist.mediaCount() if not parent.isValid() else 0

    def columnCount(self, parent=QtCore.QModelIndex()):
        return self.COLUMN_COUNT if not parent.isValid() else 0

    # not sure about this qmodelindex thing
    def index(self, row, column, parent=QtCore.QModelIndex()):
        if(self.playlist is not None and not parent.isValid() and
                row >= 0 and row < self.playlist.mediaCount() and
                column >= 0 and column < self.COLUMN_COUNT):
            return self.createIndex(row, column)
        else:
            return QtCore.QModelIndex()

        def parent(self, child):
            return QtCore.QModelIndex()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if(role == QtCore.Qt.DisplayRole and
                orientation == QtCore.Qt.Horizontal):
            return self.HEADERS[section]
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            if index.column() == self.HEADERS.index('title'):
                location = self.playlist.media(index.row()).canonicalUrl()
                return self.urlSongMappings[location].tags['title'][0]
            elif index.column() == self.HEADERS.index('artist'):
                location = self.playlist.media(index.row()).canonicalUrl()
                return self.urlSongMappings[location].tags['artist'][0]
            elif index.column() == self.HEADERS.index('album'):
                location = self.playlist.media(index.row()).canonicalUrl()
                return self.urlSongMappings[location].tags['album'][0]
            elif index.column() == self.HEADERS.index('genre'):
                location = self.playlist.media(index.row()).canonicalUrl()
                return self.urlSongMappings[location].tags['genre'][0]
            elif index.column() == self.HEADERS.index('file name'):
                return self.playlist.media(
                    index.row()).canonicalUrl().toLocalFile()
        return None

    def setPlaylist(self, playlist):
        self.beginResetModel()
        self.playlist = playlist

        if self.playlist is not None:
            self.playlist.mediaAboutToBeInserted.connect(
                self.beginInsertItems)
            self.playlist.mediaInserted.connect(self.endInsertItems)
            self.playlist.mediaAboutToBeRemoved.connect(
                self.beginRemoveItems)
            self.playlist.mediaRemoved.connect(self.endRemoveItems)
            self.playlist.mediaChanged.connect(self.changeItems)

        self.endResetModel()

    def beginInsertItems(self, start, end):
        self.beginInsertRows(QtCore.QModelIndex(), start, end)

    def endInsertItems(self):
        self.endInsertRows()

    def beginRemoveItems(self, start, end):
        self.beginRemoveRows(QtCore.QModelIndex(), start, end)

    def endRemoveItems(self):
        self.endRemoveRows()

    def changeItems(self, start, end):
        self.dataChanged.emit(self.index(start, 0),
                              self.index(end, self.COLUMN_COUNT))

    def addToPlaylist(self, songs):
        new_mappings = {}
        for song in songs:
            fileInfo = QtCore.QFileInfo(song.url)
            if fileInfo.exists():
                url = QtCore.QUrl.fromLocalFile(fileInfo.absoluteFilePath())
                if fileInfo.suffix().lower() == 'mp3':
                    self.playlist.addMedia(QMediaContent(url))
                    new_mappings[url] = song
            else:
                url = QtCore.QUrl(song.url)
                if url.isValid():
                    self.playlist.addMedia(QMediaContent(url))
                    new_mappings[url] = song
        self.urlSongMappings = new_mappings


# TODO subclass QSlider to calculate pageStep (make direct jumps)
class PlayerControlsWidget(QWidget):
    play = QtCore.pyqtSignal()
    pause = QtCore.pyqtSignal()
    stop = QtCore.pyqtSignal()
    nextSong = QtCore.pyqtSignal()
    previousSong = QtCore.pyqtSignal()
    volumeControl = QtCore.pyqtSignal(int)

    def __init__(self, defaultVolume, parent=None):
        super(PlayerControlsWidget, self).__init__(parent)
        self.playerState = QMediaPlayer.StoppedState
        self.defaultVolume = defaultVolume

        self.playButton = QToolButton(self)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.nextButton = QToolButton(self)
        self.nextButton.setIcon(
            self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.previousButton = QToolButton(self)
        self.previousButton.setIcon(
            self.style().standardIcon(QStyle.SP_MediaSkipBackward))

        self.volumeSlider = QSlider(QtCore.Qt.Horizontal, self)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(self.defaultVolume)

        self.playButton.clicked.connect(self._onPlay)
        self.nextButton.clicked.connect(self._onNext)
        self.previousButton.clicked.connect(self._onPrevious)
        self.volumeSlider.sliderMoved.connect(self._changeVolume)
        self.volumeSlider.valueChanged.connect(self._changeVolume)

        self.initGUI()

    def initGUI(self):
        hLayout = QHBoxLayout()
        hLayout.addWidget(self.previousButton)
        hLayout.addWidget(self.playButton)
        hLayout.addWidget(self.nextButton)
        hLayout.addWidget(self.volumeSlider)
        self.setLayout(hLayout)

    def _onPlay(self):
        if self.playerState in (QMediaPlayer.StoppedState,
                                QMediaPlayer.PausedState):
            self.playerState = QMediaPlayer.PlayingState
            self.play.emit()
        elif self.playerState == QMediaPlayer.PlayingState:
            self.playerState = QMediaPlayer.PausedState
            self.pause.emit()

    def _onNext(self):
        self.nextSong.emit()

    def _onPrevious(self):
        self.previousSong.emit()

    def _changeVolume(self, value):
        self.volumeControl.emit(value)


class Player(QMainWindow):
    DEFAULT_VOLUME = 30

    def __init__(self, parent=None,):
        super(Player, self).__init__(parent)

        self.player = QMediaPlayer()
        self.player.setVolume(self.DEFAULT_VOLUME)

        self.playlist = QMediaPlaylist(self.player)
        self.playlist.setCurrentIndex(1)
        self.player.positionChanged.connect(self._changeSongTimestamp)

        self.player.setPlaylist(self.playlist)

        self.playlistModel = PlaylistModel()
        self.playlistModel.setPlaylist(self.playlist)

        self.playlistView = QTableView(self)
        self.playlistView.setModel(self.playlistModel)
        self.playlistView.setCurrentIndex(
            self.playlistModel.index(self.playlist.currentIndex(), 0))
        self.playlistView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.playlistView.setShowGrid(False)
        self.playlistView.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self.playlistView.clicked.connect(self.singleClickedTest)
        self.playlistView.doubleClicked.connect(self.doubleClickedPlayPause)

        self.playlistView.setSortingEnabled(True)

        self.setPlayerControls()
        self.initUi()

    def initUi(self):
        self.statusBar()

        openFile = QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new directory')
        openFile.triggered.connect(self.choose_directory)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)

        self.centralwidget = QWidget(self)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.addWidget(self.playlistView, 1, 2, 1,
                                  PlaylistModel.COLUMN_COUNT)
        self.gridLayout.addWidget(self.playerControls, 2, 2, 1, 3)

        self.setCentralWidget(self.centralwidget)

        self.setGeometry(300, 300, 850, 800)
        self.setWindowTitle('Main Window')

    # TODO
    def _changeSongTimestamp(newPosition):
        pass

    def setPlayerControls(self):
        self.playerControls = PlayerControlsWidget(self.DEFAULT_VOLUME)
        self.playerControls.play.connect(self._play)
        self.playerControls.pause.connect(self._pause)
        self.playerControls.previousSong.connect(self._previous)
        self.playerControls.nextSong.connect(self._next)
        self.playerControls.volumeControl.connect(self._changeVolume)

    def _play(self):
        self.player.play()

    def _pause(self):
        self.player.pause()

    def _previous(self):
        # TODO play same song if in first 6-7 seconds of current song
        self.playlist.previous()

    def _next(self):
        self.playlist.next()

    def _changeVolume(self, value):
        self.player.setVolume(value)

    def choose_directory(self):
        fname = QFileDialog.getExistingDirectory(
            self, 'Open file', '/home',
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if not fname == '':
            directoryPlaylist = DirectoryPlaylist(fname)
            self.playlistModel.addToPlaylist(directoryPlaylist.songs)

    def singleClickedTest(self, index):
        # TODO stuff maybe?!
        print(self.playlistView.selectionModel().currentIndex().row())

    def doubleClickedPlayPause(self, index):
        currentIndex = self.playlist.currentIndex()
        newIndex = index.row()

        if currentIndex == newIndex:
            if self.player.state() == QMediaPlayer.StoppedState:
                self.player.play()
            elif self.player.state() == QMediaPlayer.PlayingState:
                self.player.pause()
            elif self.player.state() == QMediaPlayer.PausedState:
                self.player.play()
        else:
            self.playlist.setCurrentIndex(newIndex)
            self.player.play()

    # Not working
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif e.key() == QtCore.Qt.Key_Space:
            if self.player.state() == QMediaPlayer.PlayingState:
                self.player.pause()
            elif self.player.state() == QMediaPlayer.PausedState:
                self.player.play()
        elif e.key() == QtCore.Qt.Key_Enter:
            newIndex = self.playlist.currentIndex()
            self.playlist.setCurrentIndex(newIndex)
            self.player.play()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    player = Player()
    player.show()

    sys.exit(app.exec_())
