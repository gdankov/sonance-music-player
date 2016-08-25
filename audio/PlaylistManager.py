from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QAudio, QMediaContent
from PyQt5.QtCore import QObject, pyqtSignal, QCoreApplication, QSettings
from audio.playlist_models import Playlist, DirectoryPlaylist, CustomPlaylist

from uuid import UUID

DEFAULT_PLAYLIST_NAME = 'Untitled Unmastered'


class PlaylistManger(QObject):

    customPlaylistCreated = pyqtSignal(UUID, str)      # merge into one
    libraryPlaylistCreated = pyqtSignal(UUID)     # maybe

    currentPlaylistChanged = pyqtSignal(QMediaPlaylist, int, bool)
    currentMediaChanged = pyqtSignal(QMediaContent)

    addedToLibraryPlaylist = pyqtSignal(UUID, list)
    addedToCustomPlaylist = pyqtSignal(UUID, list)

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
        self.libraryPlaylistCreated.emit(playlist.getUuid())

    def addToLibraryPlaylist(self, directories=None):
        if directories and isinstance(directories, list):
            addedSongs = self._libraryPlaylist.add_directories(directories)
        elif directories:
            addedSongs = self._libraryPlaylist.add_directory(directories)

        if addedSongs:
            self.addedToLibraryPlaylist.emit(
                self._libraryPlaylist.getUuid(), addedSongs)

    def addSongsToCustomPlaylist(self, uuid, urls):
        playlist = self.getCustomPlaylist(uuid)
        if not playlist or not urls:
            return None
        addedSongs = []
        for url in urls:
            addedSongs.append(playlist.add_song(url))

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
        for index, playlist in enumerate(self._customPlaylists):
            if playlist.getUuid() == uuid and self.isCurrentPlaylist(playlist):
                del self._customPlaylists[index]
                if self._libraryPlaylist:
                    self._currentPlaylist = self._libraryPlaylist
                    self.currentPlaylistChanged.emit(
                        self._currentPlaylist.internalPlaylist, 0, False)
                else:
                    self._currentPlaylist = None
                    self.currentPlaylistChanged.emit(None, 0, False)
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
                title = self.__saveMetadataCall(song.get_title())
                artist = self.__saveMetadataCall(song.get_artist())
                cover = song.get_front_cover().data
        return title, artist, cover

    def __saveMetadataCall(self, call):
        try:
            return call[0]
        except IndexError:
            return ''

    def getCurrentPlaylist(self):
        return self._currentPlaylist

    def isCurrentPlaylist(self, playlist):
        return self.getCurrentPlaylist() == playlist

    def getLibraryPlaylist(self):
        return self._libraryPlaylist

    def getCustomPlaylist(self, uuid):
        for playlist in self._customPlaylists:
            if playlist.getUuid() == uuid:
                return playlist

    def hasLibraryPlaylist(self):
        if self._libraryPlaylist:
            return True
        return False

    def isLibraryPlaylist(self, uuid):
        if self.hasLibraryPlaylist:
            return self._libraryPlaylist.getUuid() == uuid
        return False
