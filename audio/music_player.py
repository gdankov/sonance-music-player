from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QAudio
from PyQt5.QtCore import QObject, pyqtSignal, QCoreApplication, QSettings
from audio.playlist_models import Playlist, DirectoryPlaylist, CustomPlaylist
from .PlaylistManager import PlaylistManger

from uuid import UUID


class AudioPlayer(QObject):

    songPositionChanged = pyqtSignal(int)
    songDurationChanged = pyqtSignal(int)
    playlistChanged = pyqtSignal(QMediaPlaylist, int)

    currentSongChanged = pyqtSignal(str, str, bytes)

    customPlaylistCreated = pyqtSignal(UUID, str)
    libraryPlaylistCreated = pyqtSignal(UUID)

    addedToLibraryPlaylist = pyqtSignal(UUID, list)
    addedToCustomPlaylist = pyqtSignal(UUID, list)

    playlistRemoved = pyqtSignal(UUID)

    def __init__(self, volumeLevel=40, parent=None):
        super(AudioPlayer, self).__init__(parent)

        self.__player = QMediaPlayer()
        self.__player.setVolume(volumeLevel)
        self.__player.currentMediaChanged.connect(self._onMediaChanged)
        self.__player.positionChanged.connect(
            lambda x: self.songPositionChanged.emit(x))
        self.__player.durationChanged.connect(
            lambda x: self.songDurationChanged.emit(x))
        #self.__player.setAudioRole(QAudio.MusicRole)  # supported in  Qt 5.6

        # print(self.__player.supportedMimeTypes())  # added
        self.__playlistManager = PlaylistManger()

        self.__playlistManager.customPlaylistCreated.connect(
            lambda uuid, name: self.customPlaylistCreated.emit(uuid, name))
        self.__playlistManager.libraryPlaylistCreated.connect(
            lambda p: self.libraryPlaylistCreated.emit(p))
        
        self.__playlistManager.currentPlaylistChanged.connect(
            self._onChangedPlaylist)
        self.__playlistManager.currentPlaylistChanged.connect(
            lambda p, i: self.playlistChanged.emit(p, i))

        # self.__playlistManager.currentMediaChanged.connect(
        #     self._onMediaChanged)

        self.__playlistManager.playlistRemoved.connect(
            lambda uuid: self.playlistRemoved.emit(uuid))

        self.__playlistManager.addedToLibraryPlaylist.connect(
            lambda uuid, l: self.addedToLibraryPlaylist.emit(uuid, l))
        self.__playlistManager.addedToCustomPlaylist.connect(
            lambda uuid, l: self.addedToCustomPlaylist.emit(uuid, l))

    def setMuted(self, muted):
        pass

    def isMuted(self):
        pass

    # signal -> mutedChanged(bool muted)

    def createCustomPlaylist(self, name=None, urls=None):
        self.__playlistManager.createCustomPlaylist(name, urls)

    def createLibraryPlaylist(self, urls=None):
        self.__playlistManager.createLibraryPlaylist(urls)

    def addToLibraryPlaylist(self, url=None):
        self.__playlistManager.addToLibraryPlaylist(url)

    def addAndSetPlaylist(self, url, index, name=None):
        self.__playlistManager.addAndSetPlaylist(url, index, name)

    def renamePlaylist(self, uuid, newName):
        self.__playlistManager.renamePlaylist(uuid, newName)

    def addSongsToCustomPlaylist(self, uuid, urls=[]):
        self.__playlistManager.addSongsToCustomPlaylist(uuid, urls)

    def setPlaylist(self, uuid, index=0):
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

    # TODO
    def setPlaybackMode(self, mode):
        # playlist.setPlaybackMode(PlaybackMode mode)
        pass

    def _onChangedPlaylist(self, playlist, index, playIt=False):
        self.__player.setPlaylist(playlist)
        if playlist:
            playlist.setCurrentIndex(index)
        if playIt:
            self.play()

    def _onMediaChanged(self, media):
        title, artist, cover = self.__playlistManager.getBasicSongInfo(media)
        self.currentSongChanged.emit(title, artist, cover)

    def saveState(self):
        # settings = QSettings(QCoreApplication.organizationName(),
        #                      QCoreApplication.applicationName())

        # settings.beginGroup("music_player")

        # if self._libraryPlaylist:
        #     libraryDirectories = self._libraryPlaylist.getDirectories()
        #     settings.beginWriteArray('library_playlist',
        #                              len(libraryDirectories))
        #     for index, value in enumerate(libraryDirectories):
        #         settings.setArrayIndex(index)
        #         settings.setValue("url", value)
        #     settings.endArray()

        # # if self._customPlaylists:
        # #     settings.beginWriteArray('custom_playlists',
        # #                              len(self._customPlaylists)):
        # #     settings.setValue()
        # #     settings.endArray()


        # settings.endGroup()
        pass

    def restoreState(self):
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
