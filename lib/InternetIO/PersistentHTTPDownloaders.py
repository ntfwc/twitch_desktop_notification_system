##    Copyright (C) 2014 ntfwc
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from httplib import HTTPConnection, HTTPSConnection
from InternetIOExceptions import HTTPResponseCodeException, HTTPContentLengthException, MaxDownloadSizeExceededException, SafeHTTPException
from HTTPObject import HTTPObject

GET_METHOD = "GET"
HTTP_OK_CODE = 200
CONTENT_LENGTH_HEADER = "content-length"
LAST_MODIFIED_HEADER = "last-modified"
EXPIRES_HEADER = "expires"
DATE_HEADER = "date"

class PersistentHTTPDownloader(object):
    def __init__(self, host, timeout):
        self.host = host
        self.timeout = timeout
        self.connection = None
        self.headers = {}

    def refresh(self):
        self.connection = HTTPConnection(self.host, timeout=self.timeout)
        try:
            self.connection.connect()
        except:
            self.connection = None

    def setHeader(self, header, value):
        self.headers[header] = value

    def __tryToGetHeaderValue(self, response, headerName):
        return response.getheader(headerName, None)

    def __tryToGetContentLength(self, response):
        contentLengthText = self.__tryToGetHeaderValue(response, CONTENT_LENGTH_HEADER)
        if contentLengthText == None:
            return None

        return int(contentLengthText)

    def __readResponseData(self, response, maxDownloadSize):
        contentLength = self.__tryToGetContentLength(response)
        if contentLength != None:
            if contentLength > maxDownloadSize:
                raise MaxDownloadSizeExceededException()
            data = response.read(contentLength)
            if len(data) != contentLength:
                raise HTTPContentLengthException()
        else:
            data = response.read(maxDownloadSize + 1)
            if len(data) > maxDownloadSize:
                raise MaxDownloadSizeExceededException()

        return data

    def __assertConnection(self):
        if self.connection == None:
            self.refresh()
            if self.connection == None:
                raise Exception("Failed to refresh connection")

    def __sendRequestAndReadHTTPObject(self, objectPath, maxDownloadSize):
        self.connection.request(GET_METHOD, objectPath, headers=self.headers)
        response = self.connection.getresponse()
        
        data = self.__readResponseData(response, maxDownloadSize)
        if response.status != HTTP_OK_CODE:
            raise HTTPResponseCodeException(response.status)

        lastModified = self.__tryToGetHeaderValue(response, LAST_MODIFIED_HEADER)
        expires = self.__tryToGetHeaderValue(response, EXPIRES_HEADER)
        date = self.__tryToGetHeaderValue(response, DATE_HEADER)
        
        return HTTPObject(data, lastModified, expires, date)

    def getHTTPObject(self, objectPath, maxDownloadSize):
        self.__assertConnection()
        
        try:
            return self.__sendRequestAndReadHTTPObject(objectPath, maxDownloadSize)
        except SafeHTTPException, e:
            raise e
        except Exception,e:
            self.close()
            raise e

    def get(self, objectPath, maxDownloadSize):
        return self.getHTTPObject(objectPath, maxDownloadSize).data

    def getHTTPObjectWithRetries(self, objectPath, maxDownloadSize, maxNumberOfRetries):
        lastException = None
        for i in xrange(1+maxNumberOfRetries):
            try:
                return self.getHTTPObject(objectPath, maxDownloadSize)
            except Exception,e:
                lastException = e

        raise lastException

    def getWithRetries(self, objectPath, maxDownloadSize, maxNumberOfRetries):
        return self.getHTTPObjectWithRetries(objectPath, maxDownloadSize, maxNumberOfRetries).data

    def close(self):
        if self.connection != None:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None


class PersistentHTTPSDownloader(PersistentHTTPDownloader):
    def refresh(self):
        self.connection = HTTPSConnection(self.host, timeout=self.timeout)
        try:
            self.connection.connect()
        except:
            self.connection = None
