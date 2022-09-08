from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QUrl, pyqtSlot
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.uic import loadUi

from remix.audio import *
import datetime
import time

INITIAL_VOL = 40


def modify_text(string):
    """
    A function to modify a string such that in every line there will be at most 25 characters
    :param string: the string to modify
    :return: the string modified accordingly
    """
    txt_len = len(string)
    if txt_len < 25:
        return string
    new_str = ""
    idx = 0
    while txt_len > idx:
        new_str += string[idx * 20: idx * 20 + 20]
        new_str += "\n"
        idx += 1
    return new_str


class ChannelWidget(QWidget):
    """
    A widget for audio files to play/pause/stop, change volume, choose playback timing, select the audio file
    """
    def __init__(self, af: AudioFile, checked_list):
        """
        The init method of the class
        :param af: the audio file that the widget represent
        :param checked_list: a list of selected audio files
        """
        super(ChannelWidget, self).__init__()
        loadUi("ui_files/ChannelModifier.ui", self)

        self.af = af
        self.checked_list = checked_list
        self.thumb.setText(modify_text(self.af.get_title()))

        # stopwatch variables
        self.count_ms = 0
        self.count_sec = 0
        self.count_min = 0
        self.count_hour = 0
        self.set = 0

        self.volumeSlider.setMinimum(0)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(INITIAL_VOL)
        self.volume = INITIAL_VOL
        self.posLabel.setText(str(self.count_hour).zfill(1) + ":" + str(self.count_min).zfill(2) + ":" +
                              str(self.count_sec).zfill(2) + ":" + str(self.count_ms).zfill(3))

        # media player variables
        self.player = QMediaPlayer()
        url = QUrl.fromLocalFile(self.af.get_path())
        self.content = QMediaContent(url)
        self.player.setMedia(self.content)
        self.player.setVolume(INITIAL_VOL)
        self.player.positionChanged.connect(self.change_position)
        self.player.durationChanged.connect(self.change_duration)

        self.playPauseButton.clicked.connect(self.play_pause_player)
        self.stopButton.clicked.connect(self.stop_player)
        self.volumeSlider.valueChanged.connect(self.change_volume)
        self.posSlider.sliderMoved.connect(self.set_position)
        self.checkBox.toggled.connect(self.select_audio)

    def change_position(self, position):
        """
        A method to move the playback slider to the given position
        :param position: a position
        :return: None
        """
        self.posSlider.setValue(position)

    def change_duration(self, duration):
        """
        A method to set the duration of the playback slider
        :param duration: the duration to set
        :return: None
        """
        self.posSlider.setRange(0, duration)

    def set_position(self, position):
        """
        A method to move the playback to the given position in time
        :param position: the position to set
        :return: None
        """
        self.player.setPosition(position)

    def change_volume(self):
        """
        A method to change the audio volume through the slider
        :return: None
        """
        vol = self.volumeSlider.value()
        self.player.setVolume(vol)
        self.af.set_track(self.af.get_track() + int((vol - self.volume) / 4))
        self.volume = vol

    def select_audio(self):
        """
        A method to select the widget through its checkbox and add it to the checked_list
        :return: None
        """
        if self.checkBox.isChecked():
            self.checked_list.append(self.af)
        else:
            if self.af in self.checked_list:
                self.checked_list.remove(self.af)

    def get_checkbox(self):
        """
        A getter for the widget checkbox
        :return: None
        """
        return self.checkBox

    def set_checkbox(self, val: bool):
        """
        A setter for the widget checkbox
        :param val: the value to set
        :return: None
        """
        self.checkBox.setChecked(val)
        self.select_audio()

    @pyqtSlot()
    def play_pause_player(self):
        """
        A function to play/pause the playback and calculate its realtime time using slots
        :return: None
        """
        self.set += 1
        # tim = datetime.datetime.now()
        tim = time.perf_counter()

        if self.set == 1:
            while True:
                QApplication.processEvents()
                # tim1 = datetime.datetime.now()
                tim1 = time.perf_counter()
                if self.set == 2:
                    self.player.pause()
                    self.set = 0
                    break
                elif self.set == 1:
                    self.player.play()
                    # if int(tim1.microsecond / 1000) - int(tim.microsecond / 1000) >= 1 or \
                    #         int(tim.microsecond / 1000) - int(tim1.microsecond / 1000) >= 1:
                    #     tim = datetime.datetime.now()
                    diff = int(tim1 * 1000) - int(tim * 1000)
                    if diff >= 1 or -diff >= 1:
                        tim = time.perf_counter()
                        self.count_ms += abs(diff)
                        # self.count_ms += 1
                        if self.count_ms > 999:
                            self.count_sec += 1
                            self.count_ms = 0
                        if self.count_sec > 59:
                            self.count_min += 1
                            self.count_sec = 0
                        if self.count_min > 59:
                            self.count_hour += 1
                            self.count_min = 0
                        self.posLabel.setText(str(self.count_hour).zfill(1) + ":" + str(self.count_min).zfill(2) + ":" +
                                              str(self.count_sec).zfill(2) + ":" + str(self.count_ms).zfill(3))

    def stop_player(self):
        """
        A method to stop the playback and reset all time values
        :return: None
        """
        self.count_ms = 0
        self.count_sec = 0
        self.count_min = 0
        self.count_hour = 0
        self.set = 0

        self.player.stop()
        self.posLabel.setText(str(self.count_hour).zfill(1) + ":" + str(self.count_min).zfill(2) + ":" +
                              str(self.count_sec).zfill(2) + ":" + str(self.count_ms).zfill(3))
