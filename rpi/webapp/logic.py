#!/usr/bin/env python3

# Mock-up structure of line following/scheduling algorithm

# scheduling of queue? based on current? picking from web-app
# current position var

import time
import datetime

position = 1

destination = None

desks = {
    1 : {'name' : 'Desk 1', 'colour' : 'purple'},
    2 : {'name' : 'Desk 2', 'colour' : 'green'},
    3 : {'name' : 'Desk 3', 'colour' : 'yellow'},
    4 : {'name' : 'Desk 4', 'colour' : 'blue'},
    5 : {'name' : 'Desk 5', 'colour' : 'red'},
    6 : {'name' : 'Desk 6', 'colour' : 'red'}
}

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

    first_junction = None
    second_junction = None
    dest_colour = desks[desk]['colour']

    # first_junction computation
    if (position == 1):
        first_junction = "right"
    elif (position == 2):
        if (destination == 1):
            first_junction = "right"
        else:
            first_junction = "left"
    elif (position == 3):
        if (destination in [1, 2]):
            first_junction = "left"
        else:
            first_junction = "right"
    elif (position = 4):
        if (destination in [5, 6]):
            first_junction = "left"
        else:
            first_junction = "right"
    elif (position = 5):
        if (destination = 6):
            first_junction = "right"
        else:
            first_junction = "left"
    else: # position 6
        first_junction = "none"

    # second junction
    if (destination == 6):
        second_junction = "none"
    elif (position == 1):
        if (destination in [2, 4]):
            second_junction = "left"
        else:
            second_junction = "right"
    elif (position == 2):
        if (destination in [1, 4]):
            second_junction = "left"
        else:
            second_junction = "right"
    elif (position == 3):
        if (destination in [2, 5]):
            second_junction = "right"
        else:
            second_junction = "left"
    elif (position == 4):
        if (destination in [1, 3]):
            second_junction = "left"
        else:
            second_junction = "right"
    elif (position == 5):
        if (destination in [1, 3]):
            second_junction = "left"
        else:
            second_junction = "right"
    else: # position 6
        if (destination in [2, 4]):
            second_junction = "right"

    # Debugging
    debug_text = "COMPUTING ROUTE." + " position: " + str(position) + ", destination: " + \
    str(destination) + "first_junction: " + str(first_junction) + \
    "second_junction: " + str(second_junction) + ". MOVING."
    print(debug_text)
    log.write("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] ")
    log.write(debug_text + "\n")

    # camera.followLine(first_junction, second_junction, dest_colour)

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
        file = open("dest.txt","r+")
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
