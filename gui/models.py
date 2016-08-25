from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtGui import QIcon, QFont

from .helper_struct import TreeNode
from util import seconds_to_hms


class TreeModel(QtCore.QAbstractItemModel):

    dataChangedEnhanced = pyqtSignal(str, str, QModelIndex)

    def __init__(self, data={}, parent=None):
        super(QtCore.QAbstractItemModel, self).__init__(parent)

        rootData = [' ']        # empty string for the root item
        self.__root = TreeNode(rootData)

    def getTopLevelIndex(self, name):
        row = self.__root.getChildIndex(name)
        column = 0
        if not row == -1:
            return self.index(row, column)
        else:
            return QModelIndex

    def getIndexFromUuid(self, uuid):
        playlistIndex = self.getTopLevelIndex('PLAYLISTS')
        playlist = self.__root.child(playlistIndex.row())
        return playlist.getChildIndexFromUuid(uuid)

    def addTopLevelItems(self, items):
        for item in items:
            node = TreeNode(item, parent=self.__root)
            self.__root.appendChild(node)

    def addChildItems(self, parentItem, childItems):
        if not self.isTopLevelItem(parentItem):
            return False

        parent = self.__root.getChildByName(parentItem)
        for child in childItems:
            if isinstance(child, tuple):
                itemData, valueData = childItems
                child = TreeNode(itemData, valueData, parent=parent)
            else:
                child = TreeNode(itemData, parent=parent)
            parent.appendChild(child)

    def isTopLevelItem(self, item):
        return item in [child.itemData() for child in self.__root.children()]

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.__root
        else:
            parentItem = parent.internalPointer()

        child = parentItem.child(row)
        if child:
            return self.createIndex(row, column, child)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        child = index.internalPointer()
        parent = child.parentItem()

        if parent is self.__root:
            return QtCore.QModelIndex()
        return self.createIndex(parent.row(), 0, parent)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.__root
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return self.__root.columnCount()
        else:
            return parent.internalPointer().columnCount()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # TODO CHECK DIFFERENT ROLES
        if not index.isValid():
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return index.internalPointer().itemData()
        elif role == QtCore.Qt.ToolTipRole:
            pass
        elif role == QtCore.Qt.DecorationRole:
            return self.__getIcon(index)
        elif role == QtCore.Qt.FontRole:
            font = QFont("Times", 15)
            return font
        # elif role == QtCore.Qt.EditRole:
        #     return "ale"

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not role == QtCore.Qt.EditRole:
            return False

        item = self.getItem(index)
        oldValue = item.itemData()
        isChanged = item.setData(value)

        if isChanged:
            self.dataChanged.emit(index, index)
            self.dataChangedEnhanced.emit(value, oldValue, index)

        return isChanged

    def flags(self, index):
        if not index.isValid():
            return 0

        if index.internalPointer() in self.__root.children():
            return QtCore.Qt.ItemIsEnabled
        elif index.parent().isValid() and index.parent().row() == 1:            #FIXIT should not be hardcoded
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | \
                QtCore.Qt.ItemNeverHasChildren | QtCore.Qt.ItemIsSelectable
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | \
            QtCore.Qt.ItemNeverHasChildren

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        return QtCore.QVariant()

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.__root

    def getItemUuid(self, index):
        return index.internalPointer().valueData()

    def insertRow(self, position, parent=QtCore.QModelIndex()):
        parentItem = self.getItem(parent)
        self.beginInsertRows(parent, position, position + 1)
        isInserted = parentItem.insertChild(position)
        self.endInsertRows()

        return isInserted

    def removeRow(self, row, parent=QtCore.QModelIndex()):
        parentItem = self.getItem(parent)

        self.beginRemoveRows(parent, row, row + 1)
        areRemoved = parentItem.removeChild(row)

        self.endRemoveRows()

        return areRemoved

    def insertPlaylistEntry(self, position, name, value,
                            parent=QtCore.QModelIndex):

        parentItem = self.getItem(parent)
        self.beginInsertRows(parent, position, position + 1)
        isInserted = parentItem.insertChild(position, name, value)
        self.endInsertRows()

        return isInserted

    def __getIcon(self, index):
        if index.internalPointer().parentItem().itemData() == 'PLAYLISTS':
            return QIcon(":/left_sidebar_icons/playlist_64x64.png")

        itemName = index.internalPointer().itemData()

        if itemName == 'Songs':
            return QIcon(":/left_sidebar_icons/music.png")
        elif itemName == 'Artists':
            pass
        elif itemName == 'Albums':
            pass
        elif itemName == 'Gengres':
            pass
        elif itemName == 'Years':
            pass


class PlaylistModel(QtCore.QAbstractTableModel):

    DEFAULT_HEADERS = ['TITLE', 'LENGTH', 'ARTIST', 'ALBUM', 'GENRE']

    def __init__(self, uuid, headers=[], parent=None):
        super(PlaylistModel, self).__init__(parent)
        if not headers:
            self.__headers = self.DEFAULT_HEADERS
        self.__uuid = uuid
        self.__column_count = len(self.__headers)
        self.__playlist = []

    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid() and self.__playlist:
            return len(self.__playlist)
        else:
            return 0

    def getUuid(self):
        return self.__uuid

    # for debugging
    def printElems(self):
        for elem in self.__playlist:
            print(elem)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.__headers) if not parent.isValid() else 0

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if self.__playlist and self.__indexExists(row, column, parent):
            return self.createIndex(row, column)
        return QtCore.QModelIndex()

    def __indexExists(self, row, column, parent):
        if parent.isValid():
            return False
        if(row >= 0 and row < self.rowCount() and
                column >= 0 and column < self.columnCount()):
            return True
        return False

    def parent(self, child):
        return QtCore.QModelIndex()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # TODO CHECK DIFFERENT ROLES
        # if index.isValid() and role == QtCore.Qt.ToolTipRole:
        #     print("HEYo")
        #     return "TOOLTIP BIATCH"
        if not index.isValid():
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole:
            audioFile = self.__playlist[index.row()]
            if index.column() == self.__headers.index('LENGTH'):
                return seconds_to_hms(audioFile.streamInfo()['length'])
            else:
                data = self.__headers[index.column()].lower()
                d = self.__saveMetadataCall(audioFile.get_values([data])[data])
                return d

        elif role == QtCore.Qt.ToolTipRole:
            pass
        elif role == QtCore.Qt.DecorationRole:
            pass
        elif role == QtCore.Qt.FontRole:
            pass

    def __saveMetadataCall(self, call):
        try:
            return call[0]
        except IndexError:
            return ''

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if(role == QtCore.Qt.DisplayRole and
                orientation == QtCore.Qt.Horizontal):
            return self.__headers[section]

        return QtCore.QVariant()


    # IF I WANT IT TO BE IDITABLE
    # def setData(self, index, value, role=QtCore.Qt.EditRole):
    #     pass

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return super(PlaylistModel, self).flags(index) | \
            QtCore.Qt.ItemIsEnabled

    # def insertRow(self, row, parent=QtCore.QModelIndex()):
    #     self.beginInsertRows(parent, row, row + 1)
    #     self.__playlist.insert(None, row)
    #     self.endInsertRows()

    #     return True

    # def removeRow(self, row, parent=QtCore.QModelIndex()):
    #     self.beginRemoveRows(parent, row, row + 1)
    #     del self.__playlist[row]
    #     self.endRemoveRows()

    #     return True

    # def insertRows(self, row, count, parent=QtCore.QModelIndex()):
    #     self.beginInsertRows(parent, row, row + count - 1)
    #     self.__playlist.insert(None, row)
    #     self.endInsertRows()

    #     return True

    # def removeRows(self, row, count, parent=QtCore.QModelIndex()):
    #     pass

    def insertMedia(self, row, mediaFiles=[], parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row + len(mediaFiles) - 1)
        currentRow = row
        for file in mediaFiles:
            self.__playlist.insert(currentRow, file)
            currentRow += 1
        self.endInsertRows()

    def removeMedia(self, row, count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row + 1)
        for i in range(row, count):
            del self.__playlist[i]
        self.endRemoveRows()
