class TreeNode:
    def __init__(self, data, parent=0):
        self.__itemData = data
        self.__parentItem = parent
        self.__childItems = []

    def appendChild(self, child):
        self.__childItems.append(child)

    def child(self, row):
        return self.__childItems[row]

    def children(self):
        return self.__childItems

    def childCount(self):
        return len(self.__childItems)

    def columnCount(self):
        return len(self.__itemData)

    def data(self):
        return self.__itemData

    def row(self):
        if self.__parentItem:
            return self.__parentItem.__childItems.index(self)
        return 0

    def parentItem(self):
        return self.__parentItem
