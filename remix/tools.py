import shutil
import tempfile
from scipy.io import wavfile
import librosa

import pydub
import validators
import os

import wget as wget
import youtube_dl
from PIL import Image

import remix.bpm
import remix.onset
from remix.audio import *


class Tools:
    """A static library holding different tools to process audios."""

    @staticmethod
    def split_audio(audiofile: AudioFile, output_path=None, output_stem_num=2):
        """
        This function splits an original audio into stems
        :param audiofile: the original audiofile
        :param output_path: the path where the stems are located after separation
        :param output_stem_num: the number of channels to split the audio into
        :return: a list of stems
        """
        if output_stem_num != 2 and output_stem_num != 4 and output_stem_num != 5:
            print("The audio can only be split into 2, 4 or 5 channels")
            return None
        title, ext = os.path.splitext(os.path.basename(audiofile.get_path()))
        if output_path is None:
            output_path = os.path.dirname(audiofile.get_path())
        cmd = "spleeter separate -o " + output_path + " -p spleeter:" + str(
            output_stem_num) + "stems " + '"' + audiofile.get_path() + '"'
        curr_dir = os.getcwd()
        os.chdir(output_path)  # change current directory to given path
        os.system(cmd)
        orig = Original(audiofile.get_path())
        audio_lst = []
        path = os.path.join(output_path, title)
        if not os.path.exists(path):
            raise Exception("Split Failed. Check your connection and retry")
        for audiofile in os.listdir(path):  # audiofile = "vocals.wav", accompaniment.wav
            split = audiofile.split('.')
            audio_title = title + " " + split[0]
            audio1 = Stem(os.path.join(path, audiofile), title=audio_title, original=orig)
            audio_lst.append(audio1)
        os.chdir(curr_dir)
        return audio_lst

    @staticmethod
    def download_from_youtube(url, working_dir):
        """
        This function downloads a video from YouTube
        :param url: link to a video from YouTube
        :return: if url is valid (title, path to downloaded file, path to thumbnail), otherwise None
        """
        if not Tools.check_url(url):
            return None
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': working_dir + '/%(title)s.%(ext)s',  # output name template

            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.cache.remove()
                ydl.download([url])
                info = ydl.extract_info(url, download=False)
                # https://stackoverflow.com/questions/23727943/how-to-get-information-from-youtube-dl-in-python
                url_title = info.get("title", None)
                url_path = working_dir + "/" + url_title + ".mp3"  # according to template
                url_thumbnail = info.get("thumbnail", None)
            return url_path, url_title, url_thumbnail
        except Exception:
            return -1

    @staticmethod
    def check_url(url):
        """
        A method to check a url validity
        :param url: the url to check
        :return: True if the url is valid, otherwise False

        >>> Tools.check_url("https://www.google.com")
        True
        >>> Tools.check_url("C:\PATH\TO\FILE")
        False
        """
        return validators.url(url) is True

    @staticmethod
    def overlay_audio(audio_list, output_path='') -> AudioFile:
        """
        A method to overlay audio files
        :param audio_list: a list of AudioFiles objects
        :param output_path: the output path
        :return: the overlaid audio
        """
        sound = audio_list[0].get_track()
        for audio in range(1, len(audio_list)):
            sound1 = audio_list[audio].get_track()
            sound2 = sound.overlay(sound1)
            sound = sound2
        if output_path == '':
            output_path = audio_list[0].get_path() + " overlay.mp3"
        sound.export(output_path, format="mp3")
        combined = Remix(output_path, audio_list[0], title=audio_list[0].get_title() + "_overlay")
        return combined

    @staticmethod
    def audio_trim(audiofile: AudioFile, output_path, start_min, start_sec, end_min=None, end_sec=None) -> (
            AudioFile, str):
        """
        A method to keep the audio slice between start and end
        :param audiofile: an AudioFile object
        :param output_path: the output path
        :param start_min: the minute at which the slicing starts
        :param start_sec: the second at which the slicing starts
        :param end_min: the minute at which the slicing ends
        :param end_sec: the second at which the slicing ends
        :return: The Remix slice and output_path
        """
        if start_min == end_min and start_sec == end_sec:
            return audiofile, output_path
        audio_mins, audio_secs = audiofile.get_duration()
        if start_min == 0 and start_sec == 0:
            start_sec += 0.001
        if end_min == audio_mins and end_sec >= audio_secs:
            end_sec = audio_secs - 0.001
        elif end_min is None and end_sec is None:
            end_min = audio_mins
            end_sec = audio_secs - 0.001
        elif (end_min is None and end_sec is not None) or (end_min is not None and end_sec is None):
            raise Exception("Usage: audio trim end_min, end_sec values must be both None or both not None")

        start_time = start_min * 60 * 1000 + start_sec * 1000  # from seconds to milliseconds
        end_time = end_min * 60 * 1000 + end_sec * 1000
        sound = audiofile.get_track()

        if not output_path:
            output_path = audiofile.get_path() + " trim.mp3"

        extract = sound[start_time:end_time]  # <pydub.audio_segment.AudioSegment object
        extract.export(output_path, format="mp3")
        extract = Remix(output_path, audiofile, title=audiofile.get_title() + "_trim")
        return extract, output_path

    @staticmethod
    def concatenate_audio(audio_list, output_path="") -> AudioFile:
        """
        A method to concatenate two or more audio files into one audio file
        and save it to `output_path`.
        :param audio_list: a list of AudioFile objects
        :param output_path: the output path
        :return: a Remix object consisting in the concatenation of all audio_clip_list files
        """
        clips = []
        name = ""
        for clip in audio_list:
            if clip is not None:
                clips.append(clip.get_track())
                name += clip.get_title()
                name += "-"

        if clips:
            final_clip = clips[0]
            j = 1
            while final_clip is None:
                final_clip = clips[j]
                j += 1
            for i in range(j, len(clips)):
                # looping on all audio files and concatenating them together, ofc order is important
                if clips[i] is not None:
                    final_clip = final_clip + clips[i]

            if output_path == "":
                output_path = audio_list[0].get_path() + name + " concat.mp3"
            final_clip.export(output_path, format='mp3')
            final_clip = Remix(output_path, audio_list[0], title=name + "_concat")
            return final_clip

    @staticmethod
    def audio_cut(audiofile: AudioFile, cut_min, cut_sec, outpath) -> (AudioFile, AudioFile):
        """
        A method to time split an audio file
        :param audiofile: an AudioFile object
        :param cut_min: the minute at which the split occurs
        :param cut_sec: the second at which the split occurs
        :param outpath: the output path
        :return: two Remix objects
        """
        if not outpath:
            outpath = audiofile.get_path()
        new_path1 = outpath + "_timesplit1.mp3"
        audio1, first_path = Tools.audio_trim(audiofile, new_path1, 0, 0, cut_min, cut_sec)
        audio1.set_title(audiofile.get_title() + "_timesplit1")

        new_path2 = outpath + "_timesplit2.mp3"
        audio2, second_path = Tools.audio_trim(audiofile, new_path2, cut_min, cut_sec,
                                               audiofile.get_duration()[0],
                                               audiofile.get_duration()[1])
        audio2.set_title(audiofile.get_title() + "_timesplit2")

        return audio1, audio2

    @staticmethod
    def audio_delete(audiofile: AudioFile, start_min, start_sec, end_min=None, end_sec=None, output_path=''):
        """
        This method cuts off the audio slice between start and end.
        :param audiofile: an AudioFile object
        :param start_min: the minute at which the cut starts
        :param start_sec: the second at which the cut starts
        :param end_min: the minute at which the cut ends
        :param end_sec: the second at which the cut ends
        :param output_path: the output path
        :return: a Remix object which track has a section cut off
        """
        if end_min is None and end_sec is not None:
            raise Exception("Usage: the end min and sec values must be both None or both not None")
        elif end_min is None and end_sec is None:
            end_min = audiofile.get_duration()[0]
            end_sec = audiofile.get_duration()[1]
        elif end_min:
            if start_min > end_min or (start_min == end_min and start_sec > end_sec):
                raise Exception("Usage: the start must indicate a time previous to the end")
        new_path1 = audiofile.get_path() + " delete1.mp3"
        if start_min == 0 and start_sec == 0:
            audio1 = None
        else:
            audio1, first_path = Tools.audio_trim(audiofile, new_path1, 0, 0, start_min, start_sec)
            audio1.set_title(audiofile.get_title() + "_delete1")

        new_path2 = audiofile.get_path() + " delete2.mp3"
        if end_min == audiofile.get_duration()[0] and end_sec >= audiofile.get_duration()[1]:
            audio2 = None
        else:
            audio2, second_path = Tools.audio_trim(audiofile, new_path2, end_min, end_sec,
                                                   audiofile.get_duration()[0],
                                                   audiofile.get_duration()[1])
            audio2.set_title(audiofile.get_title() + "_delete2")

        if output_path == '':
            output_path = audiofile.get_path() + " delete.mp3"
        return Tools.concatenate_audio([audio1, audio2], output_path)

    @staticmethod
    def fade(audiofile: AudioFile, start_fading_secs=3, end_fading_secs=3, output_path=None) -> AudioFile:
        """
        A method to fade in an audio file
        :param audiofile: an AudioFile object
        :param start_fading_secs: the fading in last
        :param end_fading_secs: the fading out last
        :param output_path: the output path
        :return: a Remix object that results from the input audiofile fading
        """
        sound = audiofile.get_track()
        start_fading = start_fading_secs * 1000
        end_fading = end_fading_secs * 1000
        mp3 = sound.fade_in(start_fading).fade_out(end_fading)
        if output_path == '':
            output_path = audiofile.get_path() + " fade.mp3"
        mp3.export(output_path, format='mp3')
        mp3 = Remix(output_path, audiofile, title=audiofile.get_title() + "_fade")
        return mp3

    @staticmethod
    def fadein(audiofile: AudioFile, fading_secs=3, output_path='') -> AudioFile:
        """
        A method to fade in an audio file
        :param audiofile: an AudioFile object
        :param fading_secs: the fading last
        :param output_path: the output path
        :return: a Remix object that results from the input audiofile fading
        """
        sound = audiofile.get_track()
        start_fading = fading_secs * 1000
        mp3 = sound.fade_in(start_fading)
        if output_path == '':
            output_path = audiofile.get_path() + " fadein.mp3"

        mp3.export(output_path, format='mp3')
        mp3 = Remix(output_path, audiofile, title=audiofile.get_title() + "_fadein")
        return mp3

    @staticmethod
    def fadeout(audiofile: AudioFile, fading_secs=3, output_path='') -> AudioFile:
        """
        A method to fade out an audio file
        :param audiofile: an AudioFile object
        :param fading_secs: the fading last
        :param output_path: the output path
        :return: a Remix object that results from the input audiofile fading
        """
        sound = audiofile.get_track()
        end_fading = fading_secs * 1000
        mp3 = sound.fade_out(end_fading)
        if output_path == '':
            output_path = audiofile.get_path() + " fadeout.mp3"

        mp3.export(output_path, format='mp3')
        mp3 = Remix(output_path, audiofile, title=audiofile.get_title() + "_fadeout")
        return mp3

    @staticmethod
    def transform_audio_position(audiofile: AudioFile, transform_secs, output_path='') -> AudioFile:
        """
        A method to transform an audio position
        :param audiofile: an AudioFile object
        :param transform_secs: the seconds to add to the audio start
        :param output_path: the output path
        :return: a Remix object that starts transform_secs after the input AudioFile
        """
        sound = audiofile.get_track()
        silence = AudioSegment.silent(transform_secs * 1000)
        end = (audiofile.get_duration()[0] * 60 + audiofile.get_duration()[1]) * 1000
        res = silence + sound[:end]
        if output_path == '':
            output_path = audiofile.get_path() + " pos_transform.mp3"

        res.export(output_path, format='mp3')
        res = Remix(output_path, audiofile, title=audiofile.get_title() + "_pos_transform")
        return res

    @staticmethod
    def export(audiofile: AudioFile, output_path, format):
        """
        A method to export an audio file
        :param audiofile: an AudioFile object
        :param output_path: the output path
        :param format: the format of the output audio file
        :return: None
        """
        if format not in ["mp3", "mp4", "wav", "m4a"]:
            raise Exception("Wrong format")
        if not os.path.exists(output_path) or not os.path.isdir(output_path):
            raise Exception("Path does not exist")
        outpath = output_path + "/" + audiofile.get_title() + "." + format
        sound = audiofile.get_track()
        sound.export(outpath, format=format)

    @staticmethod
    def duplicate(audiofile):
        """
        A method to duplicate an AudioFile object
        :param audiofile: the AudioFile to duplicate
        :return: the duplicate object
        """
        title = audiofile.get_title() + " duplicate"
        dir_path = os.path.dirname(audiofile.get_path())
        path = dir_path + '/' + title + audiofile.get_extension()
        thumb_path = audiofile.get_thumb_path()

        shutil.copyfile(audiofile.get_path(), path)
        if audiofile.get_type() == AudioFileType.Audiofile:
            dup = AudioFile(path, title, thumb_path)

        elif audiofile.get_type() == AudioFileType.Original:
            dup = Original(path, title, thumb_path)
            dup.set_stems(audiofile.get_stems_dict())

        elif audiofile.get_type() == AudioFileType.Stem:
            dup = Stem(path, title=title, original=audiofile.get_original(), thumb_path=thumb_path)
            dup.set_description(audiofile.get_description())

        elif audiofile.get_type() == AudioFileType.Remix:
            dup = Remix(path, audiofile.get_original(), title, thumb_path)
            dup.set_stems(audiofile.get_stems_dict())

        else:
            raise Exception("Input file is not instance of AudioFile or inheriting classes")

        dup.set_track(audiofile.get_track())
        dup.set_duration(audiofile.get_duration())
        dup.set_bpm(audiofile.get_bpm())
        return dup

    @staticmethod
    def rename(audiofile: AudioFile, name: str):
        """
        A method to rename an audio file
        :param audiofile: the AudioFile object to rename
        :param name: the name to assign
        :return:
        """
        audiofile.set_title(name)

    @staticmethod
    def bpm_detector(audio_seg: AudioSegment, window=10):
        """
        A method to edtect an audio bpm
        :param audio_seg: an AudioSegment object
        :param window: /
        :return: the median bpm of the audio
        """
        workdir = tempfile.TemporaryDirectory()
        temp_file_path = workdir.name + "/temp.wav"
        f = audio_seg.export(temp_file_path, format="wav")
        bpm = remix.bpm.bpm_detector(temp_file_path)
        f.close()
        workdir.cleanup()
        return bpm[0]

    @staticmethod
    def onset(audio_seg: AudioSegment):
        """
        A method to detect an audio onsets times
        :param audio_seg: an AudioSegment object
        :return: the onset times detected
        """
        workdir = tempfile.TemporaryDirectory()
        temp_file_path = workdir.name + "/temp.wav"
        f = audio_seg.export(temp_file_path, format="wav")
        onset_times = remix.onset.get_onset_times(temp_file_path)
        f.close()
        workdir.cleanup()
        return onset_times

    @staticmethod
    def speed_change(audiosegment: AudioSegment, output_path, speed=1.0) -> AudioSegment:
        """
        A method to change the speed of an audio file
        :param audiosegment: an AudioSegment object
        :param output_path: the output path
        :param speed: the ratio of the speed to apply
        :return: an AudioSegment with the speed changed by the given ratio
        """
        tmp = tempfile.TemporaryDirectory()
        audiosegment.export(tmp.name + "/wav_temp_file.wav", format='wav')
        sound, fs = librosa.load(tmp.name + "/wav_temp_file.wav")
        new_wav = librosa.effects.time_stretch(sound, rate=speed)
        wavfile.write(tmp.name + "/speed_wav_temp_file.wav", fs, new_wav)
        new_new = AudioSegment.from_wav(tmp.name + "/speed_wav_temp_file.wav")
        new_new.export(output_path, format="mp3")
        tmp.cleanup()
        return new_new

    @staticmethod
    def download_image(url: str, output_path: str) -> str:
        """
        A method to download an image
        :param url: a url
        :param output_path: the output path
        :return: output_path
        """
        output_path = output_path + "/" + url.split("/")[-1]
        wget.download(url, out=output_path)
        return output_path

    @staticmethod
    def resize_image(image_path: str, output_path: str, width: int, height: int):
        """
        A method to resize an image
        :param image_path: the path to the image to resize
        :param output_path: the path to save the resized image
        :param width: the width of the output
        :param height: the heught of the output
        :return: None
        """
        img = Image.open(image_path)
        img = img.resize((width, height), Image.ANTIALIAS)
        img.save(output_path)
