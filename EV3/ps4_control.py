#!/usr/bin/env python3
__author__ = "bythew3i"

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



### general functions
def scale(val, src, dst):
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def scale_stick(value):
    return scale(value, (0,255), (-100, 100))


def main():
    ### controller setup
    print("Controller Set Up ...")
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    gamepad = evdev.InputDevice(devices[0].fn)

    ### left motor
    l_motor_thread = MotorThread("LEFT", "A")
    l_motor_thread.setDaemon(True)
    l_motor_thread.start()

    ### right motor
    r_motor_thread = MotorThread("RIGHT", "D")
    r_motor_thread.setDaemon(True)
    r_motor_thread.start()


    ### controller listener
    sqr_cnt = 0
    cir_cnt = 0
    gopro_pow = False
    sound_config = '-a 300 -s 110'
    for event in gamepad.read_loop():
        if event.type == 3: # analog
            if event.code == 5: # right stick Y
                print("Right stick Y movement")
                l_motor_thread.speed = -scale_stick(event.value)
                r_motor_thread.speed = -scale_stick(event.value)

            if event.code == 0: # left stick X
                print("Left stick X movement")
                if event.value > 133:
                    r_motor_thread.pause = True
                elif event.value < 122:
                    l_motor_thread.pause = True
                else:
                    l_motor_thread.pause = False
                    r_motor_thread.pause = False

        if event.type == 1: # key pressed
            if event.value == 1:
                if event.code == 304: # SQR btn -> gopro photo mode
                    print("SQR button pressed")
                    option = sqr_cnt % 2
                    if option == 0:
                        cmd = "go pro photo mode"
                    elif option == 1:
                        cmd = "go pro take a photo"
                    brickman.Sound.speak(cmd, sound_config)
                    sqr_cnt += 1

                elif event.code == 305: # X btn -> turn off go pro
                    print("X button pressed")
                    brickman.Sound.speak("Go pro turn off", sound_config)

                elif event.code == 306: # O btn -> go pro video mode
                    print("O buitton pressed")
                    option = cir_cnt % 3
                    if option == 0:
                        cmd = "go pro video mode"
                    elif option == 1:
                        cmd = "go pro start recording"
                    else:
                        cmd = "go pro stop recording"
                    brickman.Sound.speak(cmd, sound_config)
                    cir_cnt += 1

                elif event.code == 307 and gopro_pow == False: # TRI btn -> turn on go
                    print("TRI button pressed")
                    gopro_pow = True
                    pass
                elif event.code == 316: # PS btn -> quit the program
                    print("Quiting ...")
                    l_motor_thread.work = False
                    r_motor_thread.work = False
                    break
            if event.value == -1:
                if event.code == 16: # left btn
                    print("left button pressed")
                    pass
                elif event.code == 17: # up btn
                    print("up button pressed")
                    pass
main()