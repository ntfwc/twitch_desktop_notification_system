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

DEFAULT_DISPLAY_TIME_SECONDS = 30

class _AbstractNotificationLibWrapper(object):
    def init(self):
        raise NotImplementedError()
    
    def notify(self, title, text):
        raise NotImplementedError()
    
    def notifyWithImage(self, title, text, image):
        raise NotImplementedError()

    def getMaxImageSizeValue(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()
