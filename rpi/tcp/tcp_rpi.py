#!/usr/bin/env python2


# Library for sending UDP commands to an EV3
# Commands include: motors

from tcpcom import TCPServer
# import sys


tcp_ip = "169.254.21.44"    # 169.254.21.44
tcp_port = 5005
tcp_reply = "Server message"
toSend = False


def onStateChanged(state, msg):
    global isConnected
    global toSend

    if state == "LISTENING":
        print("Server:-- Listening...")
    elif state == "CONNECTED":
        isConnected = True
        print("Server:-- Connected to" + msg)
    elif state == "MESSAGE":
        print("Server:-- Message received:", msg)
        server.sendMessage(tcp_reply)


def main():
    global server

    server = TCPServer(tcp_port, stateChanged=onStateChanged)


if __name__ == '__main__':
    main()
