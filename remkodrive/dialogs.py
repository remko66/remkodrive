from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pickle

class base:

    def __init__(self):
        pass

    def sluiten(self):
        self.d.done(1)

    def showdialog(self,s,x=300,y=300,w=200,h=150):
       self.d = QDialog()
       self.d.setGeometry(x,y,w,h)

       label = QLabel(s,self.d)
       label.move(10,25)
       b1 = QPushButton("ok",self.d)
       b1.move(45,110)
       b1.clicked.connect(self.sluiten)
       self.d.setWindowTitle("Dialog")
       #self.d.setWindowModality(Qt.ApplicationModal)
       self.d.show()
       self.d.exec()




class option:

    def __init__(self):
        pass

    def sluiten(self):
        file_name = "options"
        with open(file_name, 'wb') as x_file:
            pickle.dump(self.edit.toPlainText(), x_file)

        self.d.done(1)

    def showdialog(self,s,x=300,y=300,w=300,h=150):
       self.d = QDialog()
       self.d.setGeometry(x,y,w,h)


       label = QLabel("Please set sync directory(restart app after)",self.d)
       label.move(10,25)
       self.edit= QPlainTextEdit(s,self.d)
       self.edit.setPlainText(s)
       self.edit.resize(280,30)
       self.edit.move(10,50)
       b1 = QPushButton("ok",self.d)
       b1.move(90,110)
       b1.clicked.connect(self.sluiten)
       self.d.setWindowTitle("Dialog")
       #self.d.setWindowModality(Qt.ApplicationModal)
       self.d.show()
       self.d.exec()


class log:

    def __init__(self):
        pass

    def sluiten(self):
        self.d.done(1)

    def showdialog(self,list,x=300,y=300,w=600,h=600):
       self.d = QDialog()
       self.d.setGeometry(x,y,w,h)

       font = QFont()
       font.setFamily('Lucida')
       font.setFixedPitch(True)
       font.setPointSize(10)


       self.console = QTextEdit(self.d)
       self.console.readOnly = True
       self.console.resize(580,560)
       self.console.move(5,5)
       self.console.setReadOnly(True)
       t=""
       for i,l in enumerate(list):
           t+=l[0]+"--"+l[1]+"\n"
       self.console.setText(t)
       b1 = QPushButton("ok", self.d)
       b1.move(233,570)
       b1.clicked.connect(self.sluiten)
       self.d.setWindowTitle("Status")
       #self.d.setWindowModality(Qt.ApplicationModal)
       self.d.show()
       self.d.exec()




class exlude_dialog:

    def __init__(self,exlude_list,folder_list):
        self.folders=folder_list
        self.exclude=exlude_list
        self.haslist=False

    def haslist(self):
        return self.haslist

    def getlist(self):
        return self.exclude

    def sluiten(self):
        self.exclude=[]
        for i in self.q:
            if i.checkState():
                self.exclude.append(i.text())
        self.d.done(len(self.exclude))
        self.haslist=True

    def showdialog(self,s,x=300,y=300,w=200,h=600):
       self.d = QDialog()
       count=0
       self.q=[]
       for i,f in enumerate(self.folders):
           if not f.folder is None:
                    cb=QCheckBox(f.name,self.d)
                    if f.name in self.exclude:
                        cb.setChecked(True)
                    cb.move(10,25*i+25)
                    self.q.append(cb)
                    count+=1
       h = count * 25 + 50
       self.d.setGeometry(x, y, w, h )
       label = QLabel("Exclude these dirs",self.d)

       label.move(10,5)
       b1 = QPushButton("ok",self.d)
       b1.move(70,h-30)
       b1.clicked.connect(self.sluiten)
       self.d.setWindowTitle("Dialog")
       #self.d.setWindowModality(Qt.ApplicationModal)
       self.d.show()
       self.d.exec()
