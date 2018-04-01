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


from tcpcom_py3 import TCPClient
import ev3dev.auto as ev3
import ev3dev.ev3 as brickman
from time import sleep
import threading

server_ip = "169.254.23.50"
server_port = 5005

colorList = ("R", "W", "BW", "N", "BK", "BL", "G", "Y")

sound_config = '-a 300 -s 110'
GEAR_RATIO = 3
SCALE = 1.9

def main():
    global client
    global leftMotor, rightMotor

    # initialise motors
    leftMotor = CustomMotor("LEFT", "A")
    rightMotor = CustomMotor("RIGHT", "D")

    leftMotor.setPolarity("inversed")
    rightMotor.setPolarity("inversed")

    # start TCP client
    client = TCPClient(server_ip, server_port, stateChanged=onStateChanged, isVerbose=False)
    print("Client starting")

    try:
        while True:
            rc = client.connect()
            sleep(0.01)
            if rc:
                isConnected = True
                while isConnected:
                    sleep(0.001)
            else:
                print("Client:-- Connection failed")
                sleep(0.1)
    except KeyboardInterrupt:
        pass
    leftMotor.stop()
    rightMotor.stop()
    client.disconnect()
    threading.cleanup_stop_thread()


def setWheelSpeeds(leftMotor, rightMotor, wheelSpeedMessage):
    newLeftWheelSpeed = int(wheelSpeedMessage[0])
    leftMotor.speed = newLeftWheelSpeed
    leftMotor.forward()
#   print("DEBUG: Left motor set to ", newLeftWheelSpeed)

    newRightWheelSpeed = int(wheelSpeedMessage[1])
    rightMotor.speed = newRightWheelSpeed
    rightMotor.forward()
#   print("DEBUG: Right motor set to ", newRightWheelSpeed)


def onStateChanged(state, msg):
    global isConnected

    if state == "LISTENING":
        print("DEBUG: Client:-- Listening...")

    elif state == "CONNECTED":
        isConnected = True
        print("DEBUG: Client:-- Connected to ", msg)

    elif state == "DISCONNECTED":
        isConnected = False
        print("DEBUG: Client:-- Connection lost.")
        leftMotor.stop()
        rightMotor.stop()
        main()

    elif state == "MESSAGE":
#        print("DEBUG: Client:-- Message received: ", msg)

        if(msg[0:3] == "CMD"):
            wheelSpeedMessage = parseMsg(msg)
            setWheelSpeeds(leftMotor, rightMotor, wheelSpeedMessage)

        elif(msg[0:3] == "TRN"):
            degrees = int(parseMsg(msg)[0])

            # turn the robot clockwise by degrees
            leftMotor.turn(degrees)
            rightMotor.turn(degrees * -1)

        elif(msg[0:3] == "SPK"):
            msg = parseMsg(msg)
            brickman.Sound.speak(msg, sound_config)

        else:
            print("ERROR: Message not recognised")

# helper func: Discard message header and split the rest into a list
def parseMsg(msg):
    return msg[4:].split(",")


class CustomMotor:
    def __init__(self, side, out):
        self.side = side
        self.speed = 0

        self.motor = ev3.LargeMotor(ev3.OUTPUT_A)
        if out.upper() == "B":
            self.motor = ev3.LargeMotor(ev3.OUTPUT_B)
        elif out.upper() == "C":
            self.motor = ev3.LargeMotor(ev3.OUTPUT_C)
        elif out.upper() == "D":
            self.motor = ev3.LargeMotor(ev3.OUTPUT_D)

    def reverse(self):
        self.motor.run_forever(speed_sp=-self.speed*9) # scaling

    def forward(self):
        self.motor.run_forever(speed_sp=self.speed*9)

    def stop(self):
        self.motor.stop()

    def setPolarity(self, polarity):
        self.motor.polarity = polarity

    def turn(self, degrees):
        self.motor.run_to_rel_pos(position_sp=int(degrees*GEAR_RATIO*SCALE))

if __name__ == '__main__':
    main()