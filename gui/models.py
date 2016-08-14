from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QIcon, QFont

from gui.helper_struct import TreeNode


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, data={}, parent=None):
        super(QtCore.QAbstractItemModel, self).__init__(parent)

        rootData = [' ']                     # empty string for the root item
        self.__root = TreeNode(rootData)

    def addToModel(self, topLevelItem, childrenItems):
        parent = TreeNode(topLevelItem, self.__root)
        self.__root.appendChild(parent)
        for secondLevelData in childrenItems:
            child = TreeNode(secondLevelData, parent)
            parent.appendChild(child)

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

        if role == QtCore.Qt.DisplayRole:
            return index.internalPointer().data()
        elif role == QtCore.Qt.ToolTipRole:
            pass
        elif role == QtCore.Qt.DecorationRole:
            return self.__getIcon(index)
        elif role == QtCore.Qt.FontRole:
            font = QFont("Times", 15)
            return font

    def flags(self, index):
        if not index.isValid():
            return 0

        if index.internalPointer() in self.__root.children():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.QAbstractItemModel.flags(self, index)
        
        # if not index.parent.isValid():
        #     return None
        # else:
        #     return QtCore.Qt.ItemIsEnabled
        # elif parent is playlist, eddit is ok 

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        return QtCore.QVariant()

    def insertRow(self, row, parent=QtCore.QModelIndex()):
        pass

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        pass

    def removeRow(self, row, parent=QtCore.QModelIndex()):
        pass

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        pass

    # TODO def setIcon(item, icon) set icons for every item, but from outside the class

    def __getIcon(self, index):

        if index.internalPointer().parentItem().data() == 'PLAYLISTS':
            #return some icon
            pass

        itemName = index.data()

        if itemName == 'Songs':
            return QIcon("./left_sidebar_icons/music.png")
        elif itemName == 'Artists':
            pass
        elif itemName == 'Albums':
            pass
        elif itemName == 'Gengres':
            pass
        elif itemName == 'Years':
            pass


class PlaylistModel(QtCore.QAbstractTableModel):
    COLUMN_COUNT = 5
    HEADERS = ['title', 'artist', 'album', 'genre', 'file name']

    # add playlist=None
    def __init__(self, headers=[], parent=None):
        super(PlaylistModel, self).__init__(parent)
        self.__headers = headers
        self.__playlist = None
        self.urlSongMappings = {}

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self.__playlist.mediaCount() if not parent.isValid() else 0

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.__headers) if not parent.isValid() else 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # TODO CHECK DIFFERENT ROLES
        # if index.isValid() and role == QtCore.Qt.ToolTipRole:
        #     print("HEYo")
        #     return "TOOLTIP BIATCH"

        if not index.isValid() or not role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if index.column() == self.HEADERS.index('title'):
            location = self.__playlist.media(index.row()).canonicalUrl()
            return self.urlSongMappings[location].tags['title'][0]
        elif index.column() == self.HEADERS.index('artist'):
            location = self.__playlist.media(index.row()).canonicalUrl()
            return self.urlSongMappings[location].tags['artist'][0]
        elif index.column() == self.HEADERS.index('album'):
            location = self.__playlist.media(index.row()).canonicalUrl()
            return self.urlSongMappings[location].tags['album'][0]
        elif index.column() == self.HEADERS.index('genre'):
            location = self.__playlist.media(index.row()).canonicalUrl()
            return self.urlSongMappings[location].tags['genre'][0]
        elif index.column() == self.HEADERS.index('file name'):
            return self.__playlist.media(
                index.row()).canonicalUrl().toLocalFile()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if(role == QtCore.Qt.DisplayRole and
                orientation == QtCore.Qt.Horizontal):
            return self.__headers[section]

        return QtCore.QVariant()









    # not sure about this qmodelindex thing
    def index(self, row, column, parent=QtCore.QModelIndex()):
        if(self.__playlist is not None and not parent.isValid() and
                row >= 0 and row < self.__playlist.mediaCount() and
                column >= 0 and column < self.COLUMN_COUNT):
            return self.createIndex(row, column)
        else:
            return QtCore.QModelIndex()

    def parent(self, child):
        return QtCore.QModelIndex()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        # TODO CHECK DIFFERENT ROLES
        # if index.isValid() and role == QtCore.Qt.ToolTipRole:
        #     print("HEYo")
        #     return "TOOLTIP BIATCH"

        if not index.isValid() or not role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if index.column() == self.HEADERS.index('title'):
            location = self.__playlist.media(index.row()).canonicalUrl()
            return self.urlSongMappings[location].tags['title'][0]
        elif index.column() == self.HEADERS.index('artist'):
            location = self.__playlist.media(index.row()).canonicalUrl()
            return self.urlSongMappings[location].tags['artist'][0]
        elif index.column() == self.HEADERS.index('album'):
            location = self.__playlist.media(index.row()).canonicalUrl()
            return self.urlSongMappings[location].tags['album'][0]
        elif index.column() == self.HEADERS.index('genre'):
            location = self.__playlist.media(index.row()).canonicalUrl()
            return self.urlSongMappings[location].tags['genre'][0]
        elif index.column() == self.HEADERS.index('file name'):
            return self.__playlist.media(
                index.row()).canonicalUrl().toLocalFile()

    # IF I WANT IT TO BE IDITABLE
    # def setData(self, index, value, role=QtCore.Qt.EditRole):
    #     pass

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable

    def insertRow(self, row, parent=QtCore.QModelIndex()):
        pass

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        pass

    def removeRow(self, row, parent=QtCore.QModelIndex()):
        pass

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        pass

    def setPlaylist(self, playlist):
        self.beginResetModel()

        self.__playlist = playlist

        if self.__playlist is not None:
            self.__playlist.mediaAboutToBeInserted.connect(self.beginInsertItems)
            self.__playlist.mediaInserted.connect(self.endInsertItems)
            self.__playlist.mediaAboutToBeRemoved.connect(self.beginRemoveItems)
            self.__playlist.mediaRemoved.connect(self.endRemoveItems)
            self.__playlist.mediaChanged.connect(self.changeItems)

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
                    self.__playlist.addMedia(QMediaContent(url))
                    new_mappings[url] = song
            else:
                url = QtCore.QUrl(song.url)
                if url.isValid():
                    self.__playlist.addMedia(QMediaContent(url))
                    new_mappings[url] = song
        self.urlSongMappings = new_mappings
