from PyQt5.QtWidgets import QStyledItemDelegate, QStyle, QLineEdit
from PyQt5 import QtCore, QtGui


class LeftSideBarDelegate(QStyledItemDelegate):

    # Signals
    addPlaylistRequested = QtCore.pyqtSignal()
    removePlaylistRequested = QtCore.pyqtSignal(QtCore.QModelIndex)
    addToPlaylistRequested = QtCore.pyqtSignal(QtCore.QModelIndex)
    editingFinished = QtCore.pyqtSignal(QtCore.QModelIndex, str)

    def __init__(self, parent=None):

        QStyledItemDelegate.__init__(self, parent)

        self.margin = 3
        self.plusIcon = QtGui.QPixmap(
            ":/left_sidebar_icons/plus_icon.png")
        self.trashIconBlack = QtGui.QPixmap(
            ":/left_sidebar_icons/trash_black_24x24.png")
        self.trashIconWhite = QtGui.QPixmap(
            ":/left_sidebar_icons/trash_white_24x24.png")
        self.addFileIconBlack = QtGui.QPixmap(
            ":/left_sidebar_icons/plus_circle_black.png")
        self.addFileIconWhite = QtGui.QPixmap(
            ":/left_sidebar_icons/plus_circle_white.png")

    def __rightmostIconPosition(self, option):
        decorationSize = option.decorationSize
        width = decorationSize.width()

        y = option.rect.top() + self.margin
        x = option.rect.right() - width - self.margin

        newHeight = option.rect.bottom() - option.rect.top() - self.margin * 2
        return QtCore.QRect(x, y, newHeight, newHeight)

    def __secondRightmostIconPosition(self, option):
        righmostPos = self.__rightmostIconPosition(option)

        r_x = righmostPos.x()

        y = option.rect.top() + self.margin
        x = r_x - option.decorationSize.width() - self.margin

        newHeight = option.rect.bottom() - option.rect.top() - self.margin * 2
        return QtCore.QRect(x, y, newHeight, newHeight)

    def paint(self, painter, option, index):
        painter.save()

        styleOption = option
        value = index.data()
        styleOption.text = value
        styleOption.font = index.data(QtCore.Qt.FontRole)
        self.parent().style().drawControl(
            QStyle.CE_ItemViewItem, styleOption, painter)

        if(not index.parent().isValid() and option.state and
                index.data() == 'PLAYLISTS'):
            self._drawIcon(painter, option, index,
                           self.__rightmostIconPosition(option), self.plusIcon)
        elif (index.parent().isValid() and
                index.parent().data() == 'PLAYLISTS' and
                (option.state & QStyle.State_MouseOver) and
                (option.state & QStyle.State_Selected)):
            self._drawIcon(painter, option, index,
                           self.__rightmostIconPosition(option),
                           self.trashIconWhite)
            self._drawIcon(painter, option, index,
                           self.__secondRightmostIconPosition(option),
                           self.addFileIconWhite)
        elif (index.parent().isValid() and
                index.parent().data() == 'PLAYLISTS' and
                (option.state & QStyle.State_MouseOver) and not
                (option.state & QStyle.State_Selected)):
            self._drawIcon(painter, option, index,
                           self.__rightmostIconPosition(option),
                           self.trashIconBlack)
            self._drawIcon(painter, option, index,
                           self.__secondRightmostIconPosition(option),
                           self.addFileIconBlack)
        else:
            super(LeftSideBarDelegate, self).paint(painter, option, index)
        painter.restore()

    def _drawIcon(self, painter, option, index, rect, icon):
        self.initStyleOption(option, index)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawPixmap(rect, icon.scaled(rect.width(), rect.height()))

    def editorEvent(self, event, model, option, index):
        if(not index.parent().isValid() and index.data() == 'PLAYLISTS' and
                event.type() == QtCore.QEvent.MouseButtonRelease):

            mouseEvent = event
            plusButtonRect = self.__rightmostIconPosition(option)
            if plusButtonRect.contains(mouseEvent.pos()):
                self.addPlaylistRequested.emit()
                return True
            return False
        elif(index.parent().isValid() and
                index.parent().data() == 'PLAYLISTS' and
                event.type() == QtCore.QEvent.MouseButtonRelease):

            mouseEvent = event
            deleteIconRect = self.__rightmostIconPosition(option)
            if deleteIconRect.contains(mouseEvent.pos()):
                self.removePlaylistRequested.emit(index)
                return True

            addIconRect = self.__secondRightmostIconPosition(option)
            if addIconRect.contains(mouseEvent.pos()):
                self.addToPlaylistRequested.emit(index)
                return True
            return False
        else:
            return False

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        if not model.data(index) == editor.text():
            model.setData(index, editor.text(), QtCore.Qt.EditRole)
            self.editingFinished.emit(index, editor.text())

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
