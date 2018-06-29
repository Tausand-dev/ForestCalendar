import os
from copy import copy
from datetime import datetime
from datetime import timedelta
from PyQt5 import QtCore, QtWidgets, QtGui
from dateutil.relativedelta import relativedelta

from serial import Serial
import serial.tools.list_ports as find_ports

REPEAT_OPTIONS = ["Day", "Week", "Month"]

def findPorts():
    ports_objects = list(find_ports.comports())
    ports = {}
    for i in range(len(ports_objects)):
        port = ports_objects[i]
        try:
            com = RecorderSerial(port.device)
            if com.testRecorder():
                ports["%s"%port.description] = port.device
            com.close()
        except Exception as e:
            print(e)
    return ports

class RecorderSerial(Serial):
    def __init__(self, port, baudrate = 9600, timeout = 2):
        super(RecorderSerial, self).__init__(port, baudrate = baudrate, timeout = timeout)
        sleep(1)

    def testRecorder(self):
        line = self.readline()
        try:
            line = line.decode()
            if line == "Connection\r\n":
                return True
        except:
            pass
        return False

    def decode(self, line):
        return line.decode().replace("\r\n", "")

    def setTime(self, time):
        temp = time.strftime("%d%m%y%H%M%S")

        ascii_time = [ord(i) for i in temp]
        message = [0x00] + ascii_time

        ans = ""

        while True:
            self.write(message)
            ans = self.decode(serial.readline())
            try:
                datetime.strptime(ans, '%d,%m,%y,%H,%M,%S')
                break
            except:
                pass

    def getTime(self):
        self.write([1])
        ans = self.readline()
        ans = self.decode(ans)
        try:
            return datetime.strptime(ans, '%d,%m,%y,%H,%M,%S')
        except:
            return ans

    def reset(self):
        self.write([2])

class Event(object):
    def __init__(self, start, stop, is_child = False):
        self.start = start.replace(second = 0, microsecond = 0)
        self.stop = stop.replace(second = 0, microsecond = 0)
        self.is_child = is_child

    def setStart(self, start):
        self.start = start

    def setStop(self, stop):
        self.stop = stop

    # def setChild(self, from_repeat, to_repeat, every):
    #     self.is_child = True
    #     self.from_repeat = from_repeat
    #     self.to_repeat = to_repeat
    #     self.every = every
    #
    # def getDate(self):
    #     return self.date
    #
    # def getStart(self):
    #     return self.start
    #
    # def getStop(self):
    #     return self.stop
    #
    # def isChild(self):
    #     return self.is_child
    #
    # def getFromRepeat(self):
    #     return self.from_repeat
    #
    # def getToRepeat(self):
    #     return self.to_repeat
    #
    # def getEvery(self):
    #     return self.every

    def save(self):
        date = self.date.strftime('%d-%m-%y')
        start = self.start.strftime("%H-%M")
        stop = self.stop.strftime("%H-%M")
        txt = "%s-%s; %s-%s\n"%(date, start, date, stop)
        return txt

    def __str__(self):
        start = self.start.strftime("%H:%M")
        stop = self.stop.strftime("%H:%M")
        return "%s - %s"%(start, stop)

class RepeatableEvent(object):
    def __init__(self, from_date, from_time, to_date, to_time, repeat_every):
        self.every = repeat_every
        self.from_date = from_date
        self.from_time = from_time.replace(second = 0, microsecond = 0)
        self.to_date = to_date
        self.to_time = to_time.replace(second = 0, microsecond = 0)
        self._from_ = datetime.combine(from_date, self.from_time)
        self._to_ = datetime.combine(to_date, self.to_time)

    def datesGenerator(self):
        dates = []
        current_start = copy(self._from_)
        current_stop = copy(self._to_)
        hours = 0
        days = 0
        weeks = 0
        months = 0
        if self.every == "Hour": hours = 1
        elif self.every == "Day": days = 1
        elif self.every == "Week": weeks = 1
        elif self.every == "Month": months = 1
        while current_stop <= self._to_:
            dates.append((current_start, current_stop))
            current_start += relativedelta(months = months, weeks = weeks, days = days, hours = hours)
            current_stop += relativedelta(months = months, weeks = weeks, days = days, hours = hours)
        return dates


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

        self.from_time_widget = QtWidgets.QDateTimeEdit()
        self.from_time_widget.setDisplayFormat("yyyy/MM/dd HH:mm")
        self.to_time_widget = QtWidgets.QDateTimeEdit()
        self.to_time_widget.setDisplayFormat("yyyy/MM/dd HH:mm")
        self.repeat_widget = QtWidgets.QCheckBox("Repeat")
        self.repeat_widget.setTristate(False)
        self.repeat_widget.setChecked(True)
        self.every_widget = QtWidgets.QComboBox()
        self.every_widget.addItems(REPEAT_OPTIONS)
        self.from_repeat_widget = QtWidgets.QDateEdit()
        self.from_repeat_widget.setDisplayFormat("yyyy/MM/dd")
        self.to_repeat_widget = QtWidgets.QDateEdit()
        self.to_repeat_widget.setDisplayFormat("yyyy/MM/dd")

        self.times_layout.addRow(QtWidgets.QLabel("Start time:"), self.from_time_widget)
        self.times_layout.addRow(QtWidgets.QLabel("Stop time:"), self.to_time_widget)
        self.times_layout.addRow(self.repeat_widget)
        self.times_layout.addRow(QtWidgets.QLabel("Every:"), self.every_widget)
        self.times_layout.addRow(QtWidgets.QLabel("From:"), self.from_repeat_widget)
        self.times_layout.addRow(QtWidgets.QLabel("To:"), self.to_repeat_widget)

        self.event_layout.addWidget(self.event_date)
        self.event_layout.addWidget(self.event_list)
        self.event_layout.addWidget(self.button_frame)
        self.event_layout.addWidget(self.times_group)

        self.calendar_layout.addWidget(self.calendar_widget)
        self.calendar_layout.addWidget(self.event_group)

        self.button_frame = QtWidgets.QFrame()
        self.button_frame_layout = QtWidgets.QHBoxLayout(self.button_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.button_frame.setSizePolicy(sizePolicy)
        self.button_frame_layout.setAlignment(QtCore.Qt.AlignRight)

        self.export_widget = QtWidgets.QPushButton("Export Calendar")
        self.sync_widget = QtWidgets.QPushButton("Synchronize Clock")
        self.button_frame_layout.addWidget(self.sync_widget)
        self.button_frame_layout.addWidget(self.export_widget)

        self.verticalLayout.addWidget(self.time_groupBox)
        self.verticalLayout.addWidget(self.calendar_group)
        self.verticalLayout.addWidget(self.button_frame)

        self.current_date = datetime.today()
        self.events = {}
        self.is_editting = False

        self.times_group.setEnabled(False)
        self.remove_button.setEnabled(False)

        #####
        ##### SIGNALS
        #####
        self.calendar_widget.selectionChanged.connect(self.changeDate)
        self.event_list.itemSelectionChanged.connect(self.changeTimes)
        self.event_list.itemDoubleClicked.connect(self.selectHandler)
        self.add_button.clicked.connect(self.addHandler)
        self.remove_button.clicked.connect(self.removeHandler)
        self.from_time_widget.dateTimeChanged.connect(self.fromDateTimeChanged)
        self.from_repeat_widget.dateChanged.connect(self.fromDateChanged)
        self.repeat_widget.stateChanged.connect(self.repeatHandler)
        self.sync_widget.clicked.connect(self.syncHandler)
        self.export_widget.clicked.connect(self.exportHandler)

        self.repeat_widget.setChecked(False)
        # self.setMinimumWidth(300)
        self.centerOnScreen()
        self.setDateTimeWidgets()
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

    def setDateTimeWidgets(self, event = None):
        if event == None:
            now = datetime.now()
            self.from_time_widget.setDateTime(now)
            self.to_time_widget.setDateTime(now + timedelta(minutes = 1))
            self.from_time_widget.setMinimumDate(now.date())
            self.from_time_widget.setMaximumDate(now.date())
            self.to_time_widget.setMinimumDate(now.date())
            self.to_time_widget.setMaximumDate((now + timedelta(days = 1)).date())

            now = self.current_date
            self.from_repeat_widget.setDate(now)
        else:
            self.from_time_widget.setDateTime(event.getStart())
            self.to_time_widget.setDateTime(event.getStop())
            if event.isChild():
                self.repeat_widget.setChecked(True)
                self.from_repeat_widget.setDate(event.getFromRepeat())
                self.to_repeat_widget.setDate(event.getToRepeat())
                repeat = event.getEvery()
                self.every_widget.setCurrentIndex(REPEAT_OPTIONS.index(repeat))
            else:
                self.repeat_widget.setChecked(False)
                self.every_widget.setCurrentIndex(0)

    def formatDate(self, date):
        return date.strftime("%Y/%m/%d")

    def saveEvent(self, event):
        txt = self.formatDate(event.getDate())
        try:
            for item in self.events[txt]:
                if ((item.getStart() <= event.getStop()) and (item.getStop() >= event.getStart())):
                    date = item.getDate().strftime("%Y/%m/%d")
                    raise(SystemError("The following times overlap: (%s) and (%s) on %s."%(item, event, date)))
            self.events[txt].append(event)
            self.events[txt] = sorted(self.events[txt], key = str)
            self.addItems(self.events[txt])
        except KeyError:
            self.events[txt] = [event]
            self.addItems(self.events[txt])

    def addHandler(self):
        txt = self.add_button.text()
        if txt == "Edit":
            self.times_group.setEnabled(True)
            self.add_button.setText("Save")
            self.is_editting = True
        elif txt == "Save":
            old_events = copy(self.events)
            if self.is_editting:
                pos = self.event_list.currentRow()
                evt = self.events[self.formatDate(self.current_date)][pos]
                if self.repeat_widget.isChecked() and evt.isChild():
                    self.removeMultipleDates(evt)
                else:
                    self.events[self.formatDate(self.current_date)].pop(pos)
            try:
                if self.repeat_widget.isChecked():
                    start = self.from_repeat_widget.date().toPyDate()
                    stop = self.to_repeat_widget.date().toPyDate()
                    every = self.every_widget.currentText()
                    from_ = self.from_time_widget.time().toPyTime()
                    to_ = self.to_time_widget.time().toPyTime()

                    r_event = RepeatableEvent(start, from_, stop, to_, every)
                    dates = r_event.datesGenerator()
                    print(dates)
                    # dates = self.datesGenerator(start, stop, every)
                    # for date in dates:
                    #     event = Event(date, from_, to_, True, start,
                    #         stop, every)
                    #     self.saveEvent(event)
                else:
                    event = Event(self.current_date, self.from_time_widget.time().toPyTime(),
                                        self.to_time_widget.time().toPyTime())
                    self.saveEvent(event)
            except SystemError as e:
                self.errorWindow(e)
                self.events = old_events

            self.times_group.setEnabled(False)
            self.add_button.setText("Add")
            self.remove_button.setEnabled(False)
            self.event_list.clearSelection()
            self.is_editting = False
            self.repeat_widget.setChecked(False)
        elif txt == "Add":
            self.is_editting = False
            self.times_group.setEnabled(True)
            self.add_button.setText("Save")
            self.setDateTimeWidgets()

    def checkEqual(self, event1, event2):
        if event1.isChild() and event2.isChild():
            if event1.getFromRepeat() == event2.getFromRepeat():
                if event1.getToRepeat() == event2.getToRepeat():
                    if event1.getEvery() == event2.getEvery():
                        return True
        return False

    def removeMultipleDates(self, event):
        dates = self.datesGenerator(event.getFromRepeat(),
                        event.getToRepeat(), event.getEvery())
        for date in dates:
            date_txt = self.formatDate(date)
            try:
                events = self.events[date_txt]
                not_remove = []
                for evt in events:
                    if not self.checkEqual(event, evt):
                        not_remove.append(event)
                self.events[date_txt] = not_remove
            except KeyError:
                pass

    def removeHandler(self):
        pos = self.event_list.currentRow()
        event = self.events[self.formatDate(self.current_date)][pos]
        if event.isChild():
            msg = "There are multiple events associated.\nDo you want to remove all?"
            reply = QtWidgets.QMessageBox.warning(self, 'Remove',
                             msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)

            if reply != QtWidgets.QMessageBox.Cancel:
                if reply == QtWidgets.QMessageBox.Yes:
                    self.removeMultipleDates(event)
                else:
                    self.events[self.formatDate(self.current_date)].pop(pos)
                self.addItems(self.events[self.formatDate(self.current_date)])
                self.selectHandler()
        else:
            msg = "Are you sure you want to remove this event?"
            reply = QtWidgets.QMessageBox.warning(self, 'Remove',
                             msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.events[self.formatDate(self.current_date)].pop(pos)
                self.addItems(self.events[self.formatDate(self.current_date)])
                self.selectHandler()

    def addItems(self, events):
        self.event_list.blockSignals(True)
        self.event_list.clear()
        self.event_list.addItems([str(event) for event in events])
        self.event_list.blockSignals(False)

    def selectHandler(self):
        # self.timesEnabled(False)
        self.times_group.setEnabled(False)
        self.repeat_widget.setChecked(False)
        self.add_button.setText("Add")
        self.remove_button.setEnabled(False)
        self.event_list.blockSignals(True)
        self.event_list.clearSelection()
        self.event_list.blockSignals(False)
        self.is_editting = False

    def repeatHandler(self, state):
        state = bool(state)
        self.every_widget.setEnabled(state)
        self.from_repeat_widget.setEnabled(state)
        self.to_repeat_widget.setEnabled(state)

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
            self.times_group.setEnabled(False)
            self.repeat_widget.setChecked(False)
            self.is_editting = False

    def changeTimes(self):
        pos = self.event_list.currentRow()
        evt = self.events[self.formatDate(self.current_date)][pos]
        self.setDateTimeWidgets(evt)
        self.add_button.setText("Edit")
        self.times_group.setEnabled(False)
        self.remove_button.setEnabled(True)

    def fromDateTimeChanged(self):
        date = self.from_time_widget.dateTime().toPyDateTime()
        date = date + timedelta(minutes = 1)
        self.to_time_widget.setMinimumTime(date.time())

    def fromDateChanged(self):
        date = self.from_repeat_widget.date().toPyDate()
        date = datetime(date.year, date.month, date.day) + timedelta(days = 1)
        self.to_repeat_widget.setMinimumDate(date.date())

    def syncHandler(self):
        ports = findPorts()
        if len(ports):
            port = ports[ports.keys[0]]
            serial = None
            try:
                serial = RecorderSerial(port = port, timeout = 2)
                serial.setTime(datetime.now())
                serial.reset()
            except Exception as e:
                self.errorWindow(e)
            if serial != None:
                try: serial.close()
                except: pass

    def exportHandler(self):
        if self.add_button.text() == "Save":
            self.addHandler()
        keys = sorted(list(self.events.keys()))
        lines = [event.save() for key in keys for event in self.events[key]]
        if len(lines) == 0:
            self.errorWindow(Exception("Calendar is empty."))
        else:
            file = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
            if file != "":
                try:
                    path = os.path.join(file, "schedule.dat")
                    with open(path, "w") as file:
                        file.write("".join(lines))
                except Exception as e:
                    self.errorWindow(e)

    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QtWidgets.QMessageBox.question(self, 'Exit',
                         quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

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
