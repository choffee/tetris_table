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


log = logging.getLogger(__name__)

BUTTONEVENT = USEREVENT+1

shapes = [
    [[2, 2, 2, 2]],
    [[3, 3, 0],
     [0, 3, 3]],
    [[0, 0, 4],
     [4, 4, 4]],
    [[5, 5],
     [5, 5]],
    [[6, 0, 0],
     [6, 6, 6]],
    [[0, 7, 0],
     [7, 7, 7]],
    [[0, 8, 8],
     [8, 8, 0]],
]


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


class Tetris():
    """The testris game"""
    def __init__(self, board, light_board, table_buttons):
        self.board = board
        self.running = False
        self.clock = pygame.time.Clock()
        self.drop_interval = 1000  # 1 second
        self.shape_pos_y = 0
        self.shape_pos_x = 0
        self.last_drop_time = pygame.time.get_ticks()
        self.new_shape()
        self.button_state = [True] * 8
        self.ended = False
        self.score = 0
        self.lines_dropped = 0
        self.light_board = light_board
        self.buttons = table_buttons

    def new_shape(self):
        """Select a new shape and position it"""
        self.shape = shapes[randrange(len(shapes))]
        self.shape_pos_x = randrange(self.board['width'] - shape_width(self.shape))
        self.shape_pos_y = self.board['height'] - shape_height(self.shape) - self.board['height_hidden']
        if self.check_collisions():
            log.debug("End of Game...")
            self.ended = True
        self.last_drop_time = pygame.time.get_ticks()

    def time_till_next_drop(self):
        """Return number of milliseconds to next move, can be negative"""
        next_time = self.last_drop_time + self.drop_interval
        return next_time - pygame.time.get_ticks()

    def make_drop(self):
        """Move the shape down one"""
        self.last_drop_time = pygame.time.get_ticks()
        self.shape_pos_y -= 1
        log.debug("make_drop, shape_pos_y: %s", self.shape_pos_y)
        hit = False
        if self.check_collisions():
            log.debug('make_drop, Collided shape_pos_y: %s', self.shape_pos_y)
            self.shape_pos_y += 1
            self.stick_shape()
            self.new_shape()
            hit = True
        show_board_and_shape(self.board, self.light_board, self.shape, self.shape_pos_x, self.shape_pos_y)
        return hit

    def stick_shape(self):
        """Stick the shape on the board"""
        log.debug("stick_shape, Sticking shape")
        for shape_y, shape_row in enumerate(self.shape):
            for shape_x, shape_cell in enumerate(shape_row):
                try:
                    self.board['pixels'][shape_y + self.shape_pos_y][shape_x + self.shape_pos_x] += shape_cell
                except:
                    log.error("stick_shape, Dropping shape:x-%s, y-%s, %s, %s", shape_x, shape_y, self.shape_pos_x, self.shape_pos_y)

        self.check_full_lines()

    def check_full_lines(self):
        lines_closed=0
        while True:
            for i, row in enumerate(self.board['pixels'][:-1]):
                if 0 not in row:
                    remove_row(self.board, i)
                    lines_closed += 1
                    self.lines_dropped += 1
                    break
            else:
                break
        self.score += 100 * (lines_closed * lines_closed)
        if lines_closed > 0:
            try:
                self.row_sound.play()
            except:
                pass
            if self.lines_dropped > 0 and self.lines_dropped % 10 == 0:
                self.drop_interval -= 100

    def check_collisions(self):
        """Check the block is not bumping into anything"""
        log.info("check_collisions, Checking Collisions")
        for shape_y, shape_row in enumerate(self.shape):
            for shape_x, shape_cell in enumerate(shape_row):
                x_pos = self.shape_pos_x + shape_x
                y_pos = self.shape_pos_y + shape_y
                log.debug('check_collisions, x_pos: %s, y_pos: %s', x_pos, y_pos)
                try:
                    if y_pos < 0 or x_pos < 0:
                        return True
                    if self.board['pixels'][y_pos][x_pos] and shape_cell:
                        return True
                except IndexError:
                    log.debug("check_collisions, index error:%s %s", x_pos, y_pos)
                    return True
        return False

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

    def quick_drop(self):
        while not self.make_drop():
            pass

    def run(self):
        """Run the game"""
        log.info("run, Run the game")
        pygame.display.init()
        pygame.init()
        # button_event = pygame.event.Event(BUTTONEVENT, message="Button Pressed", button_values=[])
        try:
            background_sound = pygame.mixer.Sound("./sounds/tetris.ogg")
            background_sound.play( loops=-1 )
            self.row_sound = pygame.mixer.Sound("./sounds/jump.wav")
        except:
            log.debug("run, Failed to play sound: tetris.ogg")

        controls = self.buttons
        show_board_and_shape(self.board, self.light_board)
        log.debug("run, shape: %s", self.shape)
        self.running = True
        pygame.time.set_timer(USEREVENT, 100)  # every 100 miliseconds
        pygame.time.set_timer(USEREVENT+1, 10)  # every 10 milliseconds
        while self.running and not self.ended:
            event = pygame.event.wait()
            if event.type == QUIT:
                self.running = False
            if event.type == USEREVENT:
                if self.time_till_next_drop() < 0:
                    self.make_drop()
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
            print("Score: ", self.score)
            print("You cleared ", self.lines_dropped, " lines")


def main():
    """Start the main game"""
    game = Tetris()
    game.run()


if __name__ == "__main__":
    main()
