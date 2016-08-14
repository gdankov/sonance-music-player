from mutagen.mp3 import MP3

'''
############## ID3 Tags ##############

    TPE1  --  Lead performer
    TIT2  --  Title/songname
    TDRC  --  Recording time (year mostly)
    TALB  --  Album
    TPE2  --  Album artist
    TCON  --  Genre
    TRCK  --  Track number/Position in set
    TPOS  --  Part of a set (Disc number)

'''


'''
############## Audio Stream Information ##############

length  --  audio length, in seconds

channels  --  number of audio channels

bitrate  --  audio bitrate, in bits per second

sample_rate

encoder_info  --  a string containing encoder name and possibly version.
                  In case a lame tag is present this will start with "LAME ",
                  if unknown it is empty, otherwise the text format is
                  undefined.

bitrate_mode  --  a BitrateMode: 0 - Unknown
                                 1 - Constant Bitrate
                                 2 - Variable Bitrate
                                 3 - Averageg Bitrate


        Useless attributes:

version  --  MPEG version (1, 2, 2.5)

layer  --  1, 2, or 3

mode  -- One of STEREO, JOINTSTEREO, DUALCHANNEL, or MONO (0-3)
'''

valid_id3_tags = {'artist': 'TPE1',
                  'song_title': 'TIT2',
                  'album': 'TALB',
                  'album_artist': 'TPE2',
                  'year': 'TDRC',
                  'genre': 'TCON',
                  'track_number': 'TRCK',
                  'disc_number': 'TPOS'}

audio_stream_info = ['length', 'channels', 'bitrate', 'sample_rate',
                     'bitrate_mode']


class NotAMediaFileError(Exception):
    def __init__(self, cause):
        self.cause = cause

    def get_cause(self):
        return self.cause


class MP3Metadata:
    def __init__(self, song_uri):
        self.__uri = song_uri
        
        if song_uri is not None:
            self.__init()

    def 

    def get_song_name(self):
        return self.tags['title']

    def get_artist(self):
        return self.tags['artist']

    def get_album(self):
        return self.tags['album']

    def get_album_artist(self):
        return self.tags['albumartist']

    def get_genre(self):
        return self.tags['genre']

    def get_track_number(self):
        return self.tags['tracknumber']

    def get_disc_number(self):
        return self.tags['discnumber']

    def get_year(self):
        return self.tags['date']

    def get_comment(self):
        self.tags['comment']

    def get_lyrics(self):
        self.tags['lyrics']

    def get_tags(self):
        return self.tags

    def init_summary(self):
        self.summary = {summary: getattr(self.file.info, summary)
                        for summary in SUMMARIES}
        # TODO file size

    def get_summary(self):
        return self.summary

