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

from StringIO import StringIO

from _AbstractNotificationLibWrapper import _AbstractNotificationLibWrapper, DEFAULT_DISPLAY_TIME_SECONDS

DEFAULT_DISPLAY_TIME_MILLISECONDS = int(1000*DEFAULT_DISPLAY_TIME_SECONDS)
MAX_IMAGE_SIZE_VALUE = 48

APP_NAME = "twitch_notifier"

SPECIAL_CHARACTER_ENCODE_DICT = {
        "&" : "&amp;",
        "<" : "&lt;",
        ">" : "&gt;",
        "'" : "&apos;",
        '"' : "&quot;"
    }

class _FuncCallNotify(object):
    def __init__(self, libWrapper, title, text):
        self.libWrapper = libWrapper
        self.title = title
        self.text = text

    def run(self):
        self.libWrapper._basic_notify(self.title, self.text)

class _FuncCallNotifyWithImage(_FuncCallNotify):
    def __init__(self, libWrapper, title, text, image):
        _FuncCallNotify.__init__(self, libWrapper, title, text)
        self.image = image

    def run(self):
        self.libWrapper._basic_notifyWithImage(self.title, self.text, self.image)

class PyNotifyWrapper(_AbstractNotificationLibWrapper):
    def __init__(self, notifyModule):
        self.notifyModule = notifyModule
    
    def init(self):
        if not self.notifyModule.init(APP_NAME):
            raise Exception("Could not init notification lib")

    def refresh(self):
        self.stop()
        self.init()

    def __encodeSpecialCharactersInText(self, text):
        stringBuf = StringIO()
        for c in text:
            if c in SPECIAL_CHARACTER_ENCODE_DICT:
                stringBuf.write(SPECIAL_CHARACTER_ENCODE_DICT[c])
            else:
                stringBuf.write(c)

        return stringBuf.getvalue()

    def _createNotification(self, title, text):
        if text == None:
            return self.notifyModule.Notification(title)
        text = self.__encodeSpecialCharactersInText(text)
        return self.notifyModule.Notification(title, text)

    def __createNotificationObject(self, title, text):
        n = self._createNotification(title, text)
        n.set_timeout(DEFAULT_DISPLAY_TIME_MILLISECONDS)
        return n

    def _basic_notify(self, title, text):
        n = self.__createNotificationObject(title, text)
        if not n.show():
            raise Exception("Could not send notification")

    def _basic_notifyWithImage(self, title, text, image):
        n = self.__createNotificationObject(title, text)
        n.set_icon_from_pixbuf(image)
        if not n.show():
            raise Exception("Could not send notification")

    def __tryToRefresh(self):
        try:
            self.refresh()
            return True
        except:
            print "Error: Failed to refresh notification system! :("
            return False

    def __tryToRunNotificationFunc(self, notificationFunc):        
        try:
            notificationFunc.run()
        except:
            if self.__tryToRefresh():
                try:
                    notificationFunc.run()
                except:
                    print "Error: Could not send notification! :("
            else:
                print "Error: Could not send notification! :("

    def notify(self, title, text):
        notificationFunc = _FuncCallNotify(self, title, text)
        self.__tryToRunNotificationFunc(notificationFunc)

    def notifyWithImage(self, title, text, image):
        notificationFunc = _FuncCallNotifyWithImage(self, title, text, image)
        self.__tryToRunNotificationFunc(notificationFunc)

    def getMaxImageSizeValue(self):
        return MAX_IMAGE_SIZE_VALUE

    def stop(self):
        self.notifyModule.uninit()

class Notify2Wrapper(PyNotifyWrapper):
    pass
    
