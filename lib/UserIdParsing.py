import json

def parseUserIdMap(jsonData):
    parsedData = json.loads(jsonData)
    users = parsedData["users"]
    
    userIdMap = {}
    for user in users:
        name = user["name"]
        userId = user["_id"]
        userIdMap[name] = userId
    return userIdMap
