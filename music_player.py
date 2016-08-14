from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist


class AudioPlayer():
    def __init__(self, volumeLevel, parent=None):
        self.__player = QMediaPlayer()
        self.__player.setVolume(volumeLevel)

        self.__playlist = QMediaPlaylist(self.__player)
        self.__playlist.setCurrentIndex(1)

        self.__player.setPlaylist(self.__playlist)

    def getDuration(self):
        return self.__player.duration()

    def getPlaylist(self):
        return self.__playlist

    def getPlayer(self):
        return self.__player

    def getState(self):
        return self.__player.state()

    def play(self):
        self.__player.play()

    def pause(self):
        self.__player.pause()

    def previousEnhanced(self, sameSongMillis):
        if self.__player.position() < sameSongMillis:
            self.previous()
        else:
            self.__player.stop()
            self.__player.play()

    def previous(self):
        self.__playlist.previous()

    def next(self):
        self.__playlist.next()

    def setVolume(self, value):
        self.__player.setVolume(value)

    def setPosition(self, milliseconds):
        self.__player.setPosition(milliseconds)

    def playlistCurrentIndex(self):
        return self.__playlist.currentIndex()

    def setCurrentPlaylistIndex(self, index):
        self.__playlist.setCurrentIndex(index)

    # TODO
    def setPlaybackMode(self, mode):
        # playlist.setPlaybackMode(PlaybackMode mode)
        pass
