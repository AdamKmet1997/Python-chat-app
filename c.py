import threading
import socket
import hashlib
from time import gmtime, strftime
from datetime import datetime
import time
import os
import json


# -------------------- DECLARATIONS -------------------- #



HOST = '127.0.0.1'    # The remote host
PORT = 50007          # The same port as used by the server
debug = 0


# -------------------- FUNCTIONS -------------------- #



def hashData(unhashedData): #Takes in data and hashes it, returning the hash alongside the payload
    hash = hashlib.md5()
    hash.update(unhashedData)
    hashedData = hash.hexdigest()
    finishedData = "<hash "+hashedData+">-"+unhashedData
    return finishedData

def verifyHash(data): #Returns 1 if the hash is authentic
    global debug
    split = data.split('-')
    if debug == 1:
        print("[DEBUG] Data with hash: " + str(split))
    firstHash = split[0]
    secondHash = split[1]
    firstHash = firstHash[6:-1]

    hash = hashlib.md5()
    hash.update(secondHash)
    secondHash = hash.hexdigest()
    if debug == 1:
        print("[DEBUG] First hash:"+firstHash)
        print("[DEBUG] Second hash: "+secondHash)
    if firstHash == secondHash:
        return 1
    else:
        return 0

def stripHash(data): #Removes hash from data leaving just the payload
    data = data.split('-', 1)
    stripped = data[1]
    return stripped





def main(): #Main logic
    global debug
    global nickname
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    mylist = list()
    nickname = 'NO_NICKNAME'
    lastPing = datetime.now()

    if debug == 1:
        print('[DEBUG] !!!DEBUG MODE ENABLED. SET DEBUG VALUE TO 0 TO DISABLE!!!')




    def readInputThreaded(so): #Reads input from the users keyboard
        global nickname
        while nickname == 'NO_NICKNAME' or len(nickname) < 1 : #While nickname isnt set or is empty
            print "Set your nickname:"
            nick = raw_input()
            nickname = nick
            if len(nickname) > 0: #If nickname is set
                so.sendall(hashData("<newclient "+nickname+">"))


            print("[HELP] Typing <help> will give you a list of commands!")


        while 1:
            text = raw_input() #Take userinput

            if text == "": #Ignore if empty
                print("[INFO] No message entered.")

            elif "<changecolor>" in text: #Allow the user to change their terminal colors
                colourcodes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'a', 'b', 'c', 'd', 'e', 'f']
                colournames = ['black', 'blue', 'green', 'aqua', 'red', 'purple', 'yellow', 'white', 'grey', 'light blue', 'light green', 'light aqua', 'light red', 'light purple', 'light yellow', 'bright white']
                def color(i):
                	i = i.lower()
                	return colourcodes[colournames.index(i)]

                textcolor = raw_input('\nWhat colour do you want the text?  ')
                Backcolor = raw_input('\nWhat colour do you want the background?  ')
                a = color(Backcolor)
                b = color(textcolor)
                c = 'color %s%s' % (a, b)
                os.system(c)

            elif "<colorhelp>" in text: #Displays help for colors you can choose
                colournames = ['black', 'blue', 'green', 'aqua', 'red', 'purple', 'yellow', 'white', 'grey', 'light blue', 'light green', 'light aqua', 'light red', 'light purple', 'light yellow', 'bright white']
                colourprint = ', '.join([c.title() for c in colournames])
                print "[INFO] Colors available are: " +colourprint

            elif "<ping>" in text: #If a ping is sent it starts a timer which is only stopped when a "pong" is received, timing the ping
                lastPing = datetime.now()
                so.sendall(hashData(str(text)))

            elif "<show>" in text:
                so.sendall(hashData(str(text)))

            elif "<help>" in text: #Shows all commands to the user
                print "---------------------------------------------------------"
                print "|The following commands can be used in this application.|"
                print "---------------------------------------------------------"
                print "<help>\t\t\t\t\t   <--Displays all help commands-->"
                print "<colorhelp>\t\t\t\t   <--Displays all information for changing colors-->"
                print "<changecolor>\t\t\t\t   <--Edit the colors on your application (Use <colorhelp>)-->"
                print "<time>\t\t\t\t\t   <--Prints the local time in format H:M:S-->"
                print "<date>\t\t\t\t\t   <--Prints the local date time in format DDD, D:MMM:YYYY-->"
                print "<servertime>\t\t\t\t   <--Gets a precise server time and date-->"
                print "<ping>\t\t\t\t\t   <--Checks server connectivity and round trip timing-->"
                print "<connected>\t\t\t\t   <--Shows number of connected clients and client list-->"
                print "<messages>\t\t\t\t   <--Shows message count-->"
                print "<changenickname [NEW_NICKNAME]>\t\t   <--Change your nickname-->"
                print "<kick [USER]>\t\t\t\t   <--Kick a user-->"
                print "<roomname>\t\t\t\t   <--Show roomname-->"
                print "<changeroomname [NEW_ROOMNAME]>\t\t   <--Edit roomname-->"
                print "<show>\t\t\t\t\t   <--Displays previous messages-->"

            elif "<changenickname " in text: #Edits the clients nickname locally
                print("Changing nickname!")
                tagless = text[1:-1]
                splitMessage = tagless.split(' ')
                command = splitMessage[0]
                newnick = splitMessage[1]
                nickname = newnick
                so.sendall(hashData(str(text)))

            elif "<close>" in text: #Drops client connection
                try:
                    so.close()
                    break
                except Exception:
                    print "Error"

            elif "<" in text: #If any other command is here, send it directly to the server
                so.sendall(hashData(str(text)))

            else: #Otherwise if no commands are present interpret as a chat message and forward to the server
                so.sendall(hashData(str('<chat>'+nickname+'~'+text+'</chat>')))

    t = threading.Thread(target=readInputThreaded, args = (s,)) #Creates a thread which will deal with all readingInput from the clients keyboard
    t.start()






    def readFromServer(s): #Handles all inbound data from server
        global nickname
        global debug  #Set to 1 to see [data] messages from the server.
        mylist

        while 1:
            data = s.recv(16384)
            if debug == 1:
                print ('[DEBUG]: ' +data)
            mylist.append(data)
            if verifyHash(data) == 1:
                data = stripHash(data)

                if '<msg>' in data: #If a <msg> comes back, print it as a chat message
                    message = data[5:-6]
                    print("[MSG] " + message)

                if '<info>' in data: #Print message as an [INFO] message
                    message = data[6:-7]
                    print("[INFO] " + message)

                elif "<pong>" in data: #Stop ping timer and print results
                    end = datetime.now()
                    timeTaken = end - lastPing
                    print("[INFO] Ping successful. Time taken: " + str(timeTaken))

                elif "<close>" in data: #Drop connection
                    try:
                        s.close()
                        break
                    except Exception:
                        print "Error"
            else:
                if debug == 1:
                    print("[DEBUG] HASHES DO NOT MATCH")


    t = threading.Thread(target=readFromServer, args = (s,)) #Additional thread for reading server input
    t.start()

main()
#s.close()
