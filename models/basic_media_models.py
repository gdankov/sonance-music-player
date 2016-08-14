from .metadata import Metadata

ACCEPTED_TYPES = ['.mp3', '.wav', '.ogg', '.flac', '.m4a']


class Song():
    def __init__(self, abs_url):
        self.abs_url = abs_url
        self.metadata = Metadata(self.abs_url)
        self.tags = self.metadata.get_tags()
        self.summary = self.metadata.get_summary()
        # probably dont need that
        self.summary['file_name'] = self.abs_url

    def __str__(self):
        return """
Title: {}
Artist: {}
Album: {}
Album Artist: {}
Genre: {}
Track Number: {}
Disk Number: {}
Date: {}
Comment: {}
Lyrics: {}
----------
Length: {}
Sample rate: {}
Channels: {}
File Name: {}

""".format(self.tags['title'], self.tags['artist'],
           self.tags['album'], self.tags['albumartist'],
           self.tags['genre'], self.tags['tracknumber'],
           self.tags['discnumber'], self.tags['date'],
           self.tags['comment'], self.tags['lyrics'],
           self.summary['length'],
           self.summary['sample_rate'],
           self.summary['channels'],
           self.summary['file_name'])

    def __repr__(self):
        return self.__str__()

class Album():
    pass


class Artist():
    pass
