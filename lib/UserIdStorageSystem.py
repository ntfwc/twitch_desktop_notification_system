import anydbm

DBM_FILE = "cache/clientIds.dbm"

class UserIdStorageSystem(object):
    def __init__(self):
        self.dbm = anydbm.open(DBM_FILE, "c")
    
    def hasUserId(self, userName):
        return userName in self.dbm
    
    def getUserId(self, userName):
        return self.dbm.get(userName)

    def setUserId(self, userName, userId):
        self.dbm[userName] = userId

    def createMapCopy(self):
        mapCopy = {}
        for userName, clientId in self.dbm.items():
            mapCopy[userName] = clientId
        return mapCopy

    def close(self):
        self.dbm.close()
