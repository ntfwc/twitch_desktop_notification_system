class HTTPObject(object):
    def __init__(self, data, lastModified, expires, date):
        self.data = data
        self.lastModified = lastModified
        self.expires = expires
        self.date = date
