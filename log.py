import time
class log:
    def __init__(self):
        global loglist
        self.log=[]

    def keepsmall(self):
        if len(self.log)>200:
            self.log=self.log[len(self.log)-100:]
            self.giveback()

    def add(self,s):
        self.keepsmall()
        k=time.strftime("%H:%M:%S")
        i=[k,s]
        self.log.append(i)
        self.giveback


    def giveback(self):
        global loglist
        lostlist=self.log
    def tostring(self):
        s=""
        for  t in self.log:
            s+=t

        return s