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
                            QSplitter, QTreeView, QDialog, QMessageBox)

from audio.playlist_models import DirectoryPlaylist
from audio.music_player import AudioPlayer
from .widgets import PlayerControlsWidget, StackedWidget
from .delegates import LeftSideBarDelegate
from .models import TreeModel, PlaylistModel
from .left_sidebar import LeftSideBar
from collections import OrderedDict


LEFT_SIDEBAR_MENU_ITEMS = OrderedDict(
    [  # ('MAIN', ['Home', 'Settings']),
    ('LIBRARY', ['Songs', 'Artists', 'Albums', 'Genres']),
    ('PLAYLISTS', [])])



class MainWindow(QMainWindow):

    _tree_items = LEFT_SIDEBAR_MENU_ITEMS

    DEFAULT_VIEWS = LEFT_SIDEBAR_MENU_ITEMS['LIBRARY']

    DEFAULT_VIEWS_COUNT = len(DEFAULT_VIEWS)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.audioPlayer = AudioPlayer()

        self.audioPlayer.songPositionChanged.connect(self._changeSongTimestamp)
        self.audioPlayer.songDurationChanged.connect(self._setSongDuration)
        #self.audioPlayer.stateChanged.connect()
        self.audioPlayer.playlistChanged.connect(self._playlistIndexChanged)


        self._setMenus()
        self._setStatusBar()
        self._setActions()

        self._setPlayerControls()
        self._setCentralArea()
        self.renderUI()
        
        self.audioPlayer.currentSongChanged.connect(
            self.leftSidebar.changeCoverArtBoxInformation)

        # self.audioPlayer.customPlaylistCreated.connect(
        #     self.stackWidget.createCustomPlaylistView)
        self.audioPlayer.customPlaylistCreated.connect(
            self.leftSidebar.addPlaylistEntry)

        self.audioPlayer.libraryPlaylistCreated.connect(
            self.stackWidget.createLibraryPlaylisView)
        self.audioPlayer.libraryPlaylistCreated.connect(
            self.leftSidebar.createDefaults)

        self.audioPlayer.playlistRemoved.connect(
            self.stackWidget.removePlaylistView)
        self.audioPlayer.playlistRemoved.connect(
            self.leftSidebar.removePlaylistEntry)

        self.audioPlayer.createLibraryPlaylist()
        self.audioPlayer.addedToLibraryPlaylist.connect(
            self.stackWidget.appendToPlaylist)
        self.audioPlayer.addedToCustomPlaylist.connect(
            self.stackWidget.appendToPlaylist)


        self.restoreState()  # SHOUlD IT BE LAST?

    def _setMenus(self):
        pass

    def _setStatusBar(self):
        self.statusBar().showMessage("status_bar")

    def _setActions(self):
        openFile = QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new directory')
        openFile.triggered.connect(self.choose_directory)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)

    def _setPlayerControls(self):
        self.audioPlayerControls = PlayerControlsWidget(30)
        self.audioPlayerControls.play.connect(self._play)
        self.audioPlayerControls.pause.connect(self._pause)
        self.audioPlayerControls.previousSong.connect(self._previous)
        self.audioPlayerControls.nextSong.connect(self._next)
        self.audioPlayerControls.volumeControl.connect(self._changeVolume)
        self.audioPlayerControls.songTimestamp.connect(self._setTimestamp)
        self.audioPlayerControls.setSizePolicy(QSizePolicy.Preferred,
                                          QSizePolicy.Fixed)

    def _play(self):
        self.audioPlayer.play()

    def _pause(self):
        self.audioPlayer.pause()

    def _previous(self):
        self.audioPlayer.previousEnhanced(5000)

    def _next(self):
        self.audioPlayer.next()

    def _changeVolume(self, value):
        self.audioPlayer.setVolume(value)

    def _setTimestamp(self, milliseconds):
        # if not self.songDurationSlider.isSliderDown():
        self.audioPlayer.setPosition(milliseconds)

    def _setCentralArea(self):
        self.stackWidget = StackedWidget()
        self.stackWidget.widgetDoubleClicked.connect(
            self.audioPlayer.setPlaylist)
        self._setLeftSideBar()



    def _setLeftSideBar(self):
        self.leftSidebar = LeftSideBar(self._tree_items)
        self.leftSidebar.treeViewSelectionChanged.connect(
            self._onTreeSelectionChange)

        self.leftSidebar.addPlaylistRequested.connect(
            self.audioPlayer.createCustomPlaylist)

        self.leftSidebar.playlistRenamed.connect(
            self.audioPlayer.renamePlaylist)

        self.leftSidebar.addToPlaylistRequested.connect(self._addToPlaylist)

        self.leftSidebar.playlistAdded.connect(
            self.stackWidget.createCustomPlaylistView)

        self.leftSidebar.removePlaylistRequested.connect(self.audioPlayer.removePlaylist)
        # TODO connect(and make) cover art box signals
        self.leftSidebar.treeViewDoubleClicked.connect(self._onTreeDoubleClick)

    def _onTreeSelectionChange(self, index, index2):
        if not index.parent().isValid():
            return None

        if index.parent().isValid() and index.parent().data() == 'LIBRARY':
            row = self.DEFAULT_VIEWS.index(index.data())
            self.stackWidget.setCurrentIndex(row)
        if index.parent().isValid() and index.parent().data() == 'PLAYLISTS':
            row = index.row() + 1                                   # FIX THIS TOOOOOOOOOOOOOOOOOOOooo
            self.stackWidget.setCurrentIndex(row)

    def _onTreeDoubleClick(self, index):
        if (index.parent().isValid() and
                index.parent().data() == 'LIBRARY' and
                index.data() == 'Songs' and
                self.audioPlayer.hasLibraryPlaylist()):
                uuid = index.internalPointer().valueData()
                self.audioPlayer.setPlaylist(uuid, 0)
        elif index.parent().isValid() and index.parent().data() == 'PLAYLISTS':
            uuid = index.internalPointer().valueData()
            self.audioPlayer.setPlaylist(uuid, 0)

    def _onAddedPlaylistEntry(self, name):
        self.audioPlayer.createCustomPlaylist(name)

    def _onRemovedPlaylist(self, uuid):
        self.audioPlayer.removePlaylist(uuid)

    def _addToPlaylist(self, uuid):
        files = self.choose_files()
        if files:
            self.audioPlayer.addSongsToCustomPlaylist(uuid, files)

    def renderUI(self):
        splitterCentralWidget = QSplitter(orientation=QtCore.Qt.Horizontal)

        splitterCentralWidget.setContentsMargins(0, 0, 0, 0)
        splitterCentralWidget.setHandleWidth(2)
        splitterCentralWidget.addWidget(self.leftSidebar)
        splitterCentralWidget.addWidget(self.stackWidget)
        splitterCentralWidget.setChildrenCollapsible(False)  # make it an option

        self.centralWidget = QWidget()
        centralLayout = QVBoxLayout()
        centralLayout.setContentsMargins(0, 0, 0, 0)
        centralLayout.setSpacing(0)
        centralLayout.addWidget(splitterCentralWidget)
        centralLayout.addWidget(self.audioPlayerControls)

        self.centralWidget.setLayout(centralLayout)
        self.setCentralWidget(self.centralWidget)

        self.setWindowTitle('Sonance')

    def _changeSongTimestamp(self, newTimestamp):
        self.audioPlayerControls.setSongTimestamp(newTimestamp)

    def _setSongDuration(self, duration):
        self.audioPlayerControls.setSongDuration(duration)

    def _playlistIndexChanged(self, newIndex):
        # self.playlistView.setCurrentIndex(
        #     self.playlistModel.index(newIndex, 0))
        pass

    def choose_directory(self):
        fileDialog = QFileDialog(self)
        fileDialog.setAcceptMode(QFileDialog.AcceptOpen)
        fileDialog.setFileMode(QFileDialog.Directory)
        fileDialog.setViewMode(QFileDialog.Detail)
        fileDialog.setWindowTitle("Choose Media Directory")
        try:
            fileDialog.setDirectory(QtCore.QStandardPaths.standardLocations(
                                    QtCore.QStandardPaths.MusicLocation)[0])
        except IndexError:
            fileDialog.setDirectory(QtCore.QDir.homePath())

        if fileDialog.exec_() == QDialog.Accepted:
            self.audioPlayer.addToLibraryPlaylist(fileDialog.selectedFiles())

    def choose_files(self):
        fileDialog = QFileDialog(self)
        fileDialog.setAcceptMode(QFileDialog.AcceptOpen)
        fileDialog.setFileMode(QFileDialog.ExistingFiles)
        fileDialog.setViewMode(QFileDialog.Detail)
        fileDialog.setWindowTitle("Choose media files")
        #supportedMimeTypes = player.supportedMimeTypes()
        # if not supportedMimeTypes.isEmpty():
        #     supportedMimeTypes.append("audio/x-m3u")
        #     fileDialog.setMimeTypeFilters(supportedMimeTypes)
        try:
            fileDialog.setDirectory(QtCore.QStandardPaths.standardLocations(
                                    QtCore.QStandardPaths.MusicLocation)[0])
        except IndexError:
            fileDialog.setDirectory(QtCore.QDir.homePath())

        if fileDialog.exec_() == QDialog.Accepted:
            return fileDialog.selectedFiles()


    def singleClickedTest(self, index):
        # TODO stuff maybe?!
        #print(self.playlistView.selectionModel().currentIndex().row())
        pass

    def doubleClickedPlayPause(self, index):
        currentIndex = self.audioPlayer.playlistCurrentIndex()
        newIndex = index.row()

        if currentIndex == newIndex:
            if self.audioPlayer.getState() == QMediaPlayer.StoppedState:
                self._play()
            elif self.audioPlayer.getState() == QMediaPlayer.PlayingState:
                self._play()
            elif self.audioPlayer.getState() == QMediaPlayer.PausedState:
                self._play()
        else:
            self.audioPlayer.setCurrentPlaylistIndex(newIndex)
            self._play()

    # Not working
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif e.key() == QtCore.Qt.Key_Space:
            if self.audioPlayer.state() == QMediaPlayer.PlayingState:
                self.audioPlayer.pause()
            elif self.audioPlayer.state() == QMediaPlayer.PausedState:
                self.audioPlayer.play()
        elif e.key() == QtCore.Qt.Key_Enter:
            newIndex = self.playlist.currentIndex()
            self.playlist.setCurrentIndex(newIndex)
            self.audioPlayer.play()

    def closeEvent(self, event):
        if self.__promptExit():
            self.saveState()
            event.accept()
        else:
            event.ignore()

    def __promptExit(self):
        ret = QMessageBox.warning(self, "Exit?",
                                  "Are you sure you want to exit?",
                                  QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            return True
        elif ret == QMessageBox.No:
            return False

    def saveState(self):
        settings = QtCore.QSettings(QtCore.QCoreApplication.organizationName(),
                                    QtCore.QCoreApplication.applicationName())

        # settings.setValue("main_window/position", self.pos())   # and maybe change to ini for all platforms and setFallbacksEnabled(false)
        # settings.setValue("main_window/size", self.size())
        # settings.setValue("main_window/splitterSizes",
        #                   self.centralArea.saveState())
        self.audioPlayer.saveState()


    def restoreState(self):
        settings = QtCore.QSettings(QtCore.QCoreApplication.organizationName(),
                                    QtCore.QCoreApplication.applicationName())

        # pos = settings.value("main_window/position", QtCore.QPoint(200, 200))
        # size = settings.value("main_window/size", QtCore.QSize(400, 400))
        # self.resize(size)   # not working as expected this part
        # self.move(pos)      # and this probably

        # spliterSizes = settings.value("main_window/splitterSizes")
        # self.centralArea.restoreState(spliterSizes)

        self.audioPlayer.restoreState()

    def contextMenuEvent(self, event):
        print("context menu event")
        event.ignore()

    def about(self):
        # QMessageBox::about(this, tr("About Application"),
        #         tr("The <b>Application</b> example demonstrates how to "
        #            "write modern GUI applications using Qt, with a menu bar, "
        #            "toolbars, and a status bar."));
        pass


# if __name__ == '__main__':
#     app = QApplication(sys.argv)

#     player = MainWindow()
#     player.show()

#     sys.exit(app.exec_())
    
