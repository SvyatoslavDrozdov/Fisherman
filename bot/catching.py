"""
This module implements catching and fishing of fish.

THis module use YOLO8 model and use searching with template to control fishing process.
"""
import configparser
import logging
import random
import time

import cv2
import numpy as np
import pyautogui
from functions import cut_out, find_template
from ultralytics import YOLO
from vidgear.gears import ScreenGear

logger = logging.getLogger(__name__)
config = configparser.ConfigParser()
config.read('../config/setting.ini')

model_find_bait = YOLO('../weights/find_bait.pt', verbose=False)
model_check_pecking = YOLO('../weights/wait_pull.pt', verbose=False)
model_find_fishing_bar = YOLO('../weights/fishing_bar.pt', verbose=False)

Albion_template = cv2.imread('../templates/Albion.png', cv2.IMREAD_COLOR)
h_albion_line = Albion_template.shape[0]
albion_game_window_example = cv2.imread('../templates/albion_window_example.png', cv2.IMREAD_COLOR)
w_albion = albion_game_window_example.shape[1]
h_albion = albion_game_window_example.shape[0]

im_float_template = cv2.imread('../templates/im_float.png', cv2.IMREAD_COLOR)
w_im_float = im_float_template.shape[1]
h_im_float = im_float_template.shape[0]


def check_pecking(image):
    """
    Start the fishing process.

    This function implements the fishing process at given coordinates.

    Args:
        image (np.ndarray): PrtSc - print screen.

    Returns:
        wait (bool): bool variable showing do we need to pull (wait = 0) or not (wait = 1).
    """
    model_results = model_check_pecking(image, verbose=False)
    for model_result in model_results:
        boxes = model_result.boxes.xyxy
        confidences = model_result.boxes.conf
        class_ids = model_result.boxes.cls

        old_confidence = 0
        wait = 1
        for _box, confidence, class_id in zip(boxes, confidences, class_ids):
            confidence = float(confidence)
            if confidence >= old_confidence:
                old_confidence = confidence
                wait = int(class_id)
        return wait


def find_object(image, object_type):
    """
    Find object on the image.

    Args:
        image (np.ndarray): PrtSc - print screen.
        object_type (str): type of detecting object

    Returns:
        [x1, y1, x2, y2] (list): coordinates of the detecting object.
    """
    model_results = False
    critical_value = 0
    if object_type == 'bait':
        model_results = model_find_bait(image, verbose=False)
        critical_value = 0.3
    if object_type == 'fishing bar':
        model_results = model_find_fishing_bar(image, verbose=False)
        critical_value = 0.5
    if object_type == 'im_bait':
        critical_value = 0.85
        screen_img = np.array(image)
        processed_img = cv2.matchTemplate(screen_img, im_float_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(processed_img)
        x_1 = max_loc[0]
        y_1 = max_loc[1]
        x_2 = max_loc[0] + w_im_float
        y_2 = max_loc[1] + h_im_float
        if max_val >= critical_value:
            return [x_1, y_1, x_2, y_2]
        return [0, 0, 0, 0]

    for model_result in model_results:
        boxes = model_result.boxes.xyxy
        confidences = model_result.boxes.conf
        class_ids = model_result.boxes.cls
        old_confidence = 0
        x1, y1, x2, y2 = 0, 0, 0, 0
        for box, confidence, _class_id in zip(boxes, confidences, class_ids):
            confidence = float(confidence)
            if confidence >= old_confidence:
                old_confidence = confidence
                x1, y1, x2, y2 = map(int, box)
        if old_confidence <= critical_value:
            return [0, 0, 0, 0]
        return [x1, y1, x2, y2]


start_fishing_bar_coefficient = config.getfloat('GEOMETRY', 'start_fishing_bar_coefficient')
end_fishing_bar_coefficient = config.getfloat('GEOMETRY', 'end_fishing_bar_coefficient')

forward_coefficient = config.getfloat('GEOMETRY', 'forward_coefficient')
back_coefficient = config.getfloat('GEOMETRY', 'back_coefficient')


def im_float_control(image, im_float_control_parameters):
    """
    Find imaginary float on the fishing bar.

    im_float_control_parameters:
        fishing_bar_coordinates (list): coordinates of the fishing bar.
        time_fishing (float): time since last measure of imaginary float position.
        first_action (bool): needed to start program, consist information about first run.
        x_im_float_position (float): imaginary float position

    Args:
        image (np.ndarray): PrtSc - print screen.
        im_float_control_parameters (list): explained upper

    Returns:
        [x1, y1, x2, y2] (list): coordinates of the detecting object.
    """
    fishing_bar_coordinates, time_fishing, first_action, x_im_float_position = im_float_control_parameters
    x1, y1, x2, y2 = fishing_bar_coordinates
    fishing_bar_length = x2 - x1
    x_start = start_fishing_bar_coefficient * fishing_bar_length
    x_end = end_fishing_bar_coefficient * fishing_bar_length
    d_x = abs(x2 - x1)
    d_y = abs(y2 - y1)
    fishing_bar_picture = cut_out(x1, y1, d_x, d_y, image)
    x1_im_float, y1_im_float, x2_im_float, y2_im_float = find_object(fishing_bar_picture, 'im_bait')
    x_im_float = int((x1_im_float + x2_im_float) / 2)
    if first_action:
        x_im_float_position = x_im_float
        first_action = False
    else:
        dt = time.time() - time_fishing
        velocity = (x_im_float - x_im_float_position) / dt
        if velocity >= 0:
            future_position = x_im_float + velocity * forward_coefficient * dt
        else:
            future_position = x_im_float + velocity * back_coefficient * dt
        logger.debug('future_position = {0}'.format(future_position))
        if future_position >= x_end:
            pyautogui.mouseUp(button='left')
            logger.debug('Up')
        elif future_position <= x_start:
            pyautogui.mouseDown(button='left')
            logger.debug('Down')
        x_im_float_position = x_im_float

    if x1_im_float != 0 or y1_im_float != 0 or x2_im_float != 0 or y2_im_float != 0:
        return [True, first_action, x_im_float_position]
    logger.debug('IMAGINARY BAIT NOT FOUND')
    return [False, first_action, x_im_float_position]


def catch_fish():
    """Catch fish."""
    fishing_time = time.time()
    x_im_float_position = False
    first_action = True

    screen_img = cv2.imread('../start_picture/start_picture.png')
    albion_train_cord = find_template(screen_img, Albion_template)
    x_beginning_albion_train, y_beginning_albion_train, x_end_albion_train, y_end_albion_train = albion_train_cord
    h_albion_train = h_albion + h_albion_line
    cut_frame_albion = cut_out(x_beginning_albion_train, y_beginning_albion_train, w_albion, h_albion_train, screen_img)

    fishing_bar_train_cord = find_object(cut_frame_albion, 'fishing bar')
    x_1_fishing_bar_train, y_1_fishing_bar_train, x_2_fishing_bar_train, y_2_fishing_bar_train = fishing_bar_train_cord

    w_cut_bar = x_2_fishing_bar_train - x_1_fishing_bar_train
    h_cut_bar = y_2_fishing_bar_train - y_1_fishing_bar_train
    cut_frame_bar = cut_out(x_1_fishing_bar_train, y_1_fishing_bar_train, w_cut_bar, h_cut_bar, cut_frame_albion)
    find_object(cut_frame_bar, 'im_bait')

    albion_window_found = False
    x_beginning_albion, y_beginning_albion, x_end_albion, y_end_albion = 0, 0, 0, 0
    fishing = False
    waiting = True
    float_not_found_timer = time.time()
    wait_time = 1

    stream = ScreenGear().start()

    x_1_fishing_bar, y_1_fishing_bar, x_2_fishing_bar, y_2_fishing_bar = 405, 416, 621, 464
    float_not_found_counter = 0
    while True:
        frame = stream.read()
        if frame is None:
            break
        frame = np.array(frame)

        if not albion_window_found:
            x_beginning_albion, y_beginning_albion, x_end_albion, y_end_albion = find_template(frame, Albion_template)
        cut_frame = cut_out(x_beginning_albion, y_beginning_albion, w_albion, h_albion + h_albion_line, frame)
        if fishing:
            fishing_bar_place = [x_1_fishing_bar, y_1_fishing_bar, x_2_fishing_bar, y_2_fishing_bar]
            im_float_control_parameters = [fishing_bar_place, fishing_time, first_action, x_im_float_position]
            fishing, first_action, x_im_float_position = im_float_control(cut_frame, im_float_control_parameters)

            fishing_time = time.time()
            waiting = not fishing
            if waiting:
                pyautogui.mouseUp(button='left')
                break

        if waiting:
            x_1, y_1, x_2, y_2 = find_object(frame, 'bait')
            dx = x_2 - x_1
            dy = y_2 - y_1
            if x_1 ** 2 + y_1 ** 2 + x_2 ** 2 + y_2 ** 2 != 0:
                bait_picture = cut_out(x_1 - dx, y_1 - dy, 3 * dx, 3 * dy, frame)
                pecking = not bool(int(check_pecking(bait_picture)))
                if pecking and time.time() - float_not_found_timer >= wait_time:
                    logger.debug('Start fishing')
                    wait_to_pull_time = 0.5 + random.random() / 3
                    time.sleep(wait_to_pull_time)
                    pyautogui.mouseDown(button='left')
                    time.sleep(0.5)
                    fishing_time = time.time()
                    fishing = True
                    waiting = False
                    first_action = True
            else:
                logger.debug('FLOAT NOT FOUND: {0}'.format(float_not_found_counter))
                float_not_found_timer = time.time()
                float_not_found_counter += 1
                time.sleep(0.5)
        if float_not_found_counter >= 5:
            break
    stream.stop()
