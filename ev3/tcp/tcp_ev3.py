#!/usr/bin/env python2


# Library for sending UDP commands to an EV3
# Commands include: motors

from tcpcom import TCPClient
import time
# import sys


tcp_ip = "169.254.21.39"    # 169.254.21.44
tcp_port = 5005
reply = "Client reply"


def onStateChanged(state, msg):
    global isConnected

    if (state == "CONNECTING"):
        print("Client:-- Waiting for connection...")
    elif (state == "CONNECTED"):
        print("Client:-- Connection estabished.")
    elif (state == "DISCONNECTED"):
        print("Client:-- Connection lost.")
        isConnected = False
    elif (state == "MESSAGE"):
        print("Client:-- Received data:", msg)


def main():
    client = TCPClient(tcp_ip, tcp_port, stateChanged=onStateChanged)
    rc = client.connect()
    if rc:
        while(True):
            isConnected = True
            while isConnected:
                client.sendMessage(reply)
                print("Client:-- Sending message:", reply)
            print("Done")
        else:
            print("Client:-- Connection failed")


if __name__ == '__main__':
    main()
