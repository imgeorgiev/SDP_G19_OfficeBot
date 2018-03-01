#!/usr/bin/env python3
from Line_Follower import *

lineFollower = Line_Follower(200) # set speed to 30

listOfLines = [['Black', 'Red', 'Right', '0'],
               ['Blue', 'Black', 'Right', '0'],
               ['Black', 'Red', 'Right', '0'],
               ['Red', 'Green', 'Left', '0']]

print("Press enter to begin.")
while not Button().enter:
    lineFollower.checkForSpeedChange()

print("Calling line follower.")
lineFollower.follow_lines(listOfLines)

# stop motors
lineFollower.leftMotor.stop()
lineFollower.rightMotor.stop()

print("Done.")
sleep(10)