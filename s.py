import socket
import threading, Queue
from time import gmtime, strftime
import time
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

# This is the buffer string
# when input comes in from a client it is added
# into the buffer string to be relayed later
# to different clients that have connected
# Each message in the buffer is separated by a colon :


# custom say hello command
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
        print(client);
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

# # def writeToJsonFile(path,fileName,data):
# #     with open('example2.json','w') as f:
# #         json.dump(data, f, indent=2)
#
# path = './'
# fileName = 'example2'
# sample parser function. The job of this function is to take some input
# data and search to see if a command is present in the text. If it finds a
# command it will then need to extract the command.
print("Server started.")

def parseInput(data, con):
    global buffer
    print "parsing..."


    #print str(data)

    # Checking for commands
    if "<servertime>" in data:
        formatted= strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        con.send(messageInfo(str(formatted)))
    if "<time>" in data:
        time = strftime("%H:%M:%S", gmtime())
        timeString = str("Time: " + time)
        con.send(messageInfo(timeString))
    elif "<date>" in data:
        date=strftime("%a, %d %b %Y", gmtime())
        con.send(messageInfo(str(date)))
    elif "<newclient " in data: #<newclient Daniel>
        tagless = data[1:-1]
        splitMessage = tagless.split(' ')
        command = splitMessage[0]
        newclient = splitMessage[1]
        clients[newclient] = con
        messageAll(messageInfo("[ANNOUNCEMENT] New client "+newclient+" connected."))
    elif "<changenickname " in data: #<changenick Daniel>
        oldnick = getClientName(con)
        tagless = data[1:-1]
        splitMessage = tagless.split(' ')
        command = splitMessage[0]
        newnick = splitMessage[1]
        del clients[getClientName(con)] #Removes client value
        clients[newnick] = con # Adds a client value based on new nickname
        messageAll(messageInfo(oldnick+" has changed their nickname to \'"+newnick+"\'." ))
    elif "<chat>" in data: # <msg>Daniel~This is a message</msg>
        timestamp = getTimestamp()
        tagless = data[6:-7]
        buffer = buffer + tagless + ":"
        splitMessage = tagless.split('~')
        user = splitMessage[0]
        message = splitMessage[1]
        print("Message received")
        messageAll(messageMsg(timestamp+" "+user+": " + message))
    elif "<ping>" in data:
        con.send("<pong>")
    elif "<connected>" in data:
        con.send(messageInfo(getClientList()))
    elif "<kick " in data:
        kicker = getClientName(con)
        tagless = data[1:-1]
        splitMessage = tagless.split(' ')
        command = splitMessage[0]
        user = splitMessage[1]
        usercon = getClientCon(user)
        usercon.send(messageInfo("[ANNOUNCEMENT] You have been kicked by "+kicker+"."))
        usercon.send('<close>')
        messageAll(messageInfo("[ANNOUNCEMENT] \'"+user+"\' has been kicked from the chat by \'"+kicker+"\'."))
        del clients[user]
        currentConnections.remove(usercon)
    elif "<messages>" in data:
        messageAll(messageInfo("Message count: "+str(getMessageCount())))
    elif "<roomname>" in data:
        con.send(messageInfo("You are currently connected to \'"+getChatName()+"\'."))
    elif "<changeroomname " in data:
        oldname = getChatName()
        user = getClientName(con)
        newname = data[16:-1]
        messageAll(messageInfo("The room name has been changed from \'"+oldname+"\' to \'"+newname+"\' by "+user+"."))

# we a new thread is started from an incoming connection
# the manageConnection funnction is used to take the input
# and print it out on the server
# the data that came in from a client is added to the buffer.

def manageConnection(conn, addr):
    global buffer
    global currentConnections
    global mylist
    print 'Connected by', addr
    # add the new connection to the list of connections
    currentConnections.append(conn)

    while 1:
        try:
            data = conn.recv(1024)
            if data != "":
                parseInput(data,conn)# Calling the parser
        except socket.error as error:
            print("Error, removing connection.")
            print(str(currentConnections))

            for singleClient in currentConnections:
                singleClient.send(str(data))
    #    print "rec:" + str(data)
        #store messages in a list called mylist
        mylist.append(data)
        print mylist




    #conn.close()


while 1:
    s.listen(1)
    conn, addr = s.accept()
    # after we have listened and accepted a connection coming in,
    # we will then create a thread for that incoming connection.
    # this will prevent us from blocking the listening process
    # which would prevent further incoming connections
    t = threading.Thread(target=manageConnection, args = (conn,addr))

    t.start()
