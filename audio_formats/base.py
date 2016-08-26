from enum import Enum




class ImageType(Enum):

    """Indicates the kind of an `Image` stored in a file's tag.
    """

    OTHER = 0
    FILE_ICON = 1            # 32×32 pixels ‘file icon’ (PNG only)
    OTHER_FILE_ICON = 2
    FRONT_COVER = 3
    BACK_COVER = 4
    LEAFLET = 5
    MEDIA = 6               # (e.g. label side of CD)
    LEAD_ARTIST = 7
    ARTIST = 8
    CONDUCTOR = 9
    GROUP = 10
    COMPOSER = 11
    LYRICSIT = 12
    RECORDING_LOCATION = 13
    DURING_RECORDING = 14
    DURING_PERFORMANCE = 15
    SCREEN_CAPTURE = 16
    FISH = 17               # A bright coloured fish
    ILLUSTRATION = 18
    ARTIST_LOGO = 19
    PUBLISHER_LOGO = 20

    @staticmethod
    def to_str(image):
        return str(image).split('.')[-1].lower()


class Image:
    def __init__(self, data, desc=None, image_type=None, mime_type=None):
        self.data = data
        self.desc = desc
        if isinstance(image_type, int):
            try:
                image_type = list(ImageType)[image_type]
            except IndexError:
                image_type = ImageType.OTHER
        self.image_type = image_type
        self.mime = mime_type

    @property
    def mime_type(self):
        return self.mime

    @property
    def type_index(self):
        if self.type is None:
            return 0
        return self.image_type.value

    @property
    def type(self):
        return self.image_type
    


class Encoding(Enum):
    LATIN1 = 0
    '''ISO-8859-1'''

    UTF16 = 1
    """UTF-16 with BOM"""

    UTF16BE = 2
    """UTF-16BE without BOM"""

    UTF8 = 3
    """UTF-8"""


class StreamInfoMixin():
    def streamInfo(self):
        info = {}
        if hasattr(self._mutagen_file.info, 'length'):
            info['length'] = int(self._mutagen_file.info.length)
        if (hasattr(self._mutagen_file.info, 'bitrate') and
                self._mutagen_file.info.bitrate):
            info['bitrate'] = self._mutagen_file.info.bitrate
        if (hasattr(self._mutagen_file.info, 'sample_rate') and
                self._mutagen_file.info.sample_rate):
            info['sample_rate'] = self._mutagen_file.info.sample_rate
        if (hasattr(self._mutagen_file.info, 'channels') and
                self._mutagen_file.info.channels):
            info['channels'] = self._mutagen_file.info.channels
        if (hasattr(self._mutagen_file.info, 'bits_per_sample') and
                self._mutagen_file.info.bits_per_sample):
            info['bits_per_sample'] = self._mutagen_file.info.bits_per_sample
        return info

# TODO ASF - http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/ASF.html, https://github.com/exaile/exaile/blob/d86a3c1cb0ecb703d8688664718814ebd1ea5f29/xl/metadata/asf.py


class MediaFile:
    SUPPORTED_FORMATS = []

    def __init__(self, filepath):
        self._filepath = filepath
        self._mutagen_file = self._read_file(self._filepath)

    def _read_file(self, filepath):
        raise NotImplementedError()

    def get_abs_path(self):
        return self._filepath

    def get_title(self):
        return self._get_title(self._mutagen_file)

    def get_album(self):
        return self._get_album(self._mutagen_file)

    def get_artist(self):
        return self._get_artist(self._mutagen_file)

    def get_values(self, tags, get_encodings=False):
        if not isinstance(tags, list):
            return None
        return self._get_values(self._mutagen_file, tags, get_encodings)

    def get_images(self):
        return self._get_images(self._mutagen_file)

    def get_front_cover(self):
        all_available_images = self.get_images()
        try:
            return all_available_images['front_cover']
        except KeyError:
            return Image(b'')     # TODO choose another image if there's no front cover available

    def __str__(self):
        return self.get_title()
