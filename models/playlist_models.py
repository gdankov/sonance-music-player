import os
from .basic_media_models import Song

ACCEPTED_TYPES = ['.mp3', '.wav', '.ogg', '.flac', '.m4a']


class Playlist():
    def __init__(self):
        pass


class CustomPlaylist(Playlist):
    def __init__(self):
        super(CustomPlaylist, self).__init__()


class DirectoryPlaylist(Playlist):
    songs = []

    def __init__(self, url=None):
        super(DirectoryPlaylist, self).__init__()
        if url is not None:
            self.generate_playlist(url)

    def generate_playlist(self, url):
        for root, dirs, files in os.walk(url):
            for filename in files:
                container_type = os.path.splitext(filename)[1]
                if container_type in ACCEPTED_TYPES:
                    abs_path = os.path.join(root, filename)
                    song = Song(abs_path, container_type)
                    self.songs.append(song)

    def __str__(self):
        return str(self.songs)
