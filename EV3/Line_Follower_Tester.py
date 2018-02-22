#!/usr/bin/env python3
from Line_Follower import *

lineFollower = Line_Follower()

listOfLines = [['Green', 'White', 'Right', '0'],
               ['White', 'Green', 'Left', '1'],
               ['Green', 'Red', 'Right', '0'],
               ['Red', 'White', 'Right', '0'],
               ['White', 'Green', 'Left', '0']]

lineFollower.follow_lines(listOfLines)