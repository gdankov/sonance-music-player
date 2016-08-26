from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QAudio
from PyQt5.QtCore import QObject, pyqtSignal, QCoreApplication, QSettings
from audio.playlist_models import Playlist, DirectoryPlaylist, CustomPlaylist
from .PlaylistManager import PlaylistManger

from uuid import UUID


class AudioPlayer(QObject):

    songPositionChanged = pyqtSignal(int)
    songDurationChanged = pyqtSignal(int)
    stateChanged = pyqtSignal(int)
    playlistChanged = pyqtSignal(QMediaPlaylist, int)

    currentSongChanged = pyqtSignal(str, str, bytes)
    currentSelectionChanged = pyqtSignal(UUID, int)

    customPlaylistCreated = pyqtSignal(UUID, str)
    libraryPlaylistCreated = pyqtSignal(UUID)

    addedToLibraryPlaylist = pyqtSignal(UUID, list)
    addedToCustomPlaylist = pyqtSignal(UUID, list)

    updatedLibraryPlaylist = pyqtSignal(UUID, list)

    playlistRemoved = pyqtSignal(UUID)

    def __init__(self, volumeLevel=40, playbackMode=QMediaPlaylist.Sequential,
                 parent=None):
        super(AudioPlayer, self).__init__(parent)

        self.__player = QMediaPlayer()
        self.__player.setVolume(volumeLevel)

        self.__player.currentMediaChanged.connect(self._onMediaChanged)
        self.__player.stateChanged.connect(
            lambda state: self.stateChanged.emit(int(state)))
        self.__player.positionChanged.connect(
            lambda x: self.songPositionChanged.emit(x))
        self.__player.durationChanged.connect(
            lambda x: self.songDurationChanged.emit(x))

        self.__playlistManager = PlaylistManger()

        self.__playlistManager.customPlaylistCreated.connect(
            lambda uuid, name: self.customPlaylistCreated.emit(uuid, name))
        self.__playlistManager.libraryPlaylistCreated.connect(
            lambda p: self.libraryPlaylistCreated.emit(p))
        
        self.__playlistManager.currentPlaylistChanged.connect(
            self._onChangedPlaylist)
        self.__playlistManager.currentPlaylistChanged.connect(
            lambda p, i: self.playlistChanged.emit(p, i))

        self.__playlistManager.playlistRemoved.connect(
            lambda uuid: self.playlistRemoved.emit(uuid))

        self.__playlistManager.addedToLibraryPlaylist.connect(
            lambda uuid, l: self.addedToLibraryPlaylist.emit(uuid, l))
        self.__playlistManager.addedToCustomPlaylist.connect(
            lambda uuid, l: self.addedToCustomPlaylist.emit(uuid, l))

        self.__playlistManager.updatedLibraryPlaylist.connect(
            lambda uuid, l: self.updatedLibraryPlaylist.emit(uuid, l))

    def createCustomPlaylist(self, name=None, urls=None):
        self.__playlistManager.createCustomPlaylist(name, urls)

    def createLibraryPlaylist(self, urls=None):
        self.__playlistManager.createLibraryPlaylist(urls)

    def addToLibraryPlaylist(self, url=None):
        self.__playlistManager.addToLibraryPlaylist(url)

    def updateLibraryPlaylist(self, url=None):
        self.__playlistManager.updateLibraryPlaylist(url)

    def renamePlaylist(self, uuid, newName):
        self.__playlistManager.renamePlaylist(uuid, newName)

    def addSongsToCustomPlaylist(self, uuid, urls=[]):
        self.__playlistManager.addSongsToCustomPlaylist(uuid, urls)

    def removeSong(self, uuid, row):
        self.__playlistManager.removeSong(uuid, row)

    def setPlaylist(self, uuid, index=0):
        if (self.__player.playlist() and
                self.__playlistManager.isCurrentPlaylist(uuid)):
            if index == self.__player.playlist().currentIndex():
                if self.__player.state() == QMediaPlayer.PlayingState:
                    self.__player.pause()
                else:
                    self.__player.play()
            else:
                self.__player.playlist().setCurrentIndex(index)
        else:
            self.__playlistManager.setPlaylist(uuid, index)

    def hasLibraryPlaylist(self):
        return self.__playlistManager.hasLibraryPlaylist()

    def removePlaylist(self, uuid):
        self.__playlistManager.removePlaylist(uuid)

    def getCurrentPlaylist(self):
        self.__playlistManager.getCurrentPlaylist()

    def getCurrentQMediaPlaylist(self):
        self.__player.playlist()

    def isPlayerAvailable(self):
        return self.__player.isAvailable()

    def getDuration(self):
        return self.__player.duration()

    def getPlayer(self):
        return self.__player

    def getState(self):
        return self.__player.state()

    def play(self):
        if self.__player.playlist():
            self.__player.play()

    def pause(self):
        if self.__player.playlist():
            self.__player.pause()

    def stop(self):
        if self.__player.playlist():
            self.__player.stop()

    def previousEnhanced(self, sameSongMillis):
        if self.__player.position() <= sameSongMillis:
            self.previous()
        else:
            self.__player.setPosition(0)

    def previous(self):
        if self.__player.playlist():
            self.__player.playlist().previous()

    def next(self):
        if self.__player.playlist():
            self.__player.playlist().next()

    def setVolume(self, value):
        self.__player.setVolume(value)

    def setPosition(self, milliseconds):
        self.__player.setPosition(milliseconds)

    def playlistCurrentIndex(self):
        if self.__player.playlist():
            return self.__player.playlist().currentIndex()

    def setCurrentPlaylistIndex(self, index):
        if self.__player.playlist():
            self.__player.playlist().setCurrentIndex(index)

    def _onChangedPlaylist(self, playlist, index, playIt=False):
        self.__player.setPlaylist(playlist)
        if playlist:
            playlist.setCurrentIndex(index)
        if playIt:
            self.play()

    def _onMediaChanged(self, media):
        if media.isNull() and self.__player.playlist():
            self.__player.playlist().setCurrentIndex(0)
            media = self.__player.playlist().media(0)
        if media.isNull():
            return

        title, artist, cover = self.__playlistManager.getBasicSongInfo(media)

        self.currentSongChanged.emit(title, artist, cover)

        uuid = self.__playlistManager.getCurrentPlaylistUuid()
        index = self.__playlistManager.getCurrentSongIndex()
        self.currentSelectionChanged.emit(uuid, index)

    # def saveSettings(self):
    #     # settings = QSettings(QSettings.IniFormat, QSettings.UserScope,
    #     #                      QCoreApplication.organizationName(),
    #     #                      QCoreApplication.applicationName())

    #     # settings.beginGroup("music_player")

    #     # # if self.__playlistManager.getLibraryPlaylist():
    #     # #     libraryDirectories = self.__playlistManager.getLibraryPlaylist().getDirectories()
    #     # #     settings.beginWriteArray('library_playlist',
    #     # #                              len(libraryDirectories))
    #     # #     for index, value in enumerate(libraryDirectories):
    #     # #         settings.setArrayIndex(index)
    #     # #         settings.setValue("url", value)
    #     # #     settings.endArray()

    #     # customPlaylists = self.__playlistManager.getCustomPlaylists()
    #     # settings.beginWriteArray('custom_playlists',
    #     #                          len(customPlaylists))
    #     # for index, value in enumerate(customPlaylists):
    #     #     settings.setArrayIndex(index)
    #     #     playlistName = settings.value('name', value.getName())
    #     #     playlistUrls = value.getAddedSongUrls()
    #     #     settings.beginWriteArray(playlistName,
    #     #                              len(playlistUrls))
    #     #     for i, v in enumerate(playlistUrls):
    #     #         settings.setArrayIndex(i)
    #     #         settings.setValue("url", v)
    #     #     settings.endArray()
    #     # settings.endArray()

    #     # settings.endGroup()
    #     # if self.__playlistManager.getLibraryPlaylist():
    #     #     libraryDirectories = self.__playlistManager.getLibraryPlaylist().getDirectories()
    #     #     settings.beginWriteArray('library_playlist',
    #     #                              len(libraryDirectories))
    #     #     for index, value in enumerate(libraryDirectories):
    #     #         settings.setArrayIndex(index)
    #     #         settings.setValue("url", value)
    #     #     settings.endArray()

    #     customPlaylists = self.__playlistManager.getCustomPlaylists()
    #     for playlist in customPlaylists:
    #         playlistName = playlist.getName()
    #         for url in playlist:
    #             pass

    # def restoreSettings(self):
    #     settings = QSettings(QSettings.IniFormat, QSettings.UserScope,
    #                          QCoreApplication.organizationName(),
    #                          QCoreApplication.applicationName())

    #     settings.beginGroup("music_player")

    #     # size = settings.beginReadArray('library_playlist')
    #     # libraryDirectories = []
    #     # for i in range(size):
    #     #     settings.setArrayIndex(i)
    #     #     libraryDirectories.append(settings.value("url"))
    #     # settings.endArray()

    #     customPlaylists = {}
    #     size = settings.beginReadArray('custom_playlists')
    #     for i in range(size):
    #         urls = []
    #         settings.setArrayIndex(i)
    #         playlistName = settings.value('name')
    #         print(playlistName)
    #         size2 = settings.beginReadArray(playlistName)
    #         for j in range(size2):
    #             settings.setArrayIndex(j)
    #             url = settings.value("url")
    #             urls.append(url)
    #         settings.endArray()
    #         customPlaylists[playlistName] = urls
    #     settings.endArray()

    #     settings.endGroup()

    #     print('-------')
    #     print(customPlaylists)





        # settings = QSettings(QCoreApplication.organizationName(),
        #                      QCoreApplication.applicationName())
        # settings.beginGroup("music_player")

        # size = settings.beginReadArray('library_playlist')
        # if not size == 0:
        #     for i in range(0, size):
        #         settings.setArrayIndex(i)
        #         url = settings.value("url")
        # settings.endArray()

        # if url:
        #     from audio.playlist_models import DirectoryPlaylist

        #     playlist = DirectoryPlaylist()
        #     playlist.add_directory(url)
        #     self.addAndSetPlaylist(playlist, 2)

        # settings.endGroup()
        pass
