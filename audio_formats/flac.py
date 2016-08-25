import mutagen.flac
from .base import MediaFile, StreamInfoMixin, Image, ImageType


class VorbisComment(MediaFile):

    VORBIS_MAPPINGS = {'ARTIST': 'artist',
                       'TITLE': 'title',
                       'TRACKNUMBER': 'track_number',
                       'DISCNUMBER': 'disc_number',
                       'TOTALTRACKS': 'total_tracks',
                       'TOTALDISCS': 'total_discs',
                       'ALBUM': 'album',
                       'DATE': 'date',
                       'ALBUMARTIST': 'albumartist',
                       'ORGANIZATION': 'organization',
                       'VERSION': 'version',
                       'COPYRIGHT': 'copyright',
                       'LICENSE': 'license',
                       'DESCRIPTION': 'description',
                       'GENRE': 'genre',
                       'COMPOSER': 'composer',
                       'COMMENT': 'comment'
                       }

    R_VORBIS_MAPPINGS = {v: k for k, v in VORBIS_MAPPINGS.items()}

    def __init__(self, filepath):
        super(VorbisComment, self).__init__(filepath)
        if not self._mutagen_file.tags:
            self._mutagen_file.add_tags()

    def _get_title(self, mutagen_file):
        try:
            text_frame = mutagen_file.tags[self.R_VORBIS_MAPPINGS['title']][0]
        except IndexError:
            return ''
        return text_frame

    def _get_album(self, mutagen_file):
        try:
            album_frame = mutagen_file.tags[self.R_VORBIS_MAPPINGS['album']][0]
        except IndexError:
            return ''
        return album_frame

    def _get_artist(self, mutagen_file):
        try:
            artist_frame = mutagen_file.tags[
                self.R_VORBIS_MAPPINGS['artist']][0]
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
            if value in self.R_VORBIS_MAPPINGS:
                tag = self.R_VORBIS_MAPPINGS[value]
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
        images = mutagen_file.pictures
        for image in images:
            current_image = Image(data=image.data,
                                  desc=image.desc,
                                  image_type=image.type,
                                  mime_type=image.mime)
            key = ImageType.to_str(current_image.image_type)
            result_images[key] = current_image
        return result_images

    def set_tag(self, key, value):
        try:
            key_tag = self.R_VORBIS_MAPPINGS[key]
        except KeyError:
            # key_tag = key
            return False  # FOR NOW

        d = {key_tag: value}
        self._mutagen_file.tags.update(d)
        return True

    def _set_image(self, image, image_type):
        pass    # add_picture(picture

    def save(self, filething=None, deleteid3=False, padding=None):
        if not filething:
            filething = self._filepath
        self._mutagen_file.save(filething, deleteid3, padding)


class FLACMediaFile(VorbisComment, StreamInfoMixin):
    SUPPORTED_FORMATS = ['FLAC']

    def __init__(self, filepath):
        super(FLACMediaFile, self).__init__(filepath)

    def _read_file(self, filename):
        return mutagen.flac.FLAC(filename)

    def streamInfo(self):
        info = super(VorbisComment, self).streamInfo()
        if (hasattr(self._mutagen_file.info, 'min_blocksize') and
                self._mutagen_file.info.min_blocksize):
            info['min_blocksize'] = int(self._mutagen_file.info.min_blocksize)
        if (hasattr(self._mutagen_file.info, 'max_blocksize') and
                self._mutagen_file.info.max_blocksize):
            info['max_blocksize'] = self._mutagen_file.info.max_blocksize
        if (hasattr(self._mutagen_file.info, 'total_samples') and
                self._mutagen_file.info.total_samples):
            info['total_samples'] = int(self._mutagen_file.info.total_samples)
        return info
