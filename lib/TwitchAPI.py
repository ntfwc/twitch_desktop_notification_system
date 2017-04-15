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
from UserStreamData import UserStreamData,parseUserStreamData
import json

API_HOST = "api.twitch.tv"
TIMEOUT_TIME = 5.0
API_ACCEPT_HEADER = "application/vnd.twitchtv.v2+json"
CLIENT_ID = "pu6fhw9s3ywb5jxm269p8ef986kcbdu"


def getAPIConnection():
    connection = PersistentHTTPSDownloader(API_HOST, TIMEOUT_TIME)
    connection.setHeader("Accept", API_ACCEPT_HEADER)
    connection.setHeader("Client-ID", CLIENT_ID)
    return connection

MAX_DOWNLOAD_SIZE = 20000

def downloadTwitchAPIObject(apiConnection, requestPath):
    return apiConnection.get(requestPath, MAX_DOWNLOAD_SIZE)

def downloadTwitchAPIObjectWithARetry(apiConnection, requestPath):
    return apiConnection.getWithRetries(requestPath, MAX_DOWNLOAD_SIZE, 1)

STREAM_REQUEST_STRING = "/kraken/streams/%s"

def getUserStreamData(apiConnection, username):
    requestPath = STREAM_REQUEST_STRING % username
    data = downloadTwitchAPIObject(apiConnection, requestPath)
    return parseUserStreamData(data)

def getUserStreamDataWithARetry(apiConnection, username):
    requestPath = STREAM_REQUEST_STRING % username
    data = downloadTwitchAPIObjectWithARetry(apiConnection, requestPath)
    return parseUserStreamData(data)

def _parseAvatarURL(jsonData):
    parsedData = json.loads(jsonData)
    logoURL = parsedData["logo"]
    if logoURL == None:
        return DEFAULT_AVATAR_URL
    
    return logoURL

CHANNEL_REQUEST_STRING = "/kraken/channels/%s"

def getUserAvatarURL(apiConnection, username):
    requestPath = CHANNEL_REQUEST_STRING % username
    data = downloadTwitchAPIObject(apiConnection, requestPath)
    return _parseAvatarURL(data)


