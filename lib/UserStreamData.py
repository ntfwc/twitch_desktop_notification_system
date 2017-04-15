import json

class UserStreamData(object):
    def __init__(self, isStreaming, streamTitle, streamGame, viewerCount, avatarURL):
        self.isStreaming = isStreaming
        self.streamTitle = streamTitle
        self.streamGame = streamGame
        self.viewerCount = viewerCount
        self.avatarURL = avatarURL

    def hasSameBasicState(self, other):
        return (self.isStreaming == other.isStreaming and
               self.streamTitle == other.streamTitle and
               self.streamGame == other.streamGame)


DEFAULT_AVATAR_URL = "http://static-cdn.jtvnw.net/jtv_user_pictures/xarth/404_user_150x150.png"

def parseUserStreamData(jsonData):
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
        avatarURL = __adjustSchema(avatarURL)
        
        if avatarURL == None:
            avatarURL = DEFAULT_AVATAR_URL
        return UserStreamData(True, streamTitle, streamGame, viewerCount, avatarURL)

FALLBACK_SCHEMA = "http:"

def __adjustSchema(URL):
    if URL == None:
        return None
    if URL.startswith("http://") or URL.startswith("https://"):
        return URL
    elif URL.startswith("//"):
        return FALLBACK_SCHEMA + URL
    else:
        return FALLBACK_SCHEMA + "//" + URL
