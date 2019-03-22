import socket
import threading, Queue
import hashlib
import sys
from time import gmtime, strftime
import time
import os
import json


# -------------------- INITIAL SOCKET SETUP -------------------- #


HOST = '127.0.0.1'
PORT = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))


# -------------------- DECLARATIONS -------------------- #


mylist = list()
currentConnections = list() #Contains our currently connected connection references
clients = { # Stores a dictionary of users/connections
    #e.g:  'Daniel': connectionOBJECT
}
buffer = "" #Messages coming in from clients will be stored here before being forwarded to other clients
chatname = "Year 3 Group chat"
newclient = ""
usernameTaken = 0

debug = 0  #Set to 1 to enable debug mode or 0 to disable


# -------------------- FUNCTIONS -------------------- #



def log(message): #Takes in a message and logs it to a log file titled after todays date.
    timestamp = str(strftime("[%d %b %Y - %H:%M:%S]", gmtime()))
    f = open("Logs/chat_log_"+ dateString +".txt","a+")
    f.write(timestamp+" "+message+"\n")
    f.close()

def getTimestamp(): #Returns current timestamp
    time = strftime("[%H:%M:%S]", gmtime())
    return time

def getChatName(): #Returns name of chatroom
    return chatname

def setChatName(newName): #Sets name of chatroom
    global chatname
    chatname = newName
def getClientCon(name): #Returns a client connection reference from a client nickname
    clientCon = clients[name]
    return clientCon

def getClientName(con):#Returns a client name from a client connection reference
    clientName =  clients.keys()[clients.values().index(conn)]
    return clientName

def getClientList(): #Returns amount of clients connected and lists them
    population = len(clients)
    message = str(population) + " clients connected. Clients: "
    for client in clients.keys():
        message = message + "\n" + client
    return message

def messageAll(message): #Forwards a message to all users.
    for client in clients.values():
        client.send(message)

def getMessageCount(): #Returns message count
    split = buffer.split(':')
    messages = len(split)
    return messages

def messageInfo(message): #Wraps the message in <info> tags before sending so it is interpreted as an [INFO] message by the client
    message = "<info>"+message+"</info>"
    return message

def messageMsg(message): #Wraps the message in <msg> tags before sending so it is interpreted as a [MSG] message by the client
    message = "<msg>"+message+"</msg>"
    return message

def hashData(unhashedData): #Takes in a piece of data and hashes and formats it so it is ready to be sent
    hash = hashlib.md5() #Uses the md5 hashing algorithm
    hash.update(unhashedData)
    hashedData = hash.hexdigest()
    finishedData = "<hash "+hashedData+">-"+unhashedData
    return finishedData

def verifyHash(data): #Takes in hashed data and checks if the hash is the same on the server and client
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

def stripHash(data): #Strips the hash from a message, returning just the payload data
    data = data.split('-', 1)
    stripped = data[1]
    return stripped


print("Server started.")
log("\n\n-----------------------------------------"+"Server started at "+str(strftime("[%d %b %Y - %H:%M:%S]", gmtime()))+"-----------------------------------------")



# ---------------------------------------------- #



def parseInput(data, con): #Handles all messages coming in from the clients
    global buffer
    global usernameTaken
    print "Parsing..."

    if verifyHash(data) == 1: #If the hash can be verified as authentic
        data = stripHash(data) #Remove the hash data from the message

        #Following if statements are checking if a string is a substring of the incoming data and will decide what to do based on what the data contains
        if "<servertime>" in data: #Returns precise severtime
            formatted= strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
            con.send(hashData(messageInfo(str(formatted))))

        elif "<time>" in data: #Returns current time in H:M:S
            time = strftime("%H:%M:%S", gmtime())
            timeString = str("Time: " + time)
            con.send(hashData(messageInfo(timeString)))

        elif "<date>" in data: #Returns current weekday, and date in D:M:Y
            date=strftime("%a, %d %b %Y", gmtime())
            con.send(hashData(messageInfo(str(date))))

        elif "<show>" in data: #Displays previous messages to the client
            count = buffer.count(":")
            count = str(count)
            first_msg = buffer.split(":")
            show = " - ".join(str(x) for x in first_msg)
            show = "there are "+ count +" previous messages " + show
            print show
            con.send(hashData(show))

        elif "<newclient " in data: #Lets a new connecting client to be added to the chat
            tagless = data[1:-1]
            splitMessage = tagless.split(' ')
            command = splitMessage[0]
            newclient = splitMessage[1]
            usernameTaken = 0
            for k,v in clients.items(): #Checks first to see if the username has been taken
                if k == newclient:
                    print "Username taken."
                    usernameTaken = 1
                    con.send(hashData(messageInfo("Username has already been taken, closing connection.")))
                    con.send(hashData('<close>'))
            if usernameTaken == 0:
                clients[newclient] = con # Add to the dictionary of clients
                messageAll(hashData(messageInfo("[ANNOUNCEMENT] New client "+newclient+" connected. Welcome to \'"+getChatName()+"\'!")))
                log("New client \'"+newclient+"\' connected")

        elif "<changenickname " in data: #e.g <changenickname Daniel> Lets a user change their username
            oldnick = getClientName(con)
            tagless = data[1:-1]
            splitMessage = tagless.split(' ')
            command = splitMessage[0]
            newnick = splitMessage[1]
            del clients[getClientName(con)] #Removes client value
            clients[newnick] = con # Adds a client value based on new nickname
            log("Nickname changed to " + newnick + " By "+ oldnick)
            messageAll(hashData(messageInfo(oldnick+" has changed their nickname to \'"+newnick+"\'" )))

        elif "<chat>" in data: # <msg>Daniel~This is a message</msg> #Forwards incoming chat messages to clients
            timestamp = getTimestamp()
            tagless = data[6:-7]
            buffer = buffer + tagless + ":" #Adds message to the buffer
            splitMessage = tagless.split('~')
            user = splitMessage[0]
            message = splitMessage[1]
            print("Message received")
            log("[MSG]: "+user+": " + message)
            messageAll(hashData(messageMsg(timestamp+" "+user+": " + message))) #Sends messages to each client

        elif "<ping>" in data: #Replies to a ping with a pong
            con.send(hashData("<pong>"))
            log("Server pinged by " + getClientName(con))

        elif "<connected>" in data: #Lists the amount and list of users connected
            con.send(hashData(messageInfo(getClientList())))
            log("Connection list called. "+ getClientList())

        elif "<kick " in data: #<kick John> #Kicks a client
            kicker = getClientName(con)
            tagless = data[1:-1]
            splitMessage = tagless.split(' ')
            command = splitMessage[0]
            user = splitMessage[1]
            usercon = getClientCon(user)
            usercon.send(hashData(messageInfo("[ANNOUNCEMENT] You have been kicked by "+kicker+".")))
            usercon.send('<close>') #Tells the client to close the socket connection
            messageAll(hashData(messageInfo("[ANNOUNCEMENT] \'"+user+"\' has been kicked from the chat by \'"+kicker+"\'.")))
            del clients[user] #Removes user from client dictionary
            currentConnections.remove(usercon) #Removes user from currentConnections
            log(user + " has been kicked from the chat by "+ kicker)

        elif "<messages>" in data: #Sends the message count to the user
            con.send(hashData(messageInfo("Message count: "+str(getMessageCount()))))

        elif "<roomname>" in data: #Sends the chat name to the user
            con.send(hashData(messageInfo("You are currently connected to \'"+getChatName()+"\'.")))

        elif "<changeroomname " in data: #<changeroomname NewRoom> #Allows users to change the chat name
            oldname = getChatName()
            user = getClientName(con)
            newname = data[16:-1]
            setChatName(newname)
            messageAll(hashData(messageInfo("[ANNOUNCEMENT] The room name has been changed from \'"+oldname+"\' to \'"+newname+"\' by "+user+".")))
            log("Chat room name changed from " + oldname + " to "+newname+" by "+user)

    else:
        if debug == 1:
            print("[DEBUG] Hashes do not match!")




def manageConnection(conn, addr): #A manageConnection() thread will run for each client connecting
    threadData = threading.local()
    threadData.running = 1 #threadData stores a flag of whether the thread should continue running or not
    while(threadData.running == 1):
        global buffer
        global currentConnections
        global mylist
        print 'Connected by', addr
        # add the new connection to the list of connections
        currentConnections.append(conn)

        while 1:
            try:

                data = conn.recv(16384)
                if data != "":
                    parseInput(data,conn)# Calling the parser
                    mylist.append(data)
                    print mylist

                for singleClient in currentConnections:
                    singleClient.send(str(data))

            except socket.error as error:
                threadData.running = 0 #Tell thread to stop running



while 1:
    s.listen(1)
    conn, addr = s.accept()
    # after we have listened and accepted a connection coming in,
    # we will then create a thread for that incoming connection.
    # this will prevent us from blocking the listening process
    # which would prevent further incoming connections
    t = threading.Thread(target=manageConnection, args = (conn,addr)) #Start a new thread in manageConnection()
    t.start()
