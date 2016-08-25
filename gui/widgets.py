from PyQt5 import QtCore, QtGui
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtWidgets import(QTableView, QHBoxLayout, QVBoxLayout, QWidget,
                            QApplication, QMainWindow, QAction, QFileDialog,
                            QTextEdit, QAbstractItemView, QHeaderView,
                            QToolButton, QStyle, QSlider, QToolBar,
                            QGridLayout, QPushButton, QLabel, QFrame,
                            QStackedWidget, QSizePolicy, QSpacerItem,
                            QTreeWidget, QTreeWidgetItem, QListWidget,
                            QListWidgetItem, QSplitter)

from collections import OrderedDict
from uuid import UUID

from .left_sidebar import LeftSideBar
from .models import PlaylistModel
from audio.playlist_models import DirectoryPlaylist


class CustomSlider(QSlider):
    def mousePressEvent(self, event):
        self.setValue(QStyle.sliderValueFromPosition(self.minimum(),
                      self.maximum(), event.x(), self.width()))

    def mouseMoveEvent(self, event):
        self.setValue(QStyle.sliderValueFromPosition(self.minimum(),
                      self.maximum(), event.x(), self.width()))


class PlayerControlsWidget(QWidget):
    play = QtCore.pyqtSignal(name='play')
    pause = QtCore.pyqtSignal(name='pause')
    stop = QtCore.pyqtSignal(name='stop')
    nextSong = QtCore.pyqtSignal(name='next song')
    previousSong = QtCore.pyqtSignal(name='previous song')
    volumeControl = QtCore.pyqtSignal(int, name='volume control')
    songTimestamp = QtCore.pyqtSignal(int, name='song current timestamp')

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

        self.volumeSlider = CustomSlider(QtCore.Qt.Horizontal, self)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(self.defaultVolume)

        self.durationLabel = QLabel()
        self.durationLabel.setText("00:00")
        self.currentTimestampLabel = QLabel()
        self.currentTimestampLabel.setText("00:00")

        self.songTimestampSlider = CustomSlider(QtCore.Qt.Horizontal)
        #self.songTimestampSlider.setRange(0, self.player.getDuration())
        self.songTimestampSlider.setTracking(False)




        self.playButton.clicked.connect(self._onPlay)
        self.nextButton.clicked.connect(self._onNext)
        self.previousButton.clicked.connect(self._onPrevious)

        self.volumeSlider.sliderMoved.connect(self._changeVolume)
        self.volumeSlider.valueChanged.connect(self._changeVolume)

        # self.songTimestampSlider.sliderMoved.connect(self.test)
        self.songTimestampSlider.valueChanged.connect(self._changeTimeStamp)

        self.initGUI()

    def initGUI(self):
        hLayout = QHBoxLayout()
        hLayout.addWidget(self.previousButton)
        hLayout.addWidget(self.playButton)
        hLayout.addWidget(self.nextButton)
        hLayout.addWidget(self.volumeSlider)
        hLayout.addWidget(self.currentTimestampLabel)
        hLayout.addWidget(self.songTimestampSlider, 1)
        hLayout.addWidget(self.durationLabel)
        self.setLayout(hLayout)

    def setSongDuration(self, duration):
        self.songTimestampSlider.setMaximum(duration)
        self._updateDurationInfo(duration)

    def _updateDurationInfo(self, duration):
        self.setDurationLabel(duration)

    # consider exception
    def setDurationLabel(self, duration):
        if not duration:
            return

        newDuration = PlayerControlsWidget.toTimestampStr(duration)
        self.durationLabel.setText(newDuration)

    def setSongTimestamp(self, newTimestamp):
        if not self.songTimestampSlider.isSliderDown():
            previousValue = self.songTimestampSlider.blockSignals(True)
            self.songTimestampSlider.setValue(newTimestamp)
            self.songTimestampSlider.blockSignals(previousValue)

        self._updateCurrentTimestamp(newTimestamp)

    def _updateCurrentTimestamp(self, newTimestamp):
        if newTimestamp:
            newTimestampStr = PlayerControlsWidget.toTimestampStr(newTimestamp)
        else:
            newTimestampStr = "00:00"

        self.currentTimestampLabel.setText(newTimestampStr)

    @staticmethod
    def toTimestampStr(milliseconds):
        seconds = (int)(milliseconds / 1000) % 60
        minutes = (int)((milliseconds / (1000 * 60)) % 60)
        hours = (int)((milliseconds / (1000 * 60 * 60)) % 24)
        totalTime = QtCore.QTime(hours, minutes, seconds)
        timeFormat = 'hh:mm:ss' if milliseconds > 1000 * 3600 else 'mm:ss'
        timestamp = totalTime.toString(timeFormat)
        return timestamp

    @QtCore.pyqtSlot()
    def _onPlay(self):
        if self.playerState in (QMediaPlayer.StoppedState,
                                QMediaPlayer.PausedState):
            self.playerState = QMediaPlayer.PlayingState
            self.play.emit()
        elif self.playerState == QMediaPlayer.PlayingState:
            self.playerState = QMediaPlayer.PausedState
            self.pause.emit()

    @QtCore.pyqtSlot()
    def _onNext(self):
        self.nextSong.emit()

    @QtCore.pyqtSlot()
    def _onPrevious(self):
        self.previousSong.emit()

    @QtCore.pyqtSlot(int)
    def _changeVolume(self, value):
        self.volumeControl.emit(value)

    @QtCore.pyqtSlot(int)
    def _changeTimeStamp(self, value):
        self.songTimestamp.emit(value)


LEFT_SIDEBAR_MENU_ITEMS = OrderedDict(
    [  # ('MAIN', ['Home', 'Settings']),
    ('LIBRARY', ['Songs', 'Artists', 'Albums', 'Genres']),
    ('PLAYLISTS', [])])

DEFAULT_VIEWS = LEFT_SIDEBAR_MENU_ITEMS['LIBRARY']


class StackedWidget(QStackedWidget):

    DEFAULT_VIEWS_COUNT = len(DEFAULT_VIEWS)

    treeViewDataChanged = QtCore.pyqtSignal(str, str, UUID)
    playlistAdded = QtCore.pyqtSignal(str)
    playlistRemoved = QtCore.pyqtSignal(UUID)

    widgetDoubleClicked = QtCore.pyqtSignal(UUID, int)

    def __init__(self, parent=None):
        super(StackedWidget, self).__init__(parent)

        self.playlistMappings = {}

    # def _onDataChange(self, newValue, oldValue, index):
    #     playlistUuid = self._getPlaylistUuid(index)
    #     if playlistUuid:
    #         self.treeViewDataChanged.emit(newValue, oldValue, playlistUuid)

    # def _getPlaylistUuid(self, index):
    #     if index.parent().isValid() and index.parent().data() == 'PLAYLISTS':
    #         row = index.row() + self.DEFAULT_VIEWS_COUNT
    #         playlistView = self.widget(row)
    #         uuid = playlistView.model().getPlaylist().getUuid()
    #         return uuid

    def createCustomPlaylistView(self, uuid):
        playlistModel = PlaylistModel(uuid)

        playlistView = QTableView(self)
        playlistView.setModel(playlistModel)

        # playlistView.setCurrentIndex(p
        #     playlistModel.index(self.player.playlistCurrentIndex(), 0))
        playlistView.setSelectionBehavior(QAbstractItemView.SelectRows)
        playlistView.setShowGrid(False)
        # TODO TRY DIFFERENT OPTIONS
        playlistView.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        # playlistView.clicked.connect(self.singleClickedTest)
        # playlistView.doubleClicked.connect(self.doubleClickedPlayPause)
        playlistView.setSortingEnabled(True)

        playlistView.doubleClicked.connect(self._doubleCLickedWidget)

        self.playlistMappings[uuid] = playlistView
        self.insertWidget(1, playlistView)       # FUCK THIS SHIT
        #self.setCurrentIndex(1)                  # IF IT BREAKS ITS PROBABLY FROM HERE!!!!!!!!!!!! fix it
        #self.setCurrentWidget(self.playlistMappings[uuid])

    def _doubleCLickedWidget(self, index):
        uuid = index.model().getUuid()
        row = index.row()
        self.widgetDoubleClicked.emit(uuid, row)

    def removePlaylistView(self, uuid):
        if uuid in self.playlistMappings:
            widget = self.playlistMappings[uuid]
            self.removeWidget(widget)
            self.setCurrentIndex(0)
            del self.playlistMappings[uuid]

    def createLibraryPlaylisView(self, uuid):
        playlistModel = PlaylistModel(uuid)
        playlistView = QTableView(self)
        playlistView.setModel(playlistModel)
        # playlistView.setCurrentIndex(
        #     playlistModel.index(self.player.playlistCurrentIndex(), 0))
        playlistView.setSelectionBehavior(QAbstractItemView.SelectRows)
        playlistView.setShowGrid(False)
        # TODO TRY DIFFERENT OPTIONS
        playlistView.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        # playlistView.clicked.connect(self.singleClickedTest)
        # playlistView.doubleClicked.connect(self.doubleClickedPlayPause)

        playlistView.setSortingEnabled(True)
        # playlistView.doubleClicked.connect(self._doubleCLicked)
        
        playlistView.doubleClicked.connect(self._doubleCLickedWidget)
        
        # name = 'Songs'
        # self.defaultViewsMappings[name] = playlistView

        self.playlistMappings[uuid] = playlistView
        self.insertWidget(0, playlistView)
        #self.setCurrentIndex(0)
        self.setCurrentWidget(self.playlistMappings[uuid])

    @QtCore.pyqtSlot(UUID, list)
    def appendToPlaylist(self, uuid, mediaFiles):
        widget = self.playlistMappings[uuid]
        model = widget.model()
        model.insertMedia(model.rowCount(), mediaFiles)
