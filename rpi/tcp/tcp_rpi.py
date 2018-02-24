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
import pygame  # needed for joystick commands
import sys
import time


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
            print("DEBUG: Server: Message received: ", msg)
            if(msg[0:2] == "SNR"):
                reqSensorReceived = True
                sensorData = msg
                print("DEBUG: Server: Sensor message received: ", sensorData)

    def getSensors(self):
        self._server.sendMessage("RQT")
        while(not reqSensorReceived):
            pass
        return sensorData

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
        # else:
        #     raise Exception("ERROR: Wrong speed param")

        sendMsg = "CMD:" + motor + "," + str(speed)
        self._server.sendMessage(sendMsg)

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
    return scale(value, (0, 1), (-100, 100))


# Generic scale function
# Scale src range to dst range
def scale(val, src, dst):
    return (int(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]


def attenuate(val, min, max):
    if val > max:
        return max
    if val < min:
        return min


# Settings for the joystick
yAxis = 5               # Joystick axis to read for up / down position
xAxis = 0               # Joystick axis to read for left / right position


def main():

    print("Initialising TCP Server")
    s = Server(5005)

    pygame.init()
    print("Waiting for joystick... (press CTRL+C to abort)")
    while True:
        try:
            try:
                pygame.joystick.init()
                # Attempt to setup the joystick
                if(pygame.joystick.get_count() < 1):
                    # No joystick attached, set LEDs blue
                    pygame.joystick.quit()
                    time.sleep(0.1)
                else:
                    # We have a joystick, attempt to initialise it!
                    joystick = pygame.joystick.Joystick(0)
                    break
            except pygame.error:
                # Failed to connect to the joystick
                pygame.joystick.quit()
                time.sleep(0.1)
        except KeyboardInterrupt:
            # CTRL+C exit, give up
            print("\nUser aborted")
            sys.exit()
    print("Joystick found")
    print("Initialising PS4 joystick")
    joystick.init()

    try:
        print("Press CTRL+C to quit")
        yAxis = 0.0
        xAxis = 0.0
        # Loop indefinitely
        while(True):
            # Get the latest events from the system
            hadEvent = False
            events = pygame.event.get()
            # Handle each event individually
            for event in events:
                if event.type == pygame.JOYBUTTONDOWN:
                    # A button on the joystick just got pushed down
                    hadEvent = True
                elif event.type == pygame.JOYAXISMOTION:
                    # A joystick has been moved
                    hadEvent = True
                    if event.value == yAxis:
                        yPoll = True
                        ySpeed = joystick.get_axis(yAxis)
                    elif event.value == xAxis:
                        xPoll = True
                        xSpeed = joystick.get_axis(xAxis)
                if(hadEvent and xPoll and yPoll):
                    # Determine the drive power levels
                    xSpeed = scale_stick(xSpeed)
                    ySpeed = scale_stick(ySpeed)

                    l_wheel_speed = attenuate(ySpeed - xSpeed / 2)
                    r_wheel_speed = attenuate(ySpeed + xSpeed / 2)

                    s.sendCommand("L", l_wheel_speed)
                    s.sendCommand("R", r_wheel_speed)

                    xPoll = False
                    yPoll = False
    except KeyboardInterrupt:
        # CTRL+C exit, disable all drives
        s.terminate()
        print("\nUser aborted")
        sys.exit()


if __name__ == '__main__':
    main()
