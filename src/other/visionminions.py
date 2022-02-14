import cv2 as cv
import numpy as np

#read the image
img = cv.imread("../tests/listeners/vision/img/minion_match/test3.png")

#convert the BGR image to HSV colour space
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

# Masks for blue/red minion health bars and the edges
lower_blue = np.array([101, 156, 117])
upper_blue = np.array([105, 163, 212])
mask_blue = cv.inRange(hsv, lower_blue, upper_blue)

lower_red = np.array([0, 135, 118])
upper_red = np.array([4, 143, 212])
mask_red = cv.inRange(hsv, lower_red, upper_red)

lower_edge = np.array([0, 0, 10])
upper_edge = np.array([255, 255, 22])
mask_edge = cv.inRange(hsv, lower_edge, upper_edge)

#perform bitwise and on the original image arrays using the mask
mask = cv.bitwise_or(cv.bitwise_or(mask_red, mask_blue), mask_edge)
res = cv.bitwise_and(img, img, mask=mask)

#create resizable windows for displaying the images
cv.namedWindow("orig")
cv.namedWindow("res")
cv.namedWindow("mask")

#display the images
cv.imshow("orig", img)
cv.imshow("mask", mask)
cv.imshow("res", res)

if cv.waitKey(0):
    cv.destroyAllWindows()