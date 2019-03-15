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

}


# This is the buffer string
# when input comes in from a client it is added
# into the buffer string to be relayed later
# to different clients that have connected
# Each message in the buffer is separated by a colon :
buffer = ""

# custom say hello command
def sayHello():
    print "----> The hello function was called"


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
    print "parsing..."
    print(currentConnections)
    print(buffer)

    #print str(data)

    # Checking for commands
    if "<getservertime>" in data:
        print "command in data.."
        formatted= strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        #con.send(str(formatted))
        print " user requested server date and time "

    if "<time>" in data:
        time = strftime(" %H %M %S +0000", gmtime())
        t= str("time is" + time)
        print t
        con.send(t)
        print " user requested time"
    elif "<dates>" in data:
        dates=strftime("%a, %d %b %Y", gmtime())
    #    con.send(str(dates))
        print " user requested date"
    elif "<changeNickname " in data:
        tagless = data[1:-1]
        splitMessage = tagless.split(' ')
        command = splitMessage[0];
        newNickname = splitMessage[1]
        print(con)

    #:User Name-"Message">

    elif ":" in data:
        time = strftime("( %H:%M:%S) ", gmtime())
        Nmess= data.replace(':','')
        Nmess= Nmess.split('-')
        #global nickname
        nickname = Nmess[0]
        print(""+ str(time)+"" + nickname + "-> " + Nmess[1])
    #elif "<leave>" in data:
    #    print("user has left the chat")
    elif "<ping>" in data:
        con.send("<pong>")
    elif "<show>" in data:
        print mylist
    # writeToJsonFile(path,fileName,data)
    elif "<connected>" in data:
        print currentConnections



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
        data = conn.recv(1024)
        if data != "":
            parseInput(data,conn)# Calling the parser


    #    print "rec:" + str(data)

        for singleClient in currentConnections:
            singleClient.send(str(data))
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
