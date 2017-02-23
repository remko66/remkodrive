import onedrivesdk
import os
from onedrivesdk.helpers import GetAuthCodeServer
import sys
import pickle


class stuff:
    def __init__(self):

        with open("internal1", "rb") as myfile:
            self.client_secret = pickle.load(myfile)
        with open("internal2", "rb") as myfile:
            self.client_id = pickle.load(myfile)
        self.redirect_uri = 'http://localhost:8080/'
        self.api_base_url = 'https://api.onedrive.com/v1.0/'
        self.scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']
        self.client = False
        self.isconnected = False

    def getclient(self):
        return self.client

    def connect(self):
        try:
            http_provider = onedrivesdk.HttpProvider()
            auth_provider = onedrivesdk.AuthProvider(
                http_provider=http_provider,
                client_id=self.client_id,
                scopes=self.scopes)
            self.client = onedrivesdk.get_default_client(client_id=self.client_id,
                                                         scopes=self.scopes)
            auth_url = self.client.auth_provider.get_auth_url(self.redirect_uri)

            # Block thread until we have the code
            code = GetAuthCodeServer.get_auth_code(auth_url, self.redirect_uri)
            if len(code) > 10:
                self.client.auth_provider.authenticate(code, self.redirect_uri, self.client_secret)
                self.client.auth_provider.save_session()
                self.isconnected = True
        except:
            print("Unexpected error:", sys.exc_info()[0])
        return self.isconnected

    def reconnect(self):
        http_provider = onedrivesdk.HttpProvider()
        auth_provider = onedrivesdk.AuthProvider(http_provider,
                                                 self.client_id,
                                                 self.scopes)
        auth_provider.load_session()
        auth_provider.refresh_token()
        self.client = onedrivesdk.OneDriveClient(self.api_base_url, auth_provider, http_provider)
        self.isconnected = True

    def hassaved(self):
        if os.path.isfile("session.pickle"):
            return True
        else:
            return False

    def justconnect(self):
        try:
            if self.hassaved():
                self.reconnect()
            else:
                self.connect()
        except:
            pass

    def isNowConnected(self):
        try:
            self.reconnect()

        except Exception as inst:

            print(type(inst))  # the exception instance

            print(inst.args)
            print(inst)
            self.isconnected = False
        return self.isconnected

    def getclient(self):
        return self.client

    def logout(self):
        self.client = None
        if os.path.isfile("session.pickle"):
            os.remove("session.pickle")

    def getroot(self):
        if self.isconnected:
            collection = self.client.item(drive='me', id='root').children.request().get()
        else:
            collection = None
        return collection

    def getfiles(self, folder='root', path='/', list=[], exclude=[], dirtrans={}):
        print("getfiles", folder, path)
        collection = self.client.item(drive='me', id=folder).children.get()
        for i in collection:
            t = i.folder
            if not t == None:
                if (not i.name in exclude) | (folder != 'root'):
                    p2 = path + i.name + '/'
                    dirtrans[p2] = i
                    list, dirtrans = self.getfiles(folder=i.id, path=p2, list=list, exclude=exclude, dirtrans=dirtrans)

            else:
                g = [folder, path, i]
                list.append(g)

        return list, dirtrans
