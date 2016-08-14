import os
from basic_media_models import Song

ACCEPTED_TYPES = ['.mp3']        # '.wav', '.ogg', '.flac', '.m4a' and more


class Playlist():
    def __init__(self):
        pass


class CustomPlaylist(Playlist):
    def __init__(self):
        super(CustomPlaylist, self).__init__()


class DirectoryPlaylist(Playlist):
    def __init__(self, urls=[]):
        super(DirectoryPlaylist, self).__init__()
        self.__urls = urls
        self.__added_song_urls = set()
        self.__songs = []

        if not len(self.__urls) == 0:
            self.__generate_playlist(urls)

    def __generate_playlist(self, urls):
        for url in urls:
            self.__traverse_directory(url)

    def __traverse_directory(self, url):
        for root, dirs, files in os.walk(url):
                for file in files:
                    extension = os.path.splitext(file)[-1]  # get the extension
                    if extension in ACCEPTED_TYPES:
                        abs_path = os.path.join(root, file)
                        self.add_song(abs_path)

    def add_song(self, abs_path):
        if abs_path not in self.__added_song_urls:
            song = Song(abs_path)
            self.__songs.append(song)
            self.__added_song_urls.add(abs_path)

    def remove_song(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None
            # exception maybe?

        url = self.get_song_abs_path(row)
        del self.__songs[row]
        self.__added_song_urls.discard(url)

    def song_count(self):
        return len(self.__songs)

    def get_song(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None
            # exception maybe?

        return self.__songs[row]

    def get_song_name(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None
            # exception maybe?

        return self.__songs[row].song_name()

    def get_song_album(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None
            # exception maybe?

        return self.__songs[row].song_album()

    def get_song_artist(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None
            # exception maybe?

        return self.__songs[row].song_artist()

    def get_song_genre(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None
            # exception maybe?

        return self.__songs[row].song_genre()

    def get_song_year(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None
            # exception maybe?

        return self.__songs[row].song_year()

    def get_song_abs_path(self, row):
        if row < 0 or row > self.song_count() - 1:
            return None
            # exception maybe?

        return self.__songs[row].song_abs_path()

    def __str__(self):
        return str(self.__songs)











#for root, dirs, files in os.walk(url):
            #     for file in files:
            #         container_type = os.path.splitext(filename)[1]
            #         if container_type in ACCEPTED_TYPES:
            #             abs_path = os.path.join(root, filename)
            #             song = Song(abs_path, container_type)
            #             self.__songs.append(song)
