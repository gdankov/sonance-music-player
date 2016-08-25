from mutagen.id3 import Frames
from mutagen.mp3 import MP3
from .base import ImageType, Image, StreamInfoMixin, MediaFile


class ID3File(MediaFile):
    SUPPORTED_FORMATS = ['id3']

    ID3_MAPPINGS = {'TIT1': 'grouping',
                    'TIT2': 'title',
                    'TIT3': 'subtitle',
                    'TALB': 'album',
                    'TSST': 'discsubtitle',
                    'TSRC': 'isrc',
                    'TPE1': 'artist',
                    'TPE2': 'albumartist',
                    'TPE3': 'conductor',
                    'TPE4': 'remixer',
                    'TEXT': 'lyricist',
                    'TCOM': 'composer',
                    'TENC': 'encodedby',
                    'TBPM': 'bpm',
                    'TKEY': 'key',
                    'TLAN': 'language',
                    'TCON': 'genre',
                    'TMED': 'media',
                    'TMOO': 'mood',
                    'TCOP': 'copyright',
                    'TPUB': 'label',
                    'TDOR': 'originaldate',
                    'TDRC': 'date',
                    'TSSE': 'encodersettings',
                    'TSOA': 'albumsort',
                    'TSOP': 'artistsort',
                    'TSOT': 'titlesort',
                    'TRCK': 'track_number',
                    'TPOS': 'disc_number',
                    'WCOP': 'license',
                    'WOAR': 'artist_website',
                    'COMM': 'comment'
                    }

    R_ID3_MAPPINGS = {v: k for k, v in ID3_MAPPINGS.items()}

    USER_DEFINED_TAG = 'TXXX'

    INVOLVED_PERSONS_FRAMES = {'TMCL': 'instrument',
                               'TIPL': 'function'}

    ''' Maps between the value (instrument, function) and person's name.
          --`instrument` could be `guitar` or `piano` and that
                         would map to the musician's name that played it.
          --`function` could be `producer` or `DJ` and again would map to
                       musician's name as well.
    '''

    def __init__(self, filepath, id3v23=False):
        super(ID3File, self).__init__(filepath)
        self._id3v23 = id3v23

    def _get_title(self, mutagen_file):
        try:
            text_frame = mutagen_file.getall(self.R_ID3_MAPPINGS['title'])[0]
        except IndexError:
            return ''
        return text_frame.text

    def _get_album(self, mutagen_file):
        try:
            album_frame = mutagen_file.getall(self.R_ID3_MAPPINGS['album'])[0]
        except IndexError:
            return ''
        return album_frame.text

    def _get_artist(self, mutagen_file):
        try:
            artist_frame = mutagen_file.getall(
                self.R_ID3_MAPPINGS['artist'])[0]
        except IndexError:
            return ''
        return artist_frame.text

    def _get_values(self, mutagen_file, values, get_encodings):
        if not mutagen_file:
            return {}

        result_values = {}
        for value in values:
            if value in self.R_ID3_MAPPINGS:
                tag = self.R_ID3_MAPPINGS[value]

                if tag.startswith('T'):
                    text_frame = mutagen_file.getall(tag)
                    if text_frame:
                        text_frame = text_frame[0]
                        if get_encodings:
                            result_values[value] = (int(text_frame.encoding),
                                                    text_frame.text)
                        else:
                            result_values[value] = text_frame.text
                    else:
                        result_values[value] = []
                elif tag == self.R_ID3_MAPPINGS['comment']:
                    comments_frame = mutagen_file.getall(tag)
                    if comments_frame:
                        for frame in comments_frame:
                            description = frame.desc
                            text_value = frame.text
                            key = '{}:{}'.format(value, description)
                            if get_encodings:
                                encoding = int(frame.encoding)
                                result_values[key] = (encoding, text_value)
                            else:
                                result_values[key] = text_value
                    else:
                        result_values[value] = []
                elif tag.startswith('W'):
                    result_values[value] = (0, frame.url)
                else:
                    result_values[value] = (0, frame)
        return result_values

    def _get_images(self, mutagen_file):
        if not mutagen_file:
            return {}
        result_images = {}
        images = mutagen_file.getall('APIC')
        for image in images:
            current_image = Image(data=image.data,
                                  desc=image.desc,
                                  image_type=image.type,
                                  mime_type=image.mime)
            key = ImageType.to_str(current_image.image_type)
            result_images[key] = current_image
        return result_images

    def set_tag(self, key, value, encoding=3):
        try:
            key_tag = self.R_ID3_MAPPINGS[key]
        except KeyError:
            key_tag = 'TXXX:' + key_tag

        if isinstance(value, list):
            frame = Frames[key_tag](encoding=encoding,
                                    text=value)
        else:
            frame = Frames[key_tag](encoding=encoding,
                                    text=[value])

        self._mutagen_file.tags.setall(key_tag, [frame])
        return True

    def _set_image(self, image, image_type):
        pass

    def save(self, v1=1, v23_sep='/', padding=None):
        if self._id3v23:
            id3 = self.mgfile
            if hasattr(id3, 'tags'):
                id3 = id3.tags
            id3.update_to_v23()
            v2_version = 3
        else:
            v2_version = 4
        self._mutagen_file.save(self._filepath,
                                v1=v1, v2_version=v2_version,
                                v23_sep=v23_sep,
                                padding=padding)

    def delete_tag(self, tag):
        try:
            tag = self.R_ID3_MAPPINGS[tag]
        except KeyError:
            tag = 'TXXX' + tag
        self._mutagen_file.delall(tag)


class MP3AudioFile(ID3File, StreamInfoMixin):
    SUPPORTED_FORMATS = ['MP3', 'AIFF']     # aiff not tested but should work

    def __init__(self, filepath, id3v23=False):
        super(MP3AudioFile, self).__init__(filepath, id3v23)

    def _get_values(self, mutagen_file, tags, get_encodings=False):
        return super(MP3AudioFile, self)._get_values(mutagen_file.tags,
                                                     tags, get_encodings)

    def _read_file(self, filename):
        return MP3(filename)

    def get_images(self):
        return self._get_images(self._mutagen_file.tags)

    def get_title(self):
        return self._get_title(self._mutagen_file.tags)

    def get_album(self):
        return self._get_album(self._mutagen_file.tags)

    def get_artist(self):
        return self._get_artist(self._mutagen_file.tags)

    def streamInfo(self):
        info = super(MP3AudioFile, self).streamInfo()
        file = self._mutagen_file
        id3version = ''
        if file.tags and file.info.layer == 3:  # add to info
            id3version = 'ID3v{}.{}'.format(
                file.tags.version[0],
                file.tags.version[1])
        info['format'] = 'MPEG-1 Layer {} - {}'.format(file.info.layer,
                                                       id3version)
        return info
