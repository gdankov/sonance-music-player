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
from .dialogs import SettingsDialog
from collections import OrderedDict
from .util import DEFAULT_VIEWS, DEFAULT_VIEWS_COUNT, LEFT_SIDEBAR_MENU_ITEMS


class MainWindow(QMainWindow):

    _tree_items = LEFT_SIDEBAR_MENU_ITEMS

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.audioPlayer = AudioPlayer()

        self.audioPlayer.songPositionChanged.connect(self._changeSongTimestamp)
        self.audioPlayer.songDurationChanged.connect(self._setSongDuration)

        self._setActions()
        self._setMenus()

        self._setPlayerControls()
        self._setCentralArea()
        self.renderUI()

        self.audioPlayer.stateChanged.connect(
            self.audioPlayerControls.onStateChange)
        self.audioPlayer.currentSongChanged.connect(
            self.leftSidebar.changeCoverArtBoxInformation)
        self.audioPlayer.currentSelectionChanged.connect(
            self.stackWidget.setWidgetIndex)

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

        self.audioPlayer.updatedLibraryPlaylist.connect(
            self.stackWidget.updatePlaylist)

        self.restoreSettings()  # SHOUlD IT BE LAST?

    def _setMenus(self):
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('&Tools')
        self.fileMenu.addAction(self.openPreferencesAction)

    def _setActions(self):
        self.openPreferencesAction = QAction('Preferences', self)
        self.openPreferencesAction.triggered.connect(self._openPreferences)

    def _openPreferences(self):
        settingsDialog = SettingsDialog()
        dialogCode = settingsDialog.exec_()
        if dialogCode == QDialog.Accepted:
            settingsDialog.saveSettings()
            self.audioPlayer.updateLibraryPlaylist(
                settingsDialog.currentDirectories)
        if dialogCode == QDialog.Rejected:
            return

    def _setPlayerControls(self):
        self.audioPlayerControls = PlayerControlsWidget(30)
        self.audioPlayerControls.play.connect(self.audioPlayer.play)
        self.audioPlayerControls.pause.connect(self.audioPlayer.pause)
        self.audioPlayerControls.previousSong.connect(
            lambda: self.audioPlayer.previousEnhanced(5000))
        self.audioPlayerControls.nextSong.connect(self.audioPlayer.next)
        self.audioPlayerControls.volumeControl.connect(
            self.audioPlayer.setVolume)
        self.audioPlayerControls.songTimestamp.connect(
            self.audioPlayer.setPosition)
        self.audioPlayerControls.setSizePolicy(QSizePolicy.Preferred,
                                               QSizePolicy.Fixed)

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
        self.leftSidebar.treeViewDoubleClicked.connect(self._onTreeDoubleClick)

    def _onTreeSelectionChange(self, index, index2):
        if not index.parent().isValid():
            return None

        if index.parent().isValid() and index.parent().data() == 'LIBRARY':
            row = EFAULT_VIEWS.index(index.data())
            self.stackWidget.setCurrentIndex(row)
        if index.parent().isValid() and index.parent().data() == 'PLAYLISTS':
            row = index.row() + DEFAULT_VIEWS_COUNT
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
        self.splitterCentralWidget = QSplitter(
            orientation=QtCore.Qt.Horizontal)

        self.splitterCentralWidget.setContentsMargins(0, 0, 0, 0)
        self.splitterCentralWidget.setHandleWidth(2)
        self.splitterCentralWidget.addWidget(self.leftSidebar)
        self.splitterCentralWidget.addWidget(self.stackWidget)
        self.splitterCentralWidget.setChildrenCollapsible(False)

        self.centralWidget = QWidget()
        centralLayout = QVBoxLayout()
        centralLayout.setContentsMargins(0, 0, 0, 0)
        centralLayout.setSpacing(0)
        centralLayout.addWidget(self.splitterCentralWidget)
        centralLayout.addWidget(self.audioPlayerControls)

        self.centralWidget.setLayout(centralLayout)
        self.setCentralWidget(self.centralWidget)

        self.setWindowTitle('Sonance')

    def _changeSongTimestamp(self, newTimestamp):
        self.audioPlayerControls.setSongTimestamp(newTimestamp)

    def _setSongDuration(self, duration):
        self.audioPlayerControls.setSongDuration(duration)

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
        try:
            fileDialog.setDirectory(QtCore.QStandardPaths.standardLocations(
                                    QtCore.QStandardPaths.MusicLocation)[0])
        except IndexError:
            fileDialog.setDirectory(QtCore.QDir.homePath())

        if fileDialog.exec_() == QDialog.Accepted:
            return fileDialog.selectedFiles()

    def closeEvent(self, event):
        if self.__promptExit():
            self.saveWindowState()
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

    def saveWindowState(self):
        settings = QtCore.QSettings(
            QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope,
            QtCore.QCoreApplication.organizationName(),
            QtCore.QCoreApplication.applicationName())

        settings.setValue("main_window/position", self.pos())
        settings.setValue("main_window/size", self.size())
        settings.setValue("main_window/splitterSizes",
                          self.splitterCentralWidget.saveState())
        settings.setValue("main_window/state", self.saveState())

        self.audioPlayerControls.saveSettings()

    def restoreSettings(self):
        settings = QtCore.QSettings(
            QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope,
            QtCore.QCoreApplication.organizationName(),
            QtCore.QCoreApplication.applicationName())

        state = settings.value('main_window/state')
        if state:
            self.restoreState(state)

        pos = settings.value("main_window/position", QtCore.QPoint(150, 150))
        size = settings.value("main_window/size", QtCore.QSize(1200, 300))
        self.resize(size)
        self.move(pos)

        spliterSizes = settings.value("main_window/splitterSizes")
        if spliterSizes:
            self.splitterCentralWidget.restoreState(spliterSizes)

        self.audioPlayerControls.restoreSettings()
