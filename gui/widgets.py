from PyQt5 import QtCore, QtGui
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtWidgets import(QTableView, QHBoxLayout, QVBoxLayout, QWidget,
                            QApplication, QMainWindow, QAction, QFileDialog,
                            QTextEdit, QAbstractItemView, QHeaderView,
                            QToolButton, QStyle, QSlider, QToolBar,
                            QGridLayout, QPushButton, QLabel, QFrame,
                            QStackedWidget, QSizePolicy, QSpacerItem,
                            QTreeWidget, QTreeWidgetItem, QListWidget,
                            QListWidgetItem, QSplitter, QMenu, QLineEdit,
                            QDialog, QTextEdit)

from collections import OrderedDict
from uuid import UUID

from .models import PlaylistModel
from .dialogs import MetadataDialog

from .util import DEFAULT_VIEWS, DEFAULT_VIEWS_COUNT

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

    playbackModeChanged = QtCore.pyqtSignal(int)
    shuffleModeChanged = QtCore.pyqtSignal(int)

    DEFAULT_VOLUME = 40

    def __init__(self, volume, state=QMediaPlayer.StoppedState, parent=None):
        super(PlayerControlsWidget, self).__init__(parent)
        self.playerState = state
        self.volume = volume

        self.playButton = QToolButton(self)
        self.playButton.setIcon(
            QtGui.QIcon(":/playlist_controls_icons/play.png"))
        self.playButton.setAutoRaise(True)
        self.playButton.setFocusPolicy(QtCore.Qt.NoFocus)

        self.nextButton = QToolButton(self)
        self.nextButton.setIcon(
            QtGui.QIcon(":/playlist_controls_icons/next.png"))
        self.nextButton.setAutoRaise(True)
        self.nextButton.setFocusPolicy(QtCore.Qt.NoFocus)

        self.previousButton = QToolButton(self)
        self.previousButton.setIcon(
            QtGui.QIcon(":/playlist_controls_icons/previous.png"))
        self.previousButton.setAutoRaise(True)
        self.previousButton.setFocusPolicy(QtCore.Qt.NoFocus)

        self.volumeSlider = CustomSlider(QtCore.Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(self.volume)

        self.durationLabel = QLabel()
        self.durationLabel.setText("00:00")
        self.currentTimestampLabel = QLabel()
        self.currentTimestampLabel.setText("00:00")

        self.songTimestampSlider = CustomSlider(QtCore.Qt.Horizontal)
        self.songTimestampSlider.setTracking(False)

        self.playButton.clicked.connect(self._onPlayPause)
        self.nextButton.clicked.connect(self._onNext)
        self.previousButton.clicked.connect(self._onPrevious)

        self.volumeSlider.sliderMoved.connect(self._changeVolume)
        self.volumeSlider.valueChanged.connect(self._changeVolume)

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

    def _onLoopButtonToggle(self):
        if self.loopButtonState == QMediaPlaylist.Sequential:
            self.loopButtonState = QMediaPlaylist.Loop
            self.loopButton.setToolTip("Current: Playlist Loop")
        elif self.loopButtonState == QMediaPlaylist.Loop:
            self.loopButtonState = QMediaPlaylist.CurrentItemInLoop
            self.loopButton.setToolTip("Current: Current Song Loop")
        else:
            self.loopButtonState = QMediaPlaylist.Sequential
            self.loopButton.setToolTip("Current: Disabled")

        self.playbackModeChanged.emit(self.loopButtonState)

    def _onShuffleButtonToggle(self, toggled):
        if toggled:
            self.playbackModeChanged.emit(QMediaPlaylist.Random)
            self.shuffleButton.setToolTip("Current: Enabled")
        else:
            self.playbackModeChanged.emit(QMediaPlaylist.Sequential)
            self.shuffleButton.setToolTip("Current: Disabled")


    def setSongDuration(self, duration):
        self.songTimestampSlider.setMaximum(duration)
        self._updateDurationInfo(duration)

    def _updateDurationInfo(self, duration):
        self.setDurationLabel(duration)

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
    def _onPlayPause(self):
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

    @QtCore.pyqtSlot(int)
    def onStateChange(self, state):
        if state == QMediaPlayer.PlayingState:
            self.playerState = state
            self.playButton.setIcon(
                QtGui.QIcon(":/playlist_controls_icons/pause.png"))
        elif state == QMediaPlayer.StoppedState:
            self.playerState = state
            self.playButton.setIcon(
                QtGui.QIcon(":/playlist_controls_icons/play.png"))
        elif state == QMediaPlayer.PausedState:
            self.playerState = state
            self.playButton.setIcon(
                QtGui.QIcon(":/playlist_controls_icons/play.png"))

    def saveSettings(self):
        settings = QtCore.QSettings(
            QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope,
            QtCore.QCoreApplication.organizationName(),
            QtCore.QCoreApplication.applicationName())

        settings.setValue("player_controls/volume", self.volumeSlider.value())

    def restoreSettings(self):
        settings = QtCore.QSettings(
            QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope,
            QtCore.QCoreApplication.organizationName(),
            QtCore.QCoreApplication.applicationName())

        volume = settings.value("player_controls/volume", type=int)
        if not volume:
            volume = self.DEFAULT_VOLUME
        self.volumeSlider.setValue(volume)



class StackedWidget(QStackedWidget):

    treeViewDataChanged = QtCore.pyqtSignal(str, str, UUID)
    playlistAdded = QtCore.pyqtSignal(str)
    playlistRemoved = QtCore.pyqtSignal(UUID)

    widgetDoubleClicked = QtCore.pyqtSignal(UUID, int)

    def __init__(self, parent=None):
        super(StackedWidget, self).__init__(parent)

        self.playlistMappings = {}
        self.__setContextMenuActions()

    def createCustomPlaylistView(self, uuid):
        playlistModel = PlaylistModel(uuid)

        playlistView = QTableView(self)
        playlistView.setModel(playlistModel)
        playlistView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        playlistView.setSortingEnabled(True)
        playlistView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        playlistView.setSelectionBehavior(QAbstractItemView.SelectRows)
        playlistView.setShowGrid(False)
        playlistView.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        playlistView.doubleClicked.connect(self._doubleCLickedWidget)
        playlistView.customContextMenuRequested.connect(
            self.customMenuRequested)

        self.playlistMappings[uuid] = playlistView
        self.insertWidget(DEFAULT_VIEWS_COUNT, playlistView)

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
        playlistView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        playlistView.setSortingEnabled(True)
        playlistView.setSelectionBehavior(QAbstractItemView.SelectRows)
        playlistView.setShowGrid(False)
        playlistView.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        playlistView.doubleClicked.connect(self._doubleCLickedWidget)
        playlistView.customContextMenuRequested.connect(
            self.customMenuRequested)

        self.playlistMappings[uuid] = playlistView
        self.insertWidget(0, playlistView)
        self.setCurrentWidget(self.playlistMappings[uuid])

    def __setContextMenuActions(self):
        self.editAct = QAction("Edit", self)
        self.editAct.setStatusTip("Edit this file's metadata")
        self.editAct.triggered.connect(self.editData)

    @QtCore.pyqtSlot(UUID, list)
    def updatePlaylist(self, uuid, mediaFiles):
        widget = self.playlistMappings[uuid]
        model = widget.model()
        model.insertMedia(model.rowCount(), mediaFiles)
        model.reset()
        model.insertMedia(model.rowCount(), mediaFiles)

    @QtCore.pyqtSlot(UUID, list)
    def appendToPlaylist(self, uuid, mediaFiles):
        widget = self.playlistMappings[uuid]
        model = widget.model()
        model.insertMedia(model.rowCount(), mediaFiles)

    @QtCore.pyqtSlot(UUID, int)
    def setWidgetIndex(self, uuid, row):
        widget = self.playlistMappings[uuid]
        index = widget.model().index(row, 0)
        widget.setCurrentIndex(index)

    @QtCore.pyqtSlot(QtCore.QPoint)
    def customMenuRequested(self, pos):
        menu = QMenu(self)
        row = self.currentWidget().indexAt(pos).row()
        song = self.currentWidget().model().getDataAtRow(row)
        self.editAct.setData(song)
        menu.addAction(self.editAct)
        menu.popup(self.mapToGlobal(pos))

    def editData(self):
        song = self.editAct.data()
        available_metadata = song.get_values(MetadataDialog.METADATA_INFO)
        dialog = MetadataDialog(available_metadata)
        dialogCode = dialog.exec_()
        if dialogCode == QDialog.Accepted:
            result = dialog.getResultDict()
            for k, v in result.items():
                song.set_tag(k, v)
            song.save()
        if dialogCode == QDialog.Rejected:
            return

