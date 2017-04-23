import unittest
from lib.UserIdParsing import parseUserIdMap

SINGLE_USER_FILE="tests/v5-sample-responses/getUser.json"
MULTIPLE_USER_FILE="tests/v5-sample-responses/getUsers_multiple.json"

class UserIdParsingTest(unittest.TestCase):
    def test_parseSingleUserResponse(self):
        userIdMap = parseUserIdMap(readFile(SINGLE_USER_FILE))
        self.assertEquals(1, len(userIdMap))
        self.assertEquals("56648155", userIdMap["twitchplayspokemon"])
    
    def test_parseMultipleUserResponse(self):
        userIdMap = parseUserIdMap(readFile(MULTIPLE_USER_FILE))
        self.assertEquals(2, len(userIdMap))
        self.assertEquals("56648155", userIdMap["twitchplayspokemon"])
        self.assertEquals("149747285", userIdMap["twitchpresents"])

def readFile(filePath):
    with open(filePath) as f:
        return f.read()
