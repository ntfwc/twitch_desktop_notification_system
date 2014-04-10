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

from _AbstractNotificationLibWrapper import _AbstractNotificationLibWrapper, DEFAULT_DISPLAY_TIME_SECONDS

from gtkPopupNotify.gtkPopupNotify import NotificationStack

from threading import Thread
import gtk
import gobject

MAX_IMAGE_SIZE_VALUE = 70

BACKGROUND_COLOR = gtk.gdk.Color("black")
FOREGROUND_COLOR = gtk.gdk.Color("white")
EDGE_OFFSET_X = 20

HEADER_FONT = "Sans Bold 9"
MESSAGE_FONT = "Sans 8"

class _GtkThread(Thread):
    def run(self):
        gobject.threads_init()
        
        self.notifier = NotificationStack(timeout=DEFAULT_DISPLAY_TIME_SECONDS)
        self.notifier.fontdesc = (HEADER_FONT, MESSAGE_FONT, "Sans 10")
        self.notifier.bg_color = BACKGROUND_COLOR
        self.notifier.fg_color = FOREGROUND_COLOR
        self.notifier.edge_offset_x = EDGE_OFFSET_X
        gtk.main()

    def stop(self):
        gobject.idle_add(lambda: gtk.main_quit())
    

class GtkNotificationLibWrapper(_AbstractNotificationLibWrapper):
    def __init__(self):
        self.gtkThread = _GtkThread()
    
    def init(self):
        self.gtkThread.start()

    def __filterNoneText(self, text):
        if text == None:
            return ""
        return text
    
    def notify(self, title, text):
        text = self.__filterNoneText(text)
        gobject.idle_add(lambda: self.gtkThread.notifier.new_popup(title=title, message=text))
    
    def notifyWithImage(self, title, text, image):
        text = self.__filterNoneText(text)
        gobject.idle_add(lambda: self.gtkThread.notifier.new_popup(title=title, message=text, image=image))

    def getMaxImageSizeValue(self):
        return MAX_IMAGE_SIZE_VALUE

    def stop(self):
        self.gtkThread.stop()
