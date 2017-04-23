import anydbm

DBM_FILE = "cache/clientIds.dbm"

class UserIdStorageSystem(object):
    def __init__(self):
        self.dbm = anydbm.open(DBM_FILE, "c")

    def getUserId(self, userName):
        return self.dbm.get(userName)
    
    def setUserId(self, userName, userId):
        self.dbm[userName] = userId
