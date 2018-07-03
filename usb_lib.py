import os
import sys
import cons
import psutil
import shutil
from time import sleep
from threading import Thread

class SD(object):
    def __init__(self, drive):
        self.drive = drive
        space = psutil.disk_usage(self.drive)
        self.total = space.total / 1024**3
        self.used = space.used / 1024**3
        self.free = space.free / 1014**3
        self.percent = space.percent

    def getDrive(self):
        return self.drive

    def save(self, txt):
        try:
            os.remove(os.path.join(self.drive, cons.DONE_FILENAME))
        except FileNotFoundError as e:
            print("SD:", e)
        try:
            path = os.path.join(sys._MEIPASS, cons.PLUGIN_FILE)
        except AttributeError:
            path = cons.PLUGIN_FILE

        shutil.copy(path, os.path.join(self.drive, cons.PLUGIN_FILE))
        with open(os.path.join(self.drive, cons.SCHEDULE_FILENAME), "w") as file:
            file.write(txt)

    def __repr__(self):
        txt = "%s\tCapacity: %.1fGB, Used: %.1f%%"%(self.drive, self.total, self.percent)
        return txt

def locateUsb():
    disks = psutil.disk_partitions()
    if cons.CURRENT_OS == "win32":
        match = [SD(disk.mountpoint) for disk in disks if ((disk.fstype == 'FAT32') and (disk.opts == 'rw,removable'))]
    else:
        match = [SD(disk.mountpoint) for disk in disks if ((disk.fstype == 'vfat') and ('nosuid' in disk.opts ))]
    return match

def driveMonitor():
    while True:
        try:
            cons.DRIVES = locateUsb()
        except Exception as e:
            print("DRIVE MONITOR", e)
        sleep(1)

thread = Thread(target = driveMonitor)
thread.setDaemon(True)
thread.start()
