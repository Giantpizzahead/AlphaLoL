"""
https://www.pyimagesearch.com/2021/05/12/opencv-edge-detection-cv2-canny/
"""

import numpy as np
import cv2
from matplotlib import pyplot as plt

# load the image, convert it to grayscale, and blur it slightly
image = cv2.imread('vision/img/minion_match/test2.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = gray # cv2.GaussianBlur(gray, (5, 5), 0)

lower_blue = np.array([60, 35, 140])
upper_blue = np.array([180, 255, 255])

# show the original and blurred images
cv2.imshow("Original", image)
cv2.imshow("Blurred", blurred)

# compute a "wide", "mid-range", and "tight" threshold for the edges
# using the Canny edge detector
wide = cv2.Canny(blurred, 10, 200)
mid = cv2.Canny(blurred, 30, 150)
tight = cv2.Canny(blurred, 240, 250)

high_thresh, thresh_im = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
lowThresh = 0.5*high_thresh
best = cv2.Canny(blurred, lowThresh, high_thresh)

# show the output Canny edge maps
cv2.imshow("Wide Edge Map", wide)
cv2.imshow("Mid Edge Map", mid)
cv2.imshow("Tight Edge Map", tight)
cv2.imshow("Best Edge Map", best)
cv2.waitKey(0)