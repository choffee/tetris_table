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

import signal
def handler(signum, frame):
    pass

signal.signal(signal.SIGHUP, handler)

if os.getenv('TETRIS_EMU') != "TRUE":
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

board_width = 10
board_height_hidden = 2
board_height = 20 + board_height_hidden

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


def new_board():
    board = []
    # XXX replace with clever map
    for y in range(board_height):
        board.append([])
        for x in range(board_width):
            board[y].append(0)
    return board

def shape_width(shape):
    return(len(shape[0]))

def shape_height(shape):
    return(len(shape))

def drop_shape(board, shape, xpos, ypos):
    """Drop a shape into a board"""
    if len(shape) > 0:
        this_board = []
        shape_x_max = xpos + shape_width(shape)
        shape_y_max = ypos + shape_height(shape)
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


def show_board(board, shape=None, shape_x=0, shape_y=0):
    """Display the board"""
    if shape is None:
        shape = []
    for line in drop_shape(board, shape, shape_x, shape_y):
        print(line)
    light_board.show_board(drop_shape(board, shape, shape_x, shape_y))


def rotate_shape(shape):
    return [[shape[y][x]
             for y in range(shape_height(shape))]
            for x in range(shape_width(shape) - 1, -1, -1)]


def remove_row(board, row):
    del board[row]
    return board + [[0 for i in range(board_width)]]


class Tetris():
    """The testris game"""
    def __init__(self):
        self.board = new_board()
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

    def new_shape(self):
        """Select a new shape and position it"""
        self.shape = shapes[randrange(len(shapes))]
        self.shape_pos_x = randrange(board_width - shape_width(self.shape))
        self.shape_pos_y = board_height - shape_height(self.shape) - board_height_hidden
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
        print(self.shape_pos_y)
        hit = False
        if self.check_collisions():
            log.debug('Collided %s', self.shape_pos_y)
            self.shape_pos_y += 1
            self.stick_shape()
            self.new_shape()
            hit = True
        show_board(self.board, self.shape, self.shape_pos_x, self.shape_pos_y)
        return hit

    def stick_shape(self):
        """Stick the shape on the board"""
        for shape_y, shape_row in enumerate(self.shape):
            for shape_x, shape_cell in enumerate(shape_row):
                try:
                    self.board[shape_y + self.shape_pos_y][shape_x + self.shape_pos_x] += shape_cell
                except:
                    log.error("Dropping shape:x-%s, y-%s, %s, %s", shape_x, shape_y, self.shape_pos_x, self.shape_pos_y)

        self.check_full_lines()

    def check_full_lines(self):
        lines_closed=0
        while True:
            for i, row in enumerate(self.board[:-1]):
                if 0 not in row:
                    self.board = remove_row(self.board, i)
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
            if not val and self.button_state[x]:
                log.debug("Button state: %s", self.button_state)
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
        if self.shape_pos_x + len(self.shape[0]) < board_width:
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
            self.shape = rotate_shape(self.shape)
            self.shape = rotate_shape(self.shape)
        else:
            show_board(self.board, self.shape, self.shape_pos_x, self.shape_pos_y)

    def quick_drop(self):
        while not self.make_drop():
            pass

    def run(self):
        """Run the game"""
        print("Run the game")
        pygame.display.init()
        pygame.init()
        # button_event = pygame.event.Event(BUTTONEVENT, message="Button Pressed", button_values=[])
        try:
            background_sound = pygame.mixer.Sound("./tetris.ogg")
            background_sound.play(loops = -1)
            self.row_sound = pygame.mixer.Sound("./jump.wav")
        except:
            pass
       
        controls = buttons.Buttons()
        show_board(self.board)
        print(self.shape)
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
                    log.debug("Button pressed %s", button)
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
