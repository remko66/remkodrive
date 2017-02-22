from filesystemstuff import  *
import time
import onedrivesdk


class doit:
    def __init__(self,client):
        self.client=client
    def setlogger(self,logger):
        self.logger=logger

    def download(self,item,full,basepath):
        fs=systemstuff(basepath)
        path=os.path.dirname(full)
        fs.mkdir(path)
        print(basepath+path)
        t=item.last_modified_date_time
        c=time.mktime(t.timetuple())
        print("downloading",item.name,basepath,full)
        self.logger.add("downloading "+full)
        self.client.item(drive='me', id=item.id).download( full)
        os.utime(full, (c,c))
        print("download",id,full)

    def upload(self,item,path,name,basepath,dirtrans):
        path=path.replace(basepath,"")
        if item==None:
            if path in dirtrans:
                item=dirtrans[path]
            else:
                if (path+"/") in dirtrans:
                    item=dirtrans[path+"/"]
        full=basepath+path+"/"+name
        if path=='/':
            returned_item = self.client.item(drive='me', id='root').children[name].upload(full)
        else:
            returned_item = self.client.item(drive='me', id=item.id).children[name].upload(full)
        print("uploading",full)
        self.logger.add("uploading "+full)
        t = returned_item.last_modified_date_time
        c = time.mktime(t.timetuple())
        os.utime( full, (c, c))
        return returned_item
    def delete(self,item,path):
        try:
            returned_item = self.client.item(drive='me', id=item.id).delete()
        except:
            pass

    def newfolder(self,name,parent,dirtrans):
        if parent=="/":
            item='root'
        else:
            item=dirtrans[parent].id
        f = onedrivesdk.Folder()
        i = onedrivesdk.Item()
        i.name = name
        i.folder = f

        returned_item = self.client.item(drive='me', id=item).children.add(i)
        if parent=="/":
            parent=""
        newfolder=parent+"/"+name
        dirtrans[newfolder]=returned_item
        print("newfoldermade",newfolder)
        self.logger.add("new folder "+newfolder)
        return dirtrans



    def runactionqueue(self,actions,basepath,dirtrans):
        for a in actions:
            if a[0]=='download':
                self.download(a[1],a[2],basepath)
            if a[0]=='upload':
                self.upload(a[1],a[2],a[4],basepath,dirtrans)
            if a[0]=='newfolder':
                dirtrans=self.newfolder(a[1],a[4],dirtrans)
            if a[0] == 'delete':
                 self.delete(a[1], a[2])
        return dirtrans



