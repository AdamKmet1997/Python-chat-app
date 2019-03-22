import threading
import socket
import hashlib
from time import gmtime, strftime
from datetime import datetime
import time
import os
import json

HOST = '127.0.0.1'    # The remote host
PORT = 50007          # The same port as used by the server
debug = 0

def hashData(unhashedData):
    hash = hashlib.md5()
    hash.update(unhashedData)
    hashedData = hash.hexdigest()
    finishedData = "<hash "+hashedData+">-"+unhashedData
    return finishedData
def verifyHash(data):
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

def stripHash(data):
    data = data.split('-', 1)
    stripped = data[1]
    return stripped

def main():
    global debug
    global nickname
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    mylist = list()
    nickname = 'NO_NICKNAME'
    lastPing = datetime.now()

    if debug == 1:
        print('[DEBUG] !!!DEBUG MODE ENABLED. SET DEBUG VALUE TO 0 TO DISABLE!!!')
    def readInputThreaded(so):
        global nickname
        while nickname == 'NO_NICKNAME' or len(nickname) < 1 :
            print "Set your nickname:"
            nick = raw_input()
            nickname = nick
            if len(nickname) > 0:
                so.sendall(hashData("<newclient "+nickname+">"))
            print("[HELP] Typing <help> will give you a list of commands!")

        while 1:
            text = raw_input()
            if text == "":
                print("[INFO] No message entered.")
            if "<changecolor>" in text:
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
            if "<colorhelp>" in text:
                colournames = ['black', 'blue', 'green', 'aqua', 'red', 'purple', 'yellow', 'white', 'grey', 'light blue', 'light green', 'light aqua', 'light red', 'light purple', 'light yellow', 'bright white']
                colourprint = ', '.join([c.title() for c in colournames])
                print "[INFO] Colors available are: " +colourprint
            elif "<ping>" in text:
                lastPing = datetime.now()
                so.sendall(hashData(str(text)))
            elif "<show>" in text:
                so.sendall(hashData(str(text)))
            elif "<help>" in text:
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
            elif "<changenickname " in text:
                print("Changing nickname!")
                tagless = text[1:-1]
                splitMessage = tagless.split(' ')
                command = splitMessage[0]
                newnick = splitMessage[1]
                nickname = newnick
                so.sendall(hashData(str(text)))
            elif "<close>" in text:
                try:
                    so.close()
                    break
                except Exception:
                    print "Error"
            elif "<" in text:
                so.sendall(hashData(str(text)))
            else:
                so.sendall(hashData(str('<chat>'+nickname+'~'+text+'</chat>')))
            # writeToJsonFile(path,fileName,text)


    t = threading.Thread(target=readInputThreaded, args = (s,))
    t.start()



    '''
    Thread to read from the server
    '''
    def readFromServer(s):
        global nickname
        global debug  #Set to 1 to see [data] messages from the server.
        mylist

        while 1:
            data = s.recv(4096)
            if debug == 1:
                print ('[DEBUG]: ' +data)
            mylist.append(data)
            if verifyHash(data) == 1:
                data = stripHash(data)

                if '<msg>' in data:
                    message = data[5:-6]
                    print("[MSG] " + message)
                if '<info>' in data:
                    message = data[6:-7]
                    print("[INFO] " + message)
                elif "<pong>" in data:
                    end = datetime.now()
                    timeTaken = end - lastPing
                    print("[INFO] Ping successful. Time taken: " + str(timeTaken))
                elif "<close>" in data:
                    try:
                        s.close()
                        break
                    except Exception:
                        print "Error"
            else:
                if debug == 1:
                    print("[DEBUG] HASHES DO NOT MATCH")
    t = threading.Thread(target=readFromServer, args = (s,))
    t.start()

main()
#s.close()
