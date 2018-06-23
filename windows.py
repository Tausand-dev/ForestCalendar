from datetime import datetime
from datetime import timedelta
from PyQt5 import QtCore, QtWidgets, QtGui

class Event(object):
    def __init__(self, date, start, stop, is_child = False):
        self.date = date
        self.start = start
        self.stop = stop
        self.is_child = is_child

    def setDate(self, date):
        self.date = date

    def setStart(self, start):
        self.start = start

    def setStop(self, stop):
        self.stop = stop

    def getDate(self):
        return self.date

    def getStart(self):
        return self.start

    def getStop(self):
        return self.stop

    def __str__(self):
        start = self.start.strftime("%H:%M")
        stop = self.stop.strftime("%H:%M")
        return "%s - %s"%(start, stop)

class CalWidget(QtWidgets.QDateTimeEdit):
    def __init__(self, parent = None):
        now = datetime.now()
        super(CalWidget, self).__init__(now)
        self.setDisplayFormat("yyyy/MM/dd")
        self.setCalendarPopup(True)

        self.setMinimumDate(now)

class TimeLabel(QtWidgets.QLabel):
    """ From reclosedev at http://stackoverflow.com/questions/8796380/automatically-resizing-label-text-in-qt-strange-behaviour
    and Jean-Sébastien http://stackoverflow.com/questions/29852498/syncing-label-fontsize-with-layout-in-pyqt
    """
    MAX_CHARS = 19
    # global CURRENT_OS
    def __init__(self):
        QtWidgets.QLabel.__init__(self)
        self.setMinimumHeight(30)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.setAlignment(QtCore.Qt.AlignCenter)
        # self.font_name = "Monospace"
        # if CURRENT_OS == "win32":
        self.font_name = "Courier New"
        self.setFont(QtGui.QFont(self.font_name))
        self.initial_font_size = 10
        self.font_size = 10
        self.MAX_TRY = 150
        self.height = self.contentsRect().height()
        self.width = self.contentsRect().width()
        self.changeText()
        self.setFontSize(self.font_size)

        self.installEventFilter(self)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeText)
        self.timer.start()

    def setFontSize(self, size):
        """ Changes the size of the font to `size` """
        f = self.font()
        f.setPixelSize(size)
        self.setFont(f)

    def setColor(self, color):
        """ Sets the font color.
        Args:
            color (string): six digit hexadecimal color representation.
        """
        self.setStyleSheet('color: %s'%color)

    def changeText(self):
        """ Sets the text in label with its name and its value. """
        text = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.setText(text)

    def resize(self):
        """ Finds the best font size to use if the size of the window changes. """
        f = self.font()
        cr = self.contentsRect()
        height = cr.height()
        width = cr.width()
        if abs(height*width - self.height*self.width) > 1:
            self.font_size = self.initial_font_size
            for i in range(self.MAX_TRY):
                f.setPixelSize(self.font_size)
                br = QtGui.QFontMetrics(f).boundingRect(self.text())
                hd = cr.height() - br.height()
                wd = cr.width() - br.width()
                if hd > 0 and wd > 0:
                    self.font_size += 1 * min(abs(hd), abs(wd)) / 25
                else:
                    # if CURRENT_OS == 'win32':
                    self.font_size += -1
                    # else:
                    #     self.font_size += -2
                    f.setPixelSize(max(self.font_size, 1))
                    break
            self.setFont(f)
            self.height = height
            self.width = width

    def eventFilter(self, object, evt):
        """ Checks if there is the window size has changed.
        Returns:
            boolean: True if it has not changed. False otherwise. """
        ty = evt.type()
        if ty == 97: # DONT KNOW WHY
            self.resize()
            return False
        elif ty == 12:
            self.resize()
            return False
        else:
            return True

class CalendarWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(QtWidgets.QMainWindow, self).__init__(parent)
        self.setWindowTitle("Calendario")

        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)

        self.verticalLayout = QtWidgets.QVBoxLayout(wid)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)

        self.time_groupBox = QtWidgets.QGroupBox("Current time:")
        self.time_layout = QtWidgets.QVBoxLayout(self.time_groupBox)

        self.time_widget = TimeLabel()
        self.time_layout.addWidget(self.time_widget)

        self.calendar_group = QtWidgets.QGroupBox("Calendar:")
        self.calendar_layout = QtWidgets.QHBoxLayout(self.calendar_group)
        self.calendar_widget = QtWidgets.QCalendarWidget()
        self.calendar_widget.setMinimumDate(datetime.now().date())

        self.event_group = QtWidgets.QGroupBox("Events:")
        self.event_layout = QtWidgets.QVBoxLayout(self.event_group)
        self.event_date = QtWidgets.QLabel("")
        self.event_date.setAlignment(QtCore.Qt.AlignCenter)
        self.event_list = QtWidgets.QListWidget()
        self.button_frame = QtWidgets.QFrame()
        self.button_frame_layout = QtWidgets.QHBoxLayout(self.button_frame)
        self.times_group = QtWidgets.QGroupBox("Event start/stop:")
        self.times_layout = QtWidgets.QFormLayout(self.times_group)

        self.add_button = QtWidgets.QPushButton("Add")
        self.remove_button = QtWidgets.QPushButton("Remove")

        self.button_frame_layout.addWidget(self.add_button)
        self.button_frame_layout.addWidget(self.remove_button)

        self.from_time_widget = QtWidgets.QTimeEdit()
        self.to_time_widget = QtWidgets.QTimeEdit()

        self.times_layout.addRow(QtWidgets.QLabel("Start time:"), self.from_time_widget)
        self.times_layout.addRow(QtWidgets.QLabel("Stop time:"), self.to_time_widget)

        self.event_layout.addWidget(self.event_date)
        self.event_layout.addWidget(self.event_list)
        self.event_layout.addWidget(self.button_frame)
        self.event_layout.addWidget(self.times_group)

        self.calendar_layout.addWidget(self.calendar_widget)
        self.calendar_layout.addWidget(self.event_group)

        self.verticalLayout.addWidget(self.time_groupBox)
        self.verticalLayout.addWidget(self.calendar_group)

        self.current_date = datetime.today()
        self.events = {}

        self.timesEnabled(False)
        self.remove_button.setEnabled(False)

        #####
        ##### SIGNALS
        #####
        self.calendar_widget.selectionChanged.connect(self.changeDate)
        self.event_list.itemSelectionChanged.connect(self.changeTimes)
        self.event_list.itemDoubleClicked.connect(self.selectHandler)
        self.add_button.clicked.connect(self.addHandler)
        self.remove_button.clicked.connect(self.removeHandler)
        self.from_time_widget.timeChanged.connect(self.fromTimeChanged)

        self.setMinimumWidth(300)
        self.centerOnScreen()
        self.setTimeWidgets()
        self.changeDate()

    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def errorWindow(self, exception):
        error_text = str(exception)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(error_text)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def setTimeWidgets(self, from_time = None, to_time = None):
        now = datetime.now()
        if from_time == None:
            self.from_time_widget.setTime(now.time())
        else:
            self.from_time_widget.setTime(from_time)
        if to_time == None:
            self.to_time_widget.setTime((now + timedelta(minutes = 1)).time())
        else:
            self.to_time_widget.setTime(to_time)

    def timesEnabled(self, bool):
        self.from_time_widget.setEnabled(bool)
        self.to_time_widget.setEnabled(bool)

    def formatDate(self, date):
        return date.strftime("%Y/%m/%d")

    def addHandler(self):
        txt = self.add_button.text()
        if txt == "Edit":
            self.timesEnabled(True)
            self.add_button.setText("Save")
        elif txt == "Save":
            self.timesEnabled(False)
            self.add_button.setText("Add")
            self.remove_button.setEnabled(False)
            self.event_list.clearSelection()

            txt = self.formatDate(self.current_date)
            event = Event(self.current_date, self.from_time_widget.time().toPyTime(), self.to_time_widget.time().toPyTime())

            overlap = False:
            for item in self.events:
                if(item.getStart() <= event.getStop())

            try:
                self.events[txt].append(event)
            except KeyError:
                self.events[txt] = [event]
            self.addItems(self.events[txt])
        elif txt == "Add":
            self.timesEnabled(True)
            self.add_button.setText("Save")
            self.setTimeWidgets()

    def removeHandler(self):
        pos = self.event_list.currentRow()
        evt = self.events[self.formatDate(self.current_date)].pop(pos)
        self.addItems(self.events[self.formatDate(self.current_date)])
        self.selectHandler()

    def addItems(self, events):
        self.event_list.blockSignals(True)
        self.event_list.clear()
        self.event_list.addItems([str(event) for event in events])
        self.event_list.blockSignals(False)

    def selectHandler(self):
        self.timesEnabled(False)
        self.add_button.setText("Add")
        self.remove_button.setEnabled(False)
        self.event_list.blockSignals(True)
        self.event_list.clearSelection()
        self.event_list.blockSignals(False)

    def changeDate(self):
        self.current_date = self.calendar_widget.selectedDate().toPyDate()
        txt = self.formatDate(self.current_date)
        self.event_date.setText(txt)
        try:
            self.addItems(self.events[txt])
        except KeyError:
            self.event_list.blockSignals(True)
            self.event_list.clear()
            self.event_list.clearSelection()
            self.event_list.blockSignals(False)
            self.add_button.setText("Add")
            self.remove_button.setEnabled(False)

    def changeTimes(self):
        pos = self.event_list.currentRow()
        evt = self.events[self.formatDate(self.current_date)][pos]
        self.setTimeWidgets(evt.getStart(), evt.getStop())
        self.add_button.setText("Edit")
        self.timesEnabled(False)
        self.remove_button.setEnabled(True)

    def fromTimeChanged(self):
        time = self.from_time_widget.time().toPyTime()
        date = datetime(2018, 1, 1, time.hour, time.minute) + timedelta(minutes = 1)
        self.to_time_widget.setMinimumTime(date.time())
    # def closeEvent(self, event):
        # self.is_closed = True
        # event.accept()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    # icon = QtGui.QIcon('Registers/icon.ico')
    # app.setWindowIcon(icon)

    # splash_pix = QtGui.QPixmap('Registers/logo.png').scaledToWidth(500)
    # splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    # splash.show()
    app.processEvents()

    main = CalendarWindow()

    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))

    # main.setWindowIcon(icon)
    # splash.close()
    main.show()

    sys.exit(app.exec_())
