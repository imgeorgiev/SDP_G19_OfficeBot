# multi-color lines detect in HSV and distance between middle of robot vision and center of line. 

import numpy as np
import cv2


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
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([0,0,0])
        upper = np.array([180,255,75])

        mask = cv2.inRange(hsv, lower, upper)
        image = cv2.bitwise_and(image,image, mask=mask)
        image = cv2.bitwise_not(image,image, mask=mask)
        image = (255 - image)
        return image


    def RemoveBackground_HSV_Blue(self,image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([100,43,46])
        upper = np.array([124,255,255])

        mask = cv2.inRange(hsv, lower, upper)
        image = cv2.bitwise_and(image,image, mask=mask)
        image = cv2.bitwise_not(image,image, mask=mask)
        image = (255 - image)
        return image


    def RemoveBackground_HSV_Red(self,image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([156,43,46])
        upper = np.array([180,255,255])

        mask = cv2.inRange(hsv, lower, upper)
        image = cv2.bitwise_and(image,image, mask=mask)
        image = cv2.bitwise_not(image,image, mask=mask)
        image = (255 - image)
        return image


    def RemoveBackground_HSV_Green(self,image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([35,43,46])
        upper = np.array([77,255,255])

        mask = cv2.inRange(hsv, lower, upper)
        image = cv2.bitwise_and(image,image, mask=mask)
        image = cv2.bitwise_not(image,image, mask=mask)
        image = (255 - image)
        return image

    def RemoveBackground_HSV_Yellow(self,image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([26,43,46])
        upper = np.array([34,255,255])

        mask = cv2.inRange(hsv, lower, upper)
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


    # def contour_process(self, img, h, w):
    #     contour = []
    #     for i in range(len(img)):
    #         cnt = img[i]
    #         area = cv2.contourArea(cnt)
    #         if(area >= (h/20*w/20)):
    #             contour.append(cnt)
    #     return contour


    def RepackImages(self):
        img = self.image[0]
        for i in range(len(self.image)):
            if i == 0:
                img = np.concatenate((img, self.image[1]), axis=0)
            if i > 1:
                img = np.concatenate((img, self.image[i]), axis=0)

        return img

    #
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


    def SlicePart(self, im, slice):
        sl = int(self.height/slice);

        for i in range(slice):
            part = sl*i
            crop_img = im[part:part+sl, 0:self.width]
            self.image[i] = (crop_img)
            h, w  = self.image[i].shape[:2]
            middleh = int(h/2)
            middlew = int(w/2)
            # img = self.RemoveBackground_RGB(crop_img)
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


if __name__ == '__main__':
    line = line_detect()
    cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture("test.MOV")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,line.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,line.height)
    for i in range(line.slice):
        line.image.append(0)
    while(1):
        ret, origin = cap.read()
        line.SlicePart(origin, line.slice)

        ############################# RGB TEST ##############################
        # img = line.RemoveBackground_RGB(origin)
        ############################# HSV TEST ##############################
        # img = line.RemoveBackground_HSV_Black(origin)
        # img = line.RemoveBackground_HSV_Blue(origin)
        # img = line.RemoveBackground_HSV_Green(origin)
        # img = line.RemoveBackground_HSV_Yellow(origin)
        # img = line.RemoveBackground_HSV_Purple(origin)
        # img = line.RemoveBackground_HSV_Red(origin)

        # img = line.RepackImages()
        cv2.imshow('frame',img)
        # cv2.imshow('slice1', line.image[0])
        # cv2.imshow('slice2', line.image[1])
        # cv2.imshow('slice3', line.image[2])
        # cv2.imshow('slice4', line.image[3])
        # cv2.imshow('origin', origin)
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
