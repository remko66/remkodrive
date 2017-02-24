import sys
import hashlib
import os



class systemstuff:
    def __init__(self,basepath):
        self.BUF_SIZE = 65536
        self.basepath=basepath

    def mkdir(self, _dir):
        if os.path.isdir(_dir):
            pass
        elif os.path.isfile(_dir):
            raise OSError("%s exists as a regular file." % _dir)
        else:
            parent, directory = os.path.split(_dir)
            print(parent,directory)
            if parent and not os.path.isdir(parent): self.mkdir(parent)
            print(_dir)
            if directory:
                os.mkdir(_dir)


    def hashfile(self,path):
        sha1 = hashlib.sha1()
        with open(self.basepath+path, 'rb') as f:
            while True:
                data = f.read(self.BUF_SIZE)
                if not data:
                    break

                sha1.update(data)
        return sha1.sha1.hexdigest()


    def buildlist(self,path="/"):
        try:

            list=[]
            for path, dirs, files in os.walk(self.basepath+path):
                for f in files:
                    if not "." in path:
                        list.append([path,f])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        return list
