#!/usr/bin/env python3
from ev3.linefollowing.LineFollower import *

lineFollower = LineFollower(250)  # set speed to 250

listOfLines = [['Black', 'Blue', 'Left', '0'],
               ['Blue', 'Black', 'Right', '0'],
               ['Black', 'Blue', 'Right', '0'],
               ['Blue', 'Black', 'Left', '0']]

# the method checkForSpeedChange increases/decreases the speed of the motors using the up/down buttons.
print("Press enter to begin.")
while not Button().enter:
    lineFollower.checkForSpeedChange()

print("Calling line follower.")
lineFollower.follow_lines(listOfLines)

print("Done.")
sleep(5)
