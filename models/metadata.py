import mutagen

ALL_TAGS = ['title', 'artist', 'album', 'albumartist', 'genre', 'tracknumber',
            'discnumber', 'date', 'comment', 'lyrics']

SUMMARIES = ['length', 'sample_rate', 'channels']


class NotAMediaFileError(Exception):
    def __init__(self, cause):
        self.cause = cause

    def get_cause(self):
        return self.cause


class Metadata:
    def __init__(self, song_uri):
        self.uri = song_uri
        try:
            self.file = mutagen.File(self.uri, easy=True)
        except FileNotFoundError as e:
            raise NotAMediaFileError(e)

        self.init_tags()
        self.init_summary()

    def init_tags(self):
        self.tags = {tag: self.file.get(tag, ['']) for tag in ALL_TAGS}

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

