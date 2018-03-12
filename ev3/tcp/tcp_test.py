#!/usr/bin/env python3


# Library for sending UDP commands to an EV3
# Commands include: motors
# Message headers:
#   RQT: RPI -> EV3 request sensor data
#   SNR: EV3 -> RPI send sensor data
#   CMD: RPI -> EV3 send motor command
# EV3 IP: 169.254.21.39
# RPI IP: 169.254.21.44

from tcpcom_py3 import TCPServer
import pygame  # needed for joystick commands
import sys
import time
import os


tcp_ip = "169.254.21.44"    # 169.254.21.44
tcp_port = 5005
tcp_reply = "Server message"
toSend = False


class Server:
    global stateTrans
    isConnected = False
    reqSensorReceived = False
    sensorData = None

    def __init__(self, port, verbose=False):
        self._server = TCPServer(port, stateChanged=stateTrans, isVerbose=verbose)
        self._colorList = ("R", "W", "BW", "N", "BK", "BL", "G", "Y")

    def stateTrans(state, msg):
        global isConnected
        global reqSensorReceived
        global sensorData

        if state == "LISTENING":
            print("DEBUG: Server: Listening...")
        elif state == "CONNECTED":
            isConnected = True
            print("DEBUG: Server: Connected to ", msg)
        elif state == "MESSAGE":
            # print("DEBUG: Server: Message received: " + str(msg))
            if(msg[0:2] == "SNR"):
                reqSensorReceived = True
                sensorData = msg
                print("DEBUG: Server: Sensor message received: ", str(sensorData))

    # Returns designedtaed sensor values from the EV3.
    # Currently returns [int Ultrasonic, string Left color sensor, string Right color sensor]
    def getSensors(self):
        self._server.sendMessage("RQT")
        while(not self.reqSensorReceived):
            pass
        return sensorData

    # Sends a command mapped to a motor. Params:
    # Must input commands for both left and right motor
    # speed - int in range [-100, 100]
    def sendMotorCommand(self, l_motor, r_motor, pause=False, stop=False):

        # Speed input error
        if(-100 <= int(l_motor) <= 100):
            pass
        else:
            raise Exception("ERROR: Wrong l_motor arg")

        # Speed input error
        if(-100 <= int(r_motor) <= 100):
            pass
        else:
            raise Exception("ERROR: Wrong r_motor arg")

        sendMsg = "CMD:" + str(l_motor) + "," + str(r_motor)
        self._server.sendMessage(sendMsg)
        # print("DEBUG: Server : Sending ", sendMsg)

    # Sends a command to follow a line as Alex wanted
    # arguments should be self explanatory
    # current color to follow
    # next color to follow
    # on which side to look for the junction
    # num of junctions to skip before turning
    def sendLineFollow(self, currentColor, nextColor, side, numJunctionsToIgnote):
        if(currentColor not in self._colorList):
            raise Exception("ERROR: Invalid currentColor input")
        if(nextColor not in self._colorList):
            raise Exception("ERROR: Invalid nextColor input")
        side = side.upper()[0]
        if(not (side == "L" or side == "R")):
            raise Exception("ERROR: Invalid side input")

        sendMsg = "LFW:" + currentColor + "," + nextColor + "," + side + "," + str(numJunctionsToIgnote)

        self._server.sendMessage(sendMsg)

    def terminate(self):
        self._server.terminate()


# transform joystick inputs to motor outputs
def scale_stick(value):
    if value == 0.0:
        return 0.0
    else:
        return scale(value, (-1, 1), (-100, 100))


# Generic scale function
# Scale src range to dst range
def scale(val, src, dst):
    return (int(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]


def attenuate(val, min, max):
    if val > max:
        return max
    if val < min:
        return min
    return val


def main():

    print("Initialising TCP Server")
    s = Server(5005, verbose=True)

    try:
        print("Press CTRL+C to quit")
        # Loop indefinitely
        while(True):
            command = input("enter command: ")
            if (command == "w"):
                s.sendMotorCommand(50, 50)
            elif (command == "q"):
                s.sendMotorCommand(25, 25)
            elif (command == "e"):
                print(str(s.getSensors()))
            elif (command == "s"):
                s.sendMotorCommand(-25, -25)
            # elif (command == "a"):

            # elif (command == "d"):

    except KeyboardInterrupt:
        # CTRL+C exit, disable all drives
        s.terminate()
        print("\nUser aborted")
        sys.exit()


if __name__ == '__main__':
    main()