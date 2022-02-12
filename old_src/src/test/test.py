import time

import cv2 as cv
import numpy as np
import pynput
from mss import mss
from pynput.mouse import Button

bounding_box = {'top': 0, 'left': 0, 'width': 1600 // 3, 'height': 2560 // 3}
sct = mss()
mouse = pynput.mouse.Controller()


def locate_play_button():
    # Get screenshot in BGR format
    sct_img = sct.grab(bounding_box)
    scr = np.array(sct_img)[:, :, :3]
    # Load button template in BGR format
    template_pb = cv.imread("images/play_button.png", cv.IMREAD_COLOR)

    # Resize both images to make processing faster
    r = 0.3
    scr = cv.resize(scr, (int(scr.shape[1] * r), int(scr.shape[0] * r)), interpolation=cv.INTER_AREA)
    template_pb = cv.resize(template_pb, (int(template_pb.shape[1] * r), int(template_pb.shape[0] * r)),
                            interpolation=cv.INTER_AREA)
    _, template_w, template_h = template_pb.shape[::-1]

    # Locate button template in original image
    res = cv.matchTemplate(scr, template_pb, cv.TM_CCOEFF_NORMED)
    threshold = 0.7
    loc = np.where(res >= threshold)

    # Display found button locations
    scr = scr.copy()
    points = list(zip(*loc[::-1]))
    for pt in points:
        cv.rectangle(scr, pt, (pt[0] + template_w, pt[1] + template_h), (0, 0, 255), 2)
    print(f"Found at {len(points)} locations: {points}")
    cv.imshow('screen', np.array(scr))

    # Move mouse to the play button and click it!
    if points:
        pt = points[0]
        x = (pt[0] + template_w / 2.0) / r / 2
        y = (pt[1] + template_h / 2.0) / r / 2
        mouse.position = (x, y)
        mouse.press(Button.left)
        time.sleep(0.02)
        mouse.release(Button.left)


last_time = time.time()
while True:
    locate_play_button()
    print(f"FPS: {1 / (time.time() - last_time)}")
    last_time = time.time()
    time.sleep(1)
    # Quit if Cmd-Q is pressed
    if (cv.waitKey(1) & 0xFF) == ord('q'):
        cv.destroyAllWindows()
        break
