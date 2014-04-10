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

GET_METHOD = "GET"
HTTP_OK_CODE = 200
CONTENT_LENGTH_HEADER = "content_length"

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

    def __readResponseData(self, response, maxDownloadSize):
        contentLength = response.getheader(CONTENT_LENGTH_HEADER, None)
        if contentLength != None:
            if contentLength > maxDataSize:
                raise MaxDownloadSizeExceededException()
            data = response.read(contentLength)
            if len(data) != contentLength:
                raise HTTPContentLengthException()
        else:
            data = response.read(maxDownloadSize + 1)
            if len(data) > maxDownloadSize:
                raise MaxDownloadSizeExceededException()

        return data

    def __sendRequestAndReadResponse(self, objectPath, maxDownloadSize):
        self.connection.request(GET_METHOD, objectPath, headers=self.headers)
        response = self.connection.getresponse()
        
        data = self.__readResponseData(response, maxDownloadSize)
        if response.status != HTTP_OK_CODE:
            raise HTTPResponseCodeException(response.status)
        
        return data

    def __assertConnection(self):
        if self.connection == None:
            self.refresh()
            if self.connection == None:
                raise Exception("Failed to refresh connection")

    def get(self, objectPath, maxDownloadSize):
        self.__assertConnection()
        
        try:
            return self.__sendRequestAndReadResponse(objectPath, maxDownloadSize)
        except SafeHTTPException, e:
            raise e
        except Exception,e:
            self.close()
            raise e

    def getWithRetries(self, objectPath, maxDownloadSize, maxNumberOfRetries):
        lastException = None
        for i in xrange(1+maxNumberOfRetries):
            try:
                return self.get(objectPath, maxDownloadSize)
            except Exception,e:
                lastException = e

        raise lastException


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
