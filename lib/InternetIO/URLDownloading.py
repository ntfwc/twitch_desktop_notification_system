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

import urllib2
from InternetIOExceptions import HTTPResponseCodeException, HTTPContentLengthException, MaxDownloadSizeExceededException

def __tryToGetHeaderValue(messageObject, headerName):
    if headerName in messageObject:
        return messageObject[headerName]
    else:
        return None

CONTENT_LENGTH_HEADER = "content-length"

def __tryToGetContentLength(messageObject):
    contentLengthString = __tryToGetHeaderValue(messageObject, CONTENT_LENGTH_HEADER)
    if contentLengthString == None:
        return None
    else:
        return int(contentLengthString)

def __downloadData(openURL, messageObject, maxDownloadSize):
    contentLength = __tryToGetContentLength(messageObject)
    if contentLength != None:
        if contentLength > maxDownloadSize:
            raise MaxDownloadSizeExceededException()
        
        data = openURL.read(contentLength)
        if len(data) != contentLength:
            raise HTTPContentLengthException()
    else:
        data = openURL.read(maxDownloadSize + 1)
        if len(data) > maxDownloadSize:
            raise MaxDownloadSizeExceededException()
    return data

HTTP_OK_CODE = 200

def __checkResponseCode(url, openURL):
    isHTTP = False
    if url.startswith("http"):
        code = openURL.getcode()
        if code != HTTP_OK_CODE:
            raise HTTPResponseCodeException(code)
        

def downloadURLContent(url, maxDownloadSize, timeoutTime):
    u = urllib2.urlopen(url, timeout=timeoutTime)
    try:
        __checkResponseCode(url, u)

        messageObject = u.info()
        return __downloadData(u, messageObject, maxDownloadSize)
    finally:
        u.close()
        

class HTTPObject(object):
    def __init__(self, data, lastModified, expires, date):
        self.data = data
        self.lastModified = lastModified
        self.expires = expires
        self.date = date


HTTP_NOT_MODIFIED_CODE = 304

def downloadHTTPObject(url, maxDownloadSize, timeoutTime):
    u = urllib2.urlopen(url, timeout=timeoutTime)
    try:
        code = u.getcode()
        if code == HTTP_NOT_MODIFIED_CODE:
            return None
        elif code != HTTP_OK_CODE:
            raise HTTPResponseCodeException(code)

        messageObject = u.info()
        
        data = __downloadData(u, messageObject, maxDownloadSize)
        lastModified = __tryToGetHeaderValue(messageObject, "last-modified")
        expires = __tryToGetHeaderValue(messageObject, "expires")
        date = __tryToGetHeaderValue(messageObject, "date")
        
        return HTTPObject(data, lastModified, expires, date)
        
    finally:
        u.close()
    

def downloadHTTPObjectWithCustomHeaders(url, headers, maxDownloadSize, timeoutTime):
    requestObj = urllib2.Request(url)
    for headerName, value in headers:
        requestObj.add_header(headerName, value)
    return downloadHTTPObject(requestObj, maxDownloadSize, timeoutTime)

def downloadHTTPObjectIfModified(url, lastModified, maxDownloadSize, timeoutTime):
    headers = [("if-modified-since", lastModified)]
    try:
        return downloadHTTPObjectWithCustomHeaders(url, headers, maxDownloadSize, timeoutTime)
    except urllib2.HTTPError, e:
        if e.code == HTTP_NOT_MODIFIED_CODE:
            return None
        raise e
    
