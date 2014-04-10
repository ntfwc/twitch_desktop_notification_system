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

class SafeHTTPException(Exception):
    pass

class HTTPResponseCodeException(SafeHTTPException):
    def __init__(self, code):
        Exception.__init__(self, "Given non ok response code: %s" % (code,) )
        self.code = code

class HTTPContentLengthException(SafeHTTPException):
    def __init__(self):
        Exception.__init__(self, "Reported content size incorrect")

class MaxDownloadSizeExceededException(Exception):
    def __init__(self):
        Exception.__init__(self, "Maximum download size exceeded")
