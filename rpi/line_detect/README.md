# User Guide for using line_detect.py

All functions have already writen in the main, they are seperated into 6 parts.

## First part <DISTANCE>

Variable distance_<color> is a list of distance for points in specific color. The function SlicePart_<color> will return
these values, also drawing circles on original video. If you want to use line_following, this function must be used.

## Second part <HSV TEST>

Variable HSV is an image which only contains a specific color, depends on the function RemoveBackgroud_HSV_<color>. And
you can use the function in the last part imshow to get the image.

## Third part <CONCATENATE>

This part will concatenate the image. If you use the function in first part, then the function in this part is necessary for 
getting a completed output image.

## Fourth part <MOTOR SPEED>

This part will get values of motor speed(for left and right motor), through the variable in first part.

## Fifth part <COMMAND SENDING>

This part will send motor data to ev3

## Sixth part <IMAGE SHOWING>

First line will show the image with distance(relate to first and third part)
Second line will show the original video 
Third line will show the image only contains specific color(relate to second part)

