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

from urlparse import urlparse
from PersistentHTTPDownloaders import PersistentHTTPDownloader, PersistentHTTPSDownloader
from urllib2 import HTTPError
from InternetIOExceptions import HTTPResponseCodeException

def parseURL(url):
    parsedObject = urlparse(url)
    return parsedObject.scheme, parsedObject.netloc, parsedObject.path

HTTP_NOT_MODIFIED_CODE = 304
IF_MODIFIED_SINCE_HEADER = "If-Modified-Since"
#USER_AGENT_HEADER = "User-Agent"
#USER_AGENT = "Python-urllib/2.7"

class ConnectionCachingFetcher(object):
    def __init__(self, timeout):
        self.timeout = timeout
        self.connectionCache = {}

    def __createConnection(self, host, scheme):
        if scheme == "http":
            return PersistentHTTPDownloader(host, self.timeout)
        elif scheme == "https":
            return PersistentHTTPSDownloader(host, self.timeout)
        else:
            raise Exception("Given unhandled scheme '%s'" % (scheme,))

    def __getConnection(self, host, scheme):
        if host in self.connectionCache:
            return self.connectionCache[host]
        else:
            newConnection = self.__createConnection(host, scheme)
            self.connectionCache[host] = newConnection
            return newConnection

    def __downloadHTTPObjectFromConnectionWithARetry(self, connection, path, maxDownloadSize):
        return connection.getHTTPObjectWithRetries(path, maxDownloadSize, 2)

    def downloadHTTPObject(self, url, maxDownloadSize):
        scheme, host, path = parseURL(url)
        if scheme == None or host == None or path == None:
            raise Exception("Given misformatted URL")

        connection = self.__getConnection(host, scheme)
        return self.__downloadHTTPObjectFromConnectionWithARetry(connection, path, maxDownloadSize)

    def __getFromConnectionWithTempHeaders(self, connection, path, headers, maxDownloadSize):
        formerHeaders = connection.headers
        try:
            connection.headers = headers
            return self.__downloadHTTPObjectFromConnectionWithARetry(connection, path, maxDownloadSize)
        finally:
            connection.headers = formerHeaders
    
    def downloadHTTPObjectWithCustomHeaders(self, url, headers, maxDownloadSize):
        scheme, host, path = parseURL(url)
        if scheme == None or host == None or path == None:
            raise Exception("Given misformatted URL")

        connection = self.__getConnection(host, scheme)
        return self.__getFromConnectionWithTempHeaders(connection, path, headers, maxDownloadSize)

    def downloadHTTPObjectIfModified(self, url, lastModified, maxDownloadSize):
        headers = {IF_MODIFIED_SINCE_HEADER : lastModified} #USER_AGENT_HEADER : USER_AGENT}
        try:
            return self.downloadHTTPObjectWithCustomHeaders(url, headers, maxDownloadSize)
        except HTTPResponseCodeException, e:
            if e.code == HTTP_NOT_MODIFIED_CODE:
                return None
            raise e
