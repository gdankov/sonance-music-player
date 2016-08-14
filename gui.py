#!/usr/bin/env python3
import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtWidgets import(QTableView, QHBoxLayout, QVBoxLayout, QWidget,
                            QApplication, QMainWindow, QAction, QFileDialog,
                            QTextEdit, QAbstractItemView, QHeaderView,
                            QToolButton, QStyle, QSlider, QToolBar,
                            QGridLayout, QPushButton, QLabel, QFrame,
                            QStackedWidget, QSizePolicy, QSpacerItem,
                            QSplitter, QTreeView)

from models.playlist_models import DirectoryPlaylist
from music_player import AudioPlayer
from widgets import PlayerControlsWidget, SidebarWidget
from delegates import LeftSideBarDelegate
from gui.models import TreeModel


class GUIPlayer(QMainWindow):
    DEFAULT_VOLUME = 30

    def __init__(self, parent=None):
        super(GUIPlayer, self).__init__(parent)

        self.duration = 0

        self.player = AudioPlayer(self.DEFAULT_VOLUME)

        self.player.getPlayer().positionChanged.connect(
            self._changeSongTimestamp)
        self.player.getPlayer().durationChanged.connect(self._setSongDuration)
        self.player.getPlaylist().currentIndexChanged.connect(
            self._playlistIndexChanged)
        #self.player.stateChanged.connect()

        self.__setPlaylistView()
        self.__setPlayerControls()
        self.__setLeftSidebar()
        self.initUi()

    def __setPlaylistView(self):
        self.playlistModel = PlaylistModel()
        self.playlistModel.setPlaylist(self.player.getPlaylist())

        self.playlistView = QTableView(self)
        self.playlistView.setModel(self.playlistModel)

        self.playlistView.setCurrentIndex(
            self.playlistModel.index(self.player.playlistCurrentIndex(), 0))
        self.playlistView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.playlistView.setShowGrid(False)
        # TODO TRY DIFFERENT OPTIONS
        self.playlistView.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self.playlistView.clicked.connect(self.singleClickedTest)
        self.playlistView.doubleClicked.connect(self.doubleClickedPlayPause)

        self.playlistView.setSortingEnabled(True)

    def __setPlayerControls(self):
        self.playerControls = PlayerControlsWidget(self.DEFAULT_VOLUME)
        self.playerControls.play.connect(self._play)
        self.playerControls.pause.connect(self._pause)
        self.playerControls.previousSong.connect(self._previous)
        self.playerControls.nextSong.connect(self._next)
        self.playerControls.volumeControl.connect(self._changeVolume)
        self.playerControls.songTimestamp.connect(self._setTimestamp)

    def __setLeftSidebar(self):
        treeModel = TreeModel()
        treeModel.addToModel('MAIN', ['Home', 'Settings'])
        treeModel.addToModel('LIBRARY',
                             ['Songs', 'Artists', 'Albums', 'Genres', 'Years'])
        treeModel.addToModel('PLAYLISTS', [])

        self.leftBarView = QTreeView(self)
        self.leftBarView.setModel(treeModel)
        self.leftBarView.setHeaderHidden(True)
        self.leftBarView.setRootIsDecorated(False)
        self.leftBarView.setItemsExpandable(False)
        self.leftBarView.setMouseTracking(True)
        self.leftBarView.expandAll()

        delegate = LeftSideBarDelegate()
        self.leftBarView.setItemDelegate(delegate)

    def initUi(self):
       #self.statusBar()

        # openFile = QAction('Open', self)
        # # openFile.setShortcut(QKeySequence(QtCore.Qt.CTRL + QtCore.sssQt.Key_O))
        # openFile.setStatusTip('Open new directory')
        # openFile.triggered.connect(self.choose_directory)

        # menubar = self.menuBar()
        # fileMenu = menubar.addMenu('&File')
        # fileMenu.addAction(openFile)

        upperBar = QFrame()
        upperBar.setStyleSheet("border: 1px solid black;")
        back = QLabel("back")
        forward = QLabel("forward")
        home = QLabel("home")
        search = QLabel(" [--------- search bar -----------]")
        upperBarLayout = QHBoxLayout()
        upperBarLayout.addWidget(back, 0, QtCore.Qt.AlignLeft)
        upperBarLayout.addWidget(forward, 0, QtCore.Qt.AlignLeft)
        upperBarLayout.addWidget(home, 0, QtCore.Qt.AlignLeft)
        upperBarLayout.addStretch(2)
        upperBarLayout.addWidget(search, 4, QtCore.Qt.AlignLeft)
        upperBar.setLayout(upperBarLayout)
        upperBar.setSizePolicy(QSizePolicy.Expanding,
                               QSizePolicy.Fixed)

        # leftSideBar = QFrame()
        # library = QLabel("library")
        # playlists = QLabel("playlists")
        # leftBarLayout = QVBoxLayout()
        # leftBarLayout.addWidget(library)
        # leftBarLayout.addWidget(playlists)
        # leftBarLayout.addStretch()
        # leftSideBar.setLayout(leftBarLayout)
        # leftSideBar.setSizePolicy(QSizePolicy.Maximum,
        #                           QSizePolicy.Expanding)


        rightSideBar = QFrame()

        stack = QStackedWidget()
        stack.addWidget(self.playlistView)
        # stack.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        centralAreaWidget = QWidget(self)
        centralAreaLayout = QHBoxLayout()
        centralAreaLayout.addWidget(self.leftBarView)
        centralAreaLayout.addWidget(stack, 2)
        
        #centralAreaLayout.setSpacing(0)
        centralAreaLayout.setContentsMargins(0,0,0,0)
        
        centralAreaWidget.setLayout(centralAreaLayout)

        self.centralWidget = QWidget(self)
        centralLayout = QVBoxLayout()
        centralLayout.addWidget(upperBar)
        centralLayout.addWidget(centralAreaWidget)
        centralLayout.addWidget(self.playerControls)

        centralLayout.setSpacing(0)
        centralLayout.setContentsMargins(0,0,0,0)
        # centralLayout.addWidget(self.currentTimestampLabel, 2, 1, 1, 1)
        # centralLayout.addWidget(self.songDurationSlider, 2, 2, 1, 1)
        # centralLayout.addWidget(self.durationLabel, 2, 3, 1, 1)

        self.centralWidget.setLayout(centralLayout)
        self.setCentralWidget(self.centralWidget)

        self.setGeometry(300, 300, 850, 800)
        self.setWindowTitle('Main Window')

    def test(self):
        print("HEY GUYZS    ")

    def _changeSongTimestamp(self, newTimestamp):
        self.playerControls.setSongTimestamp(newTimestamp)

    def _play(self):
        self.player.play()

    def _pause(self):
        self.player.pause()

    def _previous(self):
        self.player.previousEnhanced(5000)

    def _next(self):
        self.player.next()

    def _changeVolume(self, value):
        self.player.setVolume(value)

    def _setTimestamp(self, milliseconds):
        #if not self.songDurationSlider.isSliderDown():
        self.player.setPosition(milliseconds)

    def _setSongDuration(self, duration):
        self.duration = duration
        self.playerControls.setSongDuration(duration)

    def _playlistIndexChanged(self, newIndex):
        self.playlistView.setCurrentIndex(
            self.playlistModel.index(newIndex, 0))

    def choose_directory(self):
        fname = QFileDialog.getExistingDirectory(
            self, 'Open file', '/home',
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if not fname == '':
            directoryPlaylist = DirectoryPlaylist(fname)
            self.playlistModel.addToPlaylist(directoryPlaylist.songs)

    def singleClickedTest(self, index):
        # TODO stuff maybe?!
        #print(self.playlistView.selectionModel().currentIndex().row())
        pass

    def doubleClickedPlayPause(self, index):
        currentIndex = self.player.playlistCurrentIndex()
        newIndex = index.row()

        if currentIndex == newIndex:
            if self.player.getState() == QMediaPlayer.StoppedState:
                self._play()
            elif self.player.getState() == QMediaPlayer.PlayingState:
                self._play()
            elif self.player.getState() == QMediaPlayer.PausedState:
                self._play()
        else:
            self.player.setCurrentPlaylistIndex(newIndex)
            self._play()

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


def initPlayer():
    pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    player = GUIPlayer()
    player.show()

    sys.exit(app.exec_())
