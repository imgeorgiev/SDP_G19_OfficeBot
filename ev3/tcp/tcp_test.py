# DataClient2.py

from tcpcom_py3 import TCPClient
import time

IP_ADDRESS = "169.254.23.50"
IP_PORT = 5005


def onStateChanged(state, msg):
    global isConnected
    if state == "CONNECTING":
        print("Client:-- Waiting for connection...")
    elif state == "CONNECTED":
        print("Client:-- Connection estabished.")
    elif state == "DISCONNECTED":
        print("Client:-- Connection lost.")
        isConnected = False
    elif state == "MESSAGE":
        print("Client:-- Received data:" + msg)


client = TCPClient(IP_ADDRESS, IP_PORT, stateChanged=onStateChanged)
rc = client.connect()
# if rc:
#     isConnected = True
#     while isConnected:
#         print("Client:-- Sending command: go...")
#         client.sendMessage("go")
#         time.sleep(2)
#     print("Done")
# else:
#     print("Client:-- Connection failed")   
