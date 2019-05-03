# Python sockets chat application
In this project we developed a chat application using Python 2.7. This app will contain a server and numerous clients which will communicate with each other using sockets. Clients will not be able to communicate with each other directly but all messages will be passed to the server which will decide where to send the messages on to. We developed a custom protocol specific to this application that will allow us to pass data and commands between server and clients, extract the command from the message and carry out that instruction.

## Features
- Server-Client architecture
- Logs all events/messages to a daily logfile
- Message verification on both ends using hashed communications
- CLI Based
- 11 chat commands
- Developer mode which will show all data passed between server/clients

## Authors
- Daniel Moran
- Dylan Seery
- Adam Kmet

## Demo

General Demo
![General Demo](https://i.imgur.com/D4KcNSx.png)
Available commands
![Commands demo](https://i.imgur.com/oSmc2rr.png)
Logs file
![Logs file demo](https://i.imgur.com/Jn4d3Cs.png)
Color changing demo
![Color demo](https://i.imgur.com/8aQMcYC.png)
