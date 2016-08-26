from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QAudio, QMediaContent
from PyQt5.QtCore import QObject, pyqtSignal, QCoreApplication, QSettings
from audio.playlist_models import Playlist, DirectoryPlaylist, CustomPlaylist

from uuid import UUID

DEFAULT_PLAYLIST_NAME = 'Untitled Unmastered'


class PlaylistManger(QObject):

    customPlaylistCreated = pyqtSignal(UUID, str)
    libraryPlaylistCreated = pyqtSignal(UUID)

    currentPlaylistChanged = pyqtSignal(QMediaPlaylist, int, bool)
    currentMediaChanged = pyqtSignal(QMediaContent)

    addedToLibraryPlaylist = pyqtSignal(UUID, list)
    addedToCustomPlaylist = pyqtSignal(UUID, list)

    updatedLibraryPlaylist = pyqtSignal(UUID, list)

    playlistRemoved = pyqtSignal(UUID)

    def __init__(self, parent=None):
        super(PlaylistManger, self).__init__(parent)
        self._customPlaylists = []
        self._libraryPlaylist = None
        self._currentPlaylist = None

    def createCustomPlaylist(self, name, urls=None):
        if not name:
            name = DEFAULT_PLAYLIST_NAME

        playlist = CustomPlaylist(name)

        if urls and isinstance(urls, list):
            playlist.add_directories(urls)
        elif urls:
            playlist.add_directory(urls)

        self._customPlaylists.append(playlist)
        self.customPlaylistCreated.emit(playlist.getUuid(), playlist.getName())

    def createLibraryPlaylist(self, urls=None):
        playlist = DirectoryPlaylist()

        if urls and isinstance(urls, list):
            playlist.add_directories(urls)
        elif urls:
            playlist.add_directory(urls)

        self._libraryPlaylist = playlist
        self._currentPlaylist = self._libraryPlaylist
        self.libraryPlaylistCreated.emit(playlist.getUuid())
        self.currentPlaylistChanged.emit(
            self._libraryPlaylist.internalPlaylist, 0, False)

    def addToLibraryPlaylist(self, directories=None):
        if directories and isinstance(directories, list):
            addedSongs = self._libraryPlaylist.add_directories(directories)
        elif directories:
            addedSongs = self._libraryPlaylist.add_directory(directories)

        if addedSongs:
            self.addedToLibraryPlaylist.emit(
                self._libraryPlaylist.getUuid(), addedSongs)

    def updateLibraryPlaylist(self, directories):
        self._libraryPlaylist.clear()
        if directories and isinstance(directories, list):
            addedSongs = self._libraryPlaylist.add_directories(directories)
        elif directories:
            addedSongs = self._libraryPlaylist.add_directory(directories)
        else:
            addedSongs = []

        self.updatedLibraryPlaylist.emit(
            self._libraryPlaylist.getUuid(), addedSongs)

    def addSongsToCustomPlaylist(self, uuid, urls):
        playlist = self.getCustomPlaylist(uuid)
        if not playlist or not urls:
            return None
        addedSongs = []
        for url in urls:
            song = playlist.add_song(url)
            if song:
                addedSongs.append(song)

        if addedSongs:
            self.addedToCustomPlaylist.emit(
                uuid, addedSongs)

    def renamePlaylist(self, uuid, newName):
        for playlist in self._customPlaylists:
            if playlist.getUuid() == uuid:
                playlist.setName(newName)
                return

    def setPlaylist(self, uuid, index=0):
        if self.isLibraryPlaylist(uuid):
            playlist = self._libraryPlaylist
        else:
            playlist = self.getCustomPlaylist(uuid)

        if playlist.is_empty():
            return None

        if playlist is not self._currentPlaylist:
            self._currentPlaylist = playlist
            self.currentPlaylistChanged.emit(
                playlist.internalPlaylist, index, True)
        else:
            playlist.setCurrentIndex(index)

    def removePlaylist(self, uuid):
        playlist = self.getCustomPlaylist(uuid)
        index = self.getCustomPlaylistIndex(playlist)
        if self.isCurrentPlaylist(playlist.getUuid()):
            del self._customPlaylists[index]
            self._currentPlaylist = self._libraryPlaylist
            self.currentPlaylistChanged.emit(
                self._currentPlaylist.internalPlaylist, 0, False)
            self.playlistRemoved.emit(uuid)
        elif playlist.getUuid() == uuid:
            del self._customPlaylists[index]
            self.playlistRemoved.emit(uuid)

    def getBasicSongInfo(self, media):
        title, artist, cover = None, None, None
        mediaPath = media.canonicalUrl().path()
        currentPlaylist = self._currentPlaylist

        for song in currentPlaylist.songs():
            if song.get_abs_path() == mediaPath:
                title = self.__safeMetadataCall(song.get_title())
                artist = self.__safeMetadataCall(song.get_artist())
                cover = song.get_front_cover().data
                return title, artist, cover
        return title, artist, cover

    def __safeMetadataCall(self, call):
        try:
            return call[0]
        except IndexError:
            return ''

    def currentInternalPlaylist(self):
        return self._currentPlaylist.internalPlaylist

    def currentInternalPlaylistShuffled(self):
        return self._currentPlaylist.internalPlaylist.shuffle()

    def getCurrentPlaylistUuid(self):
        return self._currentPlaylist.getUuid()

    def getCurrentSongIndex(self):
        return self._currentPlaylist.internalPlaylist.currentIndex()

    def isCurrentPlaylist(self, uuid):
        return self.getCurrentPlaylistUuid() == uuid

    def getLibraryPlaylist(self):
        return self._libraryPlaylist

    def getCustomPlaylists(self):
        return self._customPlaylists

    def getCustomPlaylist(self, uuid):
        for playlist in self._customPlaylists:
            if playlist.getUuid() == uuid:
                return playlist

    def getCustomPlaylistIndex(self, playlist):
        for i, p in enumerate(self._customPlaylists):
            if p == playlist:
                return i

    def hasLibraryPlaylist(self):
        if self._libraryPlaylist:
            return True
        return False

    def isLibraryPlaylist(self, uuid):
        if self.hasLibraryPlaylist:
            return self._libraryPlaylist.getUuid() == uuid
        return False
