import cv2
import numpy as np
import pyautogui
import keyboard
import pygetwindow
from PIL import Image
from time import sleep

# function to take a screenshot of a specific region

def set_active():
    global is_active
    if is_active:
        is_active = False
        print("Inactive")
    else:
        is_active = True
        print("Active")

def set_exit():
    global exit
    exit = True

def get_window_name():
    window_name = input("Enter the name of the window (it's probably TelegramDesktop): ")
    return window_name

def screenshot(window):
    path = './screenshots/blum.png'
    # get user input for window name
    left, top, right, bottom = window.left, window.top, window.right, window.bottom
    pyautogui.screenshot(path, region=(left+10, top+10, right - left - 10, bottom - top - 10))

    return (left+10, top+10, right - left - 10, bottom - top - 10)

# function to read image and match template
def read_img(blum, target):
    result = cv2.matchTemplate(blum, target, cv2.TM_CCOEFF_NORMED)
    return result


is_active = False
exit = False



keyboard.add_hotkey("q", set_active)

keyboard.add_hotkey("w", set_exit)

target_img = cv2.imread('./images/target2.png', cv2.IMREAD_COLOR)
target_img_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
w = target_img_gray.shape[1]
h = target_img_gray.shape[0]

threshold = 0.7

#start


window = ''

while True:
    window_name = get_window_name()
    try:
        window = pygetwindow.getWindowsWithTitle(window_name)[0]
        print(f"Window '{window_name}' found")
        break
    except IndexError:
        print(f"Window '{window}' not found")
    

print('\nPress "q" to toggle the script.\nPress "w" to exit.\n')

while True:
    if exit:
        break

    if is_active:
        screenshot_region = screenshot(window)

        # load screenshot
        blum_ss = cv2.imread('./screenshots/blum.png', cv2.IMREAD_COLOR)

        # convert screenshot to grayscale
        blum_ss_gray = cv2.cvtColor(blum_ss, cv2.COLOR_BGR2GRAY)

        # get matching result
        result = read_img(blum_ss_gray, target_img_gray)

        # find locations with high confidence
        yloc, xloc = np.where(result >= threshold)

        # create rectangles around matched areas
        rectangles = []

        rectangles = [[int(x), int(y), int(w), int(h)] for (x, y) in zip(xloc, yloc)]

        rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)

        if len(rectangles) > 0:
            last_rect = rectangles[-1]
            x, y, w, h = last_rect

            center_x = int(x + w / 2) + screenshot_region[0]
            center_y = int(y + h / 2) + screenshot_region[1]

            pyautogui.leftClick(center_x, center_y+10)

        # save the resulting image with rectangles drawn for verification
        for (x, y, w, h) in rectangles:
            cv2.rectangle(blum_ss, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imwrite('./result_image/result_with_rectangles.png', blum_ss)


print('Script stopped.')