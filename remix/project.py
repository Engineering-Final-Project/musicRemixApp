import os
from pathlib import Path
import tempfile
from shutil import copytree, rmtree, copy2
from remix.tools import Tools
from remix.audio import *


class Project:
    """a class representing a project"""

    def __init__(self, name="Untitled"):
        self._name = name
        self._originals = dict()  # {path, Original obj}
        self._current_mix = list()  # list of stems and remix audiofiles
        self._final_mix = None  # an AudioSegment object
        self._working_dir = tempfile.TemporaryDirectory()
        self._project_path = self._working_dir.name
        self._bpm = 110
        self._time_signature = {'bar': 4, 'beat_unit': 4}  # bar / beat unit. eg 3/4, bar=3 beat_unit=4
        self._num_of_bars = 0

    def __len__(self):
        beat_duration = 60 / self._bpm
        bar_duration = beat_duration * self._time_signature.get('bar')
        return bar_duration * self._num_of_bars  # in seconds

    def __str__(self):
        return self._name

    def __repr__(self):
        return self._name

    def get_path(self):
        """returns the path of the project"""
        return self._project_path

    def get_originals(self):
        """returns a list of all originals in the project"""
        return [self._originals[key] for key in self._originals]

    def get_current_mix(self):
        """returns the current mix"""
        return self._current_mix

    def set_current_mix(self, mix_name):
        """sets the current mix"""
        self._current_mix = mix_name

    def get_final_mix(self):
        return self._final_mix

    def set_name(self, name):
        """sets the name of the project"""
        self._name = name

    def get_name(self):
        """returns the name of the project"""
        return self._name

    def get_working_dir(self):
        return self._working_dir

    def set_bpm(self, bpm):
        self._bpm = bpm

    def get_bpm(self):
        return self._bpm

    def set_time_signature(self, bar, beat_unit):
        self._time_signature['bar'] = bar
        self._time_signature['beat_unit'] = beat_unit

    def get_time_signature(self):
        return self._time_signature.get('bar'), self._time_signature.get('beat_unit')

    def set_num_of_bars(self, num):
        self._num_of_bars = num

    def get_num_of_bars(self):
        return self._num_of_bars

    def get_audio_files(self):
        audio_files = list()
        for original in self.get_originals():
            audio_files.append(original)
            audio_files += original.get_stems()
        return audio_files

    def add_original(self, path: str) -> Original:
        """adds an original's path to the project"""
        # get audio
        if os.path.exists(path):
            title, ext = os.path.splitext(os.path.basename(path))
            self._originals[path] = Original(path, title=title)
            return self._originals[path]
        else:
            path, title, thumbnail = Tools.download_from_youtube(path, self._working_dir.name)
            # download image from url
            if path is not None:
                thumbnail = Tools.download_image(thumbnail, self._working_dir.name)
                Tools.resize_image(thumbnail, thumbnail, width=180, height=180)
                self._originals[path] = Original(path, title, thumbnail)
                return self._originals[path]
            else:
                raise Exception("Could not download audio")  # the exception will be caught in the main window

    def save(self):
        """saves the project to disk"""
        if self._project_path == self._working_dir.name:
            self._project_path = str(Path.home()) + '/' + self._name
            if os.path.exists(self._project_path):
                raise Exception("The default path " + self._project_path + " already exists, please provide a new path "
                                                                           "with Save As option")
            os.mkdir(self._project_path)
        self.save_as(self._project_path)

    def save_as(self, path):
        """saves the project to disk"""
        if not path:
            raise Exception("Invalid Path")
        if self._project_path == self._working_dir.name:
            self._project_path = path
        if path == self._project_path:
            if not os.path.exists(path):
                os.mkdir(path)
            rmtree(path)
            copytree(self._working_dir.name, path)
            for orig in self._originals:
                copy2(orig, path)
            for audio in self._current_mix:
                copy2(audio.get_path(), path)
        elif os.path.exists(path):
            raise Exception("The given path " + path + " already exists, please provide a new path")
        else:
            # self._project_path = path
            copytree(self._working_dir.name, path)

    def copy_pretrained_models(self):
        pretrain_dir = self._working_dir.name + "/pretrained_models"
        if not os.path.exists(pretrain_dir):
            os.mkdir(pretrain_dir)
            path = "/home/miriams/PycharmProjects/remixProject/remix/pretrained_models"
            for folder in os.listdir(path):
                stem_dir = os.path.join(path, folder)
                stem_new_dir = os.path.join(pretrain_dir, folder)
                os.mkdir(stem_new_dir)
                for file in os.listdir(stem_dir):
                    s = os.path.join(stem_dir, file)
                    d = os.path.join(stem_new_dir, file)
                    copy2(s, d)

    def split(self, audiofile: Original, stems):
        """splits the audiofile"""
        # self.copy_pretrained_models()
        audios = Tools.split_audio(audiofile, self._working_dir.name, output_stem_num=stems)  # a list of stem audiofiles
        if audios is None:
            raise Exception("Split Failed (retval is None)")
        self._current_mix += audios
        for stem in audios:
            audiofile.add_stem(stem)
        return audios

    def calculate_bpm(self, lst, name):
        bpm_sum = 0
        af_lst = []
        for af in lst:
            if af.get_type() == AudioFileType.Original or af.get_type() == AudioFileType.Audiofile:
                af_lst.append(af)
                bpm = Tools.bpm_detector(af.get_track())
                bpm_sum += bpm
                af.set_bpm(bpm)
            elif af.get_type() == AudioFileType.Stem or af.get_type() == AudioFileType.Remix:
                if af.get_original() not in af_lst:
                    af_lst.append(af)
                    bpm = Tools.bpm_detector(af.get_track())
                    bpm_sum += bpm
                    af.set_bpm(bpm)
                else:
                    af.set_bpm(af.get_original().get_bpm())
        self._bpm = bpm_sum / len(af_lst)
        for af in lst:
            af.set_track(Tools.speed_change(af.get_track(), self._working_dir.name + "/" + name, speed=self._bpm / af.get_bpm()))
            af.set_bpm(Tools.bpm_detector(af.get_track()))

    def merge(self, lst, change_bpm=False):
        """export the mix into an audio file"""
        if not lst:
            raise Exception("Select audios to overlay")

        name = ""
        for a in lst:
            name += a.get_title()
            name += " "
        if change_bpm:
            self.calculate_bpm(lst, name)
        merged = Tools.overlay_audio(lst, self._working_dir.name + "/" + name + "merged.mp3")
        if merged is None:
            raise Exception("Audio Merging Failed (retval is None)")
        self._current_mix.append(merged)
        return merged

    def trim(self, af: AudioFile, start_min, start_sec, end_min=None, end_sec=None):
        if not af:
            raise Exception("The selected file does not exist")
        outpath = self._working_dir.name + "/" + af.get_title() + "_trim.mp3"
        trimmed = Tools.audio_trim(af, outpath, start_min, start_sec, end_min, end_sec)[0]
        if trimmed is None:
            raise Exception("Audio Trim Failed (retval is None)")
        self._current_mix.append(trimmed)
        return trimmed

    def concat(self, lst):
        if not lst:
            raise Exception("Select audios to concatenate")
        outpath = self._working_dir.name + "/" + lst[0].get_title() + "_concat.mp3"
        concat = Tools.concatenate_audio(lst, outpath)
        if concat is None:
            raise Exception("Audio Concationation Failed (retval is None)")
        self._current_mix.append(concat)
        return concat

    def cut(self, af: AudioFile, cut_min, cut_sec):
        if not af:
            raise Exception("The selected file does not exist")
        outpath = self._working_dir.name + "/" + af.get_title()
        cut1, cut2 = Tools.audio_cut(af, cut_min, cut_sec, outpath)
        if cut1 is None and cut2 is None:
            raise Exception("Cut Audio Failed (retval is None)")
        elif cut1 is None:
            self._current_mix.append(cut2)
            return cut2
        elif cut2 is None:
            self._current_mix.append(cut1)
            return cut1
        else:
            self._current_mix.append(cut1)
            self._current_mix.append(cut2)
            return cut1, cut2

    def delete(self, af: AudioFile, start_min, start_sec, end_min=None, end_sec=None):
        if not af:
            raise Exception("The selected file does not exist")
        outpath = self._working_dir.name + "/" + af.get_title() + "_delete.mp3"
        deleted = Tools.audio_delete(af, start_min, start_sec, end_min, end_sec, outpath)
        if deleted is None:
            raise Exception("Delete Audio Section Failed (retval is None)")
        self._current_mix.append(deleted)
        return deleted

    def fade(self, af: AudioFile, start=3, end=3):
        if not af:
            raise Exception("The selected file does not exist")
        outpath = self._working_dir.name + "/" + af.get_title() + "_fade.mp3"
        faded = Tools.fade(af, start, end, outpath)
        if faded is None:
            raise Exception("Fade Failed (retval is None)")
        self._current_mix.append(faded)
        return faded

    def fadein(self, af: AudioFile, start=3):
        if not af:
            raise Exception("The selected file does not exist")
        outpath = self._working_dir.name + "/" + af.get_title() + "_fadein.mp3"
        faded = Tools.fadein(af, start, outpath)
        if faded is None:
            raise Exception("Fade In Failed (retval is None)")
        self._current_mix.append(faded)
        return faded

    def fadeout(self, af: AudioFile, end=3):
        if not af:
            raise Exception("The selected file does not exist")
        outpath = self._working_dir.name + "/" + af.get_title() + "_fadeout.mp3"
        faded = Tools.fadeout(af, end, outpath)
        if faded is None:
            raise Exception("Fade Out Failed (retval is None)")
        self._current_mix.append(faded)
        return faded

    def change_position(self, af: AudioFile, mins, secs):
        transform_secs = mins * 60 + secs
        if not af:
            raise Exception("The selected file does not exist")
        outpath = self._working_dir.name + "/" + af.get_title() + "_pos_transform.mp3"
        moved = Tools.transform_audio_position(af, transform_secs, outpath)
        if moved is None:
            raise Exception("Position Transform Failed (retval is None)")
        self._current_mix.append(moved)
        return moved

    def duplicate(self, af):
        if not af:
            raise Exception("The selected file does not exist")
        dup = Tools.duplicate(af)
        if dup is None:
            raise Exception("Duplication Failed (retval is None)")
        self._current_mix.append(dup)
        return dup

    def remove_audio_from_project(self, af: AudioFile):
        if af.get_type() == AudioFileType.Original:
            self._originals.pop(af.get_path(), "")
        else:
            if af in self._current_mix:
                self._current_mix.remove(af)

    def change_speed(self, af: AudioFile, speed):
        if not af:
            raise Exception("The selected file does not exist")
        outpath = self._working_dir.name + "/" + af.get_title() + "_speed" + str(speed) + "x.mp3"
        speeded = Tools.speed_change(af.get_track(), outpath, speed)
        if speeded is None:
            raise Exception("Speed Change Failed (retval is None)")
        af2 = Remix(outpath, af, title=af.get_title() + "_" + str(speed) + "x")
        self._current_mix.append(af2)
        return af2


if __name__ == "__main__":
    pr = Project("try")
    pr.copy_pretrained_models()
    pr.save_as("/home/miriams/copytry")
