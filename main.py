import sys
import cons
import windows
import __images__
from PyQt5 import QtCore, QtWidgets, QtGui

app = QtWidgets.QApplication(sys.argv)

icon = QtGui.QIcon(':/icon.ico')
app.setWindowIcon(icon)
app.processEvents()

main = windows.CalendarWindow()
locale = QtCore.QLocale("en")
main.setLocale(locale)
QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))

if cons.CURRENT_OS == 'win32':
    import ctypes
    myappid = 'forest.calendar.01' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

main.setWindowIcon(icon)
main.show()
main.centerOnScreen()

sys.exit(app.exec_())
