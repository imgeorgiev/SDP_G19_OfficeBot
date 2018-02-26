#!/usr/bin/env python3
from time import sleep

from ev3dev.auto import *

# noinspection PyPep8Naming

# ------Input--------
print('Setting input values')
power = 70
#kp = 16, ki = 0, kd = 76
#kp = 12, ki = 0.632, kd = 76
#Both work kinda well but could be smoother
kp = 12  # Proportional gain. Start value 20 ; 16,0,76 <-works pretty gud; 
ki = 0.632  # Integral gain. Start value 0.01
kd = 76  # Derivative gain. Start value 0
direction = 1
minRef = 8
maxRef = 91
target = int((maxRef-minRef)/2)
# -------------------

# Connect two large motors on output ports A and D and check that
# the device is connected using the 'connected' property.
print('Connecting motors')
left_motor = LargeMotor(OUTPUT_A);  assert left_motor.connected
right_motor = LargeMotor(OUTPUT_D);  assert right_motor.connected
# One left and one right motor should be connected

# Connect color and touch sensors and check that they
# are connected.
print('Connecting sensors')
col = ColorSensor(INPUT_4)
assert col.connected

# Change color sensor mode
print('Setting color sensor mode')
col.mode = 'COL-REFLECT'

# Adding button so it would be possible to break the loop using
# one of the buttons on the brick
print('Adding button')
btn = Button()


def steering2(course, power):
    """
    Computes how fast each motor in a pair should turn to achieve the
    specified steering.
    Input:
        course [-100, 100]:
        * -100 means turn left as fast as possible,
        *  0   means drive in a straight line, and
        *  100  means turn right as fast as possible.
        * If >100 power_right = -power
        * If <100 power_left = power
    power: the power that should be applied to the outmost motor (the one
        rotating faster). The power of the other motor will be computed
        automatically.
    Output:
        a tuple of power values for a pair of motors.
    Example:
        for (motor, power) in zip((left_motor, right_motor), steering(50, 90)):
            motor.run_forever(speed_sp=power)
    """
    if course >= 0:
        if course > 100:
            power_right = 0
            power_left = power
        else:
            power_left = power
            power_right = power - ((power * course) / 100)
    else:
        if course < -100:
            power_left = 0
            power_right = power
        else:
            power_right = power
            power_left = power + ((power * course) / 100)
    return (int(power_left), int(power_right))

def run(power, target, kp, kd, ki, direction, minRef, maxRef):
    """
    PID controlled line follower algoritm used to calculate left and right motor power.
    Input:
        power. Max motor power on any of the motors
        target. Normalized target value.
        kp. Proportional gain
        ki. Integral gain
        kd. Derivative gain
        direction. 1 or -1 depending on the direction the robot should steer
        minRef. Min reflecting value of floor or line
        maxRef. Max reflecting value of floor or line
    """
    lastError = error = integral = 0
    while not btn.any():
        refRead = col.value()
        error = target - (100 * (refRead - minRef) / (maxRef - minRef))
        derivative = error - lastError
        lastError = error
        integral = float(0.5) * integral + error
        course = (kp * error + kd * derivative + ki * integral) * direction
        for (motor, pow) in zip((left_motor, right_motor), steering2(course, power)):
            motor.run_forever(speed_sp = pow*5)
        sleep(0.01)  # Aprox 100Hz


run(power, target, kp, kd, ki, direction, minRef, maxRef)

# Stop the motors before exiting.
print('Stopping motors')
left_motor.stop()
right_motor.stop()



