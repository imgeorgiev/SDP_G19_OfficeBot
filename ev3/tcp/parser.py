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

import time
from tcpcom_py3 import TCPClient
import ev3dev.auto as ev3
import threading
import ev3dev.ev3 as brickman
# import sys

server_ip = "169.254.23.50"
server_port = 5005

sound_config = '-a 300 -s 110'
GEAR_RATIO = 3

colorList = ("R", "W", "BW", "N", "BK", "BL", "G", "Y")


def main():
    global client
    global leftMotor
    global rightMotor

    leftMotor = MotorThread("LEFT", "A")
    leftMotor.setDaemon(True)
    leftMotor.start()

    rightMotor = MotorThread("RIGHT", "D")
    rightMotor.setDaemon(True)
    rightMotor.start()

    client = TCPClient(server_ip, server_port, stateChanged=stateTrans)
    print("Client starting")

    rc = client.connect()
    try:
        while(True):
            rc = client.connect()
            if rc:
                isConnected = True  # not sure if needed
                while(isConnected):
                    pass
            else:
                print("Client:-- Connection failed")
                time.sleep(0.1)
    except KeyboardInterrupt:
        rightMotor.stop()
        leftMotor.stop()
        client.disconnect()
        threading.cleanup_stop_thread()


def stateTrans(state, msg):
    global isConnected
    global ultra
    global lineFollowMsg
    global wheelSpeedMessage
    global leftMotor, rightMotor

    if state == "LISTENING":
        print("DEBUG: Client:-- Listening...")
    elif state == "CONNECTED":
        isConnected = True
        print("DEBUG: Client:-- Connected to ", msg)
    elif state == "DISCONNECTED":
        print("DEBUG: Client:-- Connection lost.")
        leftMotor.stop()
        rightMotor.stop()
        isConnected = False
        main()
    elif state == "MESSAGE":
        print("DEBUG: Client:-- Message received: ", msg)
        if(msg[0:3] == "SPK"):
            msg = parseMsg(msg)
            brickman.Sound.speak(msg, sound_config)

        elif(msg[0:3] == "CMD"):
            wheelSpeedMessage = parseMsg(msg)
            setWheelSpeeds(leftMotor, rightMotor, wheelSpeedMessage)

        elif(msg[0:3] == "TRN"):
            degrees = int(parseMsg(msg)[0])
            leftMotor.turn(degrees)
            rightMotor.turn(degrees * -1)

        else:
            print("ERROR: Message not recognised")


# helper func: Discard message header and split the rest into a list
def parseMsg(msg):
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

    def forward(self):
        self.motor.run_forever(speed_sp=self.speed * 9)

    def reverse(self):
        self.motor.run_forever(speed_sp=-self.speed * 9)

    def pause(self):
        self.motor.run_forever(speed_sp=0)

    # turns the robot clockwise by degrees
    def turn(self, degrees):
        self.motor.run_to_rel_pos(position_sp=degrees * GEAR_RATIO)

    def stop(self):
        self.motor.stop()


def setWheelSpeeds(leftMotor, rightMotor, wheelSpeedMessage):
    leftMotor.speed = int(wheelSpeedMessage[0])
    leftMotor.forward()
    # print("DEBUG: Left motor set to ", newLeftWheelSpeed)

    rightMotor.speed = int(wheelSpeedMessage[1])
    rightMotor.forward()
    # print("DEBUG: Right motor set to ", newRightWheelSpeed)


if __name__ == '__main__':
    main()
