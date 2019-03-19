import threading
import socket
import hashlib
from time import gmtime, strftime
from datetime import datetime
import time
import json

HOST = '127.0.0.1'    # The remote host
PORT = 50007          # The same port as used by the server
debug = 1

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
        print("First hash:"+firstHash)
        print("Second hash: "+secondHash)
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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    mylist = list()
    nickname = 'NO_NICKNAME'
    lastPing = datetime.now()


    def readInputThreaded(so):
        global nickname
        print "Set your nickname"
        nick = raw_input()
        nickname = nick
        so.sendall(hashData("<newclient "+nickname+">"))
        print("[HELP] Typing <help> will give you a list of commands!")

        while 1:
            text = raw_input()
            if "<ping>" in text:
                lastPing = datetime.now()
                so.sendall(hashData(str(text)))
            elif "<help>" in text:
                print "<time>"
                print "<date>"
                print "<servertime>"
                print "<ping>"
                print "<connected>"
                print "<messages>"
                print "<changenickname [NEW_NICKNAME]>"
                print "<kick [USER]>"
                print "<roomname>"
                print "<changeroomname [NEW_ROOMNAME]>"
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
            if debug == 0:
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
                    print("Ping successfull. Time taken: " + str(timeTaken))
                elif "<show>" in data:
                    print mylist
                elif "<close>" in data:
                    try:
                        s.close()
                        break
                    except Exception:
                        print "Error"
            else:
                print("HASHES DO NOT MATCH")
    t = threading.Thread(target=readFromServer, args = (s,))
    t.start()

main()
#s.close()
