from datetime import datetime
from datetime import timedelta
from PyQt5 import QtCore, QtWidgets, QtGui

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
    FIELDS = ["Nombre", "Documento", "Dirección", "Ciudad", "Teléfono", "Correo"]
    WIDGETS = ["nombre", "documento", "direccion", "ciudad", "telefono", "correo"]
    AUTOCOMPLETE_FIELDS = ["Nombre", "Correo", "Documento", "Teléfono"]
    AUTOCOMPLETE_WIDGETS = ["nombre", "correo", "documento", "telefono"]
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

        self.event_form = QtWidgets.QGroupBox("Set event:")
        self.event_layout = QtWidgets.QFormLayout(self.event_form)

        self.from_date_widget = CalWidget(self)
        self.from_time_widget = QtWidgets.QTimeEdit()
        self.to_date_widget = CalWidget(self)
        self.to_time_widget = QtWidgets.QTimeEdit()
        self.setEventTimes()

        self.event_layout.addRow(QtWidgets.QLabel("Start date:"), self.from_date_widget)
        self.event_layout.addRow(QtWidgets.QLabel("Start time:"), self.from_time_widget)
        self.event_layout.addRow(QtWidgets.QLabel("Stop date:"), self.to_date_widget)
        self.event_layout.addRow(QtWidgets.QLabel("Stop time:"), self.to_time_widget)

        self.verticalLayout.addWidget(self.time_groupBox)
        self.verticalLayout.addWidget(self.event_form)

        self.setMinimumWidth(300)
        self.resize(self.verticalLayout.sizeHint())

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

    def setEventTimes(self, from_time = None, to_time = None):
        now = datetime.now()
        if from_time == None:
            self.from_time_widget.setTime(now.time())
        else:
            self.from_time_widget.setTime(from_time)
        if to_time == None:
            self.to_time_widget.setTime((now + timedelta(minutes = 1)).time())
        else:
            self.to_time_widget.setTime(to_time)


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
