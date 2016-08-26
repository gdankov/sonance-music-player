from PyQt5.QtWidgets import(QHBoxLayout, QVBoxLayout, QAction, QToolButton,
                            QPushButton, QLabel, QListWidget,
                            QListWidgetItem, QSplitter, QMenu, QLineEdit,
                            QDialog, QTextEdit, QFileDialog)

from PyQt5 import QtCore


class MetadataDialog(QDialog):

    METADATA_INFO = ['artist', 'title', 'album', 'albumartist', 'composer',
                     'grouping', 'genre', 'comment', 'track_number',
                     'disc_number', 'date']

    def __init__(self, available_metadata, parent=None):
        super(MetadataDialog, self).__init__(parent)
        self.available_metadata = available_metadata
        self.setLabels()
        self.setEdits(self.available_metadata)
        self.initUi()

    def setLabels(self):
        self.artistLabel = QLabel()
        self.artistLabel.setText("Artist Name:")
        self.artistLabel.setAlignment(QtCore.Qt.AlignLeft)

        self.titleLabel = QLabel()
        self.titleLabel.setText("Song Title:")
        self.titleLabel.setAlignment(QtCore.Qt.AlignLeft)

        self.albumLabel = QLabel()
        self.albumLabel.setText("Album Name:")
        self.albumLabel.setAlignment(QtCore.Qt.AlignLeft)

        self.albumArtistLabel = QLabel()
        self.albumArtistLabel.setText("Album Artist:")
        self.albumArtistLabel.setAlignment(QtCore.Qt.AlignLeft)

        self.composerLabel = QLabel()
        self.composerLabel.setText("Composer:")
        self.composerLabel.setAlignment(QtCore.Qt.AlignLeft)

        self.groupingLabel = QLabel()
        self.groupingLabel.setText("Grouping:")
        self.groupingLabel.setAlignment(QtCore.Qt.AlignLeft)

        self.genreLabel = QLabel()
        self.genreLabel.setText("Genre:")
        self.genreLabel.setAlignment(QtCore.Qt.AlignLeft)

        self.commentLabel = QLabel()
        self.commentLabel.setText("Comment:")
        self.commentLabel.setAlignment(QtCore.Qt.AlignLeft)

        self.trackNumberLabel = QLabel()
        self.trackNumberLabel.setText("Track Number:")
        self.trackNumberLabel.setAlignment(QtCore.Qt.AlignLeft)

        self.discNumberLabel = QLabel()
        self.discNumberLabel.setText("Disc number:")
        self.discNumberLabel.setAlignment(QtCore.Qt.AlignLeft)

        self.yearLabel = QLabel()
        self.yearLabel.setText("Year:")
        self.yearLabel.setAlignment(QtCore.Qt.AlignLeft)

    def setEdits(self, info_dict):
        self.artistLineEdit = QLineEdit()
        self.artistLineEdit.setText(
            self.__safeMetadataCall(info_dict, 'artist', 0))
        self.artistLineEdit.setAlignment(QtCore.Qt.AlignLeft)

        self.titleLineEdit = QLineEdit()
        self.titleLineEdit.setText(
            self.__safeMetadataCall(info_dict, 'title', 0))
        self.titleLineEdit.setAlignment(QtCore.Qt.AlignLeft)

        self.albumLineEdit = QLineEdit()
        self.albumLineEdit.setText(
            self.__safeMetadataCall(info_dict, 'album', 0))
        self.albumLineEdit.setAlignment(QtCore.Qt.AlignLeft)

        self.albumArtistLineEdit = QLineEdit()
        self.albumArtistLineEdit.setText(
            self.__safeMetadataCall(info_dict, 'albumartist', 0))
        self.albumArtistLineEdit.setAlignment(QtCore.Qt.AlignLeft)

        self.composerLineEdit = QLineEdit()
        self.composerLineEdit.setText(
            self.__safeMetadataCall(info_dict, 'composer', 0))
        self.composerLineEdit.setAlignment(QtCore.Qt.AlignLeft)

        self.groupingLineEdit = QLineEdit()
        self.groupingLineEdit.setText(
            self.__safeMetadataCall(info_dict, 'grouping', 0))
        self.groupingLineEdit.setAlignment(QtCore.Qt.AlignLeft)

        self.genreLineEdit = QLineEdit()
        self.genreLineEdit.setText(
            self.__safeMetadataCall(info_dict, 'genre', 0))
        self.genreLineEdit.setAlignment(QtCore.Qt.AlignLeft)

        self.trackNumberLineEdit = QLineEdit()
        self.trackNumberLineEdit.setText(
            self.__safeMetadataCall(info_dict, 'track_number', 0))
        self.trackNumberLineEdit.setAlignment(QtCore.Qt.AlignLeft)

        self.discNumberLineEdit = QLineEdit()
        self.discNumberLineEdit.setText(
            self.__safeMetadataCall(info_dict, 'disc_number', 0))
        self.discNumberLineEdit.setAlignment(QtCore.Qt.AlignLeft)

        self.yearLineEdit = QLineEdit()
        self.yearLineEdit.setText(
            self.__safeMetadataCall(info_dict, 'date', 0))
        self.yearLineEdit.setAlignment(QtCore.Qt.AlignLeft)

        self.commentTextEdit = QTextEdit()
        self.commentTextEdit.setText(
            self.__safeMetadataCall(info_dict, 'comment', 0))
        self.commentTextEdit.setAlignment(QtCore.Qt.AlignLeft)

    def initUi(self):
        self.artistLayout = QHBoxLayout()
        self.artistLayout.addWidget(self.artistLabel)
        self.artistLayout.addWidget(self.artistLineEdit)

        self.titleLayout = QHBoxLayout()
        self.titleLayout.addWidget(self.titleLabel)
        self.titleLayout.addWidget(self.titleLineEdit)

        self.albumLayout = QHBoxLayout()
        self.albumLayout.addWidget(self.albumLabel)
        self.albumLayout.addWidget(self.albumLineEdit)

        self.albumArtisLayout = QHBoxLayout()
        self.albumArtisLayout.addWidget(self.albumArtistLabel)
        self.albumArtisLayout.addWidget(self.albumArtistLineEdit)

        self.composerLayout = QHBoxLayout()
        self.composerLayout.addWidget(self.composerLabel)
        self.composerLayout.addWidget(self.composerLineEdit)

        self.groupingLayout = QHBoxLayout()
        self.groupingLayout.addWidget(self.groupingLabel)
        self.groupingLayout.addWidget(self.groupingLineEdit)

        self.genreLayout = QHBoxLayout()
        self.genreLayout.addWidget(self.genreLabel)
        self.genreLayout.addWidget(self.genreLineEdit)

        self.trackNumberLayout = QHBoxLayout()
        self.trackNumberLayout.addWidget(self.trackNumberLabel)
        self.trackNumberLayout.addWidget(self.trackNumberLineEdit)

        self.discNumberLayout = QHBoxLayout()
        self.discNumberLayout.addWidget(self.discNumberLabel)
        self.discNumberLayout.addWidget(self.discNumberLineEdit)

        self.yearLayout = QHBoxLayout()
        self.yearLayout.addWidget(self.yearLabel)
        self.yearLayout.addWidget(self.yearLineEdit)

        self.commentLayout = QHBoxLayout()
        self.commentLayout.addWidget(self.commentLabel)
        self.commentLayout.addWidget(self.commentTextEdit)

        self.closeButton = QPushButton("Close")
        self.saveButton = QPushButton("Save")

        self.closeButton.clicked.connect(self.reject)
        self.saveButton.clicked.connect(self.accept)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addSpacing(12)
        self.buttonLayout.addWidget(self.saveButton)
        self.buttonLayout.addWidget(self.closeButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(self.artistLayout)
        mainLayout.addLayout(self.titleLayout)
        mainLayout.addLayout(self.albumLayout)
        mainLayout.addLayout(self.albumArtisLayout)
        mainLayout.addLayout(self.composerLayout)
        mainLayout.addLayout(self.groupingLayout)
        mainLayout.addLayout(self.genreLayout)
        mainLayout.addLayout(self.trackNumberLayout)
        mainLayout.addLayout(self.discNumberLayout)
        mainLayout.addLayout(self.commentLayout)
        mainLayout.addLayout(self.buttonLayout)
        self.setLayout(mainLayout)

        self.setWindowTitle("Metadata Editor")
        self.setMinimumSize(450, 340)
        self.resize(680, 420)

    def getResultDict(self):
        result = {}
        result['artist'] = self.artistLineEdit.text()
        result['title'] = self.titleLineEdit.text()
        result['album'] = self.albumLineEdit.text()
        result['albumartist'] = self.albumArtistLineEdit.text()
        result['composer'] = self.composerLineEdit.text()
        result['grouping'] = self.groupingLineEdit.text()
        result['genre'] = self.genreLineEdit.text()
        result['track_number'] = self.trackNumberLineEdit.text()
        result['disc_number'] = self.discNumberLineEdit.text()
        result['date'] = self.yearLineEdit.text()
        result['comment'] = self.commentTextEdit.toPlainText()
        return result

    def __safeMetadataCall(self, dict_, key, index):
        try:
            value = dict_[key]
            if isinstance(value, list):
                return value[0]
            else:
                return value
        except (IndexError, KeyError):
            return ''


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.currentDirectories = []
        # self.addDirectories(directories)
        self.initButtons()
        self.initUi()

        self.restoreSettings()
        self.setLibraryDirectoriesWidget()

    def saveSettings(self):
        settings = QtCore.QSettings(
            QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope,
            QtCore.QCoreApplication.organizationName(),
            QtCore.QCoreApplication.applicationName())

        settings.beginGroup("preferences")
        settings.beginWriteArray('library_directories',
                                 len(self.currentDirectories))

        for index, value in enumerate(self.currentDirectories):
            settings.setArrayIndex(index)
            settings.setValue("url", value)
        settings.endArray()
        settings.endGroup()

    def restoreSettings(self):
        settings = QtCore.QSettings(
            QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope,
            QtCore.QCoreApplication.organizationName(),
            QtCore.QCoreApplication.applicationName())

#        settings.setValue("preferences_window/position", self.pos())

        settings.beginGroup("preferences")
        size = settings.beginReadArray('library_directories')
        if not size == 0:
            for i in range(0, size):
                settings.setArrayIndex(i)
                url = settings.value("url")
                self.currentDirectories.append(url)
        settings.endArray()
        settings.endGroup()

    def initButtons(self):
        self.libraryDirectories = QLabel()
        self.libraryDirectories.setText("Library Directories")
        self.libraryDirectories.setAlignment(QtCore.Qt.AlignLeft)

        self.addButton = QPushButton("Add Directory")
        self.addButton.clicked.connect(self._onAdd)

        self.removeButton = QPushButton("Remove Directory")
        self.removeButton.clicked.connect(self._onRemove)

        self.directoriesList = QListWidget(self)

    def addDirectories(self, directories):
        if not isinstance(directories, list):
            directories = [directories]

        for directory in directories:
            self.currentDirectories.append(directory)

    def setLibraryDirectoriesWidget(self):
        for directory in self.currentDirectories:
            newItem = QListWidgetItem(directory, self.directoriesList)

    def _onAdd(self):
        directories = self.choose_directory()
        if not directories:
            return None

        for directory in directories:
            if directory not in self.currentDirectories:
                self.currentDirectories.append(directory)
                newItem = QListWidgetItem(directory, self.directoriesList)

    def _onRemove(self):
        currentItem = self.directoriesList.currentItem()
        row = self.directoriesList.indexFromItem(currentItem).row()
        if currentItem:
            self.directoriesList.takeItem(row)
            self.currentDirectories.remove(currentItem.data(
                QtCore.Qt.DisplayRole))

    def choose_directory(self):
        fileDialog = QFileDialog(self)
        fileDialog.setAcceptMode(QFileDialog.AcceptOpen)
        fileDialog.setFileMode(QFileDialog.Directory)
        fileDialog.setViewMode(QFileDialog.Detail)
        fileDialog.setWindowTitle("Choose Media Directory")
        try:
            fileDialog.setDirectory(QtCore.QStandardPaths.standardLocations(
                                    QtCore.QStandardPaths.MusicLocation)[0])
        except IndexError:
            fileDialog.setDirectory(QtCore.QDir.homePath())

        if fileDialog.exec_() == QDialog.Accepted:
            return fileDialog.selectedFiles()

    def initUi(self):
        self.directoriesButtonsLayout = QVBoxLayout()
        self.directoriesButtonsLayout.addWidget(self.addButton)
        self.directoriesButtonsLayout.addWidget(self.removeButton)
        self.directoriesButtonsLayout.addSpacing(10)

        self.directoriesLayout = QHBoxLayout()
        self.directoriesLayout.addWidget(self.directoriesList)
        self.directoriesLayout.addLayout(self.directoriesButtonsLayout)

        self.closeButton = QPushButton("Close")
        self.saveButton = QPushButton("Save")

        self.closeButton.clicked.connect(self.reject)
        self.saveButton.clicked.connect(self.accept)

        self.bottomButtonsLayout = QHBoxLayout()
        self.bottomButtonsLayout.addStretch(1)
        self.bottomButtonsLayout.addSpacing(12)
        self.bottomButtonsLayout.addWidget(self.saveButton)
        self.bottomButtonsLayout.addWidget(self.closeButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.libraryDirectories)
        mainLayout.addLayout(self.directoriesLayout)
        mainLayout.addLayout(self.bottomButtonsLayout)
        self.setLayout(mainLayout)

        self.setWindowTitle("Settings")
        self.setMinimumSize(450, 340)
        self.resize(680, 420)
