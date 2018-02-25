# multi-color lines detect in HSV and distance between middle of robot vision and center of line.

import numpy as np
import cv2
from tcp_rpi import *


class line_detect():

    def __init__(self):
        self.width = 640
        self.height = 480
        # self.width = 1920
        # self.height = 1080
        self.image = []
        self.slice = 4



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
        lower = np.array([100,100,46])
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
        channel1Min = -0.051;
        channel1Max = 0.038;
        channel2Min = 0.432;
        channel2Max = 1.000;
        channel3Min = 0.352;
        channel3Max = 1.000;
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


    def RepackImages(self):
        img = self.image[0]
        for i in range(len(self.image)):
            if i == 0:
                img = np.concatenate((img, self.image[1]), axis=0)
            if i > 1:
                img = np.concatenate((img, self.image[i]), axis=0)

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
        rect_area = w*h
        if rect_area > 0:
            return (float(area)/rect_area)


    def SlicePart_Black(self, im, slice):
        sl = int(self.height/slice);
        distance = []

        for i in range(slice):
            part = sl*i
            crop_img = im[part:part+sl, 0:self.width]
            self.image[i] = (crop_img)
            h, w  = self.image[i].shape[:2]
            middleh = int(h/2)
            middlew = int(w/2)
            img = self.RemoveBackground_HSV_Black(crop_img)
            contours = self.image_process(img)
            contours = self.contour_process(contours, h, w)
            # print(contours)
            cv2.drawContours(crop_img, contours,-1,(0,255,0),3)
            # dis = int((middlew-contourCenterX) * self.getContourExtent(contours[0]))
            cv2.circle(crop_img, (middlew, middleh), 7, (0,0,255), -1) #Draw middle circle RED
            if contours:
                contourCenterX = self.getContourCenter(contours[0])[0]
                cv2.circle(crop_img, (contourCenterX, middleh), 7, (255,255,255), -1) #Draw dX circle WHITE
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(crop_img,str(middlew-contourCenterX),(contourCenterX+20, middleh), font, 1,(200,0,200),2,cv2.LINE_AA)
                # cv2.putText(crop_img,"Weight:%.3f"%self.getContourExtent(contours[0]),(contourCenterX+20, middleh+35), font, 0.5,(200,0,200),1,cv2.LINE_AA)
            # record the bias distance
            distance.append(middlew-contourCenterX)
        return distance[::-1]


    def SlicePart_Blue(self, im, slice):
        sl = int(self.height/slice);
        distance = []

        for i in range(slice):
            part = sl*i
            crop_img = im[part:part+sl, 0:self.width]
            self.image[i] = (crop_img)
            h, w  = self.image[i].shape[:2]
            middleh = int(h/2)
            middlew = int(w/2)
            img = self.RemoveBackground_HSV_Blue(crop_img)
            contours = self.image_process(img)
            contours = self.contour_process(contours, h, w)
            # print(contours)
            cv2.drawContours(crop_img, contours,-1,(0,255,0),3)
            # dis = int((middlew-contourCenterX) * self.getContourExtent(contours[0]))
            cv2.circle(crop_img, (middlew, middleh), 7, (0,0,255), -1) #Draw middle circle RED
            if contours:
                contourCenterX = self.getContourCenter(contours[0])[0]
                cv2.circle(crop_img, (contourCenterX, middleh), 7, (255,255,255), -1) #Draw dX circle WHITE
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(crop_img,str(middlew-contourCenterX),(contourCenterX+20, middleh), font, 1,(200,0,200),2,cv2.LINE_AA)
                # cv2.putText(crop_img,"Weight:%.3f"%self.getContourExtent(contours[0]),(contourCenterX+20, middleh+35), font, 0.5,(200,0,200),1,cv2.LINE_AA)
            # record the bias distance
            distance.append(middlew-contourCenterX)
        return distance[::-1]


    def SlicePart_Yellow(self, im, slice):
        sl = int(self.height/slice);
        distance = []

        for i in range(slice):
            part = sl*i
            crop_img = im[part:part+sl, 0:self.width]
            self.image[i] = (crop_img)
            h, w  = self.image[i].shape[:2]
            middleh = int(h/2)
            middlew = int(w/2)
            img = self.RemoveBackground_HSV_Yellow(crop_img)
            contours = self.image_process(img)
            contours = self.contour_process(contours, h, w)
            # print(contours)
            cv2.drawContours(crop_img, contours,-1,(0,255,0),3)
            # dis = int((middlew-contourCenterX) * self.getContourExtent(contours[0]))
            cv2.circle(crop_img, (middlew, middleh), 7, (0,0,255), -1) #Draw middle circle RED
            if contours:
                contourCenterX = self.getContourCenter(contours[0])[0]
                cv2.circle(crop_img, (contourCenterX, middleh), 7, (255,255,255), -1) #Draw dX circle WHITE
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(crop_img,str(middlew-contourCenterX),(contourCenterX+20, middleh), font, 1,(200,0,200),2,cv2.LINE_AA)
                # cv2.putText(crop_img,"Weight:%.3f"%self.getContourExtent(contours[0]),(contourCenterX+20, middleh+35), font, 0.5,(200,0,200),1,cv2.LINE_AA)
            # record the bias distance
            distance.append(middlew-contourCenterX)
        return distance[::-1]


    def SlicePart_Red(self, im, slice):
        sl = int(self.height/slice);
        distance = []

        for i in range(slice):
            part = sl*i
            crop_img = im[part:part+sl, 0:self.width]
            self.image[i] = (crop_img)
            h, w  = self.image[i].shape[:2]
            middleh = int(h/2)
            middlew = int(w/2)
            img = self.RemoveBackground_HSV_Red(crop_img)
            contours = self.image_process(img)
            contours = self.contour_process(contours, h, w)
            # print(contours)
            cv2.drawContours(crop_img, contours,-1,(0,255,0),3)
            # dis = int((middlew-contourCenterX) * self.getContourExtent(contours[0]))
            cv2.circle(crop_img, (middlew, middleh), 7, (0,0,255), -1) #Draw middle circle RED
            if contours:
                contourCenterX = self.getContourCenter(contours[0])[0]
                cv2.circle(crop_img, (contourCenterX, middleh), 7, (255,255,255), -1) #Draw dX circle WHITE
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(crop_img,str(middlew-contourCenterX),(contourCenterX+20, middleh), font, 1,(200,0,200),2,cv2.LINE_AA)
                # cv2.putText(crop_img,"Weight:%.3f"%self.getContourExtent(contours[0]),(contourCenterX+20, middleh+35), font, 0.5,(200,0,200),1,cv2.LINE_AA)
            # record the bias distance
            distance.append(middlew-contourCenterX)
        return distance[::-1]


    def SlicePart_Green(self, im, slice):
        sl = int(self.height/slice);
        distance = []

        for i in range(slice):
            part = sl*i
            crop_img = im[part:part+sl, 0:self.width]
            self.image[i] = (crop_img)
            h, w  = self.image[i].shape[:2]
            middleh = int(h/2)
            middlew = int(w/2)
            img = self.RemoveBackground_HSV_Green(crop_img)
            contours = self.image_process(img)
            contours = self.contour_process(contours, h, w)
            # print(contours)
            cv2.drawContours(crop_img, contours,-1,(0,255,0),3)
            # dis = int((middlew-contourCenterX) * self.getContourExtent(contours[0]))
            cv2.circle(crop_img, (middlew, middleh), 7, (0,0,255), -1) #Draw middle circle RED
            if contours:
                contourCenterX = self.getContourCenter(contours[0])[0]
                cv2.circle(crop_img, (contourCenterX, middleh), 7, (255,255,255), -1) #Draw dX circle WHITE
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(crop_img,str(middlew-contourCenterX),(contourCenterX+20, middleh), font, 1,(200,0,200),2,cv2.LINE_AA)
                # cv2.putText(crop_img,"Weight:%.3f"%self.getContourExtent(contours[0]),(contourCenterX+20, middleh+35), font, 0.5,(200,0,200),1,cv2.LINE_AA)
            # record the bias distance
            distance.append(middlew-contourCenterX)
        return distance[::-1]


    def line_following(self, distance):
        # threshold of corner
        # send command to ev3
        if abs(distance[-1]) > 0 and abs(distance[-2]) > 10:
            if distance[-1] > 0:
                return [0,-100]
            elif distance[-1] < 0:
                return [-100,0]
        else:
            return [-100,-100]


if __name__ == '__main__':
    line = line_detect()
    cap = cv2.VideoCapture(0)
    s = Server(5005)
    # cap = cv2.VideoCapture("test.MOV")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,line.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,line.height)
    for i in range(line.slice):
        line.image.append(0)
    while(1):
        ret, origin = cap.read()
        # the main function

        ############################# get distance between middle of vision and line #########################
        distance_Black = line.SlicePart_Black(origin, line.slice)
        distance_Blue = line.SlicePart_Blue(origin, line.slice)
        distance_Green = line.SlicePart_Green(origin, line.slice)
        distance_Red = line.SlicePart_Red(origin, line.slice)
        distance_Yellow = line.SlicePart_Yellow(origin, line.slice)

        ############################# RGB TEST ##############################
        # RGB = line.RemoveBackground_RGB(origin)

        ############################# HSV TEST ##############################
        # HSV = line.RemoveBackground_HSV_Black(origin)
        # HSV = line.RemoveBackground_HSV_Blue(origin)
        # HSV = line.RemoveBackground_HSV_Green(origin)
        # HSV = line.RemoveBackground_HSV_Yellow(origin)
        # HSV = line.RemoveBackground_HSV_Purple(origin)
        # HSV = line.RemoveBackground_HSV_Red(origin)

        ############################# concatenate every slice ###############
        img = line.RepackImages()

        ############################# get motor speed #######################
        [left_motor, right_motor] = line.line_following(distance_Black)

        ############################# send command to ev3 ###################
        s.sendCommand("L", left_motor)
        s.sendCommand("R", right_motor)

        ############################# output image TEST #####################
        cv2.imshow('img',img)
        # cv2.imshow('origin', origin)
        # cv2.imshow('HSV', HSV)

        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
