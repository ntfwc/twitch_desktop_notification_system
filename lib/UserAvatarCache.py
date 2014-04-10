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

from TwitchAPI import getUserAvatarURL
from ImageParsing import parseDataToPixBuf, filterImageDataToVersionWithinSizeRestriction
from InternetIO.URLDownloading import downloadHTTPObject, downloadHTTPObjectIfModified
from AvatarStorageSystem import Avatar
from AvatarStorageSystem import SQLiteAvatarStorageSystem

TIMEOUT_TIME = 5.0
MAX_DOWNLOAD_SIZE = 2*1024*1024

CACHE_FILE = "cache/avatarCache.sqlite"

class PersistentAvatarCache(object):
    def __init__(self, filePath, maxAvatarSizeValue):
        self.storageSystem = SQLiteAvatarStorageSystem(filePath)
        self.maxAvatarSizeValue = maxAvatarSizeValue

    def open(self):
        self.storageSystem.open()

    def close(self):
        self.storageSystem.close()

    def __convertHTTPObjectToAvatar(self, url, httpObj):
        data = filterImageDataToVersionWithinSizeRestriction(httpObj.data, self.maxAvatarSizeValue)
        lastModified = httpObj.lastModified
        return Avatar(url, data, lastModified)

    def __downloadAvatar(self, avatarURL):
        httpObj = downloadHTTPObject(avatarURL, MAX_DOWNLOAD_SIZE, TIMEOUT_TIME)
        return self.__convertHTTPObjectToAvatar(avatarURL, httpObj)

    def __updateRecordedAvatarURL(self, user, oldURL, newURL):
        self.storageSystem.updateUserAvatarURL(user, newURL)
        self.storageSystem.cleanCachedAvatarIfUnused(oldURL)

    def __getAvatarURL(self, user, avatarURL):
        recordedAvatarURL = self.storageSystem.getUserAvatarURL(user)
        if avatarURL == None:
            return recordedAvatarURL
        
        if recordedAvatarURL == None:
            self.storageSystem.storeUserAvatarURL(user, avatarURL)
        elif recordedAvatarURL != avatarURL:
            self.__updateRecordedAvatarURL(user, recordedAvatarURL, avatarURL)

        return avatarURL

    def __downloadAvatarIfUnmodified(self, avatarURL, lastModified):
        httpObj = downloadHTTPObjectIfModified(avatarURL, lastModified, MAX_DOWNLOAD_SIZE, TIMEOUT_TIME)
        if httpObj == None:
            return None
        return self.__convertHTTPObjectToAvatar(avatarURL, httpObj)

    def __refreshAvatar(self, cachedAvatar):
        try:
            newAvatar = self.__downloadAvatarIfUnmodified(cachedAvatar.url, cachedAvatar.lastModified)
        except:
            return cachedAvatar
        if newAvatar == None:
            return cachedAvatar
        
        self.storageSystem.updateCachedAvatar(newAvatar)
        return newAvatar

    def getAvatar(self, user, avatarURL):
        try:
            avatarURL = self.__getAvatarURL(user, avatarURL)
            if avatarURL == None:
                return None
            cachedAvatar = self.storageSystem.getAvatar(avatarURL)
            if cachedAvatar == None:
                avatar = self.__downloadAvatar(avatarURL)
                self.storageSystem.storeCachedAvatar(avatar)
            else:
                avatar = self.__refreshAvatar(cachedAvatar)

            self.storageSystem.commitUncommittedChanges()

            return avatar.data
        except Exception, e:
            self.storageSystem.rollbackUncommittedChanges()
            raise e

class UserAvatarCache(object):
    def __init__(self, apiConnection, maxAvatarSizeValue):
        self.apiConnection = apiConnection
        self.avatarURLDict = {}
        self.avatarDict = {}
        self.persistentCache = PersistentAvatarCache(CACHE_FILE, maxAvatarSizeValue)

    def open(self):
        self.persistentCache.open()

    def close(self):
        self.persistentCache.close()

    def setAvatarURL(self, user, url):
        self.avatarURLDict[user] = url
        
    def __getUserAvatarAsPixBufImage(self, user, avatarURL):
        imageData = self.persistentCache.getAvatar(user, avatarURL)
        pixBuf = parseDataToPixBuf(imageData)
        
        return pixBuf

    def __getAvatarURL(self, user):
        if user not in self.avatarURLDict:
            try:
                url = getUserAvatarURL(self.apiConnection, user)
            except:
                return None
            self.setAvatarURL(user, url)
            return url
        else:
            return self.avatarURLDict[user]

    def getAvatar(self, user):
        avatarURL = self.__getAvatarURL(user)
        if avatarURL not in self.avatarDict:
            try:
                avatar = self.__getUserAvatarAsPixBufImage(user, avatarURL)
            except:
                return None
            self.avatarDict[avatarURL] = avatar
            return avatar
        else:
            return self.avatarDict[avatarURL]
