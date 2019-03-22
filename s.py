import socket
import threading, Queue
import hashlib
import sys
from time import gmtime, strftime
import time
import os
import json



HOST = '127.0.0.1'
PORT = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
mylist = list()
currentConnections = list()
clients = {
    #e.g:  'Daniel': connectionOBJECT
}
buffer = ""
chatname = "Year 3 Group chat"
debug = 0
newclient = ""
usernameTaken = 0
# This is the buffer string
# when input comes in from a client it is added
# into the buffer string to be relayed later
# to different clients that have connected
# Each message in the buffer is separated by a colon :


# custom say hello command
def log(message):
    timestamp = str(strftime("[%d %b %Y - %H:%M:%S]", gmtime()))
    f = open("Logs/chat_log_"+ dateString +".txt","a+")
    f.write(timestamp+" "+message+"\n")
    f.close()
def getTimestamp():
    time = strftime("[%H:%M:%S]", gmtime())
    return time
def getChatName():
    return chatname
def setChatName(newName):
    global chatname
    chatname = newName
def getClientCon(name):
    clientCon = clients[name]
    return clientCon
def getClientName(con):
    clientName =  clients.keys()[clients.values().index(conn)]
    return clientName
def getClientList():
    population = len(clients)
    message = str(population) + " clients connected. Clients: "
    for client in clients.keys():
        message = message + "\n" + client
    return message
def messageAll(message):
    for client in clients.values():
        client.send(message)
def getMessageCount():
    split = buffer.split(':')
    messages = len(split)
    return messages
def messageInfo(message):
    message = "<info>"+message+"</info>"
    return message
def messageMsg(message):
    message = "<msg>"+message+"</msg>"
    return message
def hashData(unhashedData):
    hash = hashlib.md5()
    hash.update(unhashedData)
    hashedData = hash.hexdigest()
    finishedData = "<hash "+hashedData+">-"+unhashedData
    return finishedData
def verifyHash(data):
    split = data.split('-')
    firstHash = split[0]
    secondHash = split[1]
    firstHash = firstHash[6:-1]

    hash = hashlib.md5()
    hash.update(secondHash)
    secondHash = hash.hexdigest()
    if debug == 1:
        print("[DEBUG] First hash:" + firstHash)
        print("[DEBUG] Second hash:" + secondHash)
    if firstHash == secondHash:
        return 1
    else:
        return 0
def stripHash(data):
    data = data.split('-', 1)
    stripped = data[1]
    return stripped

timestamp = getTimestamp()
date = strftime("%a_%d_%b_%Y", gmtime())
dateString = str(date)
print("Server started.")
log("\n\n-----------------------------------------"+"Server started at "+str(strftime("[%d %b %Y - %H:%M:%S]", gmtime()))
+"-----------------------------------------")

def parseInput(data, con):
    global buffer
    global usernameTaken
    print "parsing..."

    if verifyHash(data) == 1:
        data = stripHash(data)

        if "<servertime>" in data:
            formatted= strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
            con.send(hashData(messageInfo(str(formatted))))
        elif "<time>" in data:
            time = strftime("%H:%M:%S", gmtime())
            timeString = str("Time: " + time)
            con.send(hashData(messageInfo(timeString)))
        elif "<date>" in data:
            date=strftime("%a, %d %b %Y", gmtime())
            con.send(hashData(messageInfo(str(date))))
        elif "<show>" in data:
            count = buffer.count(":")
            count = str(count)
            first_msg = buffer.split(":")
            show = " - ".join(str(x) for x in first_msg)
            show = "there are "+ count +" previous messages " + show
            print show
            con.send(hashData(show))
        elif "<newclient " in data: #<newclient Daniel>
            tagless = data[1:-1]
            splitMessage = tagless.split(' ')
            command = splitMessage[0]
            newclient = splitMessage[1]
            usernameTaken = 0
            for k,v in clients.items():
                if k == newclient:
                    print "Username taken."
                    usernameTaken = 1
                    con.send(hashData(messageInfo("Username has already been taken, closing connection.")))
                    con.send(hashData('<close>'))
            if usernameTaken == 0:
                clients[newclient] = con
                messageAll(hashData(messageInfo("[ANNOUNCEMENT] New client "+newclient+" connected. Welcome to \'"+getChatName()+"\'!")))
                log("New client \'"+newclient+"\' connected")

        elif "<changenickname " in data: #<changenick Daniel>
            oldnick = getClientName(con)
            tagless = data[1:-1]
            splitMessage = tagless.split(' ')
            command = splitMessage[0]
            newnick = splitMessage[1]
            del clients[getClientName(con)] #Removes client value
            clients[newnick] = con # Adds a client value based on new nickname
            log("Nickname changed to " + newnick + " By "+ oldnick)
            messageAll(hashData(messageInfo(oldnick+" has changed their nickname to \'"+newnick+"\'" )))
        elif "<chat>" in data: # <msg>Daniel~This is a message</msg>
            timestamp = getTimestamp()
            tagless = data[6:-7]
            buffer = buffer + tagless + ":"
            splitMessage = tagless.split('~')
            user = splitMessage[0]
            message = splitMessage[1]
            print("Message received")
            log("[MSG]: "+user+": " + message)
            messageAll(hashData(messageMsg(timestamp+" "+user+": " + message)))
        elif "<ping>" in data:
            con.send(hashData("<pong>"))
            log("Server pinged by " + getClientName(con))
        elif "<connected>" in data:
            con.send(hashData(messageInfo(getClientList())))
            log("Connection list called. "+ getClientList())
        elif "<kick " in data:
            kicker = getClientName(con)
            tagless = data[1:-1]
            splitMessage = tagless.split(' ')
            command = splitMessage[0]
            user = splitMessage[1]
            usercon = getClientCon(user)
            usercon.send(hashData(messageInfo("[ANNOUNCEMENT] You have been kicked by "+kicker+".")))
            usercon.send('<close>')
            messageAll(hashData(messageInfo("[ANNOUNCEMENT] \'"+user+"\' has been kicked from the chat by \'"+kicker+"\'.")))
            del clients[user]
            currentConnections.remove(usercon)
            log(user + " has been kicked from the chat by "+ kicker)

        elif "<messages>" in data:
            con.send(hashData(messageInfo("Message count: "+str(getMessageCount()))))
        elif "<roomname>" in data:
            con.send(hashData(messageInfo("You are currently connected to \'"+getChatName()+"\'.")))
        elif "<changeroomname " in data:
            oldname = getChatName()
            user = getClientName(con)
            newname = data[16:-1]
            setChatName(newname)
            messageAll(hashData(messageInfo("[ANNOUNCEMENT] The room name has been changed from \'"+oldname+"\' to \'"+newname+"\' by "+user+".")))
            log("Chat room name changed from " + oldname + " to "+newname+" by "+user)

    else:
        if debug == 1:
            print("[DEBUG] Hashes do not match!")
# we a new thread is started from an incoming connection
# the manageConnection funnction is used to take the input
# and print it out on the server
# the data that came in from a client is added to the buffer.

def manageConnection(conn, addr):
    threadData = threading.local()
    threadData.running = 1
    while(threadData.running == 1):
        global buffer
        global currentConnections
        global mylist
        print 'Connected by', addr
        # add the new connection to the list of connections
        currentConnections.append(conn)

        while 1:
            try:

                data = conn.recv(4096)
                if data != "":
                    parseInput(data,conn)# Calling the parser
                    mylist.append(data)
                    print mylist

                for singleClient in currentConnections:
                    singleClient.send(str(data))

            except socket.error as error:
                print(error)
                print("Error, removing connection.")
                print(str(currentConnections))
                threadData.running = 0
    print(str(threadData.running))

while 1:
    s.listen(1)
    conn, addr = s.accept()
    # after we have listened and accepted a connection coming in,
    # we will then create a thread for that incoming connection.
    # this will prevent us from blocking the listening process
    # which would prevent further incoming connections
    t = threading.Thread(target=manageConnection, args = (conn,addr))

    t.start()
