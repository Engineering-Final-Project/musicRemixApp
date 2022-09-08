import sys
from pathlib import Path

from remix.manager import Manager
from remix.tools import Tools
from channel_widget import *
from audio_label import *
from line_edit_widgets import *

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, \
    QListWidget, QListWidgetItem, QScrollBar, QInputDialog, QGridLayout, QFileDialog, QMessageBox, QAction, \
    QListView, QRadioButton, QButtonGroup, QDialog, QGroupBox
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt


class MainWindow:
    """
    The main window of the application
    """
    def __init__(self):
        """
        The init method of the class
        """
        self.QListWidgetLeft = None  # QListWidget
        self.QListWidgetRight = None  # QListWidget
        self.selected_audiofiles = []  # list of audiofiles to apply editing to
        self.central_widget = None
        self.manager = Manager.get_instance()
        self.window = QMainWindow()
        self.set_window()
        self.set_menu_bar()
        self.sb = self.window.statusBar()
        self.sb.showMessage(f"ready to remix")
        self.window.show()

    def set_window(self):
        """
        A method to set the main window design
        :return: None
        """
        self.window.setGeometry(200, 50, 1500, 1000)
        self.window.setWindowIcon(QIcon("assets/icon.png"))
        self.window.setStyleSheet('background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 '
                                  'rgba(165, 165, 247, 255), stop:1 rgba(255, 255, 255, 255))')
        self.window.setWindowTitle("Music Remixes and Mashups")
        self.create_central_widget()

    def create_central_widget(self):
        """
        A method to create the central widget of the main window
        :return: None
        """
        self.central_widget = QWidget()
        self.window.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(QHBoxLayout())
        self.create_side_menu()
        self.create_mixing_window()

    def create_side_menu(self):
        """
        A method to create the side menu in the central widget of the main window
        :return: None
        """
        left_widget = QWidget()
        vbox = QVBoxLayout()
        self.QListWidgetLeft = QListWidget()
        self.create_scrollbar(self.QListWidgetLeft)

        pr = self.manager.get_current_project()
        if pr is not None:
            for af in pr.get_audio_files():
                self.add_audiofile_to_side_menu(af)

        vbox.addWidget(self.QListWidgetLeft)
        left_widget.setLayout(vbox)
        left_widget.setFixedWidth(250)
        left_widget.setStyleSheet('background-color:white')
        self.central_widget.layout().addWidget(left_widget)

    def add_audiofile_to_side_menu(self, af: AudioFile):
        """
        A method to add audio files represented by widgets of type AudioLabel to the side menu
        :param af: the audio file
        :return: None
        """
        if self.QListWidgetLeft is None:
            self.QListWidgetLeft = QListWidget()
            self.create_scrollbar(self.QListWidgetLeft)

        label = AudioLabel(af)
        item = QListWidgetItem(self.QListWidgetLeft)
        item.setFlags(Qt.NoItemFlags)
        item.setSizeHint(label.size())
        self.QListWidgetLeft.addItem(item)
        self.QListWidgetLeft.setItemWidget(item, label)

    def create_mixing_window(self):
        """
        A method to create the mixing window in the central widget of the main window
        :return: None
        """
        mixing_window = QWidget()
        grid = QGridLayout()
        self.QListWidgetRight = QListWidget()
        self.QListWidgetRight.setViewMode(QListView.IconMode)
        self.create_scrollbar(self.QListWidgetRight)

        pr = self.manager.get_current_project()
        if pr is not None:
            lst = pr.get_originals() + pr.get_current_mix()
            if pr.get_final_mix() is not None:
                lst.append(pr.get_final_mix())
            for af in lst:
                self.add_channel_modifier_to_mixing_menu(af)

        grid.addWidget(self.QListWidgetRight)
        mixing_window.setLayout(grid)
        mixing_window.setStyleSheet('background-color:white')
        self.central_widget.layout().addWidget(mixing_window)

    def add_channel_modifier_to_mixing_menu(self, af: AudioFile):
        """
        A method to add audio files represented by widgets of type ChannelWidget to the mixing menu
        :param af: the audio file
        :return: None
        """
        if self.QListWidgetRight is None:
            self.QListWidgetRight = QListWidget()
            self.QListWidgetRight.setLayoutMode(QListView.IconMode)
            self.create_scrollbar(self.QListWidgetRight)

        wid = ChannelWidget(af, self.selected_audiofiles)
        item = QListWidgetItem(self.QListWidgetRight)
        item.setFlags(Qt.NoItemFlags)
        item.setSizeHint(wid.size())
        self.QListWidgetRight.addItem(item)
        self.QListWidgetRight.setItemWidget(item, wid)

    def create_scrollbar(self, list: QListWidget):
        """
        A method to create a scrollbar for a QListWidget
        :param list: a QListWidget
        :return: None
        """
        scrollbar = QScrollBar()
        scrollbar.setMaximum(100)
        scrollbar.setStyleSheet("background-color: rgb(60,60,90); width: 14px; border-radius 0px;")
        scrollbar.sliderMoved.connect(scrollbar.value)
        list.setSpacing(5)
        list.setVerticalScrollBar(scrollbar)
        list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

    # --------------------------- MENU BAR ----------------------------

    def create_messagebox(self, e, txt_msg):
        """
        A function that creates a message box to show a failure in the request or run of the program
        :param txt_msg: the text of the message that says what error was thrown
        :param e: an informative text about the error
        :return: None
        """
        msg = QMessageBox()
        msg.setGeometry(500, 500, 100, 100)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(txt_msg)
        msg.setInformativeText(str(e))
        msg.setWindowTitle(txt_msg)
        msg.exec()

    def uncheck_audio(self):
        """
        A method to deselect an audio widget in the mixing menu
        :return: None
        """
        for i in range(self.QListWidgetRight.count()):
            item = self.QListWidgetRight.item(i)
            widget = self.QListWidgetRight.itemWidget(item)
            widget.set_checkbox(False)

    def new_project_dialog(self):
        """
        A method to create a new project with name given through an input dialog
        :return: None
        """
        diag = QInputDialog()
        name, ok = diag.getText(self.window, 'New Project', 'Insert the new remix name')

        if ok:
            try:
                self.manager.create_project(str(name))
                self.window.setWindowTitle("Music Remixes and Mashups - " + str(name))
                self.sb.showMessage("Working on project " + str(name))
            except Exception as e:
                self.create_messagebox(e, "Creation of new remix failed")

    def open_project_dialog(self):
        """
        A method to open a project from the list of existing projects
        :return: None
        """
        self.diag = QDialog()
        self.diag.setFixedSize(200, 200)
        self.diag.setWindowTitle("Open Project")
        vbox = QVBoxLayout()
        pr_group = QButtonGroup()  # alternatively QGroupBox
        for name in self.manager.get_project_names():
            btn = QRadioButton(name)  # QRadioButton(btn_text)
            pr_group.addButton(btn)  # name is the btn id in the group
            vbox.addWidget(btn)
        pr_group.buttonClicked.connect(self.select_project)
        self.diag.setLayout(vbox)
        self.diag.exec()

    def select_project(self, btn):
        """
        A method to select a project from a list
        :return: None
        """
        try:
            self.diag.close()
            name = btn.text()
            self.manager.open_project(name)
            self.window.setWindowTitle("Music Remixes and Mashups - " + str(name))
            self.create_central_widget()
        except Exception as e:
            self.create_messagebox(e, "Failed Opening remix")

    def delete_project_dialog(self):
        """
        A method to delete the current project asking for confirmation
        :return: None
        """
        try:
            confirm_msg = QMessageBox()
            confirm_msg.setFixedSize(400, 200)
            confirm_msg.setIcon(QMessageBox.Question)
            confirm_msg.setWindowTitle("Confirm deletion")
            confirm_msg.setText("Are you sure you want to delete the current remix?")
            confirm_msg.setInformativeText("When a remix is deleted, it is impossible to recover it")
            confirm_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirm_msg.buttonClicked.connect(self.delete_project)
            confirm_msg.exec()
        except Exception as e:
            self.create_messagebox(e, "Delete failed")

    def delete_project(self, confirm):
        """
        A method to delete the current project
        :param confirm: the confirmation message
        :return: None
        """
        if confirm.text() == "&Yes":
            self.manager.remove_project()
            self.QListWidgetLeft = None  # QListWidget
            self.QListWidgetRight = None  # QListWidget
            self.selected_audiofiles = []  # list of audiofiles to apply editing to
            self.central_widget = None
            self.window.setWindowTitle("Music Remixes and Mashups")
            self.create_central_widget()

    def save_project_dialog(self):
        """
        A method to save the current project
        :return: None
        """
        try:
            self.manager.save()
            self.create_messagebox("The Project has been saved successfully", "Project Saved")
        except Exception as e:
            self.create_messagebox(e, "Save failed")

    def saveas_project_dialog(self):
        """
        A method to save as the current project
        :return: None
        """
        try:
            fpath, _ = QFileDialog.getSaveFileName(self.window, 'Select directory', str(Path.home()),
                                                   "Sound Files (*.mp3 *.mp4 *.wav *.m4a)")
            if fpath:
                self.manager.save_project_as(fpath)
                self.create_messagebox("The Project has been saved successfully", "Project Saved")
        except Exception as e:
            self.create_messagebox(e, "Save failed")

    def import_audio_url_dialog(self):
        """
        A method to import an audio file from a url given through an input dialog
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            diag = QInputDialog()
            path, ok = diag.getText(self.window, 'Import audio', 'Insert the URL of the audio (link from Youtube)')
            if ok:
                orig = pr.add_original(str(path))
                self.add_audiofile_to_side_menu(orig)
                self.add_channel_modifier_to_mixing_menu(orig)
        except Exception as e:
            self.create_messagebox(e, "Download failed")

    def import_audio_local_dialog(self):
        """
        A method to import an audio file from local
        :return:
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            fname, _ = QFileDialog.getOpenFileName(self.window, 'Select audio file', str(Path.home()),
                                                   "All Files (*);; Sound Files (*.mp3 *.mp4 *.wav *.m4a)")
            if fname:
                orig = pr.add_original(fname)
                self.add_audiofile_to_side_menu(orig)
                self.add_channel_modifier_to_mixing_menu(orig)
        except Exception as e:
            self.create_messagebox(e, "Import failed")

    def rename_audio_dialog(self):
        """
        A method to rename an audio file
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) != 1:
                raise Exception("A single file can be renamed at a time.\nPlease select one file")
            diag = QInputDialog()
            name, ok = diag.getText(self.window, 'Rename', 'Rename to:')
            if ok:
                Tools.rename(self.selected_audiofiles[0], name)
                self.rename_item(self.selected_audiofiles[0], name)
                self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "Audio Rename Failed")

    def rename_item(self, af, name):
        """
        A method to rename the ChannelWidget of an audio file in the mixing menu according to a given name
        :param af: the audio file renamed
        :param name: the name assigned
        :return: None
        """
        for i in range(self.QListWidgetRight.count()):
            item = self.QListWidgetRight.item(i)
            widget = self.QListWidgetRight.itemWidget(item)
            if widget.af == af:
                Tools.rename(widget.af, name)
                txt = modify_text(name)
                widget.thumb.setText(txt)
                break

    def duplicate_audio(self):
        """
        A method to duplicate a selected audio
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) != 1:
                raise Exception("A single file can be duplicated at a time.\nPlease select one file")
            dup = pr.duplicate(self.selected_audiofiles[0])
            self.add_channel_modifier_to_mixing_menu(dup)
            self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "Duplication Failed")

    def remove_audio(self):
        """
        A method to remove an audio from the current project (the audio will be only visually removed,
        but it is still saved in the working directory)
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) != 1:
                raise Exception("A single file can be removed at a time.\nPlease select one file")
            pr.remove_audio_from_project(self.selected_audiofiles[0])
            self.remove_item(self.selected_audiofiles[0])
            self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "Remove Failed")

    def remove_item(self, audio):
        """
        A method to remove the ChannelWidget of a removed audiofile from the mixing menu
        :param audio: the audio file removed
        :return: None
        """
        item_to_remove = None
        for i in range(self.QListWidgetRight.count()):
            item = self.QListWidgetRight.item(i)
            widget = self.QListWidgetRight.itemWidget(item)
            if widget.af == audio:
                item_to_remove = item
                widget.set_checkbox(False)
                widget.stop_player()
                widget.close()
                break
        if item_to_remove:
            self.QListWidgetRight.takeItem(self.QListWidgetRight.row(item_to_remove))

    def export_audio_dialog(self):
        """
        A method to export a selected audio file
        :return:None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) != 1:
                raise Exception("Export a single file at a time.\nPlease select one file")

            formats = ['*.mp3', '*.mp4', '*.wav', '*.m4a']
            wid = LineEditComboBoxWidget("Export audio", "Please insert a path to a valid folder and\nchoose a format",
                                         "Path:", "Format:", formats)
            if not wid.cancel:
                Tools.export(self.selected_audiofiles[0], wid.line1, wid.line2)
                self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "Failed Exporting Audio")

    def split_audio_dialog(self):
        """
        A method to separate an audio file into 2, 4, or 5 stems
        :return: None
        """
        try:
            if len(self.selected_audiofiles) != 1:
                raise Exception("One file must be selected to be separated at a time.\nPlease select one file")
            self.diag = QDialog()
            self.diag.setWindowTitle("Choose stems to separate audio")
            vbox = QVBoxLayout()
            pr_group = QButtonGroup()  # alternatively, use QGroupBox
            split_options = {2: "Vocals, accompaniment", 4: "Vocals, drums, bass, others",
                             5: "Vocals, drums, bass, piano, others"}
            for num in split_options:
                btn = QRadioButton(str(num) + ': ' + split_options[num])  # QRadioButton(btn_text)
                btn.setStyleSheet("QRadioButton{font: 12pt Helvetica MS;}, QRadioButton::indicator { width: 15px; "
                                  "height: 15px;};")
                pr_group.addButton(btn)  # name is the btn id in the group
                vbox.addWidget(btn)
            pr_group.buttonClicked.connect(self.split_audio)
            self.diag.setLayout(vbox)
            self.diag.exec()
        except Exception as e:
            self.create_messagebox(e, "Failed Separating Audio into Stems")

    def split_audio(self, btn):
        """
        A method to split an audio file into a selected number of stems
        :param btn: the button selected that represents the number of stems
        :return: None
        """
        self.diag.close()
        num = btn.text()
        pr = self.manager.get_current_project()
        audios = pr.split(self.selected_audiofiles[0], int(num[0]))
        for audio in audios:
            self.add_channel_modifier_to_mixing_menu(audio)
            self.rename_item(audio, audio.get_title())
        self.uncheck_audio()

    def merge_audio_dialog(self):
        """
        A method to overlay audio files and ask if BPM must be averaged
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) < 2:
                raise Exception("At least two files must be selected to merge")
            self.bpm_msg = QMessageBox()
            self.bpm_msg.setFixedSize(400, 200)
            self.bpm_msg.setIcon(QMessageBox.Icon.Question)
            self.bpm_msg.setWindowTitle("BPM Change")
            self.bpm_msg.setText("Should the files be merged after averaging bpm?")
            self.bpm_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            self.bpm_msg.buttonClicked.connect(self.merge_audio)
            self.bpm_msg.exec()
        except Exception as e:
            self.create_messagebox(e, "Failed Merging Audios")

    def merge_audio(self, msg):
        """
        A method to overlay audio files
        :param msg: a flag that indicate if BPM must be averaged or not
        :return: None
        """
        try:
            self.bpm_msg.close()
            pr = self.manager.get_current_project()
            if msg.text() == "&Yes":
                merged = pr.merge(self.selected_audiofiles, True)
            else:
                merged = pr.merge(self.selected_audiofiles, False)
            self.add_channel_modifier_to_mixing_menu(merged)
            self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "Failed Merging Audios")

    def trim_audio_dialog(self):
        """
        A method to trim an audio file according to the parameters requested through the SixLineEditWidget
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) != 1:
                raise Exception("A single file can be trimmed at a time.\nPlease select one file")

            wid = SixLineEditWidget("Trim audio", "Please select valid times to trim the audio\n(milliseconds are opt"
                                                  "ional).\nIf end times correspond to end of audio,\nleave it blank")
            if not wid.cancel:
                if not wid.end_sec:
                    end_sec = None
                else:
                    end_sec = wid.end_sec + (wid.end_ms / 1000)
                trimmed = pr.trim(self.selected_audiofiles[0], wid.start_min, wid.start_sec + (wid.start_ms / 1000),
                                  wid.end_min, end_sec)
                self.add_channel_modifier_to_mixing_menu(trimmed)
                self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "Failed Trimming Audio")

    def concat_audios(self):
        """
        A method to concatenate two audio files
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) < 2:
                raise Exception("At least two files must be selected to concatenate")
            concat = pr.concat(self.selected_audiofiles)
            self.add_channel_modifier_to_mixing_menu(concat)
            self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "Failed Audio Concatenation")

    def cut_audio_dialog(self):
        """
        A method to time split an audio file according to the parameters requested through the ThreeLineEditWidget
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) != 1:
                raise Exception("A single file can be split at a time.\nPlease select one file")

            wid = ThreeLineEditWidget("Split times", "Please select a valid time to split the\naudio. If end times "
                                                     "correspond to\nend of audio, you can leave it blank")
            if not wid.cancel:
                cut1, cut2 = pr.cut(self.selected_audiofiles[0], wid.line1, wid.line2 + (wid.line3 / 1000))
                if cut1 is None:
                    self.add_channel_modifier_to_mixing_menu(cut2)
                elif cut2 is None:
                    self.add_channel_modifier_to_mixing_menu(cut1)
                else:
                    self.add_channel_modifier_to_mixing_menu(cut1)
                    self.add_channel_modifier_to_mixing_menu(cut2)
                self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "Failed Time Splitting Audio")

    def delete_audio_dialog(self):
        """
        A method to delete a section of audio file according to the parameters requested through the SixLineEditWidget
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) != 1:
                raise Exception("A single file can be cut at a time.\nPlease select one file")
            wid = SixLineEditWidget("Cut audio", "Please select valid times to cut the audio\n(milliseconds are "
                                                 "optional).\nIf end times correspond to end of audio,\nleave it blank")
            if not wid.cancel:
                if not wid.end_ms:
                    end_sec = None
                else:
                    end_sec = wid.end_sec + (wid.end_ms / 1000)
                deleted = pr.delete(self.selected_audiofiles[0], wid.start_min, wid.start_sec + (wid.start_ms / 1000),
                                    wid.end_min, end_sec)
                deleted.set_title(self.selected_audiofiles[0].get_title() + "_cut")
                self.add_channel_modifier_to_mixing_menu(deleted)
                self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "Failed Cutting Audio")

    def fade_audio_dialog(self):
        """
        A method to fade an audio file according to the parameters requested through TwoLineEditWidget
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) != 1:
                raise Exception("Fade a single file at a time.\nPlease select one file")

            wid = TwoLineEditWidget("Fade", "For how long fading should last?")
            if not wid.cancel:
                faded = pr.fade(self.selected_audiofiles[0], wid.line1, wid.line2)
                self.add_channel_modifier_to_mixing_menu(faded)
                self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "Failed Splitting Audio")

    def fadein_dialog(self):
        """
        A method to fade the start of an audio file
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) != 1:
                raise Exception("A single file can be faded at a time.\nPlease select one file")
            diag = QInputDialog()
            secs, ok = diag.getText(self.window, 'Fade In', 'How many seconds fading should last?')
            if ok:
                faded = pr.fadein(self.selected_audiofiles[0], int(secs))
                self.add_channel_modifier_to_mixing_menu(faded)
                self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "Fade In Failed")

    def fadeout_dialog(self):
        """
        A method to fade the end of an audio file
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) != 1:
                raise Exception("A single file can be faded at a time.\nPlease select one file")
            diag = QInputDialog()
            secs, ok = diag.getText(self.window, 'Fade Out', 'How many seconds fading should last?')
            if ok:
                faded = pr.fadeout(self.selected_audiofiles[0], int(secs))
                self.add_channel_modifier_to_mixing_menu(faded)
                self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "Fade Out Failed")

    def audio_position_transform_dialog(self):
        """
        A method to change the position of the start of an audio file
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) != 1:
                raise Exception("Change position of single file at a time.\nPlease select one file")

            wid = ThreeLineEditWidget("Transform audio position", "The audio will start playing after\nthe selected "
                                                                  "time:")
            if not wid.cancel:
                pos_transform = pr.change_position(self.selected_audiofiles[0], wid.line1,
                                                   wid.line2 + (wid.line3 / 1000))
                self.add_channel_modifier_to_mixing_menu(pos_transform)
                self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "Failed Splitting Audio")

    def detect_bpm(self):
        """
        A method to detect the BPM of an audio file
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) != 1:
                raise Exception("Bpm can be detected to a single file at a time.\nPlease select one file")
            bpm = Tools.bpm_detector(self.selected_audiofiles[0].get_track())
            self.create_messagebox("The audio bpm is " + str(bpm), "Audio BPM")
            self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "BPM Detection Failed")

    def change_speed(self):
        """
        A method to change an audio file speed according to the given ratio
        :return: None
        """
        try:
            pr = self.manager.get_current_project()
            if pr is None:
                raise Exception("You must create a project first")
            if len(self.selected_audiofiles) != 1:
                raise Exception("Speed can be changed to a single file at a time.\nPlease select one file")
            diag = QInputDialog()
            ratio, ok = diag.getText(self.window, 'Speed ratio', 'Increase / decrease speed by:')
            if ok:
                speed = pr.change_speed(self.selected_audiofiles[0], float(ratio))
                self.add_channel_modifier_to_mixing_menu(speed)
                self.uncheck_audio()
        except Exception as e:
            self.create_messagebox(e, "Speed Change Failed")

    def help(self):
        """
        A method to open an informative message box with the project owners contacts
        :return: None
        """
        msg = QMessageBox()
        msg.setGeometry(500, 500, 100, 100)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("Contacts:")
        msg.setInformativeText("Miriam: 0000000")
        msg.setWindowTitle("Contact Us")
        msg.exec()

    def set_submenu_item(self, action_name, menu, shortcut, status, triggered_function=None):
        """
        A method to set a menu bar submenu
        :param action_name: the name of the action to add
        :param menu: the menu to add the submenu
        :param shortcut: a shortcut for the option
        :param status: a short informative message
        :param triggered_function: the function triggered by selecting the option
        :return: None
        """
        action = QAction(action_name, menu)
        if shortcut != "":
            action.setShortcut(shortcut)
        action.setStatusTip(status)
        if triggered_function:
            action.triggered.connect(triggered_function)
        menu.addAction(action)

    def set_file_menu(self):
        """
        A method to create the file menu in the upper menubar
        :return: None
        """
        file_menu = self.window.menuBar().addMenu("&File")
        self.set_submenu_item("New Project", file_menu, "Ctrl + n", "Create a new project", self.new_project_dialog)
        self.set_submenu_item("Open Project", file_menu, "Ctrl + o", "Open an existing project",
                              self.open_project_dialog)
        self.set_submenu_item("Save", file_menu, "Ctrl + s", "Save the current project",
                              self.save_project_dialog)
        self.set_submenu_item("Save As", file_menu, "Ctrl + Shift + s", "Save the current project as",
                              self.saveas_project_dialog)
        self.set_submenu_item("Delete Project", file_menu, "Ctrl + r", "Remove the current project",
                              self.delete_project_dialog)
        self.set_submenu_item("Quit", file_menu, "Ctrl + q", "Quit the application", self.window.close)

    def set_project_menu(self):
        """
        A method to create the project menu in the upper menubar
        :return: None
        """
        project_menu = self.window.menuBar().addMenu("&Project")
        self.set_submenu_item("Import from URL", project_menu, "Ctrl + i", "Import audio from a URL",
                              self.import_audio_url_dialog)
        self.set_submenu_item("Import from local file", project_menu, "Ctrl + l", "Import audio from a local file",
                              self.import_audio_local_dialog)
        self.set_submenu_item("Rename audio", project_menu, "", "Rename audiofile", self.rename_audio_dialog)
        self.set_submenu_item("Duplicate audio", project_menu, "", "Duplicate audiofile", self.duplicate_audio)
        self.set_submenu_item("Remove audio", project_menu, "", "Remove audiofile", self.remove_audio)
        self.set_submenu_item("Export to file", project_menu, "Ctrl + e", "Export audio to file",
                              self.export_audio_dialog)

    def set_audio_edit_menu(self):
        """
        A method to create the editing menu in the upper menubar
        :return: None
        """
        transform_menu = self.window.menuBar().addMenu("&Edit")
        self.set_submenu_item("Separate to stems", transform_menu, "Ctrl + s", "Separate to audio stems",
                              self.split_audio_dialog)
        self.set_submenu_item("Merge", transform_menu, "Ctrl + m", "Merge audio", self.merge_audio_dialog)
        self.set_submenu_item("Trim", transform_menu, "Ctrl + t", "Trim audio", self.trim_audio_dialog)
        self.set_submenu_item("Concatenate", transform_menu, "Ctrl + c", "Concatenate audio", self.concat_audios)
        self.set_submenu_item("Time Split", transform_menu, "Ctrl + p", "Split audio", self.cut_audio_dialog)  # audio_cut
        self.set_submenu_item("Cut", transform_menu, "Ctrl + r", "Remove part of the audio", self.delete_audio_dialog)  # audio_delete
        self.set_submenu_item("Fade", transform_menu, "Ctrl + f", "Fade audio", self.fade_audio_dialog)
        self.set_submenu_item("Fade in", transform_menu, "Ctrl + f", "Fade in audio", self.fadein_dialog)
        self.set_submenu_item("Fade out", transform_menu, "Ctrl + f", "Fade out audio", self.fadeout_dialog)
        self.set_submenu_item("Change position", transform_menu, "Ctrl + p", "Change audio position",
                              self.audio_position_transform_dialog)

    def set_process_menu(self):
        """
        A method to create the process menu in the upper menubar
        :return: None
        """
        process_menu = self.window.menuBar().addMenu("&Process")
        self.set_submenu_item("Detect BPM", process_menu, "", "Detect audiofile bpm", self.detect_bpm)
        self.set_submenu_item("Change Speed", process_menu, "", "Change audiofile speed", self.change_speed)

    def set_help_menu(self):
        """
        A method to create the help menu in the upper menubar
        :return: None
        """
        help_menu = self.window.menuBar().addMenu("&Help")
        self.set_submenu_item("Contact Us", help_menu, "Ctrl + H", "Contact Us", self.help)

    def set_menu_bar(self):
        """
        A method to add all menus to the upper menubar
        :return:
        """
        self.set_file_menu()
        self.set_project_menu()
        self.set_audio_edit_menu()
        self.set_process_menu()
        self.set_help_menu()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
