import cv2 as cv


def draw_box(im):
    width = im.shape[1]
    height = im.shape[0]
    scale = height / 1080
    x1 = int(width * 0.5 + 168*scale)
    y1 = int(height - 27*scale)
    x2 = int(width * 0.5 + 230*scale)
    y2 = int(height - 5*scale)
    # Draw a box around a given location
    cv.rectangle(im, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # Display image
    cv.imshow("Image", im)
    cv.waitKey(0)


# Read images
im = cv.imread("../../../logs/Screenshot 2023-04-17 062731.png")
draw_box(im)
im = cv.imread("../../../logs/Screenshot 2023-04-17 061750.png")
draw_box(im)
im = cv.imread("../../../logs/1681726367508.png")
draw_box(im)
