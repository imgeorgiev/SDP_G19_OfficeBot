#!/usr/bin/env python3

import evdev
import ev3dev.auto as ev3
import threading
import ev3dev.ev3 as brickman


### general classes
class MotorThread(threading.Thread):
    def __init__(self, side, out):
        self.pause = False
        self.speed = 0
        self.work = True
        self.side = side
        self.motor = ev3.LargeMotor(ev3.OUTPUT_A)
        if out.upper() == "B":
            self.motor = ev3.LargeMotor(ev3.OUTPUT_B)
        elif out.upper() == "C":
            self.motor = ev3.LargeMotor(ev3.OUTPUT_C)
        elif out.upper() == "D":
            self.motor = ev3.LargeMotor(ev3.OUTPUT_D)

        threading.Thread.__init__(self)

    def run(self):
        print(self.side, "wheel is ready")
        while self.work:
            if self.pause:
                self.speed = 0
            self.motor.run_direct(duty_cycle_sp=self.speed)

        self.motor.stop()


# transform joystick inputs to motor outputs
def scale_stick(value):
    return scale(value, (0,255), (-100, 100))

# Generic scale function
# Scale src range to dst range
def scale(val, src, dst):
    return (int(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]


def main():
    ### controller setup
    print("Controller Set Up ...")
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    gamepad = evdev.InputDevice(devices[0].fn)
    #if devices[0] is None:
        #print("Failed to connect to control device")
    #else:
        #print("connected to ", devices[0].fn, devices[0].name, devices[0].phys)

    ### left motor initilisation
    l_motor_thread = MotorThread("LEFT", "A")
    l_motor_thread.setDaemon(True)
    l_motor_thread.start()

    ### right motor initilisation
    r_motor_thread = MotorThread("RIGHT", "D")
    r_motor_thread.setDaemon(True)
    r_motor_thread.start()

    ### controller listener
    sqr_cnt = 0     # number of times SQR has been pressed
    cir_cnt = 0     # number of times CIRcle has been pressed
    x_poll = False
    y_poll = False
    y_speed = 0
    x_speed = 0
    cmd = ""
    sound_config = '-a 300 -s 110'
    for event in gamepad.read_loop():
        if event.type == 3: # analog input
            if event.code == 5: # right stick Y; fowrwards/backword movements
                #print("DEBUG: Right stick Y movement")
                y_speed = int(scale_stick(event.value))
                y_poll = True

            if event.code == 0: # left stick X
                # simple direction steering for the robot
                # TOOD: Optimize
                #print("DEBUG: Left stick X movement")
                #if event.value > 133:
                #    r_motor_thread.pause = True
                #elif event.value < 122:
                #    l_motor_thread.pause = True
                #else:
                    #l_motor_thread.pause = False
                    #r_motor_thread.pause = False
                x_speed = int(scale_stick(event.value))
                x_poll = True

            if x_poll and y_poll:
                l_wheel_speed = y_speed - x_speed/2
                r_wheel_speed = y_speed + x_speed/2
                if l_wheel_speed < -100:
                    l_wheel_speed = - 100
                elif l_wheel_speed > 100:
                    l_wheel_speed = 100

                if r_wheel_speed < -100:
                    r_wheel_speed = - 100
                elif r_wheel_speed > 100:
                    r_wheel_speed = 100

                l_motor_thread.speed = l_wheel_speed
                r_motor_thread.speed = r_wheel_speed
                print("left ", -l_wheel_speed)
                print("righ ", -r_wheel_speed)
                x_poll = False
                y_poll = False

        if event.type == 1: # key pressed
            print("btn event")
            if event.value == 1:
                if event.code == 304: # SQR button
                    print("DEBUG: SQR button pressed")
                    # option = sqr_cnt % 2  # switch support
                    # sqr_cnt += 1
                    cmd = "Hello"

                elif event.code == 305: # X btn -> turn off go pro
                    print("DEBUG: X button pressed")
                    cmd = "choo choo motherfucker"

                elif event.code == 306: # O btn -> go pro video mode
                    print("DEBUG: Circle button pressed")
                    # option = cir_cnt % 3  # switch support
                    # cir_cnt += 1
                    cmd = "Please move"

                elif event.code == 307: # TRIangle button
                    print("DEBUG: Triangle button pressed")
                    cmd = "The robots are taking over"

                elif event.code == 316: # PS button
                    print("DEBUG: Shutdown")
                    l_motor_thread.work = False
                    r_motor_thread.work = False

            elif event.value == -1:
                if event.code == 16: # left btn
                    print("DEBUG: left button pressed")

                elif event.code == 17: # up btn
                    print("DEBUG: up button pressed")

            brickman.Sound.speak(cmd, sound_config)
main()
