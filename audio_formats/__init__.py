import os
from .mp3 import MP3AudioFile
from .flac import FLACMediaFile
from .mp4 import MP4MediaFile

__all__ = ['base', 'mp3', 'flac', 'mp4']


class MediaFactory():

    @staticmethod
    def create_media(filepath):
        extension = os.path.splitext(filepath)[-1]
        if extension == '.mp3' or extension == '.aiff':
            return MP3AudioFile(filepath)
        elif extension == '.flac':
            return FLACMediaFile(filepath)
        elif extension == '.m4a' or extension == '.mp4':
            return MP4MediaFile(filepath)
        else:
            return None
