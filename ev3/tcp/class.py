#!/usr/bin/env python3


# Library for sending UDP commands to an EV3
# Commands include: motors
# Message headers:
#   RQT: RPI -> EV3 request sensor data
#   SNR: EV3 -> RPI send sensor data
#   CMD: RPI -> EV3 send motor command
# EV3 IP: 169.254.21.39
# RPI IP: 169.254.21.44

import evdev
from time import sleep
from tcpcom import TCPClient
from ev3dev.auto import *
import threading
# import sys

server_ip = "169.254.21.39"
server_port = 5005


class Client:
    global stateTrans
    isConnected = False

    def __init__(self, ip, port):
        self._Client = TCPClient(ip, port, stateChanged=stateTrans)
        self._LCmdMsg = None
        self._RCmdMsg = None
        self._lfwMsg = None
        self._ultra = None
        self._lColour = None
        self._rColour = None

    def connect(self):
        return self._Client.connect()

    def stateTrans(state, msg):
        global isConnected

        if state == "LISTENING":
            print("DEBUG: Client:-- Listening...")
        elif state == "CONNECTED":
            isConnected = True
            print("DEBUG: Client:-- Connected to ", msg)
        elif state == "DISCONNECTED":
            print("DEBUG: Client:-- Connection lost.")
            isConnected = False
        elif state == "MESSAGE":
            print("DEBUG: Client:-- Message received: ", msg)
            if(msg[0:2] == "RQT"):
                Client.sendSensorData()
            elif(msg[0:2] == "LFW"):
                Client.setLfwMsg(msg)
            elif(msg[0:2] == "CMD"):
                Client.setCmdMsg(msg)
            else:
                print("ERROR: Message not recognised")

    @staticmethod   # needed to make the message callable from stateTrans
    def sendSensorData(self):
        sensorMessage = "SNR:" + str(self._ultra) + "," + self._lColour + "," + self._rColour
        self._Client.sendMessage(sensorMessage)

    @staticmethod   # needed to make the message callable from stateTrans
    def setCmdMsg(self, msg):
        if (msg[4] == "L"):
            self._LCmdMsg = self.parseMsg(msg)
        elif (msg[4] == "R"):
            self._RCmdMsg = self.parseMsg(msg)

    @staticmethod   # needed to make the message callable from stateTrans
    def setLfwMsg(self, msg):
        self._lfwMsg = self.parseMsg(msg)

    def setUltra(self, val):
        self._ultra = val

    def setLColour(self, val):
        self._rColour = val

    def setRColour(self, val):
        self._lColour = val

    def getRCmdMsg(self):
        return self._RCmdMsg

    def getLCmdMsg(self):
        return self._LCmdMsg

    def getLfwMsg(self):
        return self._lfwMsg

    # helper func: Discard message header and split the rest into a list
    def parseMsg(self, msg):
        return msg[4:].split(",")


class MotorThread(threading.Thread):
    def __init__(self, side, out):
        self.work = True
        self.pause = False
        self.reverse = False
        self.speed = 0
        self.side = side

        self.motor = LargeMotor(OUTPUT_A)
        if out.upper() == "B":
            self.motor = LargeMotor(OUTPUT_B)
        elif out.upper() == "C":
            self.motor = LargeMotor(OUTPUT_C)
        elif out.upper() == "D":
            self.motor = LargeMotor(OUTPUT_D)

        threading.Thread.__init__(self)

    def run(self):
        print(self.side, "wheel is ready")
        while self.work:
            if self.reverse:
                self.speed = -self.speed
            if self.pause:
                self.speed = 0
            self.motor.run_direct(duty_cycle_sp=-self.speed)  # speed negative because forward direction is negative

        self.motor.stop()


def main():

    colorList = ("R", "W", "BW", "N", "BK", "BL", "G", "Y")

    lMotorThread = MotorThread("LEFT", "A")
    lMotorThread.setDaemon(True)
    lMotorThread.start()

    rMotorThread = MotorThread("RIGHT", "D")
    rMotorThread.setDaemon(True)
    rMotorThread.start()

    ultrasonicSensor = UltrasonicSensor(INPUT_AUTO)
    assert ultrasonicSensor.connected
    colorSensorLeft = ColorSensor('in1')
    assert colorSensorLeft.connected
    colorSensorRight = ColorSensor('in4')
    assert colorSensorRight.connected

    client = Client(server_ip, server_port)
    print("Client starting")

    rc = client.connect()
    if rc:
        while(isConnected):
            rMotorCmd = client.getLCmdMsg()
            rMotorThread.speed = rMotorCmd[1]
            print("DEBUG: Right motor set to ", rMotorCmd[1])
            lMotorCmd = client.getRCmdMsg()
            lMotorThread.speed = lMotorCmd[1]
            print("DEBUG: Left motor set to ", lMotorCmd[1])

            client.setUltra(ultrasonicSensor.value())
            client.setLColour(colorList[colorSensorLeft.color()])
            client.setRColour(colorList[colorSensorRight.color()])


if __name__ == '__main__':
    main()
