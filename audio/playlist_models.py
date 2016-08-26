import os
import uuid
from collections import defaultdict
from audio_formats.mp3 import MP3AudioFile
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5 import QtCore

from audio_formats import MediaFactory

ACCEPTED_TYPES = ['.mp3', '.flac', '.m4a', 'mp4']

UNKNOWN_ALBUMS_NAME = '[Unknown Albums]'
UNKNOWN_ARTISTS_NAME = '[Unknown Artists]'


class Playlist(QtCore.QObject):
    mediaAboutToBeInserted = QtCore.pyqtSignal(int, int)
    mediaInserted = QtCore.pyqtSignal(int, int)
    mediaAboutToBeRemoved = QtCore.pyqtSignal(int, int)
    mediaRemoved = QtCore.pyqtSignal(int, int)
    mediaChanged = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        super(Playlist, self).__init__(parent)
        self._uuid = uuid.uuid4()

    def getUuid(self):
        return self._uuid

    def isCustomPlaylist(self):
        return False


class DirectoryPlaylist(Playlist):

    def __init__(self, parent=None):
        super(DirectoryPlaylist, self).__init__(parent)

        self._directories_urls = set()
        self._added_song_urls = set()
        self._tracks = []

        self._qPlaylist = QMediaPlaylist(parent)
        self._qPlaylist.mediaAboutToBeInserted.connect(
            lambda s, e: self.mediaAboutToBeInserted.emit(s, e))
        self._qPlaylist.mediaInserted.connect(
            lambda s, e: self.mediaInserted.emit(s, e))
        self._qPlaylist.mediaAboutToBeRemoved.connect(
            lambda s, e: self.mediaAboutToBeRemoved.emit(s, e))
        self._qPlaylist.mediaRemoved.connect(
            lambda s, e: self.mediaRemoved.emit(s, e))
        self._qPlaylist.mediaChanged.connect(
            lambda s, e: self.mediaChanged.emit(s, e))

    def songs(self):
        return self._tracks

    def albums_data(self):
        return self._albumsData

    def artists_data(self):
        return self._artistsData

    def __traverse_directory(self, url, func):
        songs = []
        for root, dirs, files in os.walk(url):
                for file in files:
                    abs_path = os.path.join(root, file)
                    song = func(abs_path)
                    if song:
                        songs.append(song)
        return songs

    def is_empty(self):
        return not self._tracks

    def add_song(self, abs_path):
        if abs_path not in self._added_song_urls:
            url = QtCore.QUrl.fromLocalFile(abs_path)
            song = MediaFactory.create_media(abs_path)
            if not song:
                return None
            added = self._qPlaylist.addMedia(QMediaContent(url))
            if not added:
                return None

            self._tracks.append(song)
            self._added_song_urls.add(abs_path)
            return song

    def remove_song(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None

        if self._qPlaylist.currentIndex() == row:
            if row < self.song_count():
                self._qPlaylist.setCurrentIndex(row + 1)
            else:
                self._qPlaylist.setCurrentIndex(row - 1)

        removed = self._qPlaylist.removeMedia(row)
        if not removed:
            return

        del self._tracks[row]
        url = self.get_song_abs_path(row)
        self._added_song_urls.discard(url)

    def add_directory(self, directory):
        if directory not in self._directories_urls:
            self._directories_urls.add(directory)
            songs = self.__traverse_directory(directory, self.add_song)
            return songs
        return None

    def add_directories(self, directories):
        songs = []
        for directory in directories:
            if directory not in self._directories_urls:
                current_songs = self.add_directory(directory)
                if current_songs:
                    songs.extend(current_songs)
        return songs

    def remove_directory(self, directory):
        if directory not in self._directories_urls:
            return False  # raise Error

        self.__traverse_directory(directory, self.remove_song)

    def setCurrentIndex(self, index):
        self._qPlaylist.setCurrentIndex(index)

    def getCurrentIndex(self):
        return self._qPlaylist.currentIndex()

    def getCurrentSong(self):
        return self._qPlaylist.currentMedia()

    def clear(self):
        self._tracks = []
        self._directories_urls = set()
        self._added_song_urls = set()
        self._qPlaylist.clear()

    @property
    def internalPlaylist(self):
        return self._qPlaylist

    def song_count(self):
        return len(self._tracks)

    def get_song_metadata(self, row, tags):
        if row < 0 or row > self.song_count() - 1:
            return None
        if not isinstance(tags, list):
            tags = [tags]
        return self._tracks[row].get_values(tags)

    def get_song(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None

        return self._tracks[row]

    def get_song_title(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None
        k, v = self.get_song_metadata(row, 'title').popitem()
        try:
            return v[0]
        except IndexError:
            return None

    def get_song_album(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None
        k, v = self.get_song_metadata(row, 'album').popitem()
        try:
            return v[0]
        except IndexError:
            return None

    def get_song_artist(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None

        k, v = self.get_song_metadata(row, 'artist').popitem()
        try:
            return v[0]
        except IndexError:
            return None

    def get_song_genre(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None

        k, v = self.get_song_metadata(row, 'genre').popitem()
        try:
            return v[0]
        except IndexError:
            return None

    def get_song_abs_path(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None

        return self._tracks[row].get_abs_path()

    def getDirectories(self):
        return self._directories_urls

    def getAddedSongUrls(self):
        return self._added_song_urls

    def __str__(self):
        return str(self._tracks)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self._directories_urls == other._directories_urls and
                self._added_song_urls == other._added_song_urls)


class CustomPlaylist(DirectoryPlaylist):

    playlistRenamed = QtCore.pyqtSignal(str, str)

    def __init__(self, name, parent=None):
        super(CustomPlaylist, self).__init__(parent)
        self._name = name

    def isCustomPlaylist(self):
        return True

    def getName(self):
        return self._name

    def setName(self, name):
        if not name == self._name:
            oldValue = self._name
            self._name = name
            self.playlistRenamed.emit(name, oldValue)
