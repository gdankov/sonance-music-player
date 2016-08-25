class TreeNode:

    DEFAULT_ITEM_DATA = 'untitled'

    def __init__(self, data, valueData=None, parent=None):
        self.__itemData = data
        self.__valueData = valueData
        self.__parentItem = parent
        self.__childItems = []

    def appendChild(self, child):
        self.__childItems.append(child)
        return True

    def child(self, row):
        return self.__childItems[row]

    def childNumber(self):
        if self.__parentItem:
            return self.__parentItem.children().index(self)
        return 0

    def getChildByName(self, name):
        for index, child in enumerate(self.__childItems):
            if name == child.data():
                return child

    def getChildIndexFromUuid(self, uuid):
        for index, child in enumerate(self.__childItems):
            if uuid == child.data()[1]:
                return index

    def children(self):
        return self.__childItems

    def childCount(self):
        return len(self.__childItems)

    def columnCount(self):
        return 1

    def row(self):
        if self.__parentItem:
            return self.__parentItem.__childItems.index(self)
        return 0

    def parentItem(self):
        return self.__parentItem

    def data(self):
        return (self.__itemData, self.__valueData)

    def itemData(self):
        return self.__itemData

    def valueData(self):
        return self.__valueData

    def setData(self, newData):
        if not newData == self.__itemData:
            self.__itemData = newData
            return True

    def insertChild(self, position, name=None, value=None):
        if position < 0 or position > len(self.__childItems):
            return False

        if not name:
            name = self.DEFAULT_ITEM_DATA

        item = TreeNode(name, value, parent=self)
        self.__childItems.insert(position, item)

        return True

    def removeChild(self, position):
        if position < 0 or position > len(self.__childItems):
            return False
        del self.__childItems[position]
        return True

    def getChildIndex(self, name):
        for index, child in enumerate(self.__childItems):
            if child.itemData() == name:
                return index
        return -1
