#!/usr/bin/env python3
"""
    This is a game of "snake" for John's tetris table.
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
from operator import add

import logging
import pygame
import os
from pygame.locals import *
from pygame.color import *


log = logging.getLogger(__name__)

levelup_length = 20

BUTTONEVENT = USEREVENT+1

MOVE_L, MOVE_R, MOVE_U, MOVE_D = [[-1,0], [1,0], [0,1], [0,-1]]
COL_WALL, COL_SNAKE, COL_ERASE, COL_TARGET = [5, 4, 0, 2]

LOGO = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

class Game():
    """The snake game"""
    def __init__(self, board, light_board, table_buttons):
        self.board = board
        self.board_real_height = board['height'] - board['height_hidden']
        self.running = False
        self.clock = pygame.time.Clock()
        self.button_state = [True] * 8
        self.move_interval = 500  # 0.5 second
        self.new_level()
        self.ended = False
        self.score = 0
        self.level = 1
        self.lives = 3
        self.light_board = light_board
        self.buttons = table_buttons
        self.logo = LOGO

    def new_level(self):
        """Reset the level"""
        # Wipe the board, this should be a function of the board class TODO
        self.board['pixels'] = [[0 for _ in range(self.board['width'])] for _ in range(self.board['height'])]
        self.grow_count = 2    # 3 blocks long to start
        start_point = [int(self.board['width'] / 2), int(self.board_real_height / 2)]
        self.snake_segments = [start_point]
        self.move_vector = [1, 0]
        self.next_move_vector = False
        self.last_tick = pygame.time.get_ticks()
        self.new_target()

    def new_target(self):
        """Select a new target position """
        while True:
            self.target = [ randrange(self.board['width']), randrange(self.board_real_height) ]
            if self.target not in self.snake_segments:
                break
        self.board['pixels'][self.target[1]][self.target[0]] = COL_TARGET
        log.debug(self.board['pixels'])

    def time_till_next_drop(self):
        """Return number of milliseconds to next move, can be negative"""
        next_tick = self.last_tick + self.move_interval
        return next_tick - pygame.time.get_ticks()

    def set_direction(self, vector):
        if vector[0] == -self.move_vector[0] and vector[1] == -self.move_vector[1]:
            log.debug("Supress backward movement")
        elif not self.next_move_vector:
            self.move_vector = vector
        self.next_move_vector = vector

    def move_snake(self):
        """Move the snake one block"""
        self.last_tick = pygame.time.get_ticks()
        next_seg = list(map(add, self.snake_segments[0], self.move_vector))
        log.debug("Next Segment: %s", next_seg)
        if next_seg[0] not in range(self.board['width']) or next_seg[1] not in range(self.board_real_height):
            log.debug('Out of play: %s', next_seg)
            return False
        if next_seg == self.target:
            log.debug('Target got: %s', next_seg)
            try:
               self.row_sound.play()
            except:
                pass
            self.score += 1
            if len(self.snake_segments) > levelup_length:
                self.new_level()
                log.debug('Level %s complete - score: %s', self.level, self.score)
                self.level += 1
                self.move_interval *= 0.8
                return True
            else:
                self.new_target()
                self.grow_count += 3
        if self.board['pixels'][next_seg[1]][next_seg[0]] in [COL_SNAKE, COL_WALL]:
            log.debug('Collision at: %s', next_seg)
            return False
        # Move the head forward
        self.snake_segments.insert(0, next_seg)
        self.board['pixels'][next_seg[1]][next_seg[0]] = COL_SNAKE
        # Move the tail unless we're extending
        if self.grow_count > 0:
            self.grow_count -= 1
        else:
            erase = self.snake_segments.pop(-1)
            self.board['pixels'][erase[1]][erase[0]] = COL_ERASE
        self.light_board.show_board(self.board)
        if self.next_move_vector:
            self.move_vector = self.next_move_vector
            self.next_move_vector = False
        return True

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
        if button == 1:
            self.set_direction(MOVE_R)
        elif button == 3:
            self.set_direction(MOVE_L)
        elif button == 2:
            self.set_direction(MOVE_U)
        elif button == 0:
            self.set_direction(MOVE_D)

    def run(self):
        """Run the game"""
        log.debug("Run the game")
        pygame.display.init()
        pygame.init()
        # button_event = pygame.event.Event(BUTTONEVENT, message="Button Pressed", button_values=[])
        try:
            background_sound = pygame.mixer.Sound("./sounds/snake.ogg")
            background_sound.play(loops=-1)
            self.row_sound = pygame.mixer.Sound("./sounds/jump.wav")
        except:
            pass

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
                    if not self.move_snake():
                        self.lives -= 1
                        log.debug('Player died!  Lives remaining: %s', self.lives)
                        # death_sound.play()
                        if self.lives <= 0:
                            log.debug('Game over')
                            self.ended = True
                        else:
                            # TODO: "Ready?" Message
                            self.new_level()
            if event.type == USEREVENT+1:
                for button in self.buttons_pressed(controls.get_buttons()):
                    log.debug("Button pressed %s", button)
                    self.button_event(button)
            if event.type == KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.set_direction(MOVE_L)
                if event.key == pygame.K_RIGHT:
                    self.set_direction(MOVE_R)
                if event.key == pygame.K_UP:
                    self.set_direction(MOVE_U)
                if event.key == pygame.K_DOWN:
                    self.set_direction(MOVE_D)
                if event.key == pygame.K_q:
                    self.running = False
        if self.ended:
            print("Thanks for playing")
            print("Level: ", self.level)
            print("Score: ", self.score)


def main():
    """Start the main game"""
    game = Snake()
    game.run()


if __name__ == "__main__":
    main()
