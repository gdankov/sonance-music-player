from collections import OrderedDict

from PyQt5.QtCore import pyqtSignal, Qt, QSize, QModelIndex, QItemSelectionModel
from PyQt5.QtWidgets import QWidget, QTreeView, QVBoxLayout, QAbstractItemView
from PyQt5 import QtCore

from .models import TreeModel
from .delegates import LeftSideBarDelegate
from .cover_art_display import CoverArtBox
from audio.playlist_models import Playlist
from uuid import UUID

FRONT_COVER_MAX_WIDTH = 300
FRONT_COVER_MIN_WIDTH = 180


class LeftSideBar(QWidget):

    treeViewSelectionChanged = pyqtSignal(QModelIndex, QModelIndex)
    treeViewDoubleClicked = pyqtSignal(QModelIndex)
    
    addPlaylistRequested = pyqtSignal()
    removePlaylistRequested = pyqtSignal(UUID)
    addToPlaylistRequested = pyqtSignal(UUID)
    
    playlistAdded = pyqtSignal(UUID)
    playlistRenamed = pyqtSignal(UUID, str)

    def __init__(self, tree_items, parent=None):
        super(LeftSideBar, self).__init__(parent)
        self._tree_items = tree_items
        self._restoreSettings()

        self._setTreeView()
        self._setAlbumCoverBox()

        self._renderUI()

        self.setMinimumWidth(FRONT_COVER_MIN_WIDTH)
        self.setMaximumWidth(FRONT_COVER_MAX_WIDTH)

    def _restoreSettings(self):
        pass

    def _setTreeView(self):
        self.treeModel = TreeModel()

        self.treeModel.addTopLevelItems(self._tree_items.keys())


        # for k, v in self._tree_items.items():
        #     self.treeModel.addToModel(k, v)

        self.leftBarView = QTreeView()
        self.leftBarView.setModel(self.treeModel)
        self.leftBarView.setHeaderHidden(True)
        self.leftBarView.setRootIsDecorated(False)
        self.leftBarView.setItemsExpandable(False)
        self.leftBarView.setMouseTracking(True)
        self.leftBarView.expandAll()
        self.leftBarView.setFocusPolicy(Qt.NoFocus)
        self.leftBarView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.leftBarView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.leftBarView.setEditTriggers(QAbstractItemView.SelectedClicked)

        self.leftBarView.selectionModel().currentRowChanged.connect(
            lambda c, p: self.treeViewSelectionChanged.emit(c, p))


        # self.leftBarView.selectionModel().currentRowChanged.connect(
        #     lambda c, p: print('selected {} : {}'.format(c.internalPointer().itemData(), c.internalPointer().valueData())))

        self.leftBarView.selectionModel().setCurrentIndex(
            self.leftBarView.model().index(
                0, 0, self.leftBarView.model().index(0, 0)),
            QItemSelectionModel.Select)

        self.leftBarView.doubleClicked.connect(
            lambda i: self.treeViewDoubleClicked.emit(i))

        delegate = LeftSideBarDelegate(self.leftBarView)
        self.leftBarView.setItemDelegate(delegate)
        delegate.addPlaylistRequested.connect(
            lambda: self.addPlaylistRequested.emit())
        delegate.removePlaylistRequested.connect(
            lambda i: self.removePlaylistRequested.emit(
                self.__getUuidFromIndex(i)))
        delegate.addToPlaylistRequested.connect(
            lambda i:
            self.addToPlaylistRequested.emit(self.__getUuidFromIndex(i)))
        delegate.editingFinished.connect(self._onRenamed)

    def _onRenamed(self, index, text):
        self.playlistRenamed.emit(
            self.__getUuidFromIndex(index),
            text)

    @property
    def model(self):
        return self.treeModel

    def _onCurrentChanged(self, current, previous):
        print("SELECTION CHAINGED")
        print(current.row(), current.column())


    def _setAlbumCoverBox(self):
        self.albumCoverBox = CoverArtBox()

    def _renderUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.leftBarView, stretch=0)
        self.layout.addWidget(self.albumCoverBox, stretch=0)
        self.setLayout(self.layout)

    @QtCore.pyqtSlot(str, str, bytes)
    def changeCoverArtBoxInformation(self, title, artist, cover):
        self.albumCoverBox.setCoverArtBox(title, artist, cover)

    @QtCore.pyqtSlot(UUID, str, int, int)
    def addPlaylistEntry(self, uuid, name, row=0, column=0):
        model = self.model
        parent = model.getTopLevelIndex('PLAYLISTS')
        if model.insertPlaylistEntry(row, name, uuid, parent):
            self.playlistAdded.emit(uuid)

        child = model.index(row, column, parent)
        self.leftBarView.selectionModel().setCurrentIndex(
            child, QItemSelectionModel.SelectCurrent)
        self.leftBarView.edit(child)

    @QtCore.pyqtSlot(UUID, int, int)
    def createDefaults(self, uuid, row=0, column=0):
        model = self.model
        parent = model.getTopLevelIndex('LIBRARY')
        model.insertPlaylistEntry(row, 'Songs', uuid, parent)

    def __getUuidFromIndex(self, index):
        model = self.model
        uuid = model.getItemUuid(index)
        return uuid

    def __getIndexFromUuid(self, uuid):
        model = self.model
        row = model.getIndexFromUuid(uuid)
        return row

    @QtCore.pyqtSlot(UUID)
    def removePlaylistEntry(self, uuid):
        model = self.model
        row = self.__getIndexFromUuid(uuid)
        parent = model.getTopLevelIndex('PLAYLISTS')

        if not model.removeRow(row, parent):
            return None
