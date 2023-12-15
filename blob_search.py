#!/usr/bin/env python


import cv2
import numpy as np




def isWhite(hsv_image, y, x):
   lower = (50, 10, 100)
   upper = (140, 50, 230)
   output = [False, False, False]
   for i in range(0, 3):
       output[i] = hsv_image[y][x][i] < upper[i] and hsv_image[y][x][i] > lower[i]
   if output == [True, True, True]:
       return 1
   else:
       return 0
def blob_search(image_raw, color):




   # Convert the image into the HSV color space
   hsv_image = cv2.cvtColor(image_raw, cv2.COLOR_BGR2HSV)








   lower = (110, 10, 190)
   upper = (140, 50, 230)
   # Define a mask using the lower and upper bounds of the target color
   mask_image = cv2.inRange(hsv_image, lower, upper)


   # Find blob centers in the image coordinates
   maze = [
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,]]
  
   for i in range(0, len(maze)):
       for j in range(0, len(maze)):
           maze[i][j] = isWhite(hsv_image, 132 + 12*i, 124 + 20*j) + isWhite(hsv_image, 132 + 12*i, 124 + 20*j+2) + isWhite(hsv_image, 132 + 12*i, 124 + 20*j-2) + isWhite(hsv_image, 132 + 12*i-2, 124 + 20*j)  + isWhite(hsv_image, 132 + 12*i-2, 124 + 20*j+2) + isWhite(hsv_image, 132 + 12*i-2, 124 + 20*j-2) + isWhite(hsv_image, 132 + 12*i+2, 124 + 20*j)  + isWhite(hsv_image, 132 + 12*i+2, 124 + 20*j+2) + isWhite(hsv_image, 132 + 12*i+2, 124 + 20*j-2)
           maze[i][j] = int(1 - maze[i][j]/11)
  


   cv2.namedWindow("Camera View")
   cv2.imshow("Camera View", image_raw)
   cv2.namedWindow("Mask View")
   cv2.imshow("Mask View", mask_image)


   cv2.waitKey(2)


   # return xw_yw
   return maze



