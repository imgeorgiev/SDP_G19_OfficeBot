# this is the first version of line_detect (problem: room light will influence v ision a lot. )

import numpy as np
import cv2


class line_detect():

    def RemoveBackground(self,image):
        low = 0
        up = 150
        # create NumPy arrays from the boundaries
        lower = np.array([low, low, low], dtype = "uint8")
        upper = np.array([up, up, up], dtype = "uint8")
        #----------------COLOR SELECTION-------------- (Remove any area that is whiter than 'upper')
        mask = cv2.inRange(image, lower, upper)
        image = cv2.bitwise_and(image, image, mask = mask)
        image = cv2.bitwise_not(image, image, mask = mask)
        image = (255-image)
        return image

    def image_process(self, img):
        imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) #Convert to Gray Scale
        element = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        dst	= cv2.morphologyEx(imgray, cv2.MORPH_OPEN, element)
        ret, thresh = cv2.threshold(dst,100,255,cv2.THRESH_BINARY_INV) #Get Threshold
        _, contours, _ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #Get contour
        return contours
        # return thresh


    def contour_process(self, img, h, w):
        contour = []
        for i in range(len(img)):
            cnt = img[i]
            area = cv2.contourArea(cnt)
            if(area >= (h/5*w/5)):
                contour.append(cnt)
        return contour






if __name__ == '__main__':
    line = line_detect()
    cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture("line_black.MOV")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    width = 640
    height = 480
    while(1):
        ret, origin = cap.read()
        img = line.RemoveBackground(origin)
        contours = line.image_process(img)
        contours = line.contour_process(contours, height, width)
        img = cv2.drawContours(origin,contours,-1,(0,255,0),3)
        # img = cv2.Canny(contours, 50, 150)
        # cv2.imshow('frame',img)
        cv2.imshow('origin', origin)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
