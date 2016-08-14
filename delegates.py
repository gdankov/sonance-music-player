from PyQt5.QtWidgets import QStyledItemDelegate, QStyle
from PyQt5 import QtCore, QtGui


class LeftSideBarDelegate(QStyledItemDelegate):

    addToPlaylist = QtCore.pyqtSignal(name='add to playlist')

    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)

        self.margin = 3
        self.plusIcon = QtGui.QPixmap("plus_icon.png")

    def __iconPostion(self, option):
        decorationSize = option.decorationSize
        height = decorationSize.height()
        width = decorationSize.width()

        y = option.rect.top() + self.margin
        x = option.rect.right() - width - self.margin
        return QtCore.QRect(x, y, width - self.margin, height - self.margin)

    def paint(self, painter, option, index):
        # if(QStyle.State_MouseOver):
        #     print("WAZAS")

        super(LeftSideBarDelegate, self).paint(painter, option, index)

        painter.save()
        if(not index.parent().isValid() and
                (option.state and QStyle.State_MouseOver) and
                index.data() == 'PLAYLISTS'):
                self.initStyleOption(option, index)
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                painter.drawPixmap(self.__iconPostion(option), self.plusIcon)
        painter.restore()

    def editorEvent(self, event, model, option, index):
        if(not index.parent().isValid() and index.data() == 'PLAYLISTS' and
                event.type() == QtCore.QEvent.MouseButtonRelease):

            mouseEvent = event
            plusButtonRect = self.__iconPostion(option)
            if plusButtonRect.contains(mouseEvent.pos()):
                self.addToPlaylist.emit()
        return False

    # def sizeHint(self, option, index):
    #     s = QStyledItemDelegate.sizeHint(self, option, index)
    #     row_height = 40
    #     s.setHeight(s.height() + 10)

    #     # if not index.parent().isValid():
    #     #     s.setWidth(s.width() + self.plusIcon.width() + self.margin * 2)
    #     #     s.setHeight(max(s.height(),
    #     #                         self.plusIcon.height() + self.margin * 2))
    #     return s










# drawing shit

        # QStyledItemDelegate.paint(self, painter, option, index)
        # if not index.parent().isValid():
        #     painter.save()
        #     r = option.rect
        #     painter.translate( r.topLeft() )
        #     painter.drawLine(0,0, r.width(), 0)
        #     painter.restore()

# topLeftY = option.rect.top() 
#         topLeftX = option.rect.right() - self.plusIcon.width() 

#         bottomRightY = option.rect.bottom() 
#         bottomRightX = option.rect.right() 
        
#         topLeft = QtCore.QPoint(topLeftX, topLeftY)
#         bottomRight = QtCore.QPoint(bottomRightX, bottomRightY)
#         print(QtCore.QRect(topLeft, bottomRight))
