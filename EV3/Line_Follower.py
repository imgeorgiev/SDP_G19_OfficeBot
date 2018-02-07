#!/usr/bin/env python3
from time import sleep
from ev3dev.auto import *
import threading


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
            if self.reverse:
                self.speed = -motorSpeed
            if self.pause:
                self.speed = 0
            self.motor.run_direct(duty_cycle_sp=-self.speed)  # speed negative because forward direction is negative

        self.motor.stop()

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
                sleep(0.300)  #300ms
                Leds.set_color(Leds.LEFT, Leds.RED)
                Leds.set_color(Leds.RIGHT, Leds.RED)
                sleep(0.300)  #300ms


# Connect color and ultrasonic sensors and check that they
# are connected.
ultrasonicSensor = UltrasonicSensor(INPUT_AUTO); assert ultrasonicSensor.connected
colorSensorLeft = ColorSensor('in1'); assert colorSensorLeft.connected
colorSensorRight = ColorSensor('in4'); assert colorSensorRight.connected

# define conversion between number and color
COLORS = {0: 'None', 1: 'Black', 2: 'Blue', 3: 'Green', 4: 'Yellow', 5: 'Red', 6: 'White', 7: 'Brown'}
colorToFollow = 1

button = Button()

### left motor initilisation
l_motor_thread = MotorThread("LEFT", "A")
l_motor_thread.setDaemon(True)  # stop thread when main thread ends
l_motor_thread.start()

### right motor initilisation
r_motor_thread = MotorThread("RIGHT", "D")
r_motor_thread.setDaemon(True)
r_motor_thread.start()

### LED thread initialisaion
led_thread = FlashLEDs()
led_thread.setDaemon(True)
led_thread.start()

print("Starting motors: ")
motorSpeed = 30

# follow line until enter or backspace are pressed
while not button.enter or button.backspace:
    # if something is close to the sensor, stop motors until it's gone
    if ultrasonicSensor.value() < 90:  #90mm
        l_motor_thread.pause = True
        r_motor_thread.pause = True
        led_thread.flashing = True

        Sound.set_volume(100)
        Sound.speak("I am in danger!")

        while ultrasonicSensor.value() < 90:
            # ensures program can exit while sensor is covered
            if button.enter or button.backspace:
                break

        # while broken indicates obstacle is gone
        led_thread.flashing = False
        l_motor_thread.pause = False
        r_motor_thread.pause = False

    # reverse the left wheel if the left colour sensor is colorToFollow
    if COLORS[colorSensorLeft.color] == COLORS[colorToFollow]:
        l_motor_thread.reverse = True
    else:
        l_motor_thread.speed = motorSpeed
        l_motor_thread.reverse = False

    # reverse the right wheel if the right colour sensor is colorToFollow
    if COLORS[colorSensorRight.color] == COLORS[colorToFollow]:
        r_motor_thread.reverse = True
    else:
        r_motor_thread.speed = motorSpeed
        r_motor_thread.reverse = False
    sleep(0.01)

    # increase speed with UP button, decrease with Down
    if button.up:
        motorSpeed += 1
        print("\n" + str(motorSpeed))
    if button.down:
        motorSpeed -= 1
        print("\n" + str(motorSpeed))

    # change line color to follow with left/right
    if button.left:
        colorToFollow = (colorToFollow - 1) % len(COLORS)
        print("\nLine color: " + COLORS[colorToFollow])
    if button.right:
        colorToFollow = (colorToFollow + 1) % len(COLORS)
        print("\nLine color: " + COLORS[colorToFollow])

print("Button was pressed - Stopping motors.")
l_motor_thread.motor.stop()
r_motor_thread.motor.stop()
sleep(5)