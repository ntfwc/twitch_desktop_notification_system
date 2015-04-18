##    Copyright (C) 2014-2015 ntfwc
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

from lib.TwitchAPI import getAPIConnection, UserStreamData, getUserStreamData, getUserStreamDataWithARetry
from lib.NotificationSystems.NotificationSystem import NotificationSystem
from lib.UserAvatarCache import UserAvatarCache
from lib.ListFileIO import readList

FOLLOWED_USERS_LIST_FILE = "followedList.txt"
CACHE_DIR = "cache"

import os.path

def checkWorkingDir():
    followedUserListExists = os.path.isfile(FOLLOWED_USERS_LIST_FILE)
    cacheDirExists = os.path.isdir(CACHE_DIR)
    if not followedUserListExists and not cacheDirExists:
        raise Exception("Could not see %s or the %s directory, is the working directory correct?" % (FOLLOWED_USERS_LIST_FILE, CACHE_DIR))
    if not followedUserListExists:
        raise Exception("No %s file detected." % FOLLOWED_USERS_LIST_FILE)
    if not cacheDirExists:
        raise Exception("No %s directory detected" % CACHE_DIR)
    

import re

def isUsernameValid(username):
    regex = re.compile("[a-z0-9_]+\Z")
    return regex.match(username) != None

def getFollowedUsersList():
    followedList = readList(FOLLOWED_USERS_LIST_FILE)
    for i in xrange(len(followedList)):
        username = followedList[i].lower()
        if not isUsernameValid(username):
            raise Exception('username "%s", from followedlist, has invalid characters' % username)
        followedList[i] = username
    return followedList

def createAndInitFollowedUserStatusMap(followedUsersList):
    followedUsersStatusMap = {}
    for user in followedUsersList:
        followedUsersStatusMap[user] = UserStreamData(False, None, None, None, None)

    return followedUsersStatusMap

##import sys,traceback
##
##def printTraceback():
##    exc_type, exc_value, exc_traceback = sys.exc_info()
##    traceback.print_exception(exc_type, exc_value, exc_traceback)

def printException(exception):
    print exception.__class__.__name__ + " : " + exception.message

def printToStdOutSafely(text):
    try:
        print text
    except:
        print text.encode("utf-8")

from time import strftime

def printOutNotification(title, text):
    print "---- " + strftime("%I:%M %p ") + "---- " + title
    if text != None:
        printToStdOutSafely(text)

from time import sleep

class Main(object):
    def __init__(self, apiConnection, followedUsersStatusMap, notificationSystem, avatarCache, cycleSleepTime):
        self.apiConnection = apiConnection
        self.followedUsersStatusMap = followedUsersStatusMap
        self.notificationSystem = notificationSystem
        self.avatarCache = avatarCache
        self.cycleSleepTime = cycleSleepTime

    def sendUserStreamStatusToNotificationSystem(self, user, previousStatus, userStreamStatus):
        if userStreamStatus.isStreaming:
            if previousStatus.isStreaming != True:
                title = "%s is Streaming!" % user
                text = "Title: %s\nGame: %s\nViewer Count: %s" % (userStreamStatus.streamTitle, userStreamStatus.streamGame, userStreamStatus.viewerCount)
                self.avatarCache.setAvatarURL(user, userStreamStatus.avatarURL)
            else:
                title = "%s has updated their stream information" % user
                text = "Title: %s\nGame: %s\nViewer Count: %s" % (userStreamStatus.streamTitle, userStreamStatus.streamGame, userStreamStatus.viewerCount)
        else:
            title = "%s is no longer streaming" % user
            text = None

        printOutNotification(title, text)
        
        avatar = self.avatarCache.getAvatar(user)
        if avatar != None:
            self.notificationSystem.notifyWithImage(title, text, avatar)
        else:
            self.notificationSystem.notify(title, text)

    def updateStatusesAndNotifyOfChanges(self):
        firstUser = True
        for user, recordedStatus in self.followedUsersStatusMap.iteritems():
            if firstUser:
                try:
                    currentStatus = getUserStreamDataWithARetry(self.apiConnection, user)
                except Exception, e:
                    printException(e)
                    #printTraceback()
                    print "Warning: could not check status of user: %s" % user
                    continue
                firstUser = False
            else:
                try:
                    currentStatus = getUserStreamData(self.apiConnection, user)
                except Exception, e:
                    printException(e)
                    #printTraceback()
                    print "Warning: could not check status of user: %s" % user
                    continue
            if not currentStatus.equals(recordedStatus):
                self.followedUsersStatusMap[user] = currentStatus
                self.sendUserStreamStatusToNotificationSystem(user, recordedStatus, currentStatus)

    def mainLoop(self):
        while True:
            self.updateStatusesAndNotifyOfChanges()
            sleep(self.cycleSleepTime)

    def run(self):
        self.updateStatusesAndNotifyOfChanges()
        sleep(self.cycleSleepTime)
        self.mainLoop()


CYCLE_SLEEP_TIME = 5*60

def main():
    try:
        checkWorkingDir()
    except Exception, e:
        print e.message
        return
    try:
        followedUsersList = getFollowedUsersList()
    except Exception, e:
        print e.message
        return
    if len(followedUsersList) == 0:
        print "No users listed in followedList.txt, please add some"
        return
    followedUsersStatusMap = createAndInitFollowedUserStatusMap(followedUsersList)
    
    notificationSystem = NotificationSystem()
    
    apiConnection = getAPIConnection()
    
    avatarCache = UserAvatarCache(apiConnection, notificationSystem.getMaxImageSizeValue())
    avatarCache.open()
    
    try:
        mainProg = Main(apiConnection, followedUsersStatusMap, notificationSystem, avatarCache, CYCLE_SLEEP_TIME)
        mainProg.run()
    except KeyboardInterrupt:
        pass
    finally:
        avatarCache.close()
        notificationSystem.stop()
        apiConnection.close()

if __name__ == "__main__":
    main()
    print "Application Terminated"
