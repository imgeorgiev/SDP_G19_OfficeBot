#!/usr/bin/env python3

# Mock-up structure of line following/scheduling algorithm

# scheduling of queue? based on current? picking from web-app
# current position var

import time
import datetime

position = 1

destination = None

def wait_for_packet():
    # infinite loop while a TCP packet has not been received; blocks
    # the program until EV3 gives okay that it has encountered next_color

    # for testing:
    time.sleep(1)

    pass


def follow_line(current_color, next_color):
    # will call LineFollower(current_color, next_color), which will follow
    # current_color until it reaches next_color. it will then send a TCP
    # packet back to the RPi, allowing the next follow_line to execute
    pass

def compute_path():
    global position
    global destination

    # Debugging
    log = open("log.txt","a+")
    log.write("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] ")
    log.write("Received command to move to " + str(destination) + ".\n")

    # color to follow to get to the white line,
    # aka turning left or right using either blue or red
    color_to_white = None

    # color to follow to destination when on the white line
    color_to_dest = None

    # How many times should a color be skipped until the right
    # turn is encountered (eg. from 3 to 5, the *second* red should be used)
    # a value of 0 means the first encounter of that color should be followed
    skip_counter = 0

    # Compute color_to_white
    if (position == 1):
        color_to_white = "red"
    elif (position == 6):
        color_to_white = "blue"
    elif (position == 2):
        if (destination == 1):
            color_to_white = "red"
        else:
            color_to_white = "blue"
    elif (position == 3):
        if (destination in [1, 2]):
            color_to_white = "blue"
        else:
            color_to_white = "red"
    elif (position == 4):
        if (destination in [5, 6]):
            color_to_white = "blue"
        else:
            color_to_white = "red"
    elif (position == 5):
        if (destination == 6):
            color_to_white = "blue"
        else:
            color_to_white = "red"

    # Compute color_to_dest and skip_counter
    if (position == 1):
        if (destination == 2):
            color_to_dest = "red"
            skip_counter = 0
        elif (destination == 3):
            color_to_dest = "blue"
            skip_counter = 1
        elif (destination ==  4):
            color_to_dest = "red"
            skip_counter = 2
        elif (destination == 5):
            color_to_dest = "red"
            skip_counter = 3
        else: # dest = 6
            color_to_dest = "blue"
            skip_counter = 4
    elif (position == 2):
        if (destination == 1):
            color_to_dest = "red"
            skip_counter = 0
        elif (destination == 3):
            color_to_dest = "blue"
            skip_counter = 0
        elif (destination ==  4):
            color_to_dest = "red"
            skip_counter = 1
        elif (destination == 5):
            color_to_dest = "red"
            skip_counter = 2
        else: # dest = 6
            color_to_dest = "blue"
            skip_counter = 3
    elif (position == 3):
        if (destination == 1):
            color_to_dest = "red"
            skip_counter = 1
        elif (destination == 2):
            color_to_dest = "blue"
            skip_counter = 0
        elif (destination ==  4):
            color_to_dest = "red"
            skip_counter = 0
        elif (destination == 5):
            color_to_dest = "red"
            skip_counter = 1
        else: # dest = 6
            color_to_dest = "blue"
            skip_counter = 2
    elif (position == 4):
        if (destination == 1):
            color_to_dest = "red"
            skip_counter = 2
        elif (destination == 2):
            color_to_dest = "blue"
            skip_counter = 1
        elif (destination ==  3):
            color_to_dest = "red"
            skip_counter = 0
        elif (destination == 5):
            color_to_dest = "red"
            skip_counter = 0
        else: # dest = 6
            color_to_dest = "blue"
            skip_counter = 1
    elif (position == 5):
        if (destination == 1):
            color_to_dest = "red"
            skip_counter = 3
        elif (destination == 2):
            color_to_dest = "blue"
            skip_counter = 2
        elif (destination ==  3):
            color_to_dest = "red"
            skip_counter = 1
        elif (destination == 4):
            color_to_dest = "blue"
            skip_counter = 0
        else: # dest = 6
            color_to_dest = "blue"
            skip_counter = 0
    else: # pos = 6
        if (destination == 1):
            color_to_dest = "red"
            skip_counter = 4
        elif (destination == 2):
            color_to_dest = "blue"
            skip_counter = 3
        elif (destination ==  3):
            color_to_dest = "red"
            skip_counter = 2
        elif (destination == 4):
            color_to_dest = "blue"
            skip_counter = 1
        else: # dest = 5
            color_to_dest = "blue"
            skip_counter = 0

    # Debugging
    debug_text = "COMPUTING ROUTE." + " position: " + str(position) + ", destination: " + \
    str(destination) + ", color_to_white: " + str(color_to_white) + \
    ", color_to_dest: " + str(color_to_dest) + ", skip_counter: " + str(skip_counter) + \
    ". MOVING."
    print(debug_text)
    log.write("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] ")
    log.write(debug_text + "\n")

    # getting to the main white line
    follow_line(color_to_white,"white")
    wait_for_packet()
    print("Got to white line.")

    # getting to the right turn
    while (skip_counter != -1):
        follow_line("white", color_to_dest)
        wait_for_packet()
        skip_counter -= 1
        print("Got to color_to_dest. Decrementing skip_counter: " + str(skip_counter))
        log.write("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] ")
        log.write("Got to color_to_dest. Decrementing skip_counter: " + str(skip_counter) + ".\n")
    print("Got to needed turn.")
    log.write("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] ")
    log.write("Got to needed turn." + "\n")

    # getting to the end of the path to the dest
    follow_line(color_to_dest, "green")
    wait_for_packet()

    log.write("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] ")
    log.write("Successfully moved to " + str(destination) + ".\n")
    print("MOVED TO " + str(destination) + ". BACK TO PINGING FILE.")

    # Updates location
    position = destination
    destination = None

def main():
    global destination
    global position

    while (True):
        file = open("/home/pi/SDP_G19_OfficeBot/rpi/webapp/dest.txt","r+")
        content = file.read()
        print("File content: " + content)

        if (len(content) > 0):
            destination = int(content)

            # Manual override
            if (destination == 100 or destination == 200):
                file.seek(0)
                file.truncate()
                file.close()
                print("MANUAL OVERRIDE TRIGGERED.")
                while(True):
                    # TO-DO: trigger ps4 controls, and periodically check
                    # for 200 code to remove manual override
                    pass

            file.seek(0)
            file.truncate()
            file.close()
            print("RECEIVED DESTINATION: " + str(destination) + ".")
            if (destination != position):

                if (destination not in [1, 2, 3, 4, 5, 6, 7, 8, 9]):
                    print("Destination not valid!")
                else:
                    compute_path()
            else:
                print("Destination is the same as current position. Skipping.")
        file.close()
        time.sleep(1) # pings file every second

if __name__ == '__main__':
    main()
