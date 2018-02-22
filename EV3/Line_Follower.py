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
        self.l_motor_thread, self.r_motor_thread = self.initialiseMotors(speed)
        self.led_thread = self.initialiseLEDThread()

        # initialise sensors and check they are connected
        self.ultrasonicSensor = UltrasonicSensor(INPUT_AUTO); assert self.ultrasonicSensor.connected
        self.colorSensorLeft = ColorSensor('in1'); assert self.colorSensorLeft.connected
        self.colorSensorRight = ColorSensor('in4'); assert self.colorSensorRight.connected
        self.button = Button()

    def follow_line(self, colorToFollow, nextLineColor, sideTurnIsOn, junctionsToIgnore):

        # convert the string color back into a number (to help with performance)
        colorToFollow = self.COLOR_TO_NUMBER[colorToFollow]
        nextLineColor = self.COLOR_TO_NUMBER[nextLineColor]

        # the wheel rotation at the previous junction that was visited
        leftWheelRotationAtPreviousJunction = self.l_motor_thread.motor.position
        rightWheelRotationAtPreviousJunction = self.r_motor_thread.motor.position

        junctionsToIgnore = int(junctionsToIgnore)

        # follow line until enter or backspace are pressed
        try:
            while True:
                if self.button.enter or self.button.backspace:
                    Exception("Exit button was pressed.")

                # if something is close to the sensor, stop motors until it's gone
                if self.ultrasonicSensor.value() < 90:  # 90mm
                    self.pauseMotorsAndStartLEDFlashing()

                    self.say("I am in danger!")

                    while self.ultrasonicSensor.value() < 90:
                        if self.button.enter or self.button.backspace:
                            Exception("Exit button was pressed.")

                    # while broken indicates obstacle is gone
                    self.unpauseMotorsAndStopLEDFlashing()

                # reverse the left wheel if the left colour sensor is colorToFollow
                if self.colorSensorLeft.color == colorToFollow:
                    self.l_motor_thread.reverse = True
                else:
                    self.l_motor_thread.reverse = False

                # reverse the right wheel if the right colour sensor is colorToFollow
                if self.colorSensorRight.color == colorToFollow:
                    self.r_motor_thread.reverse = True
                else:
                    self.r_motor_thread.reverse = False

                # ~100hz
                sleep(0.01)

                # detect next line color
                if sideTurnIsOn == 'Left' and self.colorSensorLeft.color == nextLineColor \
                        or sideTurnIsOn == 'Right' and self.colorSensorRight.color == nextLineColor:
                    if (self.l_motor_thread.motor.position - leftWheelRotationAtPreviousJunction) > 240 \
                            and (self.r_motor_thread.motor.position - rightWheelRotationAtPreviousJunction) > 240:  # degrees
                        if junctionsToIgnore > 0:
                            junctionsToIgnore -= 1
                            leftWheelRotationAtPreviousJunction = self.l_motor_thread.motor.position
                            rightWheelRotationAtPreviousJunction = self.r_motor_thread.motor.position

                        else:
                            colorToFollow = nextLineColor
                            print("\nTurning! New color: " + self.NUM_TO_COLOR[colorToFollow])
                            return

                self.checkForSpeedChange()
                colorToFollow = self.checkForColorChange(colorToFollow)

        except Exception("Exit button was pressed."):
            print("Button was pressed - Stopping motors.")
            self.l_motor_thread.work = False
            self.r_motor_thread.work = False
            sleep(0.5)

    # accept a list of tuples containing the colors, and turnsides to follow
    def follow_lines(self, list_of_tuples):
        for (colorToFollow, nextLineColor, turnSide, junctionsToIgnore) in list_of_tuples:
            self.follow_line(colorToFollow, nextLineColor, turnSide, junctionsToIgnore)

    def initialiseMotors(self, speed):
        l_motor_thread = self.MotorThread("Left", "A")
        l_motor_thread.setDaemon(True)  # stop thread when main thread ends
        l_motor_thread.speed = speed
        l_motor_thread.start()

        r_motor_thread = self.MotorThread("Right", "D")
        r_motor_thread.setDaemon(True)
        r_motor_thread.speed = speed
        r_motor_thread.start()
        print("Starting motors: ")
        return l_motor_thread, r_motor_thread

    class MotorThread(threading.Thread):
        def __init__(self, side, out):
            self.work = True
            self.pause = False
            self.reverse = False
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

            while self.work:
                if self.pause:
                    self.motor.run_direct(duty_cycle_sp=0)
                elif self.reverse:
                    self.motor.run_direct(duty_cycle_sp=-self.speed)
                else:
                    self.motor.run_direct(duty_cycle_sp=self.speed)
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
        self.l_motor_thread.pause = True
        self.r_motor_thread.pause = True
        self.led_thread.flashing = True

    def unpauseMotorsAndStopLEDFlashing(self):
        self.led_thread.flashing = False
        self.l_motor_thread.pause = False
        self.r_motor_thread.pause = False

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
        self.l_motor_thread.speed -= 1
        self.r_motor_thread.speed -= 1
        print("\n" + "Left: " + str(self.l_motor_thread.speed) + "  -  Right: " + str(self.r_motor_thread.speed))

    def increaseSpeed(self):
        self.l_motor_thread.speed += 1
        self.r_motor_thread.speed += 1
        print("\n" + "Left: " + str(self.l_motor_thread.speed) + "  -  Right: " + str(self.r_motor_thread.speed))

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
