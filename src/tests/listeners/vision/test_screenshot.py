import cv2 as cv
import listeners.vision.screenshot as screenshot
from matplotlib import pyplot as plt


def test_screenshot(x1: float, y1: float, x2: float, y2: float, scale: float) -> None:
    scr = screenshot.take_screenshot(x1, y1, x2, y2, scale)
    scr = cv.cvtColor(scr, cv.COLOR_BGR2RGB)
    plt.imshow(scr)
    plt.show()


if __name__ == '__main__':
    x1 = int(input("Top left x coordinate: "))
    y1 = int(input("Top left y coordinate: "))
    x2 = int(input("Bottom right x coordinate: "))
    y2 = int(input("Bottom right y coordinate: "))
    scale = float(input("Scale: "))
    print("Displaying screenshot...")
    test_screenshot(x1, y1, x2, y2, scale)
