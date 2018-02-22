#!/usr/bin/env python2


# Library for sending UDP commands to an EV3
# Commands include: motors
# Message headers:
#   RQT: RPI -> EV3 request sensor data
#   SNR: EV3 -> RPI send sensor data
#   CMD: RPI -> EV3 send motor command
# EV3 IP: 169.254.21.39
# RPI IP: 169.254.21.44

from tcpcom import TCPClient
from ev3dev.auto import *
import threading
# import sys

leftMotor = LargeMotor('outA');  assert leftMotor.connected
rightMotor = LargeMotor('outD'); assert rightMotor.connected

ultrasonicSensor = UltrasonicSensor(INPUT_AUTO); assert ultrasonicSensor.connected
colorSensorLeft = ColorSensor('in1'); assert colorSensorLeft.connected
colorSensorRight = ColorSensor('in4'); assert colorSensorRight.connected

ip = "169.254.21.39"
port = 5005

class Client:
    global stateTrans
    isConnected = False
    reqSensorReceived = False
    sensorData = None

    def __init__(self, ip, port):
        self._Client = TCPClient(ip, port, stateChanged=stateTrans)
        # self._isConnected = False
        # self._reqSensorReceived = False
        # self._sensorData = None
        self._colorList = ("N", "BK", "BL", "G", "Y", "R", "W", "BW")

    def stateTrans(state, msg):
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
                Client.receiveLineFollowCommand(msg)
            elif(msg[0:2] == "CMD"):
                Client.receiveMotorCommand(msg)
            else:
                print("ERROR: Message not recognised")

    def sendSensorData(self):
        sensorMessage = "SNR:" + ultrasonicSensor.value() + "," + \
        self._colorList[colorSensorRight.color] + "," + self._colorList[colorSensorLeft.color]
        self._Client.sendMessage(sensorMessage)

    def receiveLineFollowCommand(self,msg):
        twoCharColors = 0
        if (msg[5] != ","):
            twoCharColors = 1
            lineToFollow = msg[4:5]
            if (msg[8] != ","):
                twoCharColors = 2
                nextLine = msg[7:8]
            else:
                nextLine = msg[7]

            if (twoCharColors == 1):
                sideToTurn = msg[9]
                junctionsToSkip = int(msg[11:len(msg)])
            else:
                sideToTurn = msg[10]
                junctionsToSkip = int(msg[12:len(msg)])

        else:
            lineToFollow = msg[4]
            if (msg[7] != ","):
                twoCharColors = 1
                nextLine = msg[6:7]
            else:
                nextLine = msg[6]

            if (twoCharColors == 0):
                sideToTurn = msg[8]
                junctionsToSkip = int(msg[10:len(msg)])
            else:
                sideToTurn = msg[9]
                junctionsToSkip = int(msg[11:len(msg)])



    def receiveMotorCommand(self,msg):
        if (msg[4] == "R"):
            motorSide = "R"
        elif(msg[4] == "L"):
            motorSide = "L"
        else:
            motorSide = None
            print("ERROR: Motor side not recognised")

        motorSpeed = int(msg[:len(msg)])


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

    client = Client(ip,port)
    print("Client starting")


    try:
        while(1):
            pass

    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()