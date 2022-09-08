from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QDialog, QComboBox
from PyQt5.uic import loadUi


NUM_ERROR_MSG = "Please insert valid numbers for minutes and seconds"
INFO_NUM_ERROR_MSG = "The inserted values represent time units and they should be values between 0 and 59"
STR_ERROR_MSG = ""
INFO_STR_ERROR_MSG = "Please choose a path and a format"


class SixLineEditWidget(QDialog):
    """
    A class to describe a dialog window with six line edits
    """
    def __init__(self, widget_title, title):
        """
        The init method of the class
        :param widget_title: the title of the window
        :param title: the open message of the window
        """
        super(SixLineEditWidget, self).__init__()
        loadUi("ui_files/4LineEditWidget.ui", self)
        self.setWindowTitle(widget_title)
        self.titleLabel.setText(title)

        self.start_min = None
        self.start_sec = None
        self.start_ms = 0
        self.end_min = None
        self.end_sec = None
        self.end_ms = 0
        self.cancel = False

        self.startminLineEdit.editingFinished.connect(self.modify_start_min)
        self.startsecLineEdit.editingFinished.connect(self.modify_start_sec)
        self.startmsLineEdit.editingFinished.connect(self.modify_start_ms)
        self.endminLineEdit.editingFinished.connect(self.modify_end_min)
        self.endsecLineEdit.editingFinished.connect(self.modify_end_sec)
        self.endmsLineEdit.editingFinished.connect(self.modify_end_ms)
        self.okButton.clicked.connect(self.register_values)
        self.cancelButton.clicked.connect(self.canc)
        self.exec()


    def register_values(self):
        """
        A method to save the values inserted in the line edits and close the window
        :return: the values inserted
        """
        if self.start_min is not None and self.start_sec is not None:
            self.close()
        else:
            create_error_message_box(NUM_ERROR_MSG, INFO_NUM_ERROR_MSG)

    def modify_start_min(self):
        """
        A method to save the start minutes value
        :return: None
        """
        val = self.startminLineEdit.text()
        if not val.isnumeric() or int(val) < 0 or int(val) > 59:
            create_error_message_box(NUM_ERROR_MSG, INFO_NUM_ERROR_MSG)
            self.startminLineEdit.clear()
            self.start_min = None
            return
        self.start_min = int(val)

    def modify_start_sec(self):
        """
        A method to save the start seconds value
        :return: None
        """
        val = self.startsecLineEdit.text()
        if not val.isnumeric() or int(val) < 0 or int(val) > 59:
            create_error_message_box(NUM_ERROR_MSG, INFO_NUM_ERROR_MSG)
            self.startsecLineEdit.clear()
            self.start_sec = None
            return
        self.start_sec = int(val)

    def modify_start_ms(self):
        """
        A method to save the start milliseconds value
        :return: None
        """
        val = self.startmsLineEdit.text()
        if not val == "" and not (val.isnumeric() or int(val) < 0 or int(val) > 999):
            create_error_message_box(NUM_ERROR_MSG, INFO_NUM_ERROR_MSG)
            self.startmsLineEdit.clear()
            self.start_ms = 0
            return
        elif val == '':
            self.start_ms = 0
        else:
            self.start_ms = int(val)

    def modify_end_min(self):
        """
        A method to save the end minutes value
        :return: None
        """
        val = self.endminLineEdit.text()
        if not val.isnumeric() or int(val) < 0 or int(val) > 59:
            create_error_message_box(NUM_ERROR_MSG, INFO_NUM_ERROR_MSG)
            self.endminLineEdit.clear()
            self.end_min = None
            return
        self.end_min = int(val)

    def modify_end_sec(self):
        """
        A method to save the end seconds value
        :return: None
        """
        val = self.endsecLineEdit.text()
        if not val.isnumeric() or int(val) < 0 or int(val) > 59:
            create_error_message_box(NUM_ERROR_MSG, INFO_NUM_ERROR_MSG)
            self.endsecLineEdit.clear()
            self.end_sec = None
            return
        self.end_sec = int(val)

    def modify_end_ms(self):
        """
        A method to save the end milliseconds value
        :return: None
        """
        val = self.endmsLineEdit.text()
        if not val == "" and not (val.isnumeric() or int(val) < 0 or int(val) > 999):
            create_error_message_box(NUM_ERROR_MSG, INFO_NUM_ERROR_MSG)
            self.endmsLineEdit.clear()
            self.end_ms = 0
            return
        elif val == '':
            self.end_ms = 0
        else:
            self.end_ms = int(val)

    def canc(self):
        """
        A method to check if the window is being closed
        :return: None
        """
        self.cancel = True
        self.close()


class ThreeLineEditWidget(QDialog):
    """
    A class that describes a dialog window with three line edits
    """
    def __init__(self, widget_title, title):
        """
        The init method of the class
        :param widget_title: the title of the window
        :param title: the open message of the window
        """
        super(ThreeLineEditWidget, self).__init__()
        loadUi("ui_files/3LineEditWidget.ui", self)

        self.setWindowTitle(widget_title)
        self.titleLabel.setText(title)

        self.line1 = None
        self.line2 = None
        self.line3 = 0
        self.cancel = False

        self.lineEdit1.editingFinished.connect(self.modify_line1)
        self.lineEdit2.editingFinished.connect(self.modify_line2)
        self.lineEdit3.editingFinished.connect(self.modify_line3)
        self.okButton.clicked.connect(self.register_values)
        self.cancelButton.clicked.connect(self.canc)

        self.exec()

    def register_values(self):
        """
        A method to save the time values inserted in the line edits and close the window
        :return:
        """
        if self.line1 is None or self.line2 is None:
            create_error_message_box(NUM_ERROR_MSG, INFO_NUM_ERROR_MSG)
            return
        self.close()

    def modify_line1(self):
        """
        A method to save the minutes value
        :return: None
        """
        val = self.lineEdit1.text()
        if not val.isnumeric() or int(val) < 0 or int(val) > 59:
            create_error_message_box(NUM_ERROR_MSG, INFO_NUM_ERROR_MSG)
            self.lineEdit1.clear()
            self.line1 = None
            return
        self.line1 = int(val)

    def modify_line2(self):
        """
        A method to save the seconds value
        :return: None
        """
        val = self.lineEdit2.text()
        if not val.isnumeric() or int(val) < 0 or int(val) > 59:
            create_error_message_box(NUM_ERROR_MSG, INFO_NUM_ERROR_MSG)
            self.lineEdit2.clear()
            self.line2 = None
            return
        self.line2 = int(val)

    def modify_line3(self):
        """
        A method to save the milliseconds value
        :return: None
        """
        val = self.lineEdit3.text()
        if not val == "" and not (val.isnumeric() or int(val) < 0 or int(val) > 999):
            create_error_message_box(NUM_ERROR_MSG, INFO_NUM_ERROR_MSG)
            self.lineEdit3.clear()
            self.line3 = 0
            return
        elif val == '':
            self.line3 = 0
        else:
            self.line3 = int(val)

    def canc(self):
        """
        A method to check if the window is being closed
        :return: None
        """
        self.cancel = True
        self.close()


class TwoLineEditWidget(QDialog):
    """
    A class that describes a dialog window with two line edits
    """
    def __init__(self, widget_title, title):
        """
        The init method of the class
        :param widget_title:the title of the window
        :param title:the open message of the window
        """
        super(TwoLineEditWidget, self).__init__()
        loadUi("ui_files/2LineEditWidget.ui", self)

        self.setWindowTitle(widget_title)
        self.titleLabel.setText(title)

        self.line1 = None
        self.line2 = None
        self.cancel = False

        self.lineEdit1.editingFinished.connect(self.modify_line1)
        self.lineEdit2.editingFinished.connect(self.modify_line2)
        self.okButton.clicked.connect(self.register_values)
        self.cancelButton.clicked.connect(self.canc)

        self.exec()

    def register_values(self):
        """
        A method to save the values inserted in the line edits and close the window
        :return: None
        """
        if self.line1 is None or self.line2 is None:
            create_error_message_box(NUM_ERROR_MSG, INFO_NUM_ERROR_MSG)
            return
        self.close()

    def modify_line1(self):
        """
        A method to save the first line edit value
        :return: None
        """
        val = self.lineEdit1.text()
        if not val.isnumeric() or int(val) < 0 or int(val) > 59:
            create_error_message_box(NUM_ERROR_MSG, INFO_NUM_ERROR_MSG)
            self.lineEdit1.clear()
            self.line1 = None
            return
        self.line1 = int(val)

    def modify_line2(self):
        """
        A method to save the second line edit value
        :return: None
        """
        val = self.lineEdit2.text()
        if not val.isnumeric() or int(val) < 0 or int(val) > 59:
            create_error_message_box(NUM_ERROR_MSG, INFO_NUM_ERROR_MSG)
            self.lineEdit2.clear()
            self.line2 = None
            return
        self.line2 = int(val)

    def canc(self):
        """
        A method to check if the window is being closed
        :return: None
        """
        self.cancel = True
        self.close()


class LineEditComboBoxWidget(QDialog):
    """
    A class that describes a dialog window with a line edit and a combo box
    """
    def __init__(self, widget_title, title, label1, label2, values_lst):
        super(LineEditComboBoxWidget, self).__init__()
        loadUi("ui_files/LineEditComboBox.ui", self)

        self.setWindowTitle(widget_title)
        self.titleLabel.setText(title)
        self.line1Label.setText(label1)
        self.line2Label.setText(label2)
        self.comboBox.addItems(values_lst)

        self.line1 = None
        self.line2 = None
        self.cancel = False

        self.lineEdit1.editingFinished.connect(self.modify_line1)
        self.comboBox.activated.connect(self.choose_combo_box)
        self.okButton.clicked.connect(self.register_values)
        self.cancelButton.clicked.connect(self.canc)

        self.exec()

    def register_values(self):
        """
        A method to save the values inserted and close the window
        :return:
        """
        if self.line1 is None or self.line2 is None:
            create_error_message_box(STR_ERROR_MSG, INFO_STR_ERROR_MSG)
            return
        self.close()

    def modify_line1(self):
        """
        A method to save the first line valueNone
        :return:
        """
        val = self.lineEdit1.text()
        self.line1 = val

    def choose_combo_box(self, idx):
        """
        A method to save the value chosen from the combo box
        :param idx: the index of the value chosen
        :return: None
        """
        val = self.comboBox.itemText(idx)
        if val is not None:
            form = val[2:]
            self.line2 = form

    def canc(self):
        """
        A method to check if the window is being closed
        :return: None
        """
        self.cancel = True
        self.close()


def create_error_message_box(txt, info):
    """
    A function that creates a message box to show a failure in the request or run of the program
    :param txt: the text of the message that says what error was thrown
    :param info: an informative text about the error
    :return: None
    """
    msg = QMessageBox()
    msg.setGeometry(500, 500, 100, 100)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle("Invalid values")
    msg.setText(txt)
    msg.setInformativeText(info)
    msg.exec()
