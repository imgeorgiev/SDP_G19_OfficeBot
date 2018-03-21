#!/usr/bin/env python3

# multi-color lines detect in HSV and distance between middle of robot vision and center of line.
import sys
sys.path.append("../tcp/")

import numpy as np
import cv2
from tcp_rpi import *
import time
import datetime
import picamera
import picamera.array


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

        weight_1 = (0.9)
        weight_2 = (0.45, 0.45)
        weight_3 = (0.3, 0.3, 0.3)
        weight_4 = (0.23, 0.23, 0.23, 0.23)

        self.weights = (weight_1, weight_2, weight_3, weight_4)

        self.threshold = 80
        self.FPS_limit = 10

        self.slicesByColor = {
            "black": [],
            "blue": [],
            "red": [],
            "purple": [],
            "green": [],
            "yellow": [],
            "white": []
        }

        # initialising numpy upper and lower bounds for cv2 mask
        blackLower = np.array([0, 0, 0])
        blackUpper = np.array([180, 255, 75])

        blueLower = np.array([100, 170, 46])
        blueUpper = np.array([124, 255, 255])

        redLower = np.array([156, 43, 46])
        redUpper = np.array([180, 255, 255])

        greenLower = np.array([35, 100, 46])
        greenUpper = np.array([85, 255, 255])

        yellowLower = np.array([22, 40, 0])
        yellowUpper = np.array([81, 255, 255])

        whiteLower = np.array([0, 0, 0])
        whiteUpper = np.array([0, 0, 150])

        purpleLower = np.array([125, 43, 46])
        purpleUpper = np.array([155, 255, 255])

        self.kernel = np.ones((5, 5), np.uint8)

        self.colorToMask = {
            "black": (blackLower, blackUpper),
            "blue": (blueLower, blueUpper),
            "red": (redLower, redUpper),
            "green": (greenLower, greenUpper),
            "yellow": (yellowLower, yellowUpper),
            "white": (whiteLower, whiteUpper),
            "purple": (purpleLower, purpleUpper),
        }

        self.previousSpeeds = (0, 0)

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
        (lower, upper) = self.colorToMask[color]

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
        return (x, y)

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

            self.slicesByColor[color].append(crop_img)

            h, w = crop_img.shape[:2]
            middleh = int(h/2)
            middlew = int(w/2)

            contours = self.image_process(crop_img)
            contours = self.contour_process(contours, h, w)

            cv2.drawContours(crop_img, contours, -1, (0, 255, 0), 3)
            cv2.circle(crop_img, (middlew, middleh), 7, (0, 0, 255), -1)  # Draw middle circle RED
            if contours:
                contourCenterX = self.getContourCenter(contours[0])[0]
                cv2.circle(crop_img, (contourCenterX, middleh), 7, (255, 255, 255), -1)  # Draw dX circle WHITE
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(crop_img, str(middlew - contourCenterX), (contourCenterX + 20, middleh), font, 1, (200, 0, 200), 2, cv2.LINE_AA)

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
        if len(distanceBiasArray) > 0:
            bias = sum(distanceBiasArray)

            # bias = sum(distance)
            print('The distance list is {}'.format(distanceBiasArray))
            print('The bias is {}'.format(bias))

            # attenuate ensures speed will be between -40 and 40   -  parser requires speed to be an integer
            speed = int(attenuate(bias/6, -40, 40))

            if abs(bias) > self.threshold:
                if bias > 0:
                    return (20 - speed, 20 + speed)
                else:
                    return (20 + abs(speed), 20 - abs(speed))
            else:
                return (50, 50)

        # no main line is detected -> reverse
        left, right = self.previousSpeeds
        return (-left, -right)


def turn(direction):
    if direction == 'right':
        server.sendTurnCommand(-60)

    elif direction == 'left':
        server.sendTurnCommand(60)


def resetDictionary(d):
    for key in d:
        d[key] = []


# noinspection PyRedundantParentheses
# returns a list of turns
def compute_path(position, destination):
    # Debugging
    log = open("log.txt", "a+")
    log.write("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] ")
    log.write("Received command to move to " + str(destination) + ".\n")

    firstTurnColor = desks[position]['color']
    secondTurnColor = desks[destination]['color']

    (firstTurnDirection, secondTurnDirection) = directionsToTurnArray[position-1][destination-1]  # -1 because desks are 1 indexed, array is 0 indexed

    # Debugging
    debug_text = "COMPUTING ROUTE." + " position: " + str(position) + ", destination: " + \
                 str(destination) + " first_junction: " + str(firstTurnDirection) + \
                 " second_junction: " + str(secondTurnDirection) + ". MOVING."
    print(debug_text)
    log.write("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] ")
    log.write(debug_text + "\n")
    log.close()
    return ((firstTurnColor, firstTurnDirection), (secondTurnColor, secondTurnDirection))


def main():
    global server, ESCAPE_KEY, camera, line, mainLineColor, resolution

    position = 1

    server = Server(5005)

    resolution = (320, 240)

    camera = picamera.PiCamera(resolution=resolution, framerate=20)

    # flip the image vertically (because the camera is upside down)
    camera.vflip = True

    # required for the camera to 'warm up'
    time.sleep(0.1)

    line = line_detect()

    mainLineColor = 'black'

    ESCAPE_KEY = 27

    while True:
        destination = getDestinationFromFile()
        if destination is not None:
            if destination == position:
                print("Destination is the same as current position. Skipping.")

            elif destination == 100 or destination == 200:
                handleManualOverride()

            else:
                if destination not in [1, 2, 3, 4, 5, 6]:
                    print("Destination not valid!")
                else:
                    path = compute_path(position, destination)

                    # follow the computed path, return when completed or escaped
                    try:
                        followPath(path)
                        position = destination
                        log_arrived_at(destination)
                    except KeyboardInterrupt:
                        # Escape key was pressed
                        server.sendMotorCommand(0, 0)
                        camera.close()
                        cv2.destroyAllWindows()
                        break

        else:
            print("File was empty.")
            time.sleep(1)


def handleManualOverride():
    print("MANUAL OVERRIDE TRIGGERED.")
    while True:
        # TODO: trigger ps4 controls, and periodically check for 200 code to remove manual override
        pass


# checks if there is a new destination to go to (written by app.py)
def getDestinationFromFile():
    file = open("dest.txt", "r+")
    content = file.read()
    if len(content) > 0:
        print("File content: " + content)
        destination = int(content)

        # empty the file
        file.seek(0)
        file.truncate()
        file.close()

        return destination
    else:
        file.close()
        return None


# follows the given path until a circle marking the end of path is detected
def followPath(path):
    for junction in path:
        followTillJunction(junction)
    followTillEnd()


def followTillJunction(junction):
    (junctionColor, turnDirection) = junction

    rawCapture = picamera.array.PiRGBArray(camera, size=resolution)
    startTime = time.time()
    # Capture images, opencv uses bgr format, not using video port is faster but takes lower quality images
    for _ in camera.capture_continuous(rawCapture, format='bgr', use_video_port=False):
        print(time.time() - startTime)

        rawCapture.truncate(0)  # clear the rawCapture array

        frame = rawCapture.array

        # reset the arrays of slices
        line.slicesByColor[mainLineColor] = []
        line.slicesByColor[junctionColor] = []

        # isolating colors and getting distance between centre of vision and centre of line
        frameWithoutBackground = line.RemoveBackground_HSV(frame, mainLineColor)
        mainLineDistanceBiases = line.computeDistanceBiases(frameWithoutBackground, line.numSlices, mainLineColor)

        HSV_startingColor = line.RemoveBackground_HSV(frame, junctionColor)
        isTurnColorInFrame = line.computeDistanceBiases(HSV_startingColor, line.numSlices, junctionColor)

        if isTurnColorInFrame:
            turn(turnDirection)
            return
        else:
            (new_left_motor_speed, new_right_motor_speed) = line.computeWheelSpeeds(mainLineDistanceBiases)

            print('DEBUG: left motor speed: {}'.format(new_left_motor_speed))
            print('DEBUG: right motor speed: {}'.format(new_right_motor_speed))

            if (new_left_motor_speed, new_right_motor_speed) != line.previousSpeeds:
                server.sendMotorCommand(new_left_motor_speed, new_right_motor_speed)
                line.previousSpeeds = (new_left_motor_speed, new_right_motor_speed)

#            printLinesToScreen(mainLineColor, junctionColor)

            # required when printing lines to the screen
#            pressedKey = cv2.waitKey(1) & 0xff
#            if pressedKey == ESCAPE_KEY:
#                raise KeyboardInterrupt('Exit key was pressed')
        startTime = time.time()


def followTillEnd():

    rawCapture = picamera.array.PiRGBArray(camera, size=resolution)

    # Capture images, opencv uses bgr format, not using video port is faster but takes lower quality images
    for _ in camera.capture_continuous(rawCapture, format='bgr', use_video_port=False):
        rawCapture.truncate(0)  # clear the rawCapture array

        frame = rawCapture.array

        # reset the array of slices
        line.slicesByColor[mainLineColor] = []

        # isolating colors and getting distance between centre of vision and centre of line
        HSV_lineColor = line.RemoveBackground_HSV(frame, mainLineColor)
        mainLineDistanceBiases = line.computeDistanceBiases(HSV_lineColor, line.numSlices, mainLineColor)

        isCircleInFrame = line.circle_detect(frame)

        if isCircleInFrame:
            # arrived at destination, turn around, stop motors and return
            server.sendTurnCommand(200) # 200 degrees instead of 180 because a slight overturning is fine

            time.sleep(2)

            server.sendMotorCommand(0, 0)
            return
        else:
            (new_left_motor_speed, new_right_motor_speed) = line.computeWheelSpeeds(mainLineDistanceBiases)

            print('DEBUG: left motor speed: {}'.format(new_left_motor_speed))
            print('DEBUG: right motor speed: {}'.format(new_right_motor_speed))

            if (new_left_motor_speed, new_right_motor_speed) != line.previousSpeeds:
                server.sendMotorCommand(new_left_motor_speed, new_right_motor_speed)
                if not (new_left_motor_speed < 0 and new_right_motor_speed < 0):
                    line.previousSpeeds = (new_left_motor_speed, new_right_motor_speed)

#        printLinesToScreen(mainLineColor)

        # required when printing lines to the screen
#        pressedKey = cv2.waitKey(1) & 0xff
#        if pressedKey == ESCAPE_KEY:
#            raise KeyboardInterrupt('Exit key was pressed')


def printLinesToScreen(*listOfColors):
    for color in listOfColors:
        slices = line.slicesByColor[color]

        # join slices back together
        image = line.RepackImages(slices)

        # output image to screen
        cv2.imshow(color, image)


if __name__ == '__main__':
    main()
