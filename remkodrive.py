from PyQt4 import QtGui, QtCore
import sys
from onedrivestuff import *
import dialogs
from tendo import singleton
from filesystemstuff import *
import json
import pickle
from setactions import *
from doactions import *
from threading import *
import subprocess
import inotify.adapters
import log


class SystemTrayIcon(QtGui.QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        self.iswatch=False
        self.logger=log.log()
        self.basepath=os.path.expanduser('~')+"/onedrive"
        self.optionsread()
        fs=systemstuff(self.basepath)
        fs.mkdir(self.basepath)
        self.exclude=self.read_exclude()
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)
        menu = QtGui.QMenu(parent)
        self.login = menu.addAction("Start syncing")
        self.forcem = menu.addAction("Force full sync")
        self.open = menu.addAction("open folder")
        self.browser=menu.addAction("Open in browser")
        self.excludemen = menu.addAction("Edit exclude list")
        self.logout = menu.addAction("Stop syncing")
        self.options = menu.addAction("Options")
        self.viewlog= menu.addAction("Status")
        exitAction = menu.addAction("Exit")
        self.setContextMenu(menu)
        exitAction.triggered.connect(QtGui.qApp.quit)
        self.options.triggered.connect(self.setoptions)
        self.login.triggered.connect(self.enter)
        self.forcem.triggered.connect(self.force)
        self.logout.triggered.connect(self.exit)
        self.browser.triggered.connect(self.inbrowser)
        self.viewlog.triggered.connect(self.viewstatus)
        self.open.triggered.connect(self.openmainfolder)
        self.excludemen.triggered.connect(self.exclude_dialog)
        self.login.setVisible(True)
        self.logout.setVisible(False)
        self.updateIcon(False)
        self.updateIcon(False)
        self.root=None
        self.insync=False
        self.intialsyncdone=False
        self.stuff = stuff()
        if self.stuff.hassaved():
            self.recon()

    def inbrowser(self):
        import webbrowser
        new = 2  # open in a new tab, if possible
        url = "https://onedrive.live.com/?id=root"
        webbrowser.open(url, new=new)

    def recon(self):
        try:
            self.stuff.reconnect()
            self.enter()
        except:
            pass

    def setoptions(self):
        dia=dialogs.option()
        dia.showdialog(self.basepath)
    def viewstatus(self):
        dia=dialogs.log()
        dia.showdialog(self.logger.log)
    def watchon(self):

        if not self.iswatch:
            self.watch = Thread(target=self.watch)
            self.watch.setDaemon(True)
            self.watch.start()
            self.iswatch = True

    def optionsread(self):
        if os.path.isfile("options"):
            with open("options", "rb") as myfile:
                self.basepath = pickle.load(myfile)



    def againread(self):
        againlist=[]
        try:
            if os.path.isfile("again"):
                with open("again", "rb") as myfile:
                    againlist = pickle.load(myfile)
        except:
            pass
            return againlist

    def againwrite(self,type,path,filename):
        list=self.againread()
        if type=='IN_CREATE':
            type='new'
        if type=='IN_MOVED_FROM':
            type="delete"

        full=path.decode() + "/" + filename.decode()
        full.replace("//","/")
        item=[type,path,filename.decode(),full]
        list.append(item)

        file_name = "again"
        with open(file_name, 'wb') as x_file:
            pickle.dump(list, x_file)

    def watch(self):
        i = inotify.adapters.InotifyTree((bytes(self.basepath, "UTF-8")))
        try:
            for event in i.event_gen():
                if event is not None:
                     (header, type_names, path, filename) = event
                     print(header,type_names,path,filename)
                     if (type_names[0]=='IN_CREATE') | (type_names[0]=='IN_MOVED_TO'):
                         print(type_names,path, filename)
                         self.logger.add("File created " + path.decode() + "/" + filename.decode())
                         self.againwrite(type_names[0],path,filename)
                     if type_names[0] == 'IN_MOVED_FROM':
                         self.logger.add("File moved or delete "+path.decode()+"/"+filename.decode())
                         self.againwrite(type_names[0], path, filename)


        finally:
            self.logger.add("the directory watcher quit!")

    def openmainfolder(self):
        subprocess.Popen(["xdg-open", self.basepath])

    def exclude_dialog(self):
        self.stuff = stuff()
        if self.stuff.isNowConnected():
            if self.root ==None:
                self.root = self.stuff.getroot()
            ex=dialogs.exlude_dialog(self.read_exclude(),self.root)
            ex.showdialog("Check dirs to exclude")
            if ex.haslist:
                self.exclude=ex.getlist()
                self.write_exclude(self.exclude)
        else:
            if self.stuff.connect():
                test = dialogs.base()
                test.showdialog("Please close the browser \nwhere you logged in\n You are now connected")
                self.do_on_connect()
            else:
                test = dialogs.base()
                test.showdialog("Could not connect")
                self.do_on_disconnect()

    def syncall(self):
        if not self.insync:
            self.insync=True
            self.set = setactions()
            thread = Thread(target=self.syncall_threaded)
            thread.setDaemon(True)
            thread.start()


    def syncall_threaded(self):
        baru=True
        while True:
            if os.path.isfile("again") | baru:
                again=self.againread()
                if os.path.isfile("again"):
                    os.remove("again")
                notyet=True
                while notyet:
                    try:
                        self.logger.add("sync started")
                        action, dirtrans,remote = self.set.checkall(self.exclude, self.basepath, self.stuff,again)
                        do = doit(self.stuff.client)
                        do.setlogger(self.logger)
                        do.runactionqueue(action, self.basepath,dirtrans)
                        self.insync=False
                        self.intialsyncdone=True
                        baru=False
                        notyet=False
                        self.logger.add("sync finished(for now)")
                        again=self.againread()
                    except:
                        self.logger.add("internet disruption? will try again soon")
                        pass
                    sleep(20)

    def do_on_connect(self):
        self.login.setVisible(False)
        self.logout.setVisible(True)
        self.updateIcon(True)
        self.root=self.stuff.getroot()
        self.syncall()
        self.watchon()
        self.logger.add("cool...we are now connected")


    def do_on_disconnect(self):
        self.login.setVisible(True)
        self.logout.setVisible(False)
        self.updateIcon(False)
        self.stuff.logout()
        self.stuff = None
        test = dialogs.base()
        test.showdialog("You are logged out")
        self.logger.add("We stopped syncing (i guess, better close this app)")

    def force(self):
        self.intialsyncdone=False
        self.enter()

    def enter(self):
        self.stuff = stuff()
        try:
            if self.stuff.isNowConnected():
                self.do_on_connect()
            else:
                if self.stuff.connect():
                    test = dialogs.base()
                    test.showdialog("Please close the browser \nwhere you logged in\n You are now connected")
                    self.do_on_connect()
                else:
                    test = dialogs.base()
                    test.showdialog("Could not connect")
                    self.do_on_disconnect()
        except:
            test = dialogs.base()
            test.showdialog("Could not connect")

    def exit(self):
        try:
            self.stuff.logout()
            self.do_on_disconnect()
        except:
            self.do_on_disconnect()

    def updateIcon(self, connected):
        if connected:
            self.setIcon(QtGui.QIcon("driveon.ico"))
        else:
            self.setIcon(QtGui.QIcon("driveoff.ico"))

    def write_exclude(self,data):
        file_name = "exclude"
        with open(file_name, 'wb') as x_file:
            pickle.dump(data, x_file)

    def read_exclude(self):
        try:
            if os.path.isfile("exclude"):
                with open("exclude", "rb") as myfile:
                    my_list = pickle.load(myfile)
                return my_list
            else:
                return []
        except:
            print(  "Unexpected error:", sys.exc_info()[0])
            return []


def main():
    global app
    f = systemstuff("/home/remko")
    app = QtGui.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_X11InitThreads)
    app.setQuitOnLastWindowClosed(False)
    w = QtGui.QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon("driveon.ico"), w)
    trayIcon.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    me = singleton.SingleInstance()
    main()
