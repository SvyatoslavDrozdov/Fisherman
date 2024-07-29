"""This module contains a different functions used in other modules."""
import configparser
import logging
import random

import cv2
import numpy as np
import pyautogui

logger = logging.getLogger(__name__)
config = configparser.ConfigParser()
config.read('../config/setting.ini')

critical_radius = config.getfloat('GEOMETRY', 'critical_radius')


def random_point_in_triangle(r1, r2, r3):
    """
    Generate a random point inside the triangle defined by the points (x1, y1), (x2, y2), and (x3, y3).

    Args:
        r1 (list): Coordinates of the first vertex.
        r2 (list): Coordinates of the second vertex.
        r3 (list): Coordinates of the third vertex.

    Returns:
        A tuple (x, y) representing the coordinates of a random point inside the triangle.
    """
    x1 = r1[0]
    y1 = r2[1]

    x2 = r2[0]
    y2 = r2[1]

    x3 = r3[0]
    y3 = r3[1]
    while True:
        u_math = random.random()
        v_math = random.random()

        # Ensure the point is inside the triangle
        if u_math + v_math > 1:
            u_math = 1 - u_math
            v_math = 1 - v_math

        # Compute the random point using barycentric coordinates
        x_cord = (1 - u_math - v_math) * x1 + u_math * x2 + v_math * x3
        y_cord = (1 - u_math - v_math) * y1 + u_math * y2 + v_math * y3
        if ((x1 - x_cord) ** 2 + (y1 - y_cord) ** 2) ** 0.5 >= critical_radius:
            logger.debug('radius: {0}'.format(((x1 - x_cord) ** 2 + (y1 - y_cord) ** 2) ** 0.5))
            return int(x_cord), int(y_cord)


def make_screen():
    """
    Make screen.

    Returns:
        screenshot_bgr (np.ndarray)
    """
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    return cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)


def cut_out(x_cord, y_cord, width, high, image):
    """
    Read coordinates.

    Args:
        x_cord (int): x coordinate
        y_cord (int): y coordinate
        width (int): width of cut picture
        high (int): high of cut picture
        image (np.ndarray): main picture from which we will get cut picture

    Returns:
        [cord_x, cord_y] (list): array with coordinates [x,y]
    """
    return image[y_cord:y_cord + high, x_cord:x_cord + width]


def find_template(image, template):
    """
    Find object using its template.

    Args:
        image (np.ndarray): image on which the search is conducted
        template (np.ndarray): template

    Returns:
        [x_template_1, y_template_1, x_template_2, y_template_2] (list): array with coordinates of the found object.
    """
    w_template = template.shape[1]
    h_template = template.shape[0]

    processed_img = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(processed_img)
    x_beginning_template, y_beginning_template = max_loc[0], max_loc[1]
    x_end_template, y_end_template = max_loc[0] + w_template, max_loc[1] + h_template

    return x_beginning_template, y_beginning_template, x_end_template, y_end_template


def show_img(image, object_coordinates):
    """
    Show image.

    Args:
        image (np.ndarray): image on which the search is conducted
        object_coordinates (list or int): if data = 0 just show image, if data = list show rectangle on image too.
    """
    if object_coordinates:
        x1, y1, x2, y2 = object_coordinates
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.imshow('img', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
