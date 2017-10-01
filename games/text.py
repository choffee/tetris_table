#!/usr/bin/env python3
"""
    This is my tetris table game.
    Copyright John Cooper - 2016

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from random import randrange

import copy
import logging
import pygame
from pygame.locals import *
from pygame.locals import USEREVENT
from pygame.color import *
import bitmapfont


log = logging.getLogger(__name__)

BUTTONEVENT = USEREVENT+1

def print_text(message, board, pos):
    "Scroll Some text over the screen"
    display_width=board.width
    display_height=board.height

    def pixel(x, y):
        if x < len(board):
            if y < len(board[0]):
                board.pixel[x][y] = 1

    with bitmapfont.BitmapFont(display_width, display_height, pixel) as bf:
        # Global state:
        bf.text(message, int(pos), 0)

def shape_width(shape):
    return(len(shape[0]))


def shape_height(shape):
    return(len(shape))


def drop_shape(board, shape, xpos, ypos):
    """Drop a shape into a board"""
    # This feels ugly, get rid of the deep copy
    # when this moves into the board class
    this_board = copy.deepcopy(board)
    if len(shape) > 0:
        this_pixels = []
        shape_x_max = xpos + shape_width(shape)
        shape_y_max = ypos + shape_height(shape)
        for board_y, board_line in enumerate(board['pixels']):
            line = []
            for board_x, cell in enumerate(board_line):
                if board_x >= xpos and board_x < shape_x_max and \
                        board_y >= ypos and board_y < shape_y_max:
                    y = board_y - ypos
                    x = board_x - xpos
                    log.debug("drop_shape, shape_pos: y:%s, x:%s", y, x)
                    line.append(cell + shape[y][x])
                else:
                    line.append(cell)
            this_pixels.append(line)
        this_board['pixels'] = this_pixels
    return this_board


def show_board_and_shape(board, light_board, shape=None, shape_x=0, shape_y=0):
    """Display the board"""
    if shape is None:
        shape = []
    for line in drop_shape(board, shape, shape_x, shape_y)['pixels']:
        log.debug("show_board_and_shape, line: %s", line)
    light_board.show_board(drop_shape(board, shape, shape_x, shape_y))


def rotate_shape(shape):
    return [[shape[y][x]
             for y in range(shape_height(shape))]
            for x in range(shape_width(shape) - 1, -1, -1)]


def remove_row(board, row):
    log.debug("remove_row, Removing row: %s", row)
    del board['pixels'][row]
    board['pixels'] += [[0 for i in range(board['width'])]]


class Text():
    """Text display"""
    def __init__(self, board, light_board, table_buttons):
        self.board = board
        self.running = False
        self.clock = pygame.time.Clock()
        self.move_interval = 10
        self.last_move_time = pygame.time.get_ticks()
        self.button_state = [True] * 8
        self.ended = False
        self.light_board = light_board
        self.buttons = table_buttons
        self.message = "York Hackspace"

    def move_text(self):
        """Move the text one"""


    def time_till_next_move(self):
        """Return number of milliseconds to next move, can be negative"""
        next_time = self.last_move_time + self.move_interval
        return next_time - pygame.time.get_ticks()



    def buttons_pressed(self, new_values):
        pressed = []
        # log.debug("Buttons pressed %s", new_values)
        for x, val in enumerate(new_values):
            if not val and self.button_state[x]:
                log.debug("buttons_pressed, Button state: %s", self.button_state)
                pressed.append(x)
            self.button_state[x] = val
        return pressed

    def button_event(self, button):
        if button == 1: # 4
            self.move_left()
        elif button == 3: # 7
            self.move_right()
        elif button == 2: # 5
            self.rotate()
        elif button == 0: # 6
            self.quick_drop()

    def move_right(self):
        """Move the shape right"""
        if self.shape_pos_x + len(self.shape[0]) < self.board['width']:
            self.shape_pos_x += 1
            if self.check_collisions():
                self.shape_pos_x -= 1
            else:
                show_board_and_shape(self.board, self.light_board, self.shape, self.shape_pos_x, self.shape_pos_y)

    def move_left(self):
        """Move the shape right"""
        if self.shape_pos_x > 0:
            self.shape_pos_x -= 1
            if self.check_collisions():
                self.shape_pos_x += 1
            else:
                show_board_and_shape(self.board, self.light_board, self.shape, self.shape_pos_x, self.shape_pos_y)

    def rotate(self):
        self.shape = rotate_shape(self.shape)
        log.info("rotate, Shape rotating")
        if self.check_collisions():
            self.shape = rotate_shape(self.shape)
            self.shape = rotate_shape(self.shape)
            self.shape = rotate_shape(self.shape)
        else:
            show_board_and_shape(self.board, self.light_board, self.shape, self.shape_pos_x, self.shape_pos_y)

    def run(self):
        """Run the game"""
        log.info("run, Run the game")
        pygame.display.init()
        pygame.init()

        controls = self.buttons
        self.light_board.show_board(self.board)
        self.running = True
        pygame.time.set_timer(USEREVENT, 100)  # every 100 miliseconds
        pygame.time.set_timer(USEREVENT+1, 10)  # every 10 milliseconds
        while self.running and not self.ended:
            event = pygame.event.wait()
            if event.type == QUIT:
                self.running = False
            if event.type == USEREVENT:
                if self.time_till_next_drop() < 0:
                    self.move_text()
            if event.type == USEREVENT+1:
                for button in self.buttons_pressed(controls.get_buttons()):
                    log.debug("run, Button pressed %s", button)
                    self.button_event(button)
            if event.type == KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.move_left()
                if event.key == pygame.K_RIGHT:
                    self.move_right()
                if event.key == pygame.K_UP:
                    self.rotate()
                if event.key == pygame.K_DOWN:
                    self.quick_drop()
                if event.key == pygame.K_q:
                    self.running = False
        if self.ended:
            print("Thanks for playing")


def main():
    """Start the main game"""
    game = Tetris()
    game.run()


if __name__ == "__main__":
    main()
