#!/usr/bin/env python3

# multi-color lines detect in HSV and distance between middle of robot vision and center of line.

import sys
sys.path.append('../tcp')

import numpy as np
import cv2
from tcp_rpi import *
import time, sched, datetime


desks = {
    1: {'name': 'Desk 1', 'color': 'purple'},
    2: {'name': 'Desk 2', 'color': 'green'},
    3: {'name': 'Desk 3', 'color': 'yellow'},
    4: {'name': 'Desk 4', 'color': 'blue'},
    5: {'name': 'Desk 5', 'color': 'red'},
    6: {'name': 'Desk 6', 'color': 'white'}
}

directionsToTurnArray = [
    [(None, None), ("right", "left"), ("right", "right"), ("right", "left"), ("right", "right"), ("right", "left")],
    [("right", "left"), (None, None), ("left", "right"), ("left", "left"), ("left", "right"), ("left", "left")],
    [("left", "left"), ("left", "right"), (None, None), ("right", "left"), ("right", "right"), ("right", "left")],
    [("right", "left"), ("right", "right"), ("right", "left"), (None, None), ("left", "right"), ("left", "left")],
    [("left", "left"), ("left", "right"), ("left", "left"), ("left", "right"), (None, None), ("right", "left")],
    [("right", "left"), ("right", "right"), ("right", "left"), ("right", "right"), ("right", "left"), (None, None)]
]

def log_arrived_at(destination):
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
        self.numSlices = 4

        weight_1 = [0.9]
        weight_2 = [0.45, 0.45]
        weight_3 = [0.3, 0.3, 0.3]
        weight_4 = [0.23, 0.23, 0.23, 0.23]

        self.weights = [weight_1, weight_2, weight_3, weight_4]

        self.threshold = 70
        self.FPS_limit = 10

        self.listOfArraySlicesByColor = {
            "black": [],
            "blue": [],
            "red": [],
            "purple": [],
            "green": [],
            "yellow": [],
            "white": []
        }

        # initialising numpy upper and lower bounds for cv2 mask
        self.blackLower = np.array([0, 0, 0])
        self.blackUpper = np.array([180, 255, 75])

        self.blueLower = np.array([100, 170, 46])
        self.blueUpper = np.array([124, 255, 255])

        self.redLower = np.array([156, 43, 46])
        self.redUpper = np.array([180, 255, 255])

        self.greenLower = np.array([35, 100, 46])
        self.greenUpper = np.array([85, 255, 255])

        self.yellowUpper = np.array([22, 40, 0])
        self.yellowLower = np.array([81, 255, 255])

        self.whiteLower = np.array([0, 0, 0])
        self.whiteUpper = np.array([0, 0, 150])

        self.purpleLower = np.array([125, 43, 46])
        self.purpleUpper = np.array([155, 255, 255])

        self.kernel = np.ones((5, 5), np.uint8)

        self.colorToMask = {
            "black": (self.blackLower, self.blackUpper),
            "blue": (self.blueLower, self.blueUpper),
            "red": (self.redLower, self.redUpper),
            "green": (self.greenLower, self.greenUpper),
            "yellow": (self.yellowLower, self.yellowUpper),
            "white": (self.whiteLower, self.whiteUpper),
            "purple": (self.purpleLower, self.purpleUpper),
        }

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

    def RemoveBackground_HSV(self, image, color):
        maskLowerAndUpper = self.colorToMask[color]
        lower = maskLowerAndUpper[0]
        upper = maskLowerAndUpper[1]

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.dilate(mask, self.kernel, iterations=5)
        mask = cv2.erode(mask, self.kernel, iterations=4)

        image = cv2.bitwise_and(image, image, mask=mask)
        image = cv2.bitwise_not(image, image, mask=mask)
        image = (255 - image)

        return image

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
            if i != 0:
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
    def computeDistanceBiases(self, image, numberOfSlices, color):
        # divide the image horizontally into numberOfSlices
        # find contours of slice

        sliceHeight = int(self.height / numberOfSlices)
        distance = []

        for i in range(numberOfSlices):
            heightOffset = sliceHeight*i
            crop_img = image[heightOffset:heightOffset + sliceHeight, 0:self.width]

            self.listOfArraySlicesByColor[color].append(crop_img)

            h, w = crop_img.shape[:2]
            middleh = int(h/2)
            middlew = int(w/2)

            contours = self.image_process(crop_img)
            contours = self.contour_process(contours, h, w)

            cv2.drawContours(crop_img, contours,-1, (0, 255, 0), 3)
            cv2.circle(crop_img, (middlew, middleh), 7, (0, 0, 255), -1)  # Draw middle circle RED
            if contours:
                contourCenterX = self.getContourCenter(contours[0])[0]
                cv2.circle(crop_img, (contourCenterX, middleh), 7, (255, 255, 255), -1)  # Draw dX circle WHITE
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(crop_img,str(middlew - contourCenterX),(contourCenterX + 20, middleh), font, 1,(200,0,200),2,cv2.LINE_AA)
#               cv2.putText(crop_img,"Weight:%.3f"%self.getContourExtent(contours[0]),(contourCenterX+20, middleh+35), font, 0.5,(200,0,200),1,cv2.LINE_AA)
#               bias = int(middlew-contourCenterX) * self.getContourExtent(contours[0])
                bias = int(middlew - contourCenterX)

                distance.append(bias)

        # return distance array reversed
        return distance[::-1]

    # this function will detect whether there is a circle(destination) in the robot vision
    @staticmethod
    def circle_detect(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 100, param1=100, param2=30, minRadius=0, maxRadius=200)
        return (circles is not None)

    # through the distance bias array, we can use this function to reach line_following
    def computeWheelSpeeds(self, distanceBiasArray):
        # threshold of corner
        # send command to ev3
        if distanceBiasArray is not None:
            num = len(distanceBiasArray) - 1
            bias = [i*j for i, j in zip(distanceBiasArray, self.weights[num])]
            bias = sum(bias)

            # bias = sum(distance)
            print('The distance list is {}'.format(distanceBiasArray))
            print('The bias is {}'.format(bias))

            # attenuate ensures speed will be between -40 and 40   -  parser requires speed to be an integer
            speed = int(attenuate(bias/6, -40, 40))

            if abs(bias) > self.threshold:
                if bias > 0:
                    return [20 - speed, 20 + speed]
                else:
                    return [20 + abs(speed), 20 - abs(speed)]
            else:
                return [50, 50]

        # no main line is detected -> reverse
        return [-50, -50]

def turn(direction):
    if direction == 'right':
        server.sendTurnCommand(-60)

    elif direction == 'left':
        server.sendTurnCommand(60)

def resetDictionary(dict):
    for key in dict:
        dict[key] = []

# noinspection PyRedundantParentheses
def compute_path(position, destination):
    # Debugging
    log = open("log.txt", "a+")
    log.write("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] ")
    log.write("Received command to move to " + str(destination) + ".\n")

    destinationDeskColor = desks[destination]['color']
    startingDeskColor = desks[position]['color']

    route = directionsToTurnArray[position-1][destination-1]  # -1 because desks are 1 indexed, array is 0 indexed

    firstTurnDirection = route[0]
    secondTurnDirection = route[1]

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
    global server

    position = 6
    destination = None
    inMotion = False

    # schedule = sched.scheduler(time.time, time.sleep)
    server = Server(5005)

    line = line_detect()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, line.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, line.height)
    cap.set(cv2.CAP_PROP_FPS, line.FPS_limit)

    mainLineColor = 'black'

    ESCAPE_KEY = 27

    # file ping counter
    while True:
        ############################# LOGIC ##############################
        if not inMotion:

            # check if there is a new destination to go to (written by app.py)
            file = open("dest.txt", "r+")
            content = file.read()

            if len(content) > 0:
                print("File content: " + content)
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

                # empty the file
                file.seek(0)
                file.truncate()
                file.close()

                print("RECEIVED DESTINATION: " + str(destination) + ".")
                if (destination != position):
                    if (destination not in [1, 2, 3, 4, 5, 6]):
                        print("Destination not valid!")
                    else:
                        [firstTurnDirection, secondTurnDirection, startingDeskColor, destinationDeskColor] = compute_path(position, destination)
                        inMotion = True
                else:
                    print("Destination is the same as current position. Skipping.")
            else:
                print("File was empty, waiting 1 second and checking again")
                time.sleep(1)

            file.close()

        # get frame from camera
        inputFrameExists, frame = cap.read()

        if not inputFrameExists:
            print('DEBUG: No input frames')
            time.sleep(1)
        else:
            if inMotion:
                if startingDeskColor == destinationDeskColor:
                    print('DEBUG: Destination does not change')
                else:
                    isCircleInFrame = line.circle_detect(frame)

                    # reset the arrays of slices
                    resetDictionary(line.listOfArraySlicesByColor)

                    # isolating colors and getting distance between centre of vision and centre of line
                    HSV_lineColor = line.RemoveBackground_HSV(frame, mainLineColor)
                    distance_mainLine = line.computeDistanceBiases(HSV_lineColor, line.numSlices, mainLineColor)

                    HSV_startingColor = line.RemoveBackground_HSV(frame, startingDeskColor)
                    isStartingColorInFrame = \
                        line.computeDistanceBiases(HSV_startingColor, line.numSlices, startingDeskColor)

                    HSV_destinationColor = line.RemoveBackground_HSV(frame, destinationDeskColor)
                    isDestinationColorInFrame = \
                        line.computeDistanceBiases(HSV_destinationColor, line.numSlices, destinationDeskColor)

                    printLinesToScreen(line, [mainLineColor, startingDeskColor, destinationDeskColor])

                    # if camera doesn't detect the first or second junctions, or the destination
                    if not (isStartingColorInFrame or isDestinationColorInFrame or isCircleInFrame):
                            [new_left_motor_speed, new_right_motor_speed] = line.computeWheelSpeeds(distance_mainLine)
                            print('DEBUG: left motor speed: {}'.format(new_left_motor_speed))
                            print('DEBUG: right motor speed: {}'.format(new_right_motor_speed))
                            server.sendMotorCommand(new_left_motor_speed, new_right_motor_speed)
                    else:
                        if isStartingColorInFrame:
                            turn(firstTurnDirection)

                        elif isDestinationColorInFrame and not isCircleInFrame:
                            turn(secondTurnDirection)

                        else:
                            inMotion = False
                            position = destination
                            log_arrived_at(destination)
                            server.sendMotorCommand(0, 0)

                    # required by cv2 visualisation
                    pressedKey = cv2.waitKey(1) & 0xff
                    if pressedKey == ESCAPE_KEY:
                        break
                    time.sleep(0.05)


    cap.release()
    cv2.destroyAllWindows()


def printLinesToScreen(line, listOfColors):
    for color in listOfColors:
        slices = line.listOfArraySlicesByColor[color]

        # join slices back together
        image = line.RepackImages(slices)

        # output image to screen
        cv2.imshow(color, image)

if __name__ == '__main__':
    main()
