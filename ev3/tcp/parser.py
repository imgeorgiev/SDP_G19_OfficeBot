#!/usr/bin/env python3
# Was forced to do this as the class implimentation didn't work exactly

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
import ev3dev.auto as ev3
import threading
# import sys

server_ip = "169.254.21.39"
server_port = 5005

# client = TCPClient(ip, port, stateChanged=stateTrans)
LCmdMsg = 0
RCmdMsg = 0
lfwMsg = None
ultra = 0
lColour = None
rColour = None

colorList = ("R", "W", "BW", "N", "BK", "BL", "G", "Y")


def stateTrans(state, msg):
    global isConnected
    global lfwMsg
    global LCmdMsg
    global RCmdMsg

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
            sendSensorData()
        elif(msg[0:2] == "LFW"):
            lfwMsg = parseMsg(msg)
        elif(msg[0:2] == "CMD"):
            if(msg[4] == "L"):
                LCmdMsg = parseMsg(msg)[1]
            elif(msg[4] == "R"):
                RCmdMsg = parseMsg(msg)[1]
        else:
            print("ERROR: Message not recognised")


def sendSensorData():
    sensorMessage = "SNR:" + str(ultra) + "," + lColour + "," + rColour
    client.sendMessage(sensorMessage)


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

        self.motor = ev3.LargeMotor(ev3.OUTPUT_A)
        if out.upper() == "B":
            self.motor = ev3.LargeMotor(ev3.OUTPUT_B)
        elif out.upper() == "C":
            self.motor = ev3.LargeMotor(ev3.OUTPUT_C)
        elif out.upper() == "D":
            self.motor = ev3.LargeMotor(ev3.OUTPUT_D)

        threading.Thread.__init__(self)

    def run(self):
        print(self.side, "wheel is ready")
        while self.work:
            if self.reverse:
                self.speed = -self.speed
            if self.pause:
                self.speed = 0
            self.motor.run_direct(duty_cycle_sp=-self.speed)

        self.motor.stop()


def main():
    global ultra
    global lColor
    global rColor
    global client

    lMotorThread = MotorThread("LEFT", "A")
    lMotorThread.setDaemon(True)
    lMotorThread.start()

    rMotorThread = MotorThread("RIGHT", "D")
    rMotorThread.setDaemon(True)
    rMotorThread.start()

    ultrasonicSensor = ev3.UltrasonicSensor(ev3.INPUT_AUTO)
    assert ultrasonicSensor.connected
    colorSensorLeft = ev3.ColorSensor('in1')
    assert colorSensorLeft.connected
    colorSensorRight = ev3.ColorSensor('in4')
    assert colorSensorRight.connected

    client = TCPClient(server_ip, server_port, stateChanged=stateTrans)
    print("Client starting")

    rc = client.connect()
    if rc:
        isConnected = True  # not sure if needed
        while(isConnected):
            rMotorThread.speed = RCmdMsg
            print("DEBUG: Right motor set to ", RCmdMsg)
            lMotorThread.speed = LCmdMsg
            print("DEBUG: Left motor set to ", LCmdMsg)

            ultra = ultrasonicSensor.value()
            lColor = colorList[colorSensorLeft.color]
            rColor = colorList[colorSensorRight.color]


if __name__ == '__main__':
    main()
