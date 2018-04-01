#!/usr/bin/env python3

# multi-color lines detect in HSV and distance between middle of robot vision and center of line.
import sys
sys.path.append("../tcp/")
sys.path.append("../")

import numpy as np
import cv2
from tcp_rpi import *
import time
import datetime
import picamera
import picamera.array
import ir_reader
# import joystick


desks = {
    1: {'name': 'Desk 1', 'color': 'orange'},
    2: {'name': 'Desk 2', 'color': 'green'},
    3: {'name': 'Desk 3', 'color': 'purple'},
    4: {'name': 'Desk 4', 'color': 'yellow'},
    5: {'name': 'Desk 5', 'color': 'red'},
    6: {'name': 'Desk 6', 'color': 'blue'}
}

directionsToTurnArray = [
    [(None, None), ("left", "left"), ("left", "right"), ("left", "right"), ("left", "left"), ("left", "right")],
    [("right", "right"), (None, None), ("left", "right"), ("left", "right"), ("left", "left"), ("left", "right")],
    [("left", "right"), ("left", "right"), (None, None), ("right", "right"), ("right", "left"), ("right", "right")],
    [("left", "right"), ("left", "right"), ("left", "left"), (None, None), ("right", "left"), ("right", "right")],
    [("right", "right"), ("right", "right"), ("right", "left"), ("right", "left"), (None, None), ("left", "right")],
    [("left", "right"), ("left", "right"), ("left", "left"), ("left", "left"), ("left", "right"), (None, None)]
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

        self.previousSpeeds = (0, 0)

        self.slicesByColor = {
            "black": [],
            "blue": [],
            "red": [],
            "purple": [],
            "green": [],
            "yellow": [],
            "white": [],
            "pink" : [],
            "brown": [],
            "gray": [],
            "orange": [],
        }

        # initialising numpy upper and lower bounds for cv2 mask
        blackLower = self.transfer([0, 0, 0])
        blackUpper = self.transfer([0.278, 1, 0.294])

        blueLower = self.transfer([0.583, 0.709, 0.309])
        blueUpper = self.transfer([0.625, 1, 0.765])

        redLower = self.transfer([-0.017, 0.581, 0.304])
        redUpper = self.transfer([0.050, 0.941, 0.787])

        whiteLower = self.transfer([0, 0, 0])
        whiteUpper = self.transfer([0, 0, 0.589])

        pinkLower = self.transfer([0.943, 0.736, 0.283])
        pinkUpper = self.transfer([0.993, 1, 0.739])

        brownLower = self.transfer([0.035, 0.485, 0.411])
        brownUpper = self.transfer([0.123, 1, 0.813])

        # not sure with this range
        grayLower = self.transfer([0., 0, 0.236])
        grayUpper = self.transfer([0.717, 0.253, 0.552])

        greenLower = self.transfer([0.479, 0.853, 0.197])
        greenUpper = self.transfer([0.553, 1, 0.776])

        orangeLower = self.transfer([0.046, 0.757, 0.357])
        orangeUpper = self.transfer([0.102, 1, 1])

        purpleLower = self.transfer([0.766, 0.464, 0.240])
        purpleUpper = self.transfer([0.848, 0.749, 0.787])

        yellowLower = self.transfer([0.105, 0.480, 0.309])
        yellowUpper = self.transfer([0.182, 1, 0.807])

        self.kernel = np.ones((5, 5), np.uint8)

        self.colorToMask = {
            "black": (blackLower, blackUpper),
            "blue": (blueLower, blueUpper),
            "red": (redLower, redUpper),
            "green": (greenLower, greenUpper),
            "yellow": (yellowLower, yellowUpper),
            "white": (whiteLower, whiteUpper),
            "purple": (purpleLower, purpleUpper),
            "pink" : (pinkLower, pinkUpper),
            "brown": (brownLower, brownUpper),
            "gray": (grayLower, grayUpper),
            "orange": (orangeLower, orangeUpper),
        }


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

    def transfer(self, color_Range):
        color_Range[0] = int(color_Range[0]*180)
        color_Range[1] = int(color_Range[1]*255)
        color_Range[2] = int(color_Range[2]*255)
        return np.array([color_Range[0], color_Range[1], color_Range[2]])

    # Process the image and return the contour of line, it will change image to gray scale
    @staticmethod
    def getContours(img):
        element = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))

        imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to Gray Scale

        # remove noise from image, such that only 15x15 pixel blocks exist
        dst = cv2.morphologyEx(imgray, cv2.MORPH_OPEN, element)

        # ignore any pixels with values greater than 100 (only want the darker pixels)
        _, threshold = cv2.threshold(dst, 100, 255, cv2.THRESH_BINARY_INV)

        _, contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        return contours

    # get the center of contour
    @staticmethod
    def getContourCenter(contour):
        M = cv2.moments(contour)

        if M["m00"] == 0:
            return 0

        x = int(M["m10"] / M["m00"])
        y = int(M["m01"] / M["m00"])
        return (x, y)

    # return contours greater than requiredPercentageSize% of the image area
    @staticmethod
    def thresholdContourSize(img, height, width, requiredPercentageSize=20):
        totalImageArea = height * width;
        contour = []
        for i in range(len(img)):
            cnt = img[i]
            area = cv2.contourArea(cnt)

            # if contour takes up 20% or more of the total area
            if (area >= totalImageArea/requiredPercentageSize):
                contour.append(cnt)

        return contour

    # it will concatenate the image in array
    @staticmethod
    def repackSlices(slices):
        image = slices[0]
        for i in range(len(slices)):
            if i != 0:
                image = np.concatenate((image, slices[i]), axis=0)
        return image

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

        # ignore the 20% of each side of the image
        widthOffset = int(self.width*0.2)

        for i in range(numberOfSlices):
            heightOffset = sliceHeight*i
            crop_img = image[heightOffset:heightOffset + sliceHeight, widthOffset:self.width-widthOffset]

            self.slicesByColor[color].append(crop_img)

            height, width = crop_img.shape[:2]
            middleh = int(height/2)
            middlew = int(width/2)

            contours = self.getContours(crop_img)
            contours = self.thresholdContourSize(contours, height, width)

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

    def isColorInFrame(self, image):
        height, width = image.shape[:2]

        # get contours of image
        contours = self.getContours(image)

        # get contours larger than 10% of image area
        contours = self.thresholdContourSize(contours, height, width, 10)
        return len(contours) > 0

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
                    self.previousSpeeds = (20 - speed, 20 + speed)
                    return (20 - speed, 20 + speed)
                else:
                    self.previousSpeeds = (20 + abs(speed), 20 - abs(speed))
                    return (20 + abs(speed), 20 - abs(speed))
            else:
                return (50, 50)

        # no main line is detected -> reverse
        else:
            return (-50, -50)


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
    debug_text = "COMPUTING ROUTE.\n" \
                 "Position: {} ({})\tDestination: {} ({})\n" \
                 "First Junction: {}\tSecond Junction: {}\n" \
                 "MOVING.".format(position, firstTurnColor, destination, secondTurnColor, firstTurnDirection, secondTurnDirection)
    print(debug_text)
    log.write("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] ")
    log.write(debug_text + "\n")
    log.close()

    return ((firstTurnColor, firstTurnDirection), (secondTurnColor, secondTurnDirection))


def main():
    global server, ESCAPE_KEY, camera, line, mainLineColor, resolution, ir_sensors, IR_THRESHOLD

    position = 1

    server = Server(5005)

    resolution = (320, 240)

    camera = picamera.PiCamera(resolution=resolution, framerate=60)

    # flip the image vertically and horizontally (because the camera is upside down)
    camera.vflip = True
    camera.hflip = True

    # required for the camera to 'warm up'
    time.sleep(0.1)

    line = line_detect()

    # set up ir sensors and threshold
    ir_sensors = IR_Bus()
    IR_THRESHOLD = 100

    mainLineColor = 'black'

    ESCAPE_KEY = 27

    while True:
        destination = getDestinationFromFile()
        if destination is not None:
            if destination == position:
                print("Destination is the same as current position. Skipping.")

            elif destination == 100:
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
                        # wait 5 secs when it reaches destination
                        time.sleep(5)
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
    print("MANUAL OVERRIDE ENABLED.")
    # run ps4 controller loop
    # clear out webapp queue, reset location on both web-app and logic
    # will have to write to file so that web-app is aware of it
    print("MANUAL OVERRIDE DISABLED.")


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
    # Capture images, opencv uses bgr format, using video port is faster but takes lower quality images
    for _ in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):

        rawCapture.truncate(0)  # clear the rawCapture array

        frame = rawCapture.array

        # reset the arrays of slices
        line.slicesByColor[mainLineColor] = []
        line.slicesByColor[junctionColor] = []

        # isolating colors and getting distance between centre of vision and centre of line
        frameWithoutBackground = line.RemoveBackground_HSV(frame, mainLineColor)
        mainLineDistanceBiases = line.computeDistanceBiases(frameWithoutBackground, line.numSlices, mainLineColor)

        HSV_turnColor = line.RemoveBackground_HSV(frame, junctionColor)
        isTurnColorInFrame = line.isColorInFrame(HSV_turnColor)

        if isTurnColorInFrame:
            print("Turning " + turnDirection)
            turn(turnDirection)
            time.sleep(3)
            return
        else:
            (new_left_motor_speed, new_right_motor_speed) = line.computeWheelSpeeds(mainLineDistanceBiases)

            print('DEBUG: left motor speed: {}'.format(new_left_motor_speed))
            print('DEBUG: right motor speed: {}'.format(new_right_motor_speed))

            server.sendMotorCommand(new_left_motor_speed, new_right_motor_speed)

#            printLinesToScreen(mainLineColor, junctionColor)

            # required when printing lines to the screen
#            pressedKey = cv2.waitKey(1) & 0xff
#            if pressedKey == ESCAPE_KEY:
#                raise KeyboardInterrupt('Exit key was pressed')
        print(time.time() - startTime)
        startTime = time.time()


def followTillEnd():

    rawCapture = picamera.array.PiRGBArray(camera, size=resolution)
    startTime = time.time()

    # Capture images, opencv uses bgr format, using video port is faster but takes lower quality images
    for _ in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
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

            server.sendMotorCommand(new_left_motor_speed, new_right_motor_speed)

        print(time.time() - startTime)
        startTime = time.time()

#        printLinesToScreen(mainLineColor)

        # required when printing lines to the screen
#        pressedKey = cv2.waitKey(1) & 0xff
#        if pressedKey == ESCAPE_KEY:
#            raise KeyboardInterrupt('Exit key was pressed')


def printLinesToScreen(*listOfColors):
    for color in listOfColors:
        slices = line.slicesByColor[color]

        # join slices back together
        image = line.repackSlices(slices)

        # output image to screen
        cv2.imshow(color, image)

def isIRSensorValueClose():
    values = ir_sensors.read()
    if values is None:
        return False

    for v in values:
        if int(v) < IR_THRESHOLD:
            return True

    return False

if __name__ == '__main__':
    main()
