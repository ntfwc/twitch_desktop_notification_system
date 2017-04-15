import unittest
from lib.UserStreamData import UserStreamData,parseUserStreamData

RUNNING_STREAM_FILE="tests/v5-sample-responses/stream-running.json"
OFFLINE_STREAM_FILE="tests/v5-sample-responses/stream-offline.json"

class UserStreamDataTest(unittest.TestCase):
    def test_hasSameBasicState(self):
        stream = UserStreamData(True,
                                "title1",
                                "game1",
                                1,
                                "logo1")
        streamWithNewTitle = UserStreamData(True,
                                "title2",
                                "game1",
                                1,
                                "logo1")
        streamWithNewGame = UserStreamData(True,
                                "title1",
                                "game2",
                                1,
                                "logo1")
        streamWithNewViewerCount = UserStreamData(True,
                                "title1",
                                "game1",
                                2,
                                "logo1")
        streamWithNewAvatarUrl = UserStreamData(True,
                                "title1",
                                "game1",
                                1,
                                "logo2")
        offlineStream = UserStreamData(False,
                                None,
                                None,
                                None,
                                None)
        self.assertFalse(stream.hasSameBasicState(streamWithNewTitle))
        self.assertFalse(stream.hasSameBasicState(streamWithNewGame))
        self.assertTrue(stream.hasSameBasicState(streamWithNewViewerCount))
        self.assertTrue(stream.hasSameBasicState(streamWithNewAvatarUrl))
        self.assertFalse(stream.hasSameBasicState(offlineStream))

    def test_parseRunningStream(self):
        parsed = parseUserStreamData(readFile(RUNNING_STREAM_FILE))
        self.assertEquals(True, parsed.isStreaming)
        self.assertEquals("Twitch Plays Pokemon (Enter moves via chat!!!)", parsed.streamTitle)
        self.assertEquals("Twitch Plays", parsed.streamGame)
        self.assertEquals(186, parsed.viewerCount)
        self.assertEquals("https://static-cdn.jtvnw.net/jtv_user_pictures/twitchplayspokemon-profile_image-62a73e208674dfec-300x300.png",
                          parsed.avatarURL)

    def test_parseOfflineStream(self):
        parsed = parseUserStreamData(readFile(OFFLINE_STREAM_FILE))
        self.assertEquals(False, parsed.isStreaming)
        self.assertEquals(None, parsed.streamTitle)
        self.assertEquals(None, parsed.streamGame)
        self.assertEquals(None, parsed.viewerCount)
        self.assertEquals(None, parsed.avatarURL)

def readFile(filePath):
    with open(filePath) as f:
        return f.read()