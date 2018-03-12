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
from time import sleep

server_ip = "169.254.23.50"
server_port = 5005

colorList = ("R", "W", "BW", "N", "BK", "BL", "G", "Y")

GEAR_RATIO = 3

def main():
    global leftMotor, rightMotor, ultrasonicSensor, client, isConnected
    # initialise motors
    leftMotor = CustomMotor("LEFT", "A")
    rightMotor = CustomMotor("RIGHT", "D")

    # initialise sensors
    ultrasonicSensor = ev3.UltrasonicSensor(ev3.INPUT_AUTO); assert ultrasonicSensor.connected

    # start TCP client
    client = TCPClient(server_ip, server_port, stateChanged=onStateChanged)
    print("Client starting")

    rc = client.connect()
    try:
        while True:
            if not rc:
                print("Client:-- Connection failed")
                sleep(1)
    except KeyboardInterrupt:
        pass
    leftMotor.stop()
    rightMotor.stop()
    client.disconnect()


def setWheelSpeeds(leftMotor, rightMotor, wheelSpeedMessage):
    newLeftWheelSpeed = int(wheelSpeedMessage[0])
    leftMotor.speed = newLeftWheelSpeed
    leftMotor.forward()
    print("DEBUG: Left motor set to ", newLeftWheelSpeed)

    newRightWheelSpeed = int(wheelSpeedMessage[1])
    rightMotor.speed = newRightWheelSpeed
    rightMotor.forward()
    print("DEBUG: Right motor set to ", newRightWheelSpeed)


def onStateChanged(state, msg):
    if state == "CONNECTED":
        isConnected = True
        # print("DEBUG: Client:-- Connected to ", msg)

    elif state == "DISCONNECTED":
        # print("DEBUG: Client:-- Connection lost.")
        isConnected = False

#   elif state == "LISTENING":
#       pass
#       print("DEBUG: Client:-- Listening...")

    elif state == "MESSAGE":
        # print("DEBUG: Client:-- Message received: ", msg)
        if(msg[0:3] == "RQT"):
            ultra = ultrasonicSensor.value()
            sendSensorData(ultra)

#       elif(msg[0:3] == "LFW"):
#           lineFollowMsg = parseMsg(msg)

        elif(msg[0:3] == "CMD"):
            wheelSpeedMessage = parseMsg(msg)
            setWheelSpeeds(leftMotor, rightMotor, wheelSpeedMessage)

        elif(msg[0:3] == "TRN"):
            turnMessage = parseMsg(msg)
            clockwise = int(turnMessage[0])
            degreesToTurn = int(turnMessage[1])
            turn([leftMotor, rightMotor], clockwise, degreesToTurn)

        else:
            print("ERROR: Message not recognised")


def sendSensorData(ultra):
    sensorMessage = "SNR:" + str(ultra)
    client.sendMessage(sensorMessage)


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

    def pause(self):
        self.motor.run_forever(speed_sp=0)

    def forward(self):
        self.motor.run_forever(speed_sp=self.speed*9)

    def stop(self):
        self.motor.stop()

    def setPolarity(self, polarity):
        self.motor.polarity = polarity

    def isReversing(self):
        return self.motor.speed < 0

    def isGoingForward(self):
        return self.motor.speed > 0

    def turn(self, degrees):
            self.motor.run_to_rel_pos(degrees*GEAR_RATIO)

# turns the robot by degrees, anticlockwise if clockwise is false
def turn(motors, clockwise, degrees):
        leftMotor = motors[0]
        rightMotor = motors[1]
        multiplier = 1
        if not clockwise:
            multiplier = -1
        leftMotor.turn(degrees*multiplier)
        rightMotor.turn(degrees*-multiplier)

if __name__ == '__main__':
    main()
