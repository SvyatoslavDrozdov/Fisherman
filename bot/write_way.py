"""This module implements writing of the bot's path."""

import time

import cv2
import numpy as np
import pyautogui
from functions import find_template
from orientation import get_current_position
from pynput import keyboard, mouse

way_name = "way.txt"

Albion_template = cv2.imread('/home/svyat/PycharmProjects/AlbionFisherman/templates/Albion.png', cv2.IMREAD_COLOR)
w_albion_line = Albion_template.shape[1]
h_albion_line = Albion_template.shape[0]

screenshot = pyautogui.screenshot()
screenshot_np = np.array(screenshot)
screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

x_beginning_albion, y_beginning_albion, x_end_albion, y_end_albion = find_template(screenshot_bgr, Albion_template)

left_button_counter = 0
X_click_mouse = []
Y_click_mouse = []


def write_n_positions(position_number):
    """
    Find imaginary float on the fishing bar.

    Args:
        position_number (int): number of mouse click positions.

    Returns:
        [X_answer, Y_answer] (list): coordinates of the detecting mouse's clicks.
    """
    global left_button_counter
    global X_click_mouse
    global Y_click_mouse

    def on_mouse_click(x, y, button, pressed):
        global left_button_counter
        global X_click_mouse
        global Y_click_mouse

        if button == mouse.Button.left and pressed:
            left_button_counter += 1
            time.sleep(2)
            print('Ready to new input')
            if left_button_counter == 1:
                x_RP, y_RP = get_current_position()
                X_click_mouse.append(x_RP)
                Y_click_mouse.append(y_RP)
            else:
                X_click_mouse.append(x - x_beginning_albion)
                Y_click_mouse.append(y - y_beginning_albion)

            if left_button_counter == position_number:
                write_listener.stop()

    write_listener = mouse.Listener(on_click=on_mouse_click)
    write_listener.start()
    write_listener.join()
    left_button_counter = 0

    X_answer = np.array(X_click_mouse)
    Y_answer = np.array(Y_click_mouse)
    X_click_mouse = []
    Y_click_mouse = []
    return X_answer, Y_answer


def add_standard_way_point():
    x_RP_array, y_RP_array = write_n_positions(1)
    way_file = open(f'/home/svyat/PycharmProjects/AlbionFisherman/geolocation/{way_name}', 'a')
    line = 'S' + ' ' + '(' + str(x_RP_array[0]) + ',' + str(y_RP_array[0]) + ')' + '\n'
    way_file.write(line)
    way_file.close()


def add_node_way_point():
    """Add new node point."""
    x_RP_array, y_RP_array = write_n_positions(3)
    way_file = open(f'/home/svyat/PycharmProjects/AlbionFisherman/geolocation/{way_name}', 'a')
    line = 'N' + ' ' + '(' + str(x_RP_array[0]) + ',' + str(y_RP_array[0]) + ')' + ' ' + '(' + str(
        x_RP_array[1]) + ',' + str(y_RP_array[1]) + ')' + ' ' + '(' + str(x_RP_array[2]) + ',' + str(
        y_RP_array[2]) + ')' + '\n'
    way_file.write(line)
    way_file.close()


print('Press Z to add standard way point.')
print('Press X to add node way point.')
print('Press C to add exit.')


def on_press(key):
    try:
        keyboard_button = key.char
        if keyboard_button == 'z':
            print('Adding standard waypoint.')
            add_standard_way_point()
            print('Added standard waypoint')
        elif keyboard_button == 'x':
            print('Adding node waypoint.')
            add_node_way_point()
            print('Added node waypoint')
        elif keyboard_button == 'c':
            return False
    except AttributeError:
        pass


with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
