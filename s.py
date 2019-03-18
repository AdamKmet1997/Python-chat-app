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
chatname = "Group chat"

# This is the buffer string
# when input comes in from a client it is added
# into the buffer string to be relayed later
# to different clients that have connected
# Each message in the buffer is separated by a colon :


# custom say hello command
def getTimestamp():
    time = strftime("[%H:%M:%S]", gmtime())
    return time
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

# # def writeToJsonFile(path,fileName,data):
# #     with open('example2.json','w') as f:
# #         json.dump(data, f, indent=2)
#
# path = './'
# fileName = 'example2'
# sample parser function. The job of this function is to take some input
# data and search to see if a command is present in the text. If it finds a
# command it will then need to extract the command.
def parseInput(data, con):
    global buffer
    print "parsing..."


    #print str(data)

    # Checking for commands
    if "<getservertime>" in data:
        print "command in data.."
        formatted= strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        con.send(str('<info>'+formatted+'</info>'))
    if "<time>" in data:
        time = strftime("%H:%M:%S", gmtime())
        t= str("Time: " + time)
        print t
        con.send('<info>'+t+'</info>')
    elif "<date>" in data:
        date=strftime("%a, %d %b %Y", gmtime())
        con.send(str('<info>'+date+'</info>'))
    elif "<newclient " in data: #<newclient Daniel>
        tagless = data[1:-1]
        splitMessage = tagless.split(' ')
        command = splitMessage[0]
        newclient = splitMessage[1]
        clients[newclient] = con
        messageAll("<msg>[ANNOUNCEMENT] New client "+newclient+" connected.</msg>")
    elif "<changenickname " in data: #<changenick Daniel>
        tagless = data[1:-1]
        splitMessage = tagless.split(' ')
        command = splitMessage[0]
        newnick = splitMessage[1]
        del clients[getClientName(con)] #Removes client value
        clients[newnick] = con # Adds a client value based on new nickname
        print(clients)
        #con.send('<changenickname '+newnick+'>')
    #:User Name-"Message">
    elif "<chat>" in data: # <msg>Daniel~This is a message</msg>
        timestamp = getTimestamp()
        tagless = data[6:-7]
        buffer = buffer + tagless + ":"
        splitMessage = tagless.split('~')
        user = splitMessage[0]
        message = splitMessage[1]
        messageAll("<msg>"+timestamp+" "+user+": " + message+"</msg>")

    #elif "<leave>" in data:
    #    print("user has left the chat")
    elif "<ping>" in data:
        con.send("<pong>")
    elif "<connected>" in data:
        con.send('<info>'+getClientList()+'</info>')
    elif "<kick " in data:
        kicker = getClientName(con)
        tagless = data[1:-1]
        splitMessage = tagless.split(' ')
        command = splitMessage[0]
        user = splitMessage[1]
        usercon = getClientCon(user)
        usercon.send("<msg>[ANNOUNCEMENT] You have been kicked by "+kicker+".</msg>")
        usercon.send('<close>')
        del clients[user]
        currentConnections.remove(usercon)
        messageAll("<msg>[ANNOUNCEMENT] "+user+" has been kicked by "+kicker+".</msg>")
    elif "<messages>" in data:
        con.send("<info>Message count: "+str(getMessageCount())+"</info>")


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


        except:
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
