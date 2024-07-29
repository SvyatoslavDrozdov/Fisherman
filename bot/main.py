"""
This is the entry point of program.

This module implements walking and fishing rod control at the same time.
"""
import configparser
import logging
import random
import time

import cv2
import numpy as np
import pyautogui
from catching import catch_fish
from functions import find_template, random_point_in_triangle
from orientation import x_origin, y_origin
from walking import go_to_the_point

logger = logging.getLogger(__name__)
config = configparser.ConfigParser()
config.read('../config/setting.ini')


def setup_logging():
    """Set up logging for the application."""
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('../logs/my_app.log')
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


bot_working_time = config.getfloat('TIME', 'bot_working_time')


def main():
    """Implement logging."""
    setup_logging()
    logger.debug('Started')
    bot_started_time = time.time()

    worm_timer = time.time()
    pie_timer = time.time()
    time.sleep(time_before_worm)
    pyautogui.press(worm_button)
    time.sleep(time_before_pie)
    pyautogui.press(pie_button)

    while True:
        worm_timer, pie_timer = bot_control(worm_timer, pie_timer)
        if time.time() - bot_started_time >= bot_working_time:
            break
    logger.debug('Finished')


mouse_motion_time = config.getfloat('TIME', 'mouse_motion_time')
min_distance_time = config.getfloat('TIME', 'min_distance_time')
max_distance_time = config.getfloat('TIME', 'max_distance_time')
time_before_fish = config.getfloat('TIME', 'time_before_fish')
create_bait_time = config.getfloat('TIME', 'create_bait_time')


def start_fishing(x_coordinates, y_coordinates, random_fishing_number):
    """
    Start the fishing process.

    This function implements the fishing process at given coordinates.

    Args:
        x_coordinates (list of int): List of x-coordinates for fishing spots.
        y_coordinates (list of int): List of y-coordinates for fishing spots.
        random_fishing_number (int): Number of times to fish at random coordinates.
    """
    for fish_iter in range(0, random_fishing_number):
        time.sleep(time_before_fish)
        logger.debug('fish iteration {0}'.format(fish_iter))
        pyautogui.moveTo(x_coordinates[fish_iter], y_coordinates[fish_iter], mouse_motion_time)
        pyautogui.mouseDown()
        distance_time = random.uniform(min_distance_time, max_distance_time)
        time.sleep(distance_time)
        pyautogui.mouseUp()
        time.sleep(create_bait_time)
        catch_fish()


Albion_template = cv2.imread('../templates/Albion.png', cv2.IMREAD_COLOR)
screenshot_bgr = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
albion_position_xy = find_template(screenshot_bgr, Albion_template)
x_albion = albion_position_xy[0]
y_albion = albion_position_xy[1]


def read_coordinates(line_data, point_num):
    """
    Read coordinates.

    This function read coordinates.

    Args:
        line_data (list): line consisting of array of points coordinate.
        point_num (int): number of point in line.

    Returns:
        [cord_x, cord_y] (list): array with coordinates [x,y]
    """
    line_data_num = line_data[point_num].replace('(', '').replace(')', '')
    cord_x, cord_y = line_data_num.split(',')

    if point_num == 1:
        cord_x = int(cord_x)
        cord_y = int(cord_y)
    else:
        cord_x = int(cord_x) + x_albion
        cord_y = int(cord_y) + y_albion
    return [cord_x, cord_y]


origin_position = [x_origin, y_origin]
fish_number = config.getint('FISH', 'num_fish')

time_before_worm = config.getfloat('TIME', 'time_before_worm')
time_before_pie = config.getfloat('TIME', 'time_before_pie')
worm_button = config.get('BUTTON', 'worm_button')
pie_button = config.get('BUTTON', 'pie_button')

worm_update_time = config.getfloat('TIME', 'worm_update_time')
pie_update_time = config.getfloat('TIME', 'pie_update_time')


def use_buffs(worm_timer, pie_timer):
    """
    Use buffs.

    Args:
        worm_timer (float): time since last use of worm
        pie_timer (float): time since last use of pie

    Returns:
        worm_timer, pie_timer (list): array with renewed times of buffs
    """
    current_time = time.time()
    if current_time - worm_timer >= worm_update_time:
        worm_timer = current_time
        pyautogui.press('1')
    if current_time - pie_timer >= pie_update_time:
        pie_timer = current_time
        pyautogui.press('2')
    return worm_timer, pie_timer


def bot_control(worm_timer, pie_timer):
    """
    Implement walking and fishing rod control at the same time.

    Args:
        worm_timer (float): time since last use of worm
        pie_timer (float): time since last use of pie

    Returns:
        worm_timer, pie_timer (list): array with renewed times of buffs
    """
    with open('../geolocation/way_1.txt', 'r') as way_file:
        for line in way_file:
            worm_timer, pie_timer = use_buffs(worm_timer, pie_timer)
            if line.replace('\n', ''):
                line = line.strip()
                line_data = line.split(' ')
                type_of_point = line_data[0]

                stand_point_x, stand_point_y = read_coordinates(line_data, 1)
                logger.debug('x_1, y_1 = {0}, {1}'.format(stand_point_x, stand_point_y))
                go_to_the_point(stand_point_x, stand_point_y)
                if type_of_point == 'N':
                    x_fish = []
                    y_fish = []
                    first_point = read_coordinates(line_data, 2)
                    second_point = read_coordinates(line_data, 3)
                    random_add_fish_number = random.randint(-2, 2)
                    for _ in range(fish_number + random_add_fish_number):
                        random_point = random_point_in_triangle(origin_position, first_point, second_point)
                        x_fish.append(random_point[0])
                        y_fish.append(random_point[1])
                    start_fishing(x_fish, y_fish, fish_number + random_add_fish_number)
    return worm_timer, pie_timer


if __name__ == '__main__':
    main()
