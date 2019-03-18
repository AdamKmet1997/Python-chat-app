import threading
# Echo client program
import socket
from time import gmtime, strftime
from datetime import datetime
import time
import json

HOST = '127.0.0.1'    # The remote host
PORT = 50007          # The same port as used by the server

def main():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    mylist = list()
    nickname = 'NO_NICKNAME'
    lastPing = datetime.now()


    # method tp save messages into the file .json
    # def writeToJsonFile(path,fileName,dat):
    #     filePath = './' + path + './' +fileName + '.json'
    #     with open(filePath, 'w') as fp:
    #         json.dump(dat , fp)
    #
    # path = './'
    # fileName = 'example2'
    # when we send data to the server, we are using a colon
    # at the end of a sentence to mark the end of the current sentence
    # later when the input comes back, we will then be breaking the input
    # into individual parts using the colon : to separate the lines
    def readInputThreaded(so):
        global nickname
        print "Set your nickname"
        nick = raw_input()
        nickname = nick
        so.sendall("<newclient "+nickname+">")

        while 1:

            text = raw_input()
            if "<ping>" in text:
                lastPing = datetime.now()
                so.sendall(str(text))
            elif "<changenickname " in text:
                print("Changing nickname!")
                tagless = text[1:-1]
                splitMessage = tagless.split(' ')
                command = splitMessage[0]
                newnick = splitMessage[1]
                nickname = newnick
            elif "<close>" in text:
                try:
                    so.close()
                    break
                except Exception:
                    print "Error"

            elif "<" in text:
                so.sendall(str(text))
            else:
                so.sendall(str('<chat>'+nickname+'~'+text+'</chat>'))

            # writeToJsonFile(path,fileName,text)


    t = threading.Thread(target=readInputThreaded, args = (s,))
    t.start()



    '''
    Thread to read from the server
    '''
    def readFromServer(s):
        global nickname
        debug = 0  #Set to 1 to see [data] messages from the server.
        mylist

        while 1:
            data = s.recv(100)
            if debug == 1:
                print ('[DATA]: ' +data)
            mylist.append(data)


            #:User Name-"Message">
            if '<msg>' in data:
                message = data[5:-6]
                print("[MSG] " + message)
            if ":" in data:
                time = strftime("( %H:%M:%S) ", gmtime())
                Nmess= data.replace(':','')
                Nmess= Nmess.split('-')
                #global nickname
                #nickname = Nmess[0]
                #print(""+ str(time)+"" + nickname + "-> " + Nmess[1])
            elif "<getservertime>" in data:
                print "command in data.."
                formatted= strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                print(str(formatted))
            elif "<time>" in data:
                print(str(data))
            elif "<dates>" in data:
                dates=strftime("%a, %d %b %Y", gmtime())
                print(str(dates))
            #elif "<leave>" in data:
            #    s.close()
            elif "<pong>" in data:
                end = datetime.now()
                timeTaken = end - lastPing
                print("Ping successfull. Time taken: " + str(timeTaken))
            elif "<help>" in data:
                print "<time>"
                print "<dates>"
                print "<getservertime>"
                print "<ping>"
                print "<showclients>"
            elif "<show>" in data:
                print mylist
            elif "<close>" in data:
                try:
                    s.close()
                    break
                except Exception:
                    print "Error"


            #nickname = new
                #print("Old nickname = " + nickname + " new nickname = " + NewNick)






    t = threading.Thread(target=readFromServer, args = (s,))
    t.start()


main()
#s.close()
