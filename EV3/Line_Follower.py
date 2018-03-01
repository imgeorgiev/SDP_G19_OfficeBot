#!/usr/bin/env python3
from time import sleep
from ev3dev.auto import *
import threading

# noinspection PyPep8Naming
class Line_Follower:
    # define conversion between number and color
    NUM_TO_COLOR = {0: 'None', 1: 'Black', 2: 'Blue', 3: 'Green', 4: 'Yellow', 5: 'Red', 6: 'White', 7: 'Brown'}
    COLOR_TO_NUMBER = {'None': 0, 'Black': 1, 'Blue': 2, 'Green': 3, 'Yellow': 4, 'Red': 5, 'White': 6, 'Brown': 7}

    def __init__(self, speed=30):

        # initialise motors and LEDs
        self.leftMotor, self.rightMotor = self.initialiseMotors(speed)
        self.led_thread = self.initialiseLEDThread()

        # initialise sensors and check they are connected
#       self.ultrasonicSensor = UltrasonicSensor(INPUT_AUTO); assert self.ultrasonicSensor.connected
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

        # reverse wheel by default
        self.leftMotor.reverse()
        self.rightMotor.reverse()

        # follow line until enter or backspace are pressed
        while True:
#            if self.button.enter or self.button.backspace:
#                print("Button was pressed - Stopping motors.")
#                self.l_motor_thread.work = False
#                self.r_motor_thread.work = False
#                sleep(0.5)
#                break
#
#            # when something is close to the sensor, stop motors until it's gone
#            if self.ultrasonicSensor.value() < 90:  # 90mm
#                self.pauseMotorsAndStartLEDFlashing()
#
#                self.say("I am in danger!")
#
#                while self.ultrasonicSensor.value() < 90:
#                    if self.button.enter or self.button.backspace:
#                        Exception("Exit button was pressed.")
#
#                # while being broken indicates obstacle is gone
#                self.unpauseMotorsAndStopLEDFlashing()


            # reverse the left wheel if the left colour sensor is colorToFollow
            if self.colorSensorLeft.color == colorToFollow:
                if self.leftMotor.motor.speed > 0:
                    self.leftMotor.reverse()
            else:
                if self.leftMotor.motor.speed < 0:
                    self.leftMotor.forward()

            # reverse the right wheel if the right colour sensor is colorToFollow
            if self.colorSensorRight.color == colorToFollow:
                if self.rightMotor.motor.speed > 0:
                    self.rightMotor.reverse()
            else:
                if self.rightMotor.motor.speed < 0:
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
                        colorToFollow = nextLineColor
                        self.leftMotor.pause()
                        print("Waiting for Right sensor to find " + self.NUM_TO_COLOR[nextLineColor])
                        while not self.colorSensorRight.color == nextLineColor:
                            pass
                        self.leftMotor.forward()
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
                        colorToFollow = nextLineColor
                        self.rightMotor.pause()
                        print("Waiting for left sensor to find " + self.NUM_TO_COLOR[nextLineColor])
                        while not self.colorSensorLeft.color == nextLineColor:
                            pass
                        self.rightMotor.forward()
                        return

            sleep(0.01) # 100 Hz


#            self.checkForSpeedChange()
#            colorToFollow = self.checkForColorChange(colorToFollow)

    # accept a list of tuples containing the colors, and turnsides to follow
    def follow_lines(self, list_of_tuples):
        for (colorToFollow, nextLineColor, turnSide, junctionsToIgnore) in list_of_tuples:
            self.follow_line(colorToFollow, nextLineColor, turnSide, junctionsToIgnore)

    def initialiseMotors(self, speed):
        print("Initialising motors: ")

        leftMotor = self.MotorThread("Left", "A")
        leftMotor.setDaemon(True)  # stop thread when main thread ends
        leftMotor.speed = speed
        leftMotor.pause()
        leftMotor.motor.polarity ='inversed'

        rightMotor = self.MotorThread("Right", "D")
        rightMotor.setDaemon(True)
        rightMotor.speed = speed
        rightMotor.pause()
        rightMotor.motor.polarity = 'inversed'

        leftMotor.start()
        rightMotor.start()

        return leftMotor, rightMotor

    class MotorThread(threading.Thread):
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

            threading.Thread.__init__(self)

        def run(self):
            print(self.side, "wheel is ready")

        def reverse(self):
            self.motor.run_forever(speed_sp=-self.speed)

        def pause(self):
            self.motor.run_forever(speed_sp=0)

        def forward(self):
            self.motor.run_forever(speed_sp=self.speed)

        def stop(self):
            self.motor.stop()

    def initialiseLEDThread(self):
        led_thread = self.FlashLEDs()
        led_thread.setDaemon(True)
        led_thread.start()
        return led_thread

    class FlashLEDs(threading.Thread):
        def __init__(self):
            self.flashing = False
            threading.Thread.__init__(self)

        def run(self):
            while True:
                # reset LED colors to green
                Leds.set_color(Leds.LEFT, Leds.GREEN)
                Leds.set_color(Leds.RIGHT, Leds.GREEN)

                while self.flashing:
                    Leds.set_color(Leds.LEFT, Leds.GREEN)
                    Leds.set_color(Leds.RIGHT, Leds.GREEN)
                    sleep(0.300)  # 300ms
                    Leds.set_color(Leds.LEFT, Leds.RED)
                    Leds.set_color(Leds.RIGHT, Leds.RED)
                    sleep(0.300)  # 300ms

    def pauseMotorsAndStartLEDFlashing(self):
        self.leftMotor.pause()
        self.rightMotor.pause()
        self.led_thread.flashing = True

    def unpauseMotorsAndStopLEDFlashing(self):
        self.led_thread.flashing = False
        self.leftMotor.forward()
        self.rightMotor.forward()

    def say(self, message):
        Sound.set_volume(100)
        Sound.speak(message)

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

    def checkForColorChange(self, colorToFollow):
        # change line color to follow with left/right
        if self.button.left:
            colorToFollow = (colorToFollow - 1) % len(self.NUM_TO_COLOR)
            print("\nLine color: " + self.NUM_TO_COLOR[colorToFollow])
        if self.button.right:
            colorToFollow = (colorToFollow + 1) % len(self.NUM_TO_COLOR)
            print("\nLine color: " + self.NUM_TO_COLOR[colorToFollow])
        return colorToFollow

    if __name__ == '__main__':
        pass
