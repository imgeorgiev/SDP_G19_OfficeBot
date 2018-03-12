# multi-color lines detect in HSV and distance between middle of robot vision and center of line.

import numpy as np
import cv2
from tcp_rpi import *
import time, sched


class line_detect():

    def __init__(self):
        # self.width = 640
        # self.height = 480
        self.width = 320
        self.height = 240
        self.image_black = []
        self.image_blue = []
        self.image_red = []
        self.slice = 4
        self.weight_4 = [0.23, 0.23, 0.23, 0.23]
        self.weight_3 = [0.3, 0.3, 0.3]
        self.weight_2 = [0.45, 0.45]
        self.weight_1 = [0.9]
        self.threshold = 70
        self.FPS_limit = 10



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


    def RemoveBackground_HSV_Black(self,image):
        # modify 'V' of upper to change the captured range
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([0,0,0])
        upper = np.array([180,255,75])
        # upper = np.array([180,255,110])

        mask = cv2.inRange(hsv, lower, upper)
        kernel = np.ones((5,5),np.uint8)
        mask = cv2.dilate(mask,kernel,iterations=5)
        mask = cv2.erode(mask,kernel,iterations=4)
        image = cv2.bitwise_and(image,image, mask=mask)
        image = cv2.bitwise_not(image,image, mask=mask)
        image = (255 - image)
        return image


    def RemoveBackground_HSV_Blue(self,image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([100,170,46])
        upper = np.array([124,255,255])

        mask = cv2.inRange(hsv, lower, upper)
        kernel = np.ones((5,5),np.uint8)
        mask = cv2.dilate(mask,kernel,iterations=5)
        mask = cv2.erode(mask,kernel,iterations=4)
        image = cv2.bitwise_and(image,image, mask=mask)
        image = cv2.bitwise_not(image,image, mask=mask)
        image = (255 - image)
        return image


    def RemoveBackground_HSV_Red(self,image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        channel1Min = 156;
        channel1Max = 180;
        channel2Min = 43;
        channel2Max = 255;
        channel3Min = 46;
        channel3Max = 255;
        lower = np.array([channel1Min,channel2Min,channel3Min])
        # lower = self.transfer(lower)
        upper = np.array([channel1Max,channel2Max,channel3Max])
        # upper = self.transfer(upper)

        mask = cv2.inRange(hsv, lower, upper)
        kernel = np.ones((5,5),np.uint8)
        mask = cv2.dilate(mask,kernel,iterations=5)
        mask = cv2.erode(mask,kernel,iterations=4)
        image = cv2.bitwise_and(image,image, mask=mask)
        image = cv2.bitwise_not(image,image, mask=mask)
        image = (255 - image)
        return image


    def RemoveBackground_HSV_Green(self,image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        channel1Min = 35;
        channel1Max = 85;
        channel2Min = 100;
        channel2Max = 255;
        channel3Min = 46;
        channel3Max = 255;
        lower = np.array([channel1Min,channel2Min,channel3Min])
        upper = np.array([channel1Max,channel2Max,channel3Max])

        mask = cv2.inRange(hsv, lower, upper)
        kernel = np.ones((5,5),np.uint8)
        mask = cv2.dilate(mask,kernel,iterations=5)
        mask = cv2.erode(mask,kernel,iterations=4)
        image = cv2.bitwise_and(image,image, mask=mask)
        image = cv2.bitwise_not(image,image, mask=mask)
        image = (255 - image)
        return image

    def RemoveBackground_HSV_Yellow(self,image):
        # modify the ‘H’ of upper to change the captured range
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        channel1Min = 0.062
        channel1Max = 0.225
        channel2Min = 0.155
        channel2Max = 1.000
        channel3Min = 0.000
        channel3Max = 1.000
        lower = np.array([channel1Min,channel2Min,channel3Min])
        lower = self.transfer(lower)
        upper = np.array([channel1Max,channel2Max,channel3Max])
        upper = self.transfer(upper)

        mask = cv2.inRange(hsv, lower, upper)
        kernel = np.ones((5,5),np.uint8)
        mask = cv2.dilate(mask,kernel,iterations=5)
        mask = cv2.erode(mask,kernel,iterations=4)
        image = cv2.bitwise_and(image,image, mask=mask)
        image = cv2.bitwise_not(image,image, mask=mask)
        image = (255 - image)
        return image


    def RemoveBackground_HSV_Purple(self,image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([125,43,46])
        upper = np.array([155,255,255])

        mask = cv2.inRange(hsv, lower, upper)
        image = cv2.bitwise_and(image,image, mask=mask)
        image = cv2.bitwise_not(image,image, mask=mask)
        image = (255 - image)
        return image


    def transfer(self, array):
        array[0] = array[0]*360
        array[1] = array[1]*255
        array[2] = array[2]*255
        return array


    def image_process(self, img):
        imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) #Convert to Gray Scale
        element = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        dst	= cv2.morphologyEx(imgray, cv2.MORPH_OPEN, element)
        ret, thresh = cv2.threshold(dst,100,255,cv2.THRESH_BINARY_INV) #Get Threshold
        _, contours, _ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #Get contour
        # mainContour = max(contours, key=cv2.contourArea)
        # return mainContour
        return contours
        # return thresh


    def getContourCenter(self, contour):
        M = cv2.moments(contour)

        if M["m00"] == 0:
            return 0
        x = int(M["m10"]/M["m00"])
        y = int(M["m01"]/M["m00"])
        return [x,y]


    def contour_process(self, img, h, w):
        contour = []
        for i in range(len(img)):
            cnt = img[i]
            area = cv2.contourArea(cnt)
            if(area >= (h/20*w/20)):
                contour.append(cnt)
        return contour


    def RepackImages(self, image):
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



    def getContourExtent(self, contour):
        area = cv2.contourArea(contour)
        x,y,w,h = cv2.boundingRect(contour)
        rect_area = w*h*3
        if rect_area > 0:
            return (float(area)/rect_area)


    def SlicePart(self, im, slice, color):
        sl = int(self.height/slice);
        distance = []

        for i in range(slice):
            part = sl*i
            crop_img = im[part:part+sl, 0:self.width]
            # middlew = middlew - 40
            # print(middlew)
            if color == 'BLACK':
                self.image_black.append(crop_img)
                h, w  = self.image_black[i].shape[:2]
                middleh = int(h/2)
                middlew = int(w/2)-70
                img = self.RemoveBackground_HSV_Black(crop_img)
            # elif color == 'RED':
            #     self.image_black.append(crop_img)
            #     h, w  = self.image_red[i].shape[:2]
            #     middleh = int(h/2)
            #     middlew = int(w/2)-70
            #     img = self.RemoveBackground_HSV_Red(crop_img)
            # elif color == 'BLUE':
            #     self.image_black.append(crop_img)
            #     h, w  = self.image_blue[i].shape[:2]
            #     middleh = int(h/2)
            #     middlew = int(w/2)-70
            #     img = self.RemoveBackground_HSV_Blue(crop_img)
            # elif color == 'GREEN':
            #     self.image_black.append(crop_img)
            #     h, w  = self.image_green[i].shape[:2]
            #     middleh = int(h/2)
            #     middlew = int(w/2)-70
            #     img = self.RemoveBackground_HSV_Green(crop_img)
            # elif color == 'YELLOW':
            #     self.image_black.append(crop_img)
            #     h, w  = self.image_yellow[i].shape[:2]
            #     middleh = int(h/2)
            #     middlew = int(w/2)-70
            #     img = self.RemoveBackground_HSV_Yellow(crop_img)
            # elif color == 'PURPLE':
            #     self.image_black.append(crop_img)
            #     h, w  = self.image_purple[i].shape[:2]
            #     middleh = int(h/2)
            #     middlew = int(w/2)-70
            #     img = self.RemoveBackground_HSV_Purple(crop_img)
            contours = self.image_process(img)
            contours = self.contour_process(contours, h, w)
            # print(contours)
            # cv2.drawContours(crop_img, contours,-1,(0,255,0),3)
            # dis = int((middlew-contourCenterX) * self.getContourExtent(contours[0]))
            # cv2.circle(crop_img, (middlew, middleh), 7, (0,0,255), -1) #Draw middle circle RED
            if contours:
                contourCenterX = self.getContourCenter(contours[0])[0]
                # cv2.circle(crop_img, (contourCenterX, middleh), 7, (255,255,255), -1) #Draw dX circle WHITE
                # font = cv2.FONT_HERSHEY_SIMPLEX
                # cv2.putText(crop_img,str(middlew-contourCenterX),(contourCenterX+20, middleh), font, 1,(200,0,200),2,cv2.LINE_AA)
                # cv2.putText(crop_img,"Weight:%.3f"%self.getContourExtent(contours[0]),(contourCenterX+20, middleh+35), font, 0.5,(200,0,200),1,cv2.LINE_AA)
                # bias = int(middlew-contourCenterX) * self.getContourExtent(contours[0])
                bias = int(middlew-contourCenterX)
            # record the bias distance
                distance.append(bias)
        return distance[::-1]


    def line_following(self, distance):
        # threshold of corner
        # send command to ev3
        if distance:
            num = len(distance)
            if num == 1:
                bias = [i*j for i,j in zip(distance, self.weight_1)]
                bias = sum(bias)
            elif num == 2:
                bias = [i*j for i,j in zip(distance, self.weight_2)]
                bias = sum(bias)
            elif num == 3:
                bias = [i*j for i,j in zip(distance, self.weight_3)]
                bias = sum(bias)
            elif num == 4:
                bias = [i*j for i,j in zip(distance, self.weight_4)]
                bias = sum(bias)
            # bias = sum(distance)
            print('the distance list is {}'.format(distance))
            print('the bias is {}'.format(bias))
            speed = attenuate(bias/4, -40, 40)
            if abs(bias) > self.threshold:
                if bias > 0:
                    return [20, 20+speed]
                else:
                    return [20+abs(speed), 20]
            else:
                return [50, 50]

    def turn_R_angle(self, dir):
        if dir == 'right':
            # for time in range(1,3):

        elif dir == 'left':

        elif dir == 'none':



if __name__ == '__main__':
    line = line_detect()
    cap = cv2.VideoCapture(0)
    # schedule = sched.scheduler(time.time, time.sleep)
    s = Server(5005)
    # cap = cv2.VideoCapture("test.MOV")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,line.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,line.height)
    cap.set(CV_CAP_PROP_FPS,line.FPS_limit);
    prev_l = 0
    prev_r = 0
    # turn = False
    # while(1):
    #     s.sendMotorCommand(0,50)
    #     pring('DEBUG: Test for sending (0,50) to ev3')
    while(1):
        ret, origin = cap.read()
        time.sleep(0.1)
        if(ret):
            # the main function
            line.image_red = []
            line.image_blue = []
            line.image_black = []
            # for i in range(line.slice):
            #     line.image_red.append(0)
            #     line.image_blue.append(0)
            #     line.image_black.append(0)

            ############################# HSV TEST ##############################
            HSV_black = line.RemoveBackground_HSV_Black(origin)
            # HSV_blue = line.RemoveBackground_HSV_Blue(origin)
            # HSV = line.RemoveBackground_HSV_Green(origin)
            # HSV = line.RemoveBackground_HSV_Yellow(origin)
            # HSV = line.RemoveBackground_HSV_Purple(origin)
            # HSV_red = line.RemoveBackground_HSV_Red(origin)

            ############################# get distance between middle of vision and line #########################
            distance_Black = line.SlicePart(HSV_black, line.slice, 'BLACK')
            # distance_Blue = line.SlicePart(HSV_blue, line.slice, 'BLUE')
            # distance_Green = line.SlicePart(origin, line.slice, 'GREEN')
            # distance_Red = line.SlicePart(HSV_red, line.slice, 'RED')
            # distance_Yellow = line.SlicePart(origin, line.slice, 'YELLOW')

            ############################# concatenate every slice ###############
            # img_black = line.RepackImages(line.image_black)
            # img_blue = line.RepackImages(line.image_blue)
            # img_red = line.RepackImages(line.image_red)

            ############################# get motor speed #######################
            # assume we get a command from webapp, next line is blue line
            # if distance_Black:
            #     if not distance_Blue:
            #         [left_motor, right_motor] = line.line_following(distance_Black)
            #     else:
            #         [left_motor, right_motor] = line.line_following(distance_Blue)
            # if not distance_Black:
            #     if not distance_Red and not distance_Blue:
            #         [left_motor, right_motor] = [-200, 200]
            #     elif distance_Blue:
            #         [left_motor, right_motor] = line.line_following(distance_Blue)
            #     elif distance_Red:
            #         [left_motor, right_motor] = line.line_following(distance_Red)
            # if distance_Black:
            #     [left_motor, right_motor] = line.line_following(distance_Black)

            ############################# assumption code #################
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

            # need color signal to specify turn left or right
            if distance_Black:
                [left_motor, right_motor] = line.line_following(distance_Black)
                prev_l = left_motor
                prev_r = right_motor
            # if distance_Blue:
            #     [left_motor, right_motor] = line.line_following(distance_Blue)
            #     prev_l = left_motor
            #     prev_r = right_motor
            # elif not distance_Blue:
            #     [left_motor, right_motor] = line.line_following(distance_Black)
            #     prev_l = left_motor
            #     prev_r = right_motor
            else:
                [left_motor, right_motor] = [-prev_l, -prev_r]
            print("left motor speed is {}".format(left_motor))
            print("right motor speed is {}".format(right_motor))

            ############################# send command to ev3 ###################
            # schedule.enter(1, 1, s.sendMotorCommand, argument=(int(left_motor), int(right_motor)))
            # schedule.run()
            s.sendMotorCommand(int(left_motor), int(right_motor))

            ############################# output image TEST #####################
            # cv2.imshow('img_black',img_black)
            # cv2.imshow('img_blue', img_blue)
            # cv2.imshow('img_red',img_red)
            # cv2.imshow('origin', origin)
            # cv2.imshow('HSV', HSV)


            # k = cv2.waitKey(1) & 0xff
            # if k == 27:
            #     break
            # time.sleep(0.05)
        else:
            print('DEBUG: No frames input')
    cap.release()
    cv2.destroyAllWindows()
