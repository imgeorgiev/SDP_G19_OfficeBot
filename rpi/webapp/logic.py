#!/usr/bin/env python3

# multi-color lines detect in HSV and distance between middle of robot vision and center of line.

import sys
# TODO: modify path for when on rpi
sys.path.append('/home/vaida/SDP_G19_OfficeBot/rpi/tcp')

import numpy as np
import cv2
from tcp_rpi import *
import time, sched, datetime


desks = {
    1: {'name': 'Desk 1', 'colour': 'purple'},
    2: {'name': 'Desk 2', 'colour': 'green'},
    3: {'name': 'Desk 3', 'colour': 'yellow'},
    4: {'name': 'Desk 4', 'colour': 'blue'},
    5: {'name': 'Desk 5', 'colour': 'red'},
    6: {'name': 'Desk 6', 'colour': 'white'}
}

def log_success():
    log = open("log.txt", "a+")
    log.write("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] ")
    log.write("Successfully moved to " + str(destination) + ".\n")
    print("MOVED TO " + str(destination) + ". BACK TO PINGING FILE.")
    log.close()


# noinspection PyPep8Naming,PyRedundantParentheses
class line_detect():
    def __init__(self):
        self.width = 320
        self.height = 240
        self.slice = 4

        self.weight_1 = [0.9]
        self.weight_2 = [0.45, 0.45]
        self.weight_3 = [0.3, 0.3, 0.3]
        self.weight_4 = [0.23, 0.23, 0.23, 0.23]

        self.threshold = 70
        self.FPS_limit = 10

        self.image_black = []
        self.image_blue = []
        self.image_red = []
        self.image_purple = []
        self.image_green = []
        self.image_yellow = []
        self.image_white = []

        # initialising numpy upper and lower bounds for cv2 mask
        self.blackLower = np.array([0, 0, 0])
        self.blackUpper = np.array([180, 255, 75])

        self.blueLower = np.array([100, 170, 46])
        self.blueUpper = np.array([124, 255, 255])

        self.redLower = np.array([156, 43, 46])
        self.redUpper = np.array([180, 255, 255])

        self.greenLower = np.array([35, 100, 46])
        self.greenUpper = np.array([85, 255, 255])

        self.yellowUpper = np.array([22.32, 39.525, 0])
        self.yellowLower = np.array([81, 255, 255])

        self.whiteLower = np.array([0, 0, 0])
        self.whiteUpper = np.array([0, 0, 150])

        self.purpleLower = np.array([125, 43, 46])
        self.purpleUpper = np.array([155, 255, 255])

        self.kernel = np.ones((5, 5), np.uint8)

    # def RemoveBackground_RGB(self,image):
    #     low = 0
    #     up = 120
    #     # create NumPy arrays from the boundaries
    #     lower = np.array([low, low, low], dtype = "uint8")
    #     upper = np.array([up, up, up], dtype = "uint8")
    #     #----------------COLOR SELECTION-------------- (Remove any area that is whiter than 'upper')
    #     mask = cv2.inRange(image, lower, upper)
    #     image = cv2.bitwise_and(image, image, mask = mask)
    #     return image

    def RemoveBackground_HSV(self, image, lower, upper):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.dilate(mask, self.kernel, iterations=5)
        mask = cv2.erode(mask, self.kernel, iterations=4)

        image = cv2.bitwise_and(image, image, mask=mask)
        image = cv2.bitwise_not(image, image, mask=mask)
        image = (255 - image)

        return image

    # remove anything not black
    def RemoveBackground_HSV_Black(self, image):
        return self.RemoveBackground_HSV(image, self.blackLower, self.blackUpper)

    # remove anything not blue
    def RemoveBackground_HSV_Blue(self, image):
        return self.RemoveBackground_HSV(image, self.blueLower, self.blueUpper)

    # remove anything not red
    def RemoveBackground_HSV_Red(self, image):
        return self.RemoveBackground_HSV(image, self.redLower, self.redUpper)

    # remove anything not green
    def RemoveBackground_HSV_Green(self, image):
        return self.RemoveBackground_HSV(image, self.greenLower, self.greenUpper)

    # remove anything not yellow
    def RemoveBackground_HSV_Yellow(self, image):
        return self.RemoveBackground_HSV(image, self.yellowLower, self.yellowUpper)

    # remove anything not white
    def RemoveBackground_HSV_White(self, image):
        return self.RemoveBackground_HSV(image, self.whiteLower, self.whiteUpper)

    # remove anything not purple
    def RemoveBackground_HSV_Purple(self, image):
        return self.RemoveBackground_HSV(image, self.purpleLower, self.purpleUpper)

    # Process the image and return the contour of line, it will change image to gray scale
    @staticmethod
    def image_process(img):
        imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to Gray Scale
        element = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        dst = cv2.morphologyEx(imgray, cv2.MORPH_OPEN, element)
        _, threshold = cv2.threshold(dst, 100, 255, cv2.THRESH_BINARY_INV)  # Get Threshold
        _, contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # Get contour
        # mainContour = max(contours, key=cv2.contourArea)
        # return mainContour
        return contours
        # return thresh

    # get the center of contour
    @staticmethod
    def getContourCenter(contour):
        M = cv2.moments(contour)

        if M["m00"] == 0:
            return 0

        x = int(M["m10"] / M["m00"])
        y = int(M["m01"] / M["m00"])
        return [x, y]

    # it will delete contours which area less than a specifiy threshold
    @staticmethod
    def contour_process(img, h, w):
        contour = []
        for i in range(len(img)):
            cnt = img[i]
            area = cv2.contourArea(cnt)
            # this is the threshold
            if (area >= (h/20 * w/20)):
                contour.append(cnt)
        return contour

    # it will concatenate the image in array
    @staticmethod
    def RepackImages(image):
        img = image[0]
        for i in range(len(image)):
            if i == 0:
                img = np.concatenate((img, image[1]), axis=0)
            if i > 1:
                img = np.concatenate((img, image[i]), axis=0)
        return img

    # def draw(self, img, contour):
    #     if self.getContourCenter(contour) != 0:
    #         self.contourCenterX = self.getContourCenter(contour)[0]
    #     self.dir =  int((self.middleX-self.contourCenterX) * self.getContourExtent(contour))
    #     cv2.drawContours(img,contour,-1,(0,255,0),3) #Draw Contour GREEN
    #     cv2.circle(img, (self.contourCenterX, self.middleY), 7, (255,255,255), -1) #Draw dX circle WHITE
    #     cv2.circle(img, (self.middleX, self.middleY), 3, (0,0,255), -1) #Draw middle circle RED

    @staticmethod
    def getContourExtent(contour):
        area = cv2.contourArea(contour)
        _, _, w, h = cv2.boundingRect(contour)
        rect_area = w*h*3
        if rect_area > 0:
            return (float(area) / rect_area)

    # this is the main function which will return an array which contains all distance bias for every point
    def SlicePart(self, im, slice, color):
        sl = int(self.height / slice)
        distance = []

        for i in range(slice):
            part = sl*i
            crop_img = im[part:part + sl, 0:self.width]
            # middlew = middlew - 40
            # print(middlew)
            if color == 'black':
                image_blacks = [crop_img]

                self.image_black.append(crop_img)
                h, w = self.image_black[i].shape[:2]
                middleh = int(h/2)
                middlew = int(w/2)
                img = self.RemoveBackground_HSV_Black(crop_img)

            elif color == 'red':
                self.image_red.append(crop_img)
                h, w = self.image_red[i].shape[:2]
                middleh = int(h/2)
                middlew = int(w/2)
                img = self.RemoveBackground_HSV_Red(crop_img)

            elif color == 'blue':
                self.image_blue.append(crop_img)
                h, w = self.image_blue[i].shape[:2]
                middleh = int(h/2)
                middlew = int(w/2)
                img = self.RemoveBackground_HSV_Blue(crop_img)

            elif color == 'green':
                self.image_green.append(crop_img)
                h, w = self.image_green[i].shape[:2]
                middleh = int(h/2)
                middlew = int(w/2)
                img = self.RemoveBackground_HSV_Green(crop_img)

            elif color == 'yellow':
                self.image_yellow.append(crop_img)
                h, w = self.image_yellow[i].shape[:2]
                middleh = int(h/2)
                middlew = int(w/2)
                img = self.RemoveBackground_HSV_Yellow(crop_img)

            elif color == 'purple':
                self.image_purple.append(crop_img)
                h, w = self.image_purple[i].shape[:2]
                middleh = int(h/2)
                middlew = int(w/2)
                img = self.RemoveBackground_HSV_Purple(crop_img)

            elif color == 'white':
                self.image_white.append(crop_img)
                h, w  = self.image_white[i].shape[:2]
                middleh = int(h/2)
                middlew = int(w/2)
                img = self.RemoveBackground_HSV_White(crop_img)

            contours = self.image_process(img)
            contours = self.contour_process(contours, h, w)
            # print(contours)
            cv2.drawContours(crop_img, contours,-1, (0, 255, 0), 3)
            cv2.circle(crop_img, (middlew, middleh), 7, (0, 0, 255), -1) #Draw middle circle RED
            if contours:
                contourCenterX = self.getContourCenter(contours[0])[0]
                cv2.circle(crop_img, (contourCenterX, middleh), 7, (255, 255, 255), -1) #Draw dX circle WHITE
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(crop_img,str(middlew - contourCenterX),(contourCenterX + 20, middleh), font, 1,(200,0,200),2,cv2.LINE_AA)
#               cv2.putText(crop_img,"Weight:%.3f"%self.getContourExtent(contours[0]),(contourCenterX+20, middleh+35), font, 0.5,(200,0,200),1,cv2.LINE_AA)
#               bias = int(middlew-contourCenterX) * self.getContourExtent(contours[0])
                bias = int(middlew - contourCenterX)

                # record the bias distance
                distance.append(bias)
        return distance[::-1]

    # this function will detect whether there is a circle(destination) in the robot vision
    @staticmethod
    def circle_detect(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 100, param1=100, param2=30, minRadius=0, maxRadius=200)
        return (circles is not None)

    # through the distance bias array, we can use this function to reach line_following
    def line_following(self, distance):
        # threshold of corner
        # send command to ev3
        if distance:
            num = len(distance)
            if num == 1:
                bias = [i*j for i, j in zip(distance, self.weight_1)]
                bias = sum(bias)
            elif num == 2:
                bias = [i*j for i, j in zip(distance, self.weight_2)]
                bias = sum(bias)
            elif num == 3:
                bias = [i*j for i, j in zip(distance, self.weight_3)]
                bias = sum(bias)
            elif num == 4:
                bias = [i*j for i, j in zip(distance, self.weight_4)]
                bias = sum(bias)

            # bias = sum(distance)
            print('The distance list is {}'.format(distance))
            print('The bias is {}'.format(bias))

            speed = attenuate(bias/6, -40, 40)
            if abs(bias) > self.threshold:
                if bias > 0:
                    return [20 - speed, 20 + speed]
                else:
                    return [20 + abs(speed), 20 - abs(speed)]
            else:
                return [50, 50]

    def turn_R_angle(self, dir):
        if dir == 'right':
            s.sendTurnCommand(-60)

        elif dir == 'left':
            s.sendTurnCommand(60)

# noinspection PyRedundantParentheses
def compute_path(position, destination):
    # Debugging
    log = open("log.txt", "a+")
    log.write("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] ")
    log.write("Received command to move to " + str(destination) + ".\n")

    firstTurnDirection = None
    secondTurnDirection = None
    destinationDeskColor = desks[destination]['colour']
    startingDeskColor = desks[position]['colour']

    # first_junction computation
    if (position == 1):
        firstTurnDirection = "right"
    elif (position == 2):
        if (destination == 1):
            firstTurnDirection = "right"
        else:
            firstTurnDirection = "left"
    elif (position == 3):
        if (destination in [1, 2]):
            firstTurnDirection = "left"
        else:
            firstTurnDirection = "right"
    elif (position == 4):
        if (destination in [5, 6]):
            firstTurnDirection = "left"
        else:
            firstTurnDirection = "right"
    elif (position == 5):
        if (destination == 6):
            firstTurnDirection = "right"
        else:
            firstTurnDirection = "left"
    else:  # position 6
        firstTurnDirection = "none"

    # second junction
    if (destination == 6):
        secondTurnDirection = "none"
    elif (position == 1):
        if (destination in [2, 4]):
            secondTurnDirection = "left"
        else:
            secondTurnDirection = "right"
    elif (position == 2):
        if (destination in [1, 4]):
            secondTurnDirection = "left"
        else:
            secondTurnDirection = "right"
    elif (position == 3):
        if (destination in [2, 5]):
            secondTurnDirection = "right"
        else:
            secondTurnDirection = "left"
    elif (position == 4):
        if (destination in [1, 3]):
            secondTurnDirection = "left"
        else:
            secondTurnDirection = "right"
    elif (position == 5):
        if (destination in [1, 3]):
            secondTurnDirection = "left"
        else:
            secondTurnDirection = "right"
    else:  # position 6
        if (destination in [2, 4]):
            secondTurnDirection = "right"

    # Debugging
    debug_text = "COMPUTING ROUTE." + " position: " + str(position) + ", destination: " + \
                 str(destination) + " first_junction: " + str(firstTurnDirection) + \
                 " second_junction: " + str(secondTurnDirection) + ". MOVING."
    print(debug_text)
    log.write("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] ")
    log.write(debug_text + "\n")
    log.close()
    return [firstTurnDirection, secondTurnDirection, startingDeskColor, destinationDeskColor]


def main():
    global destination

    position = 1
    destination = None
    arrived = False

    # schedule = sched.scheduler(time.time, time.sleep)
    s = Server(5005)

    line = line_detect()
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, line.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, line.height)
    cap.set(cv2.CAP_PROP_FPS, line.FPS_limit)

    # file ping counter
    file_ping = 0
    while True:
        ############################# LOGIC ##############################
        file_ping = file_ping % 100

        if arrived and (file_ping == 0):
            file = open("dest.txt", "r+")
            content = file.read()
            print("File content: " + content)

            if len(content) > 0:
                destination = int(content)

                # Manual override
                if destination == 100 or destination == 200:
                    file.seek(0)
                    file.truncate()
                    file.close()
                    print("MANUAL OVERRIDE TRIGGERED.")
                    while True:
                        # TODO: trigger ps4 controls, and periodically check for 200 code to remove manual override
                        pass

                file.seek(0)
                file.truncate()
                file.close()
                print("RECEIVED DESTINATION: " + str(destination) + ".")
                if (destination != position):
                    if (destination not in [1, 2, 3, 4, 5, 6, 7, 8, 9]):
                        print("Destination not valid!")
                    else:
                        [firstTurnDirection, secondTurnDirection, startingDeskColor, destinationDeskColor] = compute_path(position, destination)

                        # Updates location
                        position = destination
                        destination = None
                else:
                    print("Destination is the same as current position. Skipping.")
            file.close()
            # time.sleep(1) # pings file every second
        file_ping += 1

        ############################# CAMERA ##############################
        inputFrameExists, readFrame = cap.read()
        if not inputFrameExists:
            print('DEBUG: No input frames')
        else:
            # the main function
            prev_dest = 'white'
            isCircleInFrame = line.circle_detect(readFrame)

            line.image_red = []
            line.image_blue = []
            line.image_black = []
            line.image_purple = []
            line.image_green = []
            line.image_yellow = []
            line.image_white = []

            ############################# HSV TEST ##############################
            HSV_black = line.RemoveBackground_HSV_Black(readFrame)
            HSV_blue = line.RemoveBackground_HSV_Blue(readFrame)
            HSV_green = line.RemoveBackground_HSV_Green(readFrame)
            HSV_yellow = line.RemoveBackground_HSV_Yellow(readFrame)
            HSV_purple = line.RemoveBackground_HSV_Purple(readFrame)
            HSV_red = line.RemoveBackground_HSV_Red(readFrame)
            HSV_white = line.RemoveBackground_HSV_White(readFrame)

            ############################# get distance between middle of vision and line #########################
            distance_Black = line.SlicePart(HSV_black, line.slice, 'black')
            distance_Blue = line.SlicePart(HSV_blue, line.slice, 'blue')
            distance_Green = line.SlicePart(HSV_green, line.slice, 'green')
            distance_Red = line.SlicePart(HSV_red, line.slice, 'red')
            distance_Yellow = line.SlicePart(HSV_yellow, line.slice, 'yellow')
            distance_Purple = line.SlicePart(HSV_purple, line.slice, 'purple')
            distance_White = line.SlicePart(HSV_white, line.slice, 'white')

            ############################# concatenate every slice ###############
            img_black = line.RepackImages(line.image_black)
            img_blue = line.RepackImages(line.image_blue)

            # output images to screen
            cv2.imshow('img_black',img_black)
            cv2.imshow('img_blue', img_blue)

            ############################# pseudocode #################
            # if the robot doesn't turn:
            # if distance_Black:
            # if not some_color(get from webapp):
            # line_following(black)
            # elif some_color(get from webapp):
            # line_following(some_color):
            # elif not distance_Black:
            # if not some_color(get from webapp):
            # turn_itself
            # elif some_color:
            # line_following(some_color)

            # if the robot has already turned:
            # if signal detected:
            # decide turn left or right
            # turn left or right, until signal at a "specific position".
            # reset turn
            # line_following(black)
            # if not signal detected:
            # line_following(some_color)

            ############################# send command to ev3 ###################
            # schedule.enter(1, 1, s.sendMotorCommand, argument=(int(left_motor), int(right_motor)))
            # schedule.run()
            # s.sendMotorCommand(int(left_motor), int(right_motor))

            # if first junction is none, then we only need to do once turning.
            # Only dest_color is detected, then call turn_R_angle

            if prev_dest == destinationDeskColor:
                print('DEBUG: dest does not change')
            else:
                if firstTurnDirection == 'none':
                    if destinationDeskColor == 'red':
                        if distance_Red and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Red and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif destinationDeskColor == 'blue':
                        if distance_Blue and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Blue and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif destinationDeskColor == 'green':
                        if distance_Green and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Green and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif destinationDeskColor == 'yellow':
                        if distance_Yellow and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Yellow and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif destinationDeskColor == 'purple':
                        if distance_Purple and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Purple and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif destinationDeskColor == 'white':
                        if distance_White and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_White and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)

                # if second junction is none, then we only need to do once turning.
                # Only post_color is detected, then call turn_R_angle
                elif secondTurnDirection == 'none':
                    if startingDeskColor == 'red':
                        if distance_Red and not isCircleInFrame:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Red and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'blue':
                        if distance_Blue and not isCircleInFrame:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Blue and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'green':
                        if distance_Green and not isCircleInFrame:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Green and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'yellow':
                        if distance_Yellow and not isCircleInFrame:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Yellow and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'purple':
                        if distance_Purple and not isCircleInFrame:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Purple and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'white':
                        if distance_White and not isCircleInFrame:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_White and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)

                # if first_junction and second_junction all have values
                #  we detect color combination and call function
                else:
                    if startingDeskColor == 'blue' and destinationDeskColor == 'red':
                        if distance_Blue:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Red and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Red and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'red' and destinationDeskColor == 'blue':
                        if distance_Red:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Blue and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Blue and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)

                    elif startingDeskColor == 'yellow' and destinationDeskColor == 'red':
                        if distance_Yellow:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Red and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Red and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'red' and destinationDeskColor == 'yellow':
                        if distance_Red:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Yellow and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Yellow and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)

                    elif startingDeskColor == 'green' and destinationDeskColor == 'red':
                        if distance_Green:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Red and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Red and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'red' and destinationDeskColor == 'green':
                        if distance_Red:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Green and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Green and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)

                    elif startingDeskColor == 'green' and destinationDeskColor == 'red':
                        if distance_Green:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Red and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Red and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'red' and destinationDeskColor == 'green':
                        if distance_Red:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Green and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Green and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)

                    elif startingDeskColor == 'purple' and destinationDeskColor == 'red':
                        if distance_Purple:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Red and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Red and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'red' and destinationDeskColor == 'purple':
                        if distance_Red:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Purple and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Purple and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)

                    elif startingDeskColor == 'blue' and destinationDeskColor == 'yellow':
                        if distance_Blue:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Yellow and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Yellow and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'yellow' and destinationDeskColor == 'blue':
                        if distance_Yellow:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Blue and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Blue and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)

                    elif startingDeskColor == 'blue' and destinationDeskColor == 'green':
                        if distance_Blue:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Green and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Green and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'green' and destinationDeskColor == 'blue':
                        if distance_Green:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Blue and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Blue and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)

                    elif startingDeskColor == 'blue' and destinationDeskColor == 'purple':
                        if distance_Blue:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Purple and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Purple and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'purple' and destinationDeskColor == 'blue':
                        if distance_Purple:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Blue and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Blue and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)

                    elif startingDeskColor == 'yellow' and destinationDeskColor == 'green':
                        if distance_Yellow:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Green and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Green and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'green' and destinationDeskColor == 'yellow':
                        if distance_Green:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Yellow and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Yellow and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)

                    elif startingDeskColor == 'yellow' and destinationDeskColor == 'purple':
                        if distance_Yellow:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Purple and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Purple and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'purple' and destinationDeskColor == 'yellow':
                        if distance_Purple:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Yellow and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Yellow and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)

                    elif startingDeskColor == 'green' and destinationDeskColor == 'purple':
                        if distance_Green:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Purple and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Purple and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'purple' and destinationDeskColor == 'green':
                        if distance_Purple:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Green and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Green and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            log_success()
                            arrived = False
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'white' and destinationDeskColor == 'purple':
                        if distance_White:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Purple and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Purple and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'purple' and destinationDeskColor == 'white':
                        if distance_Purple:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_White and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_White and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            log_success()
                            arrived = False
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'white' and destinationDeskColor == 'red':
                        if distance_White:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Red and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Red and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'red' and destinationDeskColor == 'white':
                        if distance_Red:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_White and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_White and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            log_success()
                            arrived = False
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'white' and destinationDeskColor == 'blue':
                        if distance_White:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Blue and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Blue and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'blue' and destinationDeskColor == 'white':
                        if distance_Blue:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_White and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_White and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            log_success()
                            arrived = False
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'white' and destinationDeskColor == 'yellow':
                        if distance_White:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Yellow and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Yellow and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'yellow' and destinationDeskColor == 'white':
                        if distance_Yellow:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_White and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_White and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            log_success()
                            arrived = False
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'white' and destinationDeskColor == 'green':
                        if distance_White:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_Green and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_Green and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            arrived = False
                            log_success()
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)
                    elif startingDeskColor == 'green' and destinationDeskColor == 'white':
                        if distance_Green:
                            line.turn_R_angle(firstTurnDirection)
                        elif distance_White and not isCircleInFrame:
                            line.turn_R_angle(secondTurnDirection)
                        elif distance_White and isCircleInFrame:
                            prev_dest = destinationDeskColor
                            log_success()
                            arrived = False
                            pass
                        else:
                            [new_left_motor_speed, new_right_motor_speed] = line.line_following(distance_Black)

                # if prev_l != new_left_motor_speed or new_right_motor_speed != prev_r:
                print('DEBUG: left motor speed: {}'.format(new_left_motor_speed))
                print('DEBUG: right motor speed: {}'.format(new_right_motor_speed))

                s.sendMotorCommand(new_left_motor_speed, new_right_motor_speed)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
