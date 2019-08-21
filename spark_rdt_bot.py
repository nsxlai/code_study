#!/usr/bin/env python
import json
import sys
import requests
import getopt

'''
{
            "id": "Y2lzY29zcGFyazovL3VzL1JPT00vYjFkOGJlYjAtMzJhMy0xMWU4LTgzMTAtNzc1NzRmODliODU2",
            "title": "Novum Model S RDT",
            "type": "group",
            "isLocked": false,
            "lastActivity": "2018-04-13T03:59:43.974Z",
            "creatorId": "Y2lzY29zcGFyazovL3VzL1BFT1BMRS81NGYzZjU0ZC03Yjk0LTRlZWQtOWU4Mi03OWE4YTE0N2M5YWQ",
            "created": "2018-03-28T16:18:47.963Z"
        }
'''
MY_ACCESS_TOKEN = "NGQyN2MyYjgtM2ZlZi00ZTBiLWFjMTItM2ZlNGEzYWM2YmM3MjdhNTNmNDItZDZm"
ROOM_ACCESS_TOKEN = "Y2lzY29zcGFyazovL3VzL1JPT00vYjFkOGJlYjAtMzJhMy0xMWU4LTgzMTAtNzc1NzRmODliODU2"
ROOM_NAME = "Novum Model S RDT"  # Room name
C_MESSAGE = 'This is a test 3'  # Message to the room


# try:
#     MEMBERS = ['raylai@cisco.com', ]
#     opts, args = getopt.getopt(sys.argv[1:],"h:r:m:p:t:",["help=","room=","msg=","people=","token="])
#
#     ACCESS_TOKEN = "NGQyN2MyYjgtM2ZlZi00ZTBiLWFjMTItM2ZlNGEzYWM2YmM3MjdhNTNmNDItZDZm" #Access Token
#     ROOM_NAME	 = "Novum Model S RDT" #Room name
#     YOUR_MESSAGE = '' #Message to the room
#     MEMBERS      = []
#
#     for opt, arg in opts:
#             if opt in ("-h","--help"):
#                     print "spark_rdt_bot.py -h <help> -r <room name> -m <message> -p <list of emails in group> -t <access token>"
#             elif opt in ("-r","--room"):
#                     ROOM_NAME = arg
#             elif opt in ("-m","--msg"):
#                     YOUR_MESSAGE = arg
#             elif opt in ("-p","--people"):
#                     MEMBERS = arg.strip('[]').split(',')
#             elif opt in ("-t","--token"):
#                     ACCESS_TOKEN = arg
#             else:
#                     pass
#
#     print ACCESS_TOKEN
#     print ROOM_NAME
#     print YOUR_MESSAGE
#     print MEMBERS
# except:
#     print "spark_rdt_bot.py -h <help> -r <room name> -m <message> -p <list of emails in group> -t <access token>"
#     quit()

# sets the header to be used for authentication and data format to be sent.
def setHeaders():
    accessToken_hdr = 'Bearer ' + MY_ACCESS_TOKEN
    spark_header = {'Authorization': accessToken_hdr, 'Content-Type': 'application/json; charset=utf-8'}
    return spark_header


# check if spark room already exists.  If so return the room ID
def findRoom(the_header, room_name):
    roomId = None
    uri = 'https://api.ciscospark.com/v1/rooms'
    resp = requests.get(uri, headers=the_header)
    resp = resp.json()
    for room in resp["items"]:
        if room["title"] == room_name:
            # print room
            # print "MISSION: findRoom: REPLACE None WITH CODE THAT PARSES JSON TO ASSIGN ROOM ID VALUE TO VARIABLE roomId")
            roomId = room["id"]
            # print "findRoom: " + roomId + "\n"
            break
    return (roomId)


# checks if room already exists and if true returns that room ID. If not creates a new room and returns the room id.
def createRoom(the_header, room_name):
    roomId = findRoom(the_header, room_name)
    if roomId == None:
        roomInfo = {"title": room_name}
        uri = 'https://api.ciscospark.com/v1/rooms'
        resp = requests.post(uri, json=roomInfo, headers=the_header)
        var = resp.json()
        # print "MISSION: createRoom: REPLACE None WITH CODE THAT PARSES JSON TO ASSIGN ROOM ID VALUE TO VARIABLE roomId."
        roomId = var["id"]
    # print "createRoom: " + roomId + "\n\n"
    return (roomId)


# adds a new member to the room.  Member e-mail is test@test.com
def addMembers(the_header, roomId):
    for member in MEMBERS:
        member = {"roomId": roomId, "personEmail": member, "isModerator": False}
        uri = 'https://api.ciscospark.com/v1/memberships'
        resp = requests.post(uri, json=member, headers=the_header)
    return MEMBERS


# posts a message to the room
def postMsg(the_header, roomId, message):
    message = {"roomId": roomId, "text": message}
    uri = 'https://api.ciscospark.com/v1/messages'
    resp = requests.post(uri, json=message, headers=the_header)


# print "postMsg JSON: " + resp.json()
# print resp.json()

# MISSION: WRITE CODE TO RETRIEVE AND DISPLAY DETAILS ABOUT THE ROOM.
def getRoomInfo(the_header, roomId):
    print
    "In function getRoomInfo:\n"
    # MISSION: Replace None in the uri variable with the Spark REST API call
    uri = "https://api.ciscospark.com/v1/rooms/" + roomId
    if uri == None:
        sys.exit("Please add the uri call to get room details.  See the Spark API Ref Guide")
    resp = requests.get(uri, headers=the_header)
    resp = resp.json()
    for key, item in resp.items():
        print
        key + ": " + str(item)
    return resp


if __name__ == '__main__':
    # if ACCESS_TOKEN==None or ROOM_NAME==None or YOUR_MESSAGE==None:
    #     sys.exit("Please check that variables ACCESS_TOKEN, ROOM_NAME and YOUR_MESSAGE have values assigned.")

    # Fetch the standard header format with the given access token
    header = setHeaders()
    # passing the ROOM_NAME for the room to be created
    # room_id=createRoom(header,ROOM_NAME)
    # room_id = findRoom(header, ROOM_NAME)
    # if room_id == None:
    #     sys.exit("Please check that functions findRoom and createRoom return the room ID value.")
    # passing roomId to members function here to add member to the room.
    # addMembers(header,room_id)

    # passing roomId to message function here to Post Message to a room.
    postMsg(header, ROOM_ACCESS_TOKEN, C_MESSAGE)

    # print("MISSION: ADD FUNCTION CALL getRoomInfo(header,room_id)")
    # getRoomInfo(header,room_id)