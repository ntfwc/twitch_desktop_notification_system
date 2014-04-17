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

class Avatar(object):
    def __init__(self, url, data, lastModified):
        self.url = url
        self.data = data
        self.lastModified = lastModified

class AvatarStorageSystem(object):
    def open(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()
    
    def commitUncommittedChanges(self):
        raise NotImplementedError()
    
    def rollbackUncommittedChanges(self):
        raise NotImplementedError()
    
    def storeUserAvatarURL(self, user, avatarURL):
        raise NotImplementedError()
    
    def updateUserAvatarURL(self, user, avatarURL):
        raise NotImplementedError()
    
    def deleteUser(self, user):
        raise NotImplementedError()
    
    def storeCachedAvatar(self, avatar):
        raise NotImplementedError()
    
    def updateCachedAvatar(self, avatar):
        raise NotImplementedError()
    
    def deleteCachedAvatar(self, url):
        raise NotImplementedError()
    
    def getUserAvatarURL(self, user):
        raise NotImplementedError()
    
    def getAvatar(self, avatarURL):
        raise NotImplementedError()
    
    def cleanCachedAvatarIfUnused(self, removedURL):
        raise NotImplementedError()

import sqlite3
import os.path

GET_TABLE_NAMES_QUERY = """SELECT name
FROM sqlite_master
WHERE type='table';"""

GET_INDEX_NAMES_QUERY = """SELECT name
FROM sqlite_master
WHERE type='index';"""

NEEDED_TABLE_NAMES = [
    "user_avatar_urls",
    "cached_avatars"
    ]

NEEDED_INDEX_NAMES = [
    "url_search"
    ]

TABLE_DEFINITION_USER_AVATAR_URLS ="""
CREATE TABLE user_avatar_urls (
    user TEXT PRIMARY KEY,
    avatar_url TEXT
    );
"""

TABLE_DEFINITION_CACHED_AVATARS = """
CREATE TABLE cached_avatars (
    url TEXT PRIMARY KEY,
    data BLOB NOT NULL,
    last_modified TEXT NOT NULL
    );
"""

INDEX_DEFINITION_USER_AVATAR_URL_SEARCH = """
CREATE INDEX url_search
ON user_avatar_urls(avatar_url);
"""

class _SQLiteDatabaseConnectionManager(object):
    def __init__(self, filePath):
        self.filePath = filePath
        self.conn = None

    def __getSingleTextColumnResultQueryAsSet(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        tablesNames = set()
        for value in cursor.fetchall():
            tablesNames.add(value[0].lower())
        return tablesNames

    def __resultsContainEverythingInList(self, query, aList):
        queryResults = self.__getSingleTextColumnResultQueryAsSet(query)
        for item in aList:
            if item not in queryResults:
                return False
        return True

    def __databaseHasCorrectTableNames(self):
        return self.__resultsContainEverythingInList(GET_TABLE_NAMES_QUERY, NEEDED_TABLE_NAMES)

    def __databaseHasCorrectIndexNames(self):
        return self.__resultsContainEverythingInList(GET_INDEX_NAMES_QUERY, NEEDED_INDEX_NAMES)

    def __isDatabaseValid(self):
        return self.__databaseHasCorrectTableNames() and self.__databaseHasCorrectIndexNames()

    def __createTable(self, tableDefinition):
        self.conn.execute(tableDefinition)

    def __createIndex(self, indexDefinition):
        self.conn.execute(indexDefinition)

    def __createDatabase(self):
        self.__createTable(TABLE_DEFINITION_USER_AVATAR_URLS)
        self.__createTable(TABLE_DEFINITION_CACHED_AVATARS)
        self.__createIndex(INDEX_DEFINITION_USER_AVATAR_URL_SEARCH)
    
    def createConnection(self):
        fileExists = os.path.isfile(self.filePath)
        if not fileExists and os.path.exists(self.filePath):
            raise Exception("Given file path is not a file")

        self.conn = sqlite3.connect(self.filePath)
        
        databaseIsValid = True
        if fileExists:
            databaseIsValid = self.__isDatabaseValid()
        else:
            self.__createDatabase()
            
        if not databaseIsValid:
            raise Exception("Given invalid database")

        return self.conn

BEGIN_TRANSACTION_COMMAND = """
BEGIN TRANSACTION;
"""

STORE_USER_AVATAR_URL_COMMAND = """
INSERT INTO user_avatar_urls
VALUES(?,?);
"""

STORE_CACHED_AVATAR_COMMAND = """
INSERT INTO cached_avatars
VALUES(?,?,?);
"""

QUERY_GET_USER_AVATAR_URL = """
SELECT avatar_url
FROM user_avatar_urls
WHERE user == ?;
"""

QUERY_GET_CACHED_AVATAR = """
SELECT data, last_modified
FROM cached_avatars
WHERE url == ?;
"""

UPDATE_USER_AVATAR_URL_COMMAND = """
UPDATE user_avatar_urls
SET avatar_url = ?
WHERE user == ?;
"""

QUERY_DOES_URL_HAVE_AVATAR = """
SELECT EXISTS(
SELECT 1
FROM cached_avatars
WHERE url == ?
);
"""

UPDATE_CACHED_AVATAR_COMMAND = """
UPDATE cached_avatars
SET data = ?, last_modified = ?
WHERE url = ?;
"""

QUERY_DOES_URL_HAVE_USER = """
SELECT EXISTS(
SELECT 1
FROM user_avatar_urls
WHERE avatar_url == ?
);
"""

DELETE_USER_COMMAND = """
DELETE
FROM user_avatar_urls
WHERE user = ?;
"""

DELETE_CACHED_AVATAR_COMMAND = """
DELETE
FROM cached_avatars
WHERE url = ?;
"""


class SQLiteAvatarStorageSystem(AvatarStorageSystem):    
    def __init__(self, filePath):
        self.filePath = filePath
        self.conn = None
        self.uncommittedChanges = False

    def open(self):
        self.conn = _SQLiteDatabaseConnectionManager(self.filePath).createConnection()

    def close(self):
        self.conn.close()

    def __runSQLCommand(self, command):
        self.conn.execute(command)

    def __runSQLCommandWithParameters(self, command, parameters):
        self.conn.execute(command, parameters)

    def commitUncommittedChanges(self):
        if self.uncommittedChanges:
            self.conn.commit()

    def rollbackUncommittedChanges(self):
        if self.uncommittedChanges:
            self.conn.rollback()

    def storeUserAvatarURL(self, user, avatarURL):
        self.__runSQLCommandWithParameters(STORE_USER_AVATAR_URL_COMMAND, (user, avatarURL))
        self.uncommittedChanges = True

    def updateUserAvatarURL(self, user, avatarURL):
        self.__runSQLCommandWithParameters(UPDATE_USER_AVATAR_URL_COMMAND, (avatarURL, user))
        self.uncommittedChanges = True

    def deleteUser(self, user):
        self.__runSQLCommandWithParameters(DELETE_USER_COMMAND, (user,))
        self.uncommittedChanges = True

    def storeCachedAvatar(self, avatar):
        self.__runSQLCommandWithParameters(STORE_CACHED_AVATAR_COMMAND, (avatar.url, buffer(avatar.data), avatar.lastModified))
        self.uncommittedChanges = True

    def updateCachedAvatar(self, avatar):
        self.__runSQLCommandWithParameters(UPDATE_CACHED_AVATAR_COMMAND, (buffer(avatar.data), avatar.lastModified, avatar.url))
        self.uncommittedChanges = True

    def deleteCachedAvatar(self, url):
        self.__runSQLCommandWithParameters(DELETE_CACHED_AVATAR_COMMAND, (url,))
        self.uncommittedChanges = True

    def __getCursorForQueryWithParameters(self, query, parameters):
        cursor = self.conn.cursor()
        cursor.execute(query, parameters)
        return cursor

    def __getAllResultsOfQueryWithParameters(self, query, parameters):
        cursor = self.__getCursorForQueryWithParameters(query, parameters)
        return cursor.fetchall()

    def __getResultOfSingleRowResultQueryWithParameters(self, query, parameters):
        rows = self.__getAllResultsOfQueryWithParameters(query, parameters)
        if len(rows) == 0:
            return None
        else:
            return rows[0]

    def __getResultOfSingleRowSingleColumnQueryWithParameters(self, query, parameters):
        row = self.__getResultOfSingleRowResultQueryWithParameters(query, parameters)
        if row == None:
            return None
        return row[0]

    def doesURLHaveAvatarRecord(self, url):
        return self.__getResultOfSingleRowSingleColumnQueryWithParameters(QUERY_DOES_URL_HAVE_AVATAR, (url,)) == 1
    
    def doesURLHaveUser(self, url):
        return self.__getResultOfSingleRowSingleColumnQueryWithParameters(QUERY_DOES_URL_HAVE_USER, (url,)) == 1

    def getUserAvatarURL(self, user):
        avatarURL = self.__getResultOfSingleRowSingleColumnQueryWithParameters(QUERY_GET_USER_AVATAR_URL, (user,))
        if avatarURL == None:
            return None
        return str(avatarURL)

    def getAvatar(self, avatarURL):
        avatarRow = self.__getResultOfSingleRowResultQueryWithParameters(QUERY_GET_CACHED_AVATAR, (avatarURL,))
        if avatarRow == None:
            return None

        data = str(avatarRow[0])
        lastModified = str(avatarRow[1])

        return Avatar(avatarURL, data, lastModified)

    def cleanCachedAvatarIfUnused(self, removedURL):
        if self.doesURLHaveUser(removedURL):
            return

        self.deleteCachedAvatar(removedURL)
