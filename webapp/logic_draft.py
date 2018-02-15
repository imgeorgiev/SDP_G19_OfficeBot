#!/usr/bin/env python3

# Mock-up structure of line following/scheduling algorithm

# scheduling of queue? based on current? picking from web-app
# current position var

import time

position = 1

destination = None

def main():

    while (True):
        # TODO write a draft polling & print every few seconds
        file = open("dest.txt","r+")
        content = file.read()
        print("Content of file is: " + content)
        if (len(content) > 0):
            destination = int(content)
            file.seek(0)
            file.truncate()
            file.close()
            print("Moving to " + str(destination))
            move_path(destination)
        time.sleep(1)

def move_path(destination):
    # General logic for moving the robot to the destination
    # move_to_main_line()
    # wait_for("move_to_main_line ok")
    # turn_towards_destination("main enter", position, destination)
    # wait_for("turn_towards_destination ok")
    # move_towards(destination)
    # wait_for("move_towards ok")
    # turn_towards_destination("main exit", position, destination)
    # move_towards(destination)
    # wait_for("move_towards ok")
    time.sleep(5)
    print("Moved to " + str(destination) + ".")

if __name__ == '__main__':
    main()

# def query_app():
#     # Pulls the most immediate destination from the web-app.
#     pass

# def move_to_main_line():
#     # Moves the robot from a desk to the intersection with the main black line
#     pass
#
# def wait_for(acknowledgment):
#     # Blocks until ev3 has sent an acknowledgment of succeeding in the task
#     # Is this necessary, or should we just continuously send commands to the brick?
#
#     # Also updates position variable
#     pass
#
# def turn_towards_destination(state, position, destination):
#     # Uses current location and destination to decide whether the robot should
#     # follow the main line to the left or to the right, and what direction
#     # it should turn towards when it reached the appropriate colour
#     # Differentiate between the two situations with the state variable
#     pass
#
# def move_towards(destination):
#     # Simple line-following until the colour of destination is reached
#     # Possibly might need to differentiate between main line->color stop and
#     # colour line-> end of line stop, with a "type" variable
#     pass
