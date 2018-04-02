import pygame  # needed for joystick commands
import sys
import time
import os


class psControl:

    def __init__(self, xAxis=0, yAxis=5, exitButton=9):
        # Using PS3 settings by default
        self._xAxis = xAxis
        self._yAxis = yAxis
        self._exitButton = exitButton
        self._axisFactor = 100  # number to scale the joy outputs with
        self._joystick = None
        self._prevSpeed = [0, 0]
        self._prevXSpeed = 0
        self._prevYSpeed = 0
        self.pairController()

    # transform joystick inputs to motor outputs
    def scale_stick(self, value):
        if value == 0.0:
            return 0.0
        else:
            return self.scale(value, (-1, 1), (-100, 100))

    # Generic scale function
    # Scale src range to dst range
    def scale(self, val, src, dst):
        return (int(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

    def attenuate(self, val, min, max):
        if val > max:
            return max
        if val < min:
            return min
        return val

    def pairController(self):
        pygame.init()
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.display.init()
        self._screen = pygame.display.set_mode((1, 1))
        print("pairing controller")
        while True:
            try:
                try:
                    pygame.joystick.init()
                    # Attempt to setup the joystick
                    if(pygame.joystick.get_count() < 1):
                        # No joystick attached, set LEDs blue
                        pygame.joystick.quit()
                        time.sleep(0.1)
                        print("no joystick found, trying again")
                    else:
                        # We have a joystick, attempt to initialise it!
                        self._joystick = pygame.joystick.Joystick(0)
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
        self._joystick.init()

    # reads the joystick inputs and returns motor commands
    # if running fine it returns True
    # if received new motor command returns the motor commands as a list
    # if exit button is pressed returns False
    def spin(self):
        xSpeed = 0
        ySpeed = 0
        xPoll = False
        yPoll = False

        # Get the latest events from the system
        hadEvent = False
        events = pygame.event.get()
        # Handle each event individually
        for event in events:
            if event.type == pygame.JOYBUTTONDOWN:
                # A button on the joystick just got pushed down
                hadEvent = True
                # print("DEBUG: had keypress event", event.button)
                self._prevButton = event.button

            elif event.type == pygame.JOYBUTTONUP:
                hadEvent = True
                # print("DEBUG: had keypress release", event.button)

                if (event.button == self._prevButton and event.button == self._exitButton):
                    return False

            elif event.type == pygame.JOYAXISMOTION:
                # A joystick has been moved
                # print("DEBUG: had joystick event")
                # print(event.dict, event.joy, event.axis, event.value)
                hadEvent = True
                if event.axis == self._yAxis:
                    yPoll = True
                    axisVal = -self._joystick.get_axis(self._yAxis) * self._axisFactor
                    if axisVal != self._prevYSpeed:
                        self._prevYSpeed = axisVal
                        ySpeed = axisVal
                    # print("DEBUG: y axis used", str(ySpeed))
                if event.axis == self._xAxis:
                    xPoll = True
                    axisVal = -self._joystick.get_axis(self._xAxis) * self._axisFactor
                    if axisVal != self._prevXSpeed:
                        self._prevXSpeed = axisVal
                        xSpeed = axisVal
                    # print("DEBUG: x axis used", str(xSpeed))

            if hadEvent:
                # Determine the drive power levels
                # print("xspeed: " + str(xSpeed) + " yspeed: " + str(ySpeed))
                # xSpeed = scale_stick(xSpeed)
                # ySpeed = scale_stick(ySpeed)
                xPoll = False
                yPoll = False
                hadEvent = False

                leftSpeed = ySpeed - (xSpeed / 2)
                rightSpeed = ySpeed + (xSpeed / 2)
                # print("l_wheel: " + str(leftSpeed) + " r_wheel: " + str(rightSpeed))
                leftSpeed = int(self.attenuate(leftSpeed, -100, 100))
                rightSpeed = int(self.attenuate(rightSpeed, -100, 100))
                newSpeed = [leftSpeed, rightSpeed]
                # print("l_wheel: " + str(l_wheel_speed) + " r_wheel: " + str(r_wheel_speed))

                # print("DEBUG: Joystick command send reached")
                if (self._prevSpeed != newSpeed):
                    self._prevSpeed = newSpeed
                    return newSpeed
        return True


def main():
    joy = psControl()
    print("Starting main loop")

    while True:
        joy_val = joy.spin()
        if joy_val is not True:
            print(joy_val)

        if joy_val is False:
            print("exiting while true loop")
            break

    print("Finishing program")


if __name__ == '__main__':
    main()
