"""This implements walking and navigation proces."""
import configparser
import logging
import random
import time

import cv2
import pyautogui
from functions import find_template, make_screen
from orientation import get_reference_position

logger = logging.getLogger(__name__)
config = configparser.ConfigParser()
config.read('../config/setting.ini')

Albion_template = cv2.imread('../templates/Albion.png', cv2.IMREAD_COLOR)
w_albion_line = Albion_template.shape[1]
h_albion_line = Albion_template.shape[0]
ReferencePoint_template = cv2.imread('../templates/RP.png', cv2.IMREAD_COLOR)

albion_screen = make_screen()
x_character, y_character = (512, 375)
x_beginning_albion, y_beginning_albion, x2_albion, y2_albion = find_template(albion_screen, Albion_template)
x_origin, y_origin = x_beginning_albion + x_character, y_beginning_albion + y_character

walking_coefficient = config.getfloat('GEOMETRY', 'walking_coefficient')


def go_to_the_point(x_end_on_map, y_end_on_map):
    """
    Go to the point with coordinates x_end_on_map, y_end_on_map.

    Args:
        x_end_on_map (int): x coordinate of the end position.
        y_end_on_map (int): y coordinate of the end position.
    """
    step_counter = 0
    start_x_rp_relative = 0
    start_y_rp_relative = 0
    while True:
        old_start_x_rp_relative = start_x_rp_relative
        old_start_y_rp_relative = start_y_rp_relative
        step_counter += 1
        standard_step = 100 * (1 + random.random())
        logger.debug('Step {0}'.format(step_counter))

        first_screen = make_screen()
        start_x_rp, start_y_rp, start_x_sec_rp, start_y_sec_rp = get_reference_position(first_screen)
        start_x_rp_relative = start_x_rp - x_beginning_albion
        start_y_rp_relative = start_y_rp - y_beginning_albion

        if old_start_x_rp_relative == start_x_rp_relative and old_start_y_rp_relative == start_y_rp_relative:
            logger.debug('Can not move')
            break

        delta_x_on_map = x_end_on_map - start_x_rp_relative
        delta_y_on_map = y_end_on_map - start_y_rp_relative

        delta_x_on_world = int(walking_coefficient * delta_x_on_map)
        delta_y_on_world = int(walking_coefficient * delta_y_on_map)
        if (delta_x_on_world ** 2 + delta_y_on_world ** 2) ** 0.5 > standard_step:
            step_resize = (delta_x_on_world ** 2 + delta_y_on_world ** 2) ** 0.5 / standard_step
            logger.debug('step_resize = {0}'.format(step_resize))
        else:
            logger.debug('else: step_resize = 1')
            step_resize = 1

        end_point_abs_x = x_origin + delta_x_on_world / step_resize
        end_point_abs_y = y_origin + delta_y_on_world / step_resize

        pyautogui.moveTo(end_point_abs_x, end_point_abs_y, 0.5)
        pyautogui.mouseDown()
        time.sleep(0.1)
        pyautogui.mouseUp()

        second_screen = make_screen()
        end_x_rp, end_y_rp, end_x_sec_rp, end_y_sec_rp = get_reference_position(second_screen)
        end_x_rp_relative = end_x_rp - x_beginning_albion
        end_y_rp_relative = end_y_rp - y_beginning_albion

        if abs(x_end_on_map - end_x_rp_relative) <= 0 and abs(y_end_on_map - end_y_rp_relative) <= 0:
            logger.debug('|Δx| = {0}'.format(abs(x_end_on_map - end_x_rp_relative)))
            logger.debug('|Δy| = {0}'.format(abs(y_end_on_map - end_y_rp_relative)))
            break
