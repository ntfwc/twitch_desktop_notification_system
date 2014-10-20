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

from InternetIO.PersistentHTTPDownloaders import PersistentHTTPDownloader,PersistentHTTPSDownloader
import json

API_HOST = "api.twitch.tv"
TIMEOUT_TIME = 5.0
API_ACCEPT_HEADER = "application/vnd.twitchtv.v2+json"


def getAPIConnection():
    connection = PersistentHTTPSDownloader(API_HOST, TIMEOUT_TIME)
    connection.setHeader("Accept", API_ACCEPT_HEADER)
    return connection

class UserStreamData(object):
    def __init__(self, isStreaming, streamTitle, streamGame, viewerCount, avatarURL):
        self.isStreaming = isStreaming
        self.streamTitle = streamTitle
        self.streamGame = streamGame
        self.viewerCount = viewerCount
        self.avatarURL = avatarURL

    def equals(self, other):
        return (self.isStreaming == other.isStreaming and
               self.streamTitle == other.streamTitle and
               self.streamGame == other.streamGame)

FALLBACK_SCHEMA = "http:"

def __assertSchema(URL):
    if URL == None:
        return None
    if URL.startswith("http://") or URL.startswith("https://"):
        return URL
    elif URL.startswith("//"):
        return FALLBACK_SCHEMA + URL
    else:
        return FALLBACK_SCHEMA + "//" + URL

DEFAULT_AVATAR_URL = "http://static-cdn.jtvnw.net/jtv_user_pictures/xarth/404_user_150x150.png"

def _parseUserStreamData(jsonData):
    parsedData = json.loads(jsonData)
    streamData = parsedData["stream"]
    if streamData == None:
        return UserStreamData(False, None, None, None, None)
    else:
        channelData = streamData["channel"]
        streamTitle = channelData["status"]
        streamGame = streamData["game"]
        viewerCount = streamData["viewers"]
        avatarURL = channelData["logo"]
        avatarURL = __assertSchema(avatarURL)
        
        if avatarURL == None:
            avatarURL = DEFAULT_AVATAR_URL
        return UserStreamData(True, streamTitle, streamGame, viewerCount, avatarURL)

MAX_DOWNLOAD_SIZE = 20000

def downloadTwitchAPIObject(apiConnection, requestPath):
    return apiConnection.get(requestPath, MAX_DOWNLOAD_SIZE)

def downloadTwitchAPIObjectWithARetry(apiConnection, requestPath):
    return apiConnection.getWithRetries(requestPath, MAX_DOWNLOAD_SIZE, 1)

STREAM_REQUEST_STRING = "/kraken/streams/%s"

def getUserStreamData(apiConnection, username):
    requestPath = STREAM_REQUEST_STRING % (username,)
    data = downloadTwitchAPIObject(apiConnection, requestPath)
    return _parseUserStreamData(data)

def getUserStreamDataWithARetry(apiConnection, username):
    requestPath = STREAM_REQUEST_STRING % (username,)
    data = downloadTwitchAPIObjectWithARetry(apiConnection, requestPath)
    return _parseUserStreamData(data)

def _parseAvatarURL(jsonData):
    parsedData = json.loads(jsonData)
    logoURL = parsedData["logo"]
    if logoURL == None:
        return DEFAULT_AVATAR_URL
    
    return logoURL

CHANNEL_REQUEST_STRING = "/kraken/channels/%s"

def getUserAvatarURL(apiConnection, username):
    requestPath = CHANNEL_REQUEST_STRING % (username,)
    data = downloadTwitchAPIObject(apiConnection, requestPath)
    return _parseAvatarURL(data)


