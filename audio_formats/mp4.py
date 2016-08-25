from mutagen.mp4 import MP4
from .base import Image, MediaFile, StreamInfoMixin


class MP4MediaFile(MediaFile, StreamInfoMixin):
    MP4_MAPPINGS = {'\xa9nam': 'title',
                    '\xa9alb': 'album',
                    '\xa9ART': 'artist',
                    'aART': 'albumartist',
                    '\xa9wrt': 'composer',
                    '\xa9day': 'date',
                    '\xa9cmt': 'comment',
                    'desc': 'description',
                    'purd': 'purchase_date',
                    '\xa9grp': 'grouping',
                    '\xa9gen': 'genre',
                    '\xa9lyr': 'lyrics',
                    'purl': 'podcast_url',
                    'egid': 'podcast_episode_guid',
                    'catg': 'podcast_category',
                    'keyw': 'podcast_keywords',
                    '\xa9too': 'encoded_by',
                    'cprt': 'copyright',
                    'soal': 'album_sort_order',
                    'soaa': 'album_artist_sort_order',
                    'soar': 'artist_sort_order',
                    'sonm': 'title_sort_order',
                    'soco': 'composer_sort_order',
                    'sosn': 'show_sort_order',
                    'tvsh': 'show_name',
                    'tmpo': 'bpm',
                    'covr': 'front_cover'
                    }

    R_MP4_MAPPINGS = {v: k for k, v in MP4_MAPPINGS.items()}

    def __init__(self, filepath):
        super(MP4MediaFile, self).__init__(filepath)

    def _read_file(self, filepath):
        return MP4(filepath)

    def _get_title(self, mutagen_file):
        try:
            text_frame = mutagen_file.tags[self.R_MP4_MAPPINGS['title']][0]
        except IndexError:
            return ''
        return text_frame

    def _get_album(self, mutagen_file):
        try:
            album_frame = mutagen_file.tags[self.R_MP4_MAPPINGS['album']][0]
        except IndexError:
            return ''
        return album_frame

    def _get_artist(self, mutagen_file):
        try:
            artist_frame = mutagen_file.tags[self.R_MP4_MAPPINGS['artist']][0]
        except IndexError:
            return ''
        return artist_frame

    def _get_values(self, mutagen_file, values, get_encodings):
        if not mutagen_file:
            return {}
        if not mutagen_file.tags:
            mutagen_file.add_tags()

        result_values = {}
        for value in values:
            if value in self.R_MP4_MAPPINGS:
                tag = self.R_MP4_MAPPINGS[value]
                try:
                    result = mutagen_file.tags[tag]
                    result_values[value] = result
                except(KeyError, IndexError):
                    result_values[value] = []
        return result_values

    def _get_images(self, mutagen_file):
        if not mutagen_file:
            return {}
        if not mutagen_file.tags:
            mutagen_file.add_tags()

        result_images = {}
        try:
            images = mutagen_file[self.R_MP4_MAPPINGS['front_cover']]
        except KeyError:
            return {}

        for image in images:
            current_image = Image(data=image,
                                  image_type=image.imageformat)
            result_images['front_cover'] = current_image
        return result_images

    def _set_image(self, image, image_type):
        pass

    def set_tag(self, key, value):
        if not isinstance(value, list):
            value = [value]
        try:
            key_tag = self.R_MP4_MAPPINGS[key]
            self._mutagen_file.tags[key_tag] = value
        except KeyError:
            # key_tag = key
            return None  # FOR NOW

    def streamInfo(self):
        info = super(MP4MediaFile, self).streamInfo()
        if (hasattr(self._mutagen_file.info, 'codec') and
                self._mutagen_file.info.codec):
            info['codec'] = self._mutagen_file.info.codec
        if (hasattr(self._mutagen_file.info, 'codec_description') and
                self._mutagen_file.info.codec_description):
            info['codec_description'] = self._mutagen_file.info.codec_description
        return info

    def save(self, filething=None, padding=None):
        if not filething:
            filething = self._filepath
        self._mutagen_file.save(filething, padding)
