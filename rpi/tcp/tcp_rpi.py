#!/usr/bin/env python2


# Library for sending UDP commands to an EV3
# Commands include: motors
# Message headers:
#   RQT: RPI -> EV3 request sensor data
#   SNR: EV3 -> RPI send sensor data
#   CMD: RPI -> EV3 send motor command
# EV3 IP: 169.254.21.39
# RPI IP: 169.254.21.44

from tcpcom import TCPServer
# import sys


tcp_ip = "169.254.21.44"    # 169.254.21.44
tcp_port = 5005
tcp_reply = "Server message"
toSend = False


class Server:
    global stateTrans
    isConnected = False
    reqSensorReceived = False
    sensorData = None

    def __init__(self, port):
        self._server = TCPServer(port, stateChanged=stateTrans)
        # self._isConnected = False
        # self._reqSensorReceived = False
        # self._sensorData = None
        self._colorList = ("R", "W", "BW", "N", "BK", "BL", "G", "Y")

    def stateTrans(state, msg):
        if state == "LISTENING":
            print("DEBUG: Server:-- Listening...")
        elif state == "CONNECTED":
            isConnected = True
            print("DEBUG: Server:-- Connected to ", msg)
        elif state == "MESSAGE":
            print("DEBUG: Server:-- Message received: ", msg)
            if(msg[0:2] == "SNR"):
                reqSensorReceived = True
                sensorData = msg
                print("DEBUG: Server:-- Sensor message received: ",
                    sensorData)

    def getSensors(self):
        self._server.sendMessage("RQT")
        while(not self._reqSensorReceived):
            pass
        return self._sensorData

    # Sends a command mapped to a motor. Params:
    # motor - either L or R, stands for left or right
    # speed - int in range [-100, 100]
    def sendCommand(self, motor, speed, pause=False, stop=False):
        # Motor input error
        motor.upper()
        motor = motor[0]
        if(not (motor == 'L' or motor == 'R')):
            raise Exception("ERROR: Wrong motor param")

        # Speed input error
        if(speed > 100):
            speed = 100
        elif(speed < -100):
            speed = -100
        else:
            raise Exception("ERROR: Wrong speed param")

        sendMsg = str("CMD:", motor, "'", speed, "'", pause, "'", stop)
        self._server.sendMessage(sendMsg)

    def sendLineFollow(self, currentColor, nextColor, side, numJunctionsToIgnote):
        if(currentColor not in self._colorList):
            raise Exception("ERROR: Invalid currentColor input")
        if(nextColor not in self._colorList):
            raise Exception("ERROR: Invalid nextColor input")
        side = side.upper()[0]
        if(not (side == "L" or side == "R")):
            raise Exception("ERROR: Invalid side input")

        sendMsg = str("LFW:", currentColor, ",", nextColor, ",",
            side, ",", numJunctionsToIgnote)

        self._server.sendMessage(sendMsg)


def main():
    Server(5005)

    try:
        while(1):
            pass

    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
