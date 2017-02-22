from onedrivestuff import *
from filesystemstuff  import *
from time import *
import os
import datetime
class setactions:
    def __init__(self):
        self.stuf =stuff()


    def modification_date(self,filename):
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)


    def examine(self,full,item):
        if item==None:
            return 0
        loc=self.modification_date(full)
        rem=item.last_modified_date_time
        dif=rem.utcnow()-loc.utcnow()
        dif=round(dif.total_seconds())
        if dif>0:
            return 1
        else:
            if dif<0:
                return 2

    def addaction(self,action,remote,local,remote2="",local2=""):
        a=[action,remote,local,remote2,local2]
        print(a)
        return a

    def getitem(self,localitem,remote,basepath):
        index=None
        localpath=localitem[0].replace(basepath,"")
        if localpath !="/":
            localpath+="/"
        localname=localitem[1]
        for i, r in enumerate(remote):
            if r[1]==localpath:
                if r[2].name==localname:
                    index=r[2]
                    break
        return index

    def folderexists(self,remote,folder,dirtrans):

        ex=False
        index=None
        if folder=="":
            folder="/"
        if folder=="/":
            return True,"root"
        if folder in dirtrans:
            index=dirtrans[folder]
        if index==None:
            if (folder+"/") in dirtrans:
                index=dirtrans[folder+"/"]
        if not index==None:
            ex=True
        return ex,index

    def make_unique(self,original_list):
        unique_list = []
        [unique_list.append(obj) for obj in original_list if obj not in unique_list]
        return unique_list

    def checkfolders(self,remote,folder,action,dirtrans):
        makelist=[]
        count=0
        full=folder
        bool,index=self.folderexists(remote,folder,dirtrans)
        while not bool:
            count+=1
            if count==10:
                break
            i=folder.rfind("/")
            if i<0:
                break
            foldername = folder[i+1:]
            folder=folder[:i]
            under=folder
            if under=="":
                under="/"
            makelist.append([foldername,under])
            bool, index = self.folderexists(remote,folder,dirtrans)
        if bool:
             for foldername in makelist:
                 action.append(self.addaction("newfolder",foldername[0],"",index,foldername[1]))
        return action

    def isinagaindelete(self,full,again):
        isit=False
        for a in again:
            if a[3]==full:
                if a[0]=='delete':
                    isit=True
                    break
        return isit
    def checkall(self,exclude,basepath,client,again):
        actions=[]
        remote,dirtrans=client.getfiles(exclude=exclude)
        system=systemstuff(basepath)
        here=system.buildlist()
        comblist=[]
        for h in here:
            co=h[0]+"/"+h[1]
            co=co.replace("//","/")
            comblist.append(co)
        for i,r in enumerate(remote):
            full=basepath+r[1]+r[2].name
            if not full in comblist:
                if not self.isinagaindelete(full,again):
                    actions.append(self.addaction("download",r[2],full))
                else:
                    actions.append(self.addaction("delete", r[2], full))
            else:
                a=self.examine(full,r[2])
                if a==1:
                    actions.append(self.addaction("download", r[2], full))
                if a==2:
                    actions.append(self.addaction("upload", r[2], full))

        for k in here:
            i=self.getitem(k,remote,basepath)
            if (i==None) | (self.examine(k[0]+"/"+k[1],i)==2):
                actions = self.checkfolders(remote, k[0].replace(basepath,""), actions,dirtrans)
                actions.append(self.addaction("upload", i, k[0],None,k[1]))
        actions=self.make_unique(actions)
        return actions,dirtrans,remote

