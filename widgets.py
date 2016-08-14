from PyQt5 import QtCore, QtGui
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtWidgets import(QTableView, QHBoxLayout, QVBoxLayout, QWidget,
                            QApplication, QMainWindow, QAction, QFileDialog,
                            QTextEdit, QAbstractItemView, QHeaderView,
                            QToolButton, QStyle, QSlider, QToolBar,
                            QGridLayout, QPushButton, QLabel, QFrame,
                            QStackedWidget, QSizePolicy, QSpacerItem,
                            QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem)


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
        self.playerControls.setDurationLabel(duration)

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


# class SidebarWidget(QWidget):

#     def __init__(self):
#         QWidget.__init__(self)

#         self.treeWidget = QTreeWidget(self)

#         self.treeWidget.setHeaderHidden(True)
#         self.addItems(self.treeWidget.invisibleRootItem())
#         self.treeWidget.setRootIsDecorated(False)
#         self.treeWidget.setItemsExpandable(False)
#         self.initUi()
#         # delegate = TreeWidgetDelegate(self)
#         # #self.treeWidget.setItemDelegate(delegate)
#         # self.treeWidget.setStyleSheet("QTreeWidget::item { border-bottom: 1px solid black;}")

#         p = QtGui.QPalette(self.treeWidget.palette())
#         p.setColor(QtGui.QPalette.Base, QtCore.Qt.white)
#         self.treeWidget.setPalette(p)

#     def initUi(self):
#         layout = QVBoxLayout()
#         layout.addWidget(self.treeWidget)
#         self.setLayout(layout)

#     def setItemDelegate(self, delegate):
#         self.treeWidget.setItemDelegate(delegate)

#     def addItems(self, parent):
#         column = 0
#         library = self.addParent(parent, column, 'Library')
#         playlists = self.addParent(parent, column, 'Playlists')

#         self.addChild(library, column, 'Songs')
#         self.addChild(library, column, 'Albums')
#         self.addChild(library, column, 'Artists')
#         self.addChild(library, column, 'Genres')

#         #playlists.setSizeHint(0, QtCore.QSize(50, 50))

#         self.addChild(playlists, column, 'playlist1')
#         self.addChild(playlists, column, 'playlist2')

#     def addParent(self, parent, column, title):
#         item = QTreeWidgetItem(parent, [title])
#         font = QtGui.QFont("Helvetica [Cronyx]", 15, QtGui.QFont.Bold)
#         #b = QtGui.QBrush(QtCore.Qt.blue)
#         b = QtGui.QBrush(QtGui.QColor('#D3D3D3'))
#         item.setForeground( 0 , b )
#         item.setFont( 0,  font )
#         #item.setData(column, QtCore.Qt.UserRole, data)
#         item.setExpanded(True)
#         item.setFlags(QtCore.Qt.ItemIsEnabled)
#         return item

#     def addChild(self, parent, column, title):
#         item = QTreeWidgetItem(parent, [title])
#         return item



class SidebarWidget(QTreeWidget):

    def __init__(self):
        QTreeWidget.__init__(self)
        self.setHeaderHidden(True)
        self.setColumnCount(1)
        self.addItems(self.invisibleRootItem())
        self.setRootIsDecorated(False)
        self.setItemsExpandable(False)
        #self.setStyleSheet("QTreeWidget::item { border-top: 1px solid black;}")

        p = QtGui.QPalette(self.palette())
        p.setColor(QtGui.QPalette.Base, QtCore.Qt.white)
        self.setPalette(p)

    def addItems(self, parent):
        column = 0
        library = self.addParent(parent, column, 'Library')
        playlists = self.addParent(parent, column, 'Playlists')

        self.addChild(library, column, 'Songs')
        self.addChild(library, column, 'Albums')
        self.addChild(library, column, 'Artists')
        self.addChild(library, column, 'Genres')

        #playlists.setSizeHint(0, QtCore.QSize(50, 50))

        self.addChild(playlists, column, 'playlist1')
        self.addChild(playlists, column, 'playlist2')

    def addParent(self, parent, column, title):
        item = QTreeWidgetItem(parent, [title])
        font = QtGui.QFont("Helvetica [Cronyx]", 15, QtGui.QFont.Bold)
        #b = QtGui.QBrush(QtCore.Qt.blue)
        # b = QtGui.QBrush(QtGui.QColor('#D3D3D3'))
        # item.setForeground( 0 , b )
        # item.setFont( 0,  font )
        #item.setData(column, QtCore.Qt.UserRole, data)
        item.setExpanded(True)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        return item

    def addChild(self, parent, column, title):
        item = QTreeWidgetItem(parent, [title])
        font = QtGui.QFont("Helvetica [Cronyx]", 13)
        item.setFont(0,  font )
        item.setIcon(0, QtGui.QIcon("./left_sidebar_icons/music.png"))
        return item

# add something like setSizePolicy(QSizePolicy.Maximum,
        #                           QSizePolicy.Expanding)



# class SidebarWidget(QWidget):
#     def __init__(self):
#         QWidget.__init__(self)
#         self.musicLabel = QLabel("MUSIC")
#         self.musicLabel.setAlignment(QtCore.Qt.AlignCenter)
#         self.playlistsLabel = QLabel("PLAYLISTS")
#         self.list1 = QListWidget()
#         self.list2 = QListWidget()

#         self.addItem(self.list1, "songs")
#         self.addItem(self.list1, "albums")
#         self.addItem(self.list1, "artists")

#         self.addItem(self.list2, "p1")
#         self.addItem(self.list2, "p2")

#         self.initUI()

#     def initUI(self):
#         layout = QVBoxLayout()
#         layout.addWidget(self.musicLabel)
#         layout.addWidget(self.list1)

#         layout.addWidget(self.playlistsLabel)
#         layout.addWidget(self.list2)

#         layout.setSpacing(0)
#         layout.setContentsMargins(0,0,0,0)

#         self.setLayout(layout)

#     def addItem(self, list_, name):
#         item = QListWidgetItem(name, list_)
