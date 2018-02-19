#!/usr/bin/env python3
from time import sleep
from ev3dev.auto import *
import threading

class Line_Follower:
    def __init__(self):
        ultrasonicSensor = UltrasonicSensor(INPUT_AUTO); assert ultrasonicSensor.connected
        colorSensorLeft = ColorSensor('in1'); assert colorSensorLeft.connected
        colorSensorRight = ColorSensor('in4'); assert colorSensorRight.connected
        button = Button()

    def main(self):
        # Connect color and ultrasonic sensors and check that they
        # are connected.
        global COLORS, l_motor_thread, r_motor_thread, led_thread

        ultrasonicSensor = UltrasonicSensor(INPUT_AUTO); assert ultrasonicSensor.connected
        colorSensorLeft = ColorSensor('in1'); assert colorSensorLeft.connected
        colorSensorRight = ColorSensor('in4'); assert colorSensorRight.connected

        # define conversion between number and color
        COLORS = {0: 'None', 1: 'Black', 2: 'Blue', 3: 'Green', 4: 'Yellow', 5: 'Red', 6: 'White', 7: 'Brown'}

        # FOR TESTING PURPOSES TODO remove
        lineColorToFollow = 5  # red
        nextColor = 3  # blue
        turnSide = 'left'
        speed = 30

        self.follow_line(lineColorToFollow, nextColor, speed, turnSide)


    def follow_line(self, colorToFollow, nextLineColor, speed, sideTurnIsOn):
        self.initialiseMotors(speed)
        self.initialiseLEDThread()

        # follow line until enter or backspace are pressed
        while True:
            if self.button.enter or self.button.backspace:
                Exception("Exit button was pressed.")

            # if something is close to the sensor, stop motors until it's gone
            if self.ultrasonicSensor.value() < 90:  # 90mm
                self.pauseMotorsAndStartLEDFlashing()

                self.sayImInDanger()

                while self.ultrasonicSensor.value() < 90:
                    if self.button.enter or self.button.backspace:
                        Exception("Exit button was pressed.")

                # while broken indicates obstacle is gone
                self.unpauseMotorsAndStopLEDFlashing()


            # reverse the left wheel if the left colour sensor is colorToFollow
            if self.colorSensorLeft.color == colorToFollow:
                l_motor_thread.reverse = True
            else:
                l_motor_thread.reverse = False

            # reverse the right wheel if the right colour sensor is colorToFollow
            if self.colorSensorRight.color == colorToFollow:
                r_motor_thread.reverse = True
            else:
                r_motor_thread.reverse = False

            # ~100hz
            sleep(0.01)

            # detect next line color
            if sideTurnIsOn == 'LEFT' and self.colorSensorLeft.color == nextLineColor \
                    or sideTurnIsOn == 'RIGHT' and self.colorSensorRight.color == nextLineColor:
                colorToFollow = nextLineColor
                print("\nTurning! New color: " + COLORS[colorToFollow])

            self.checkForSpeedChange()

            colorToFollow = self.checkForColorChange(colorToFollow)

        print("Button was pressed - Stopping motors.")
        l_motor_thread.motor.stop()
        r_motor_thread.motor.stop()
        sleep(0.5)


    def initialiseMotors(self, speed):
        l_motor_thread = self.MotorThread("LEFT", "A")
        l_motor_thread.setDaemon(True)  # stop thread when main thread ends
        l_motor_thread.speed = speed
        l_motor_thread.start()

        r_motor_thread = self.MotorThread("RIGHT", "D")
        r_motor_thread.setDaemon(True)
        r_motor_thread.speed = speed
        r_motor_thread.start()
        print("Starting motors: ")


    ### general classes
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
                if self.pause:
                    self.motor.run_direct(duty_cycle_sp=0)
                elif self.reverse:
                    self.motor.run_direct(duty_cycle_sp=-self.speed)
                else:
                    self.motor.run_direct(duty_cycle_sp=self)
            self.motor.stop()


    def initialiseLEDThread(self):
        led_thread = self.FlashLEDs()
        led_thread.setDaemon(True)
        led_thread.start()


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
        l_motor_thread.pause = True
        r_motor_thread.pause = True
        led_thread.flashing = True


    def unpauseMotorsAndStopLEDFlashing(self):
        led_thread.flashing = False
        l_motor_thread.pause = False
        r_motor_thread.pause = False


    def sayImInDanger(self):
        Sound.set_volume(100)
        Sound.speak("I am in danger!")


    def checkForSpeedChange(self):
        # increase speed with UP button, decrease with Down
        if self.button.up:
            self.increaseSpeed()
        if self.button.down:
            self.decreaseSpeed()


    def decreaseSpeed(self):
        l_motor_thread.speed -= 1
        r_motor_thread.speed -= 1
        print("\n" + "Left: " + str(l_motor_thread.speed) + "  -  Right: " + str(r_motor_thread.speed))


    def increaseSpeed(self):
        l_motor_thread.speed += 1
        r_motor_thread.speed += 1
        print("\n" + "Left: " + str(l_motor_thread.speed) + "  -  Right: " + str(r_motor_thread.speed))


    def checkForColorChange(self, colorToFollow):
        # change line color to follow with left/right
        if self.button.left:
            colorToFollow = (colorToFollow - 1) % len(COLORS)
            print("\nLine color: " + COLORS[colorToFollow])
        if self.button.right:
            colorToFollow = (colorToFollow + 1) % len(COLORS)
            print("\nLine color: " + COLORS[colorToFollow])
        return colorToFollow


    if __name__ == '__main__':
        main()
