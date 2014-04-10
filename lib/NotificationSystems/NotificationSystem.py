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

def _getWrapper():
    try:
        import notify2
        from NotifyLibWrappers import Notify2Wrapper
        return Notify2Wrapper(notify2)
    except:
        pass

    try:
        import pynotify
        from NotifyLibWrappers import PyNotifyWrapper
        return PyNotifyWrapper(pynotify)
    except:
        pass
    
    try:
        from GtkNotificationLibWrapper import GtkNotificationLibWrapper
        return GtkNotificationLibWrapper()
    except:
        pass

    raise Exception("Dependencies Not Met!")

class NotificationSystem(object):
    def __init__(self):
        self.libWrapper = _getWrapper()
        self.hasInit = False

    def __assertInit(self):
        if not self.hasInit:
            try:
                self.libWrapper.init()
            except:
                return
            self.hasInit = True

    def notify(self, title, text):
        self.__assertInit()
        if not self.hasInit:
            return
        
        self.libWrapper.notify(title, text)

    def notifyWithImage(self, title, text, image):
        self.__assertInit()
        if not self.hasInit:
            return
        
        self.libWrapper.notifyWithImage(title, text, image)

    def getMaxImageSizeValue(self):
        return self.libWrapper.getMaxImageSizeValue()

    def stop(self):
        if self.hasInit:
            self.libWrapper.stop()
