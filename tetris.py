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

import logging
import pygame
import os
from pygame.locals import *
from pygame.color import *

if os.getenv('PI') == 1:
    os.putenv('SDL_FBDEV', '/dev/fb0')
    os.putenv('SDL_VIDEODRIVER', 'fbcons')
    os.putenv('SDL_NOMOUSE', '1')
    os.putenv('SDL_NOSOUND', '1')
    import lights
    import buttons
else:
    import nolights as lights
    import nobuttons as buttons

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

width = 10
height = 20

BUTTONEVENT = USEREVENT+1

colors = [
    [0, 0, 0],          # 0 - Black
    [255, 255, 255],    # 1 - White
    [255, 0, 0],        # 2 - Red
    [0, 255, 0],        # 3 - Green
    [0, 0, 255],        # 4 - Blue
    [255, 128, 0],      # 5 - Orange
    [255, 0, 255],      # 6 - Purple
    [0, 255, 255],      # 7 - Cyan
]

shapes = [
    [[2, 2, 2, 2]],
    [[3, 3, 0],
     [0, 3, 3]],
    [[4, 0, 0],
     [4, 4, 4]],
    [[5, 5],
     [5, 5]]
]

def new_board():
    board = []
    # XXX replace with clever map
    for y in range(height):
        board.append([])
        for x in range(width):
            board[y].append(0)
    return board

def drop_shape(board, shape, xpos, ypos):
    """Drop a shape into a board"""
    if len(shape) > 0:
        this_board = []
        shape_x_max = xpos + len(shape[0])
        shape_y_max = ypos + len(shape)
        for board_y, board_line in enumerate(board):
            line = []
            for board_x, cell in enumerate(board_line):
                if board_x >= xpos and board_x < shape_x_max and \
                        board_y >= ypos and board_y < shape_y_max:
                    log.debug("shape_pos: y:%s, x:%s", board_y - ypos, board_x - xpos)
                    line.append(cell + shape[board_y - ypos][board_x - xpos])
                else:
                    line.append(cell)
            this_board.append(line)
        return this_board
    else:
        return board

light_board = lights.Board()
def show_board(board, shape=[], shape_x=0, shape_y=0):
    """Display the board"""
    for line in drop_shape(board, shape, shape_x, shape_y):
        print(line)
    light_board.show_board(drop_shape(board, shape, shape_x, shape_y))

def rotate_shape(shape):
    shape = zip(*shape.rotated())
    return shape

class Tetris():
    """The testris game"""
    def __init__(self):
        self.board = new_board()
        self.running = False
        self.clock = pygame.time.Clock()
        self.drop_interval = 1000 # 1 second
        self.shape_pos_y = 0
        self.shape_pos_x = 0
        self.last_drop_time = pygame.time.get_ticks()
        self.new_shape()
        self.button_state = [True] * 8

    def new_shape(self):
        """Select a new shape and position it"""
        self.shape = shapes[randrange(len(shapes))]
        self.shape_pos_x = randrange(width - len(self.shape))
        self.shape_pos_y = 20 - len(self.shape[0])
        self.last_drop_time = pygame.time.get_ticks()

    def time_till_next_drop(self):
        """Return number of milliseconds to next move, can be negative"""
        next_time = self.last_drop_time + self.drop_interval
        return next_time - pygame.time.get_ticks()

    def make_drop(self):
        """Move the shape down one"""
        self.last_drop_time = pygame.time.get_ticks()
        self.shape_pos_y -= 1
        print(self.shape_pos_y)
        if self.check_collisions():
            log.debug('Collided %s', self.shape_pos_y)
            self.shape_pos_y += 1
            self.stick_shape()
            self.new_shape()
        else:
            show_board(self.board, self.shape, self.shape_pos_x, self.shape_pos_y)


    def stick_shape(self):
        """Stick the shape on the board"""
        for shape_y, shape_row in enumerate(self.shape):
            for shape_x, shape_cell in enumerate(shape_row):
                self.board[shape_y + self.shape_pos_y][shape_x + self.shape_pos_x] += shape_cell


    def check_collisions(self):
        """Check the block is not bumping into anything"""
        print("Checking Collisions")
        for shape_y, shape_row in enumerate(self.shape):
            for shape_x, shape_cell in enumerate(shape_row):
                x_pos = self.shape_pos_x + shape_x
                y_pos = self.shape_pos_y + shape_y
                log.debug('x_check: %s, y_check: %s', x_pos, y_pos)
                try:
                    if y_pos < 0 or x_pos < 0:
                        return True
                    if self.board[y_pos][x_pos] and shape_cell:
                        return True
                except IndexError:
                    log.debug("index error:%s %s", x_pos, y_pos)
                    return True
        return False

    def buttons_pressed(self, new_values):
        pressed = []
        # log.debug("Buttons pressed %s", new_values)
        for x, val in enumerate(new_values):
            if val != self.button_state[x]:
                self.button_state[x] = val
                log.debug("Button state: %s", self.button_state)
                pressed.append(x)
        return pressed

    def button_event(self, button):
        if button == 0:
            self.move_left()
        elif button == 3:
            self.move_right()
        elif button == 1:
            self.rotate()

    def move_right(self):
        """Move the shape right"""
        if self.shape_pos_x + len(self.shape) < width:
            self.shape_pos_x += 1
            if self.check_collisions():
              self.shape_pos_x -= 1
            else:
              show_board(self.board, self.shape, self.shape_pos_x, self.shape_pos_y)

    def move_left(self):
        """Move the shape right"""
        if self.shape_pos_x > 0:
            self.shape_pos_x -= 1
            if self.check_collisions():
              self.shape_pos_x += 1
            else:
              show_board(self.board, self.shape, self.shape_pos_x, self.shape_pos_y)


    def rotate(self):
        self.shape = rotate_shape(self.shape)
        log.debug("Shape rotating")
        if self.check_collisions():
            self.shape = rotate_shape(self.shape)

    def run(self):
        """Run the game"""
        print("Run the game")
        pygame.display.init()
        #button_event = pygame.event.Event(BUTTONEVENT, message="Button Pressed", button_values=[])
        controls = buttons.Buttons()
        show_board(self.board)
        print(self.shape)
        self.running = True
        pygame.time.set_timer(USEREVENT, 100) # every 100 miliseconds
        pygame.time.set_timer(USEREVENT+1, 10) # every 10 milliseconds
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                if event.type == USEREVENT:
                    if self.time_till_next_drop() < 0:
                        self.make_drop()
                if event.type == USEREVENT+1:
                    for button in self.buttons_pressed(controls.get_buttons()):
                        log.debug("Button pressed %s", button)
                        self.button_event(button)

def main():
    """Start the main game"""
    game = Tetris()
    game.run()

if __name__ == "__main__":
    main()
