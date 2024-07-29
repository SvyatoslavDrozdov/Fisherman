"""This module links coordinates on the map with coordinates on the minimap."""

import configparser
import logging

import cv2
from functions import find_template, make_screen

logger = logging.getLogger(__name__)
config = configparser.ConfigParser()
config.read('../config/setting.ini')

Albion_template = cv2.imread('/home/svyat/PycharmProjects/AlbionFisherman/templates/Albion.png', cv2.IMREAD_COLOR)

w_albion_line = Albion_template.shape[1]
h_albion_line = Albion_template.shape[0]
ReferencePoint_template = cv2.imread('/home/svyat/PycharmProjects/AlbionFisherman/templates/RP.png', cv2.IMREAD_COLOR)

x_character = config.getfloat('GEOMETRY', 'x_character')
y_character = config.getfloat('GEOMETRY', 'y_character')

screen = make_screen()
x1_albion, y1_albion, x2_albion, y2_albion = find_template(screen, Albion_template)
x_origin, y_origin = x1_albion + x_character, y1_albion + y_character


def get_reference_position(frame):
    """
    Give position of the reference object.

    Args:
        frame (np.ndarray): PrtSc - print screen.

    Returns:
        [x_start,y_start,x_end,y_end] (list): array with coordinates of the reference object.
    """
    return find_template(frame, ReferencePoint_template)


def get_current_position():
    """
    Give current position of the reference object relatively to the Albion.

    Returns:
        [x,y] (list): array with coordinates of the reference object relatively to the Albion.
    """
    img = make_screen()
    x_rp, y_rp, x_sec_rp, y_sec_rp = get_reference_position(img)
    return x_rp - x1_albion, y_rp - y1_albion
