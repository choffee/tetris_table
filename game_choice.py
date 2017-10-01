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
from pygame.locals import *
from pygame.color import *


log = logging.getLogger(__name__)

levelup_length = 20

BUTTONEVENT = USEREVENT+1

MOVE_L, MOVE_R, MOVE_U, MOVE_D = [[-1,0], [1,0], [0,1], [0,-1]]
COL_WALL, COL_SNAKE, COL_ERASE, COL_TARGET = [5, 4, 0, 2]


class Games():
    """The snake game"""
    def __init__(self, board, light_board, table_buttons, games):
        self.board = board
        self.board_real_height = board['height'] - board['height_hidden']
        self.running = False
        self.clock = pygame.time.Clock()
        self.button_state = [True] * 8
        self.move_interval = 500  # 0.5 second
        self.ended = False
        self.light_board = light_board
        self.buttons = table_buttons
        self.games = games


    def show_logo(self, logo):
        self.board['pixels'] = logo
        self.light_board.show_board(self.board)

    def next_game(self, selected_game, direction):
        if selected_game + direction < 0:
            selected_game = len(self.games) - 1
        elif selected_game + direction > len(self.games) - 1:
            selected_game = 0
        else:
            selected_game += direction
        return selected_game


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
        if button == 4:
            self.set_direction(MOVE_L)
        elif button == 7:
            self.set_direction(MOVE_R)
        elif button == 5:
            self.set_direction(MOVE_U)
        elif button == 6:
            self.set_direction(MOVE_D)

    def run(self):
        """Select the game"""
        log.debug("Run the game")
        pygame.display.init()
        pygame.init()

        selected_game = 0

        controls = self.buttons
        self.light_board.show_board(self.board)
        self.running = True
        self.show_logo(self.games[selected_game].LOGO)
        pygame.time.set_timer(USEREVENT, 100)  # every 100 miliseconds
        pygame.time.set_timer(USEREVENT+1, 10)  # every 10 milliseconds
        while self.running and not self.ended:
            event = pygame.event.wait()
            if event.type == QUIT:
                self.running = False
            if event.type == USEREVENT+1:
                for button in self.buttons_pressed(controls.get_buttons()):
                    log.debug("Button pressed %s", button)
                    self.button_event(button)
            if event.type == KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_game = self.next_game(selected_game, -1)
                if event.key == pygame.K_RIGHT:
                    selected_game = self.next_game(selected_game, 1)
                if event.key == pygame.K_UP:
                    self.running = False
                    self.ended = True
                if event.key == pygame.K_DOWN:
                    self.ended = True
                    self.running = False
                if event.key == pygame.K_q:
                    self.ended = True
                    self.running = False
                self.show_logo(self.games[selected_game].LOGO)
        if self.ended:
            return self.games[selected_game]
