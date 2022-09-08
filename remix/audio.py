import enum
import os
from pydub import AudioSegment


class AudioFileType(enum.Enum):
    """
    An Enum class to list the audio file types
    """
    Audiofile = 0
    Original = 1
    Stem = 2
    Remix = 3


class AudioFile:
    """
    A class that describes audio files
    """
    def __init__(self, path, title=None, thumb_path=None):
        """
        A constructor that receives a local path and creates an Audiofile object
        :param path: a local path
        :param title: the title of the video
        :param thumb_path: the path to thumbnail
        """
        self._path = path  # includes title and extension of the audiofile
        if not os.path.exists(path):  # the path is not valid
            raise ValueError("Invalid path")
        self._track = AudioSegment.from_file(path)
        track_mins = (len(self._track) / 1000.0) // 60
        track_secs = (len(self._track) / 1000.0) - track_mins * 60
        self._duration = (track_mins, track_secs)
        self._bpm = None

        self._title, self._ext = os.path.splitext(os.path.basename(path))
        if title is not None:
            self._title = title
        self._thumb_path = thumb_path

        self.stack = []
        self.queue = []

    def __str__(self):
        """
        A string representation of the class
        :return: None
        """
        return self._path

    def get_duration(self):
        """
        A getter for the audio file duration
        :return: the audio file duration
        """
        return self._duration

    def get_type(self):
        """
        A getter for the audio file type
        :return: the audio file type
        """
        return AudioFileType.Audiofile

    def get_title(self):
        """
        A getter for the audio file title
        :return: the audio file title
        """
        return self._title

    def get_path(self):
        """
        A getter for the audio file path
        :return: the audio file path
        """
        return self._path

    def get_thumb_path(self):
        """
        A getter for the audio file thumbnail path
        :return: the audio file thumbnail path
        """
        return self._thumb_path

    def get_extension(self):
        """
        A getter for the audio file extension
        :return: the audio file extension
        """
        return self._ext  # Might be null, to check

    def get_track(self):
        """
        A getter for the audio file track
        :return: the audio file track
        """
        return self._track

    def set_track(self, track):
        """
        A setter for the audio file track
        :return: None
        """
        self._track = track

    def get_stack(self):
        """
        A getter for the audio file stack
        :return: the audio file stack
        """
        return self.stack

    def get_queue(self):
        """
        A getter for the audio file queue
        :return: the audio file queue
        """
        return self.queue

    def set_title(self, title):
        """
        A setter for the audio file title
        :return: None
        """
        self._title = title

    def set_duration(self, duration):
        """
        A setter for the audio file duration
        :return: None
        """
        self._duration = duration

    def get_bpm(self):
        """
        A getter for the audio file bpm
        :return: the audio file bpm
        """
        return self._bpm

    def set_bpm(self, bpm):
        """
        A setter for the audio file bpm
        :return: None
        """
        self._bpm = bpm

    def save(self, save_path=None):
        """
        A method to save the audio file
        :param save_path: the path for the audio file
        :return: None
        """
        if not save_path:
            save_path = self._path
        self._track.export(save_path, bitrate="320k", format="mp3")

    def reverse(self):
        """
        A method to reverse the audio file
        :return: None
        """
        self.stack.append(self._track)
        self._track = self._track.reverse()

    def undo(self):
        """
        A method to undo the last action on the audio file
        :return: None
        """
        self.queue.insert(0, self._track)
        self._track = self.stack.pop()

    def redo(self):
        """
        A method to redo the last undone action on the audio file
        :return: None
        """
        self.stack.append(self._track)
        self._track = self.queue[0]
        self.queue.pop(0)


class Original(AudioFile):
    """
    A class that describes an original track (inheriting from AudioFile)
    """
    def __init__(self, path, title=None, thumb_path=None):
        """
        The init method of the class
        :param path: a local path
        :param title: the title of the track
        :param thumb_path: the path to the track thumbnail
        """
        super().__init__(path, title, thumb_path)
        self._stems = dict()

    def add_stem(self, stem):
        """
        A method to add a stem to the stem dictionary
        :param stem: the stem to add
        :return: None
        """
        self._stems[stem.get_title()] = stem

    def get_stems_dict(self):
        """
        A getter to the stem dictionary
        :return: the stem dictionary
        """
        return self._stems

    def get_stems(self):
        """
        A getter to the original stems
        :return: a list of stems
        """
        return list(self._stems[key] for key in self._stems)

    def set_stems(self, stems):
        """
        A setter for the stem dictionary
        :param stems: the dict to set
        :return: None
        """
        self._stems = stems

    def get_stem(self, stem_title):
        """
        A method to get a stem by its title
        :param stem_title: the stem title
        :return: None
        """
        return self._stems.get(stem_title, None)

    def get_type(self):
        """
        A getter for the original type
        :return: the original type
        """
        return AudioFileType.Original


class Stem(AudioFile):
    """
    A class that describes a stem (inheriting from AudioFile)
    """
    def __init__(self,  path,  title, original, thumb_path=None, description=None):
        super().__init__(path, title, thumb_path)
        self._original = original
        self._description = description  # instrument

    def get_type(self):
        """
        A getter for the stem type
        :return: the stem type
        """
        return AudioFileType.Stem

    def get_original(self):
        """
        A getter for the stem original
        :return: the stem original
        """
        return self._original

    def set_original(self, orig):
        """
        A setter for the stem original
        :param orig: the original to set
        :return: None
        """
        self._original = orig

    def get_description(self):
        """
        A getter for the stem description
        :return: the stem description
        """
        return self._description

    def set_description(self, description):
        """
        A setter for the stem description
        :param description: the description to set
        :return: None
        """
        self._description = description


class Remix(AudioFile):
    """
    A class that describes a remix (inheriting from AudioFile)
    """
    def __init__(self, path, original, title=None, thumb_path=None):
        super().__init__(path, title, thumb_path)
        self._original = original
        self._stems = dict()

    def add_stem(self, stem):
        """
        A method to add a stem to the stem dictionary
        :param stem: the stem to add
        :return: None
        """
        self._stems[stem.get_title()] = stem

    def get_stems_dict(self):
        """
        A getter to the stem dictionary
        :return: the stem dictionary
        """
        return self._stems

    def get_stems(self):
        """
        A getter to the remix stems
        :return: a list of stems
        """
        return list(self._stems[key] for key in self._stems)

    def set_stems(self, stems):
        """
        A setter for the stem dictionary
        :param stems: the dict to set
        :return: None
        """
        self._stems = stems

    def get_stem(self, stem_title):
        """
        A method to get a stem by its title
        :param stem_title: the stem title
        :return: None
        """
        return self._stems.get(stem_title, None)

    def get_type(self):
        """
        A getter for the remix type
        :return: the remix type
        """
        return AudioFileType.Remix

    def get_original(self):
        """
        A getter for the remix original
        :return: the remix original
        """
        return self._original

    def set_original(self, orig):
        """
        A setter for the remix original
        :param orig: the original to set
        :return: None
        """
        self._original = orig
