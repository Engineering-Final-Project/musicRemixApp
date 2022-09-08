from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.uic import loadUi

from remix.audio import *
from channel_widget import modify_text


class AudioLabel(QWidget):
    """
    A class that represent an audio label widget with audio track thumbnail and title
    """
    def __init__(self, af: AudioFile):
        """
        The init method of the class
        :param af: an AudioFile object
        """
        super(AudioLabel, self).__init__()
        loadUi("ui_files/AudioLabel.ui", self)

        self.af = af
        self.setFixedSize(200, 250)
        self.set_label()
        self.nameLabel.setText(modify_text(self.af.get_title()))
        self.nameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_label(self):
        """
        A method to set the thumbnail in the label
        :return: None
        """
        self.thumbLabel.setFixedWidth(180)
        self.thumbLabel.setFixedHeight(180)
        self.thumbLabel.setStyleSheet("border: 3px solid #000061;")
        self.thumbLabel.setStyleSheet("background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 "
                                      "rgba(165, 165, 247, 255), stop:1 rgba(255, 255, 255, 255));")
        font = QFont()
        font.setFamily("Cantarell")
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(9)
        self.thumbLabel.setFont(font)
        self.thumbLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.af.get_thumb_path():
            self.thumbLabel.setPixmap(QPixmap(self.af.get_thumb_path()))
        else:
            txt = modify_text(self.af.get_title())
            self.thumbLabel.setText("\n" + txt)
