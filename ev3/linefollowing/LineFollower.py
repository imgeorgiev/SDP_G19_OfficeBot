#!/usr/bin/env python3
from time import sleep
from ev3dev.auto import *

# noinspection PyPep8Naming
class LineFollower:

    # define conversion between number and color
    NUM_TO_COLOR = {0: 'None', 1: 'Black', 2: 'Blue', 3: 'Green', 4: 'Yellow', 5: 'Red', 6: 'White', 7: 'Brown'}
    COLOR_TO_NUMBER = {'None': 0, 'Black': 1, 'Blue': 2, 'Green': 3, 'Yellow': 4, 'Red': 5, 'White': 6, 'Brown': 7}

    def __init__(self, speed=200):

        # initialise motors and LEDs
        self.leftMotor, self.rightMotor = self.initialiseMotors(speed)

        # initialise sensors and check they are connected
        self.colorSensorLeft = ColorSensor('in1'); assert self.colorSensorLeft.connected
        self.colorSensorRight = ColorSensor('in4'); assert self.colorSensorRight.connected
        self.button = Button()

    def follow_line(self, colorToFollow, nextLineColor, sideTurnIsOn, junctionsToIgnore=0):
        print("Following: " + colorToFollow)
        # convert the string color back into a number (to help with performance)
        colorToFollow = self.COLOR_TO_NUMBER[colorToFollow]
        nextLineColor = self.COLOR_TO_NUMBER[nextLineColor]

        # the wheel rotation at the previous junction that was visited
        leftWheelRotationAtPreviousJunction = self.leftMotor.motor.position
        rightWheelRotationAtPreviousJunction = self.rightMotor.motor.position

        junctionsToIgnore = int(junctionsToIgnore)

        # start both wheels
        self.leftMotor.forward()
        self.rightMotor.forward()

        # follow line until enter or backspace are pressed
        while True:
            # reverse the left wheel if the left colour sensor is colorToFollow
            if self.colorSensorLeft.color == colorToFollow:
                if self.leftMotor.isGoingForward():
                    self.leftMotor.reverse()
            else:
                if self.leftMotor.isReversing():
                    self.leftMotor.forward()

            # reverse the right wheel if the right colour sensor is colorToFollow
            if self.colorSensorRight.color == colorToFollow:
                if self.leftMotor.isGoingForward():
                    self.rightMotor.reverse()
            else:
                if self.rightMotor.isReversing():
                    self.rightMotor.forward()

            # detect if next line color is on left side
            if sideTurnIsOn == 'Left' and self.colorSensorLeft.color == nextLineColor:
                if (self.leftMotor.motor.position - leftWheelRotationAtPreviousJunction) > 240 \
                        and (self.rightMotor.motor.position - rightWheelRotationAtPreviousJunction) > 240:  # degrees
                    if junctionsToIgnore > 0:
                        junctionsToIgnore -= 1
                        leftWheelRotationAtPreviousJunction = self.leftMotor.motor.position
                        rightWheelRotationAtPreviousJunction = self.rightMotor.motor.position

                    else:
                        self.leftMotor.stop()
                        print("Waiting for Right sensor to find " + self.NUM_TO_COLOR[nextLineColor])
                        while not self.colorSensorRight.color == nextLineColor:
                            pass
                        self.rightMotor.stop()
                        return

            # detect if next line color is on right side
            if sideTurnIsOn == 'Right' and self.colorSensorRight.color == nextLineColor:
                if (self.leftMotor.motor.position - leftWheelRotationAtPreviousJunction) > 240 \
                        and (self.rightMotor.motor.position - rightWheelRotationAtPreviousJunction) > 240:
                    if junctionsToIgnore > 0:
                        junctionsToIgnore -= 1
                        leftWheelRotationAtPreviousJunction = self.leftMotor.motor.position
                        rightWheelRotationAtPreviousJunction = self.rightMotor.motor.position

                    else:
                        self.rightMotor.stop()
                        print("Waiting for left sensor to find " + self.NUM_TO_COLOR[nextLineColor])
                        while not self.colorSensorLeft.color == nextLineColor:
                            pass
                        self.leftMotor.stop()
                        return

            sleep(0.01)  # 100 Hz

    def initialiseMotors(self, speed):
        print("Initialising motors: ")

        leftMotor = self.CustomMotor("Left", "A")
        leftMotor.speed = speed
        leftMotor.setPolarity('inversed')

        rightMotor = self.CustomMotor("Right", "D")
        rightMotor.speed = speed
        rightMotor.setPolarity('inversed')
        return leftMotor, rightMotor

    class CustomMotor:
        def __init__(self, side, out):
            self.side = side
            self.speed = 0

            self.motor = LargeMotor(OUTPUT_A)
            if out.upper() == "B":
                self.motor = LargeMotor(OUTPUT_B)
            elif out.upper() == "C":
                self.motor = LargeMotor(OUTPUT_C)
            elif out.upper() == "D":
                self.motor = LargeMotor(OUTPUT_D)

        def reverse(self):
            self.motor.run_forever(speed_sp=-self.speed)

        def pause(self):
            self.motor.run_forever(speed_sp=0)

        def forward(self):
            self.motor.run_forever(speed_sp=self.speed)

        def stop(self):
            self.motor.stop()

        def setPolarity(self, polarity):
            self.motor.polarity = polarity

        def isReversing(self):
            return self.motor.speed < 0

        def isGoingForward(self):
            return self.motor.speed > 0

    # accept a list of tuples containing the colors, and turnsides to follow
    def follow_lines(self, list_of_tuples):
        for (colorToFollow, nextLineColor, turnSide, junctionsToIgnore) in list_of_tuples:
            self.follow_line(colorToFollow, nextLineColor, turnSide, junctionsToIgnore)

    def checkForSpeedChange(self):
        # increase speed with UP button, decrease with Down
        if self.button.up:
            self.increaseSpeed()
        if self.button.down:
            self.decreaseSpeed()

    def decreaseSpeed(self):
        self.leftMotor.speed -= 1
        self.rightMotor.speed -= 1
        print("\n" + "Left: " + str(self.leftMotor.speed) + "  -  Right: " + str(self.rightMotor.speed))

    def increaseSpeed(self):
        self.leftMotor.speed += 1
        self.rightMotor.speed += 1
        print("\n" + "Left: " + str(self.leftMotor.speed) + "  -  Right: " + str(self.rightMotor.speed))

    if __name__ == '__main__':
        pass
