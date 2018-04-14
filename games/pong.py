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

# from random import randrange
# from operator import add

import logging
import pygame
from pygame.locals import USEREVENT, QUIT, KEYDOWN
# from pygame.color import *


log = logging.getLogger(__name__)

levelup_length = 20

BUTTONEVENT = USEREVENT+1

MOVE_L, MOVE_R, MOVE_U, MOVE_D = [[-1, 0], [1, 0], [0, 1], [0, -1]]
COL_WALL, COL_SNAKE, COL_ERASE, COL_TARGET = [5, 4, 0, 2]

LOGO = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]


class Game():
    """The pong game"""
    def __init__(self, board, light_board, table_buttons):
        self.board = board
        self.board_real_height = board['height'] - board['height_hidden']
        self.running = False
        self.clock = pygame.time.Clock()
        self.button_state = [True] * 8
        self.move_interval = 500  # 0.5 second
        self.ended = False
        self.score_p1 = 0
        self.score_p2 = 0
        self.bat_width = 2
        self.bats_position = [0, 0]
        self.ball_position = [0, 5]
        self.last_winner = 1
        self.velocity = [1, 1]
        self.level = 1
        self.light_board = light_board
        self.buttons = table_buttons
        self.logo = LOGO
        self.new_level()

    def new_level(self):
        """Reset the level"""
        # Wipe the board, this should be a function of the board class TODO
        self.board['pixels'] = [[0 for _ in range(self.board['width'])] for _ in range(self.board['height'])]
        self.move_vector = [1, 0]
        self.next_move_vector = False
        if self.last_winner == 1:
            ball_y = 1
            ball_x = self.bats_position[0]
            self.velocity = [1, 1]
        else:
            ball_x = self.board_real_height = 1
            ball_x = self.bats_position[1]
            self.velocity = [1, -1]
        self.ball_position = [5, 5]
        self.move_ball([ball_x, ball_y])
        self.draw_bats()
        self.last_tick = pygame.time.get_ticks()

    def draw_bats(self):
        for bat_num, bat_pos in enumerate(self.bats_position):
            if bat_num == 1:
                y_pos = self.board_real_height - 1
            else:
                y_pos = 0
            for x in range(self.board['width']):
                if x >= bat_pos and x <= bat_pos + self.bat_width:
                    pixel = 1
                else:
                    pixel = 0
                print(self.board['pixels'])
                print(x, y_pos)
                self.board['pixels'][y_pos][x] = pixel
        self.light_board.show_board(self.board)

    def move_ball(self, new_position):
        """Move the ball to new location"""
        x_pos, y_pos = new_position
        self.board['pixels'][self.ball_position[1]][self.ball_position[0]] = 0
        self.board['pixels'][y_pos][x_pos] = 1
        self.ball_position = new_position
        self.light_board.show_board(self.board)

    def get_next_ball_position(self):
        """Returns the next ball position based on time and velocity"""
        x_pos = self.ball_position[0]
        y_pos = self.ball_position[1]
        x_pos += self.velocity[0]
        y_pos += self.velocity[1]
        return [x_pos, y_pos]

    def hits_bat(self, new_position):
        x_pos, y_pos = new_position
        for bat in [1, 2]:
            if bat == 1:
                bat_y = 0
            else:
                bat_y = self.board_real_height
            if y_pos == bat_y:
                bat_x = self.bats_position[bat - 1]
                if x_pos >= bat_x and x_pos <= bat_x + self.bat_width:
                    self.velocity[1] = -(self.velocity[1])
                    return True
        return False

    def hits_wall(self, new_position):
        """ Do we hit the sidewall ?"""
        if new_position[0] < 0 or new_position[0] > self.board['width'] - 1:
            self.velocity[0] = -(self.velocity[0])
            return True
        return False

    def scores_at_end(self, new_position):
        """ Does somebody score at the end? """
        has_score = False
        if new_position[1] < 1:
            self.score_p2 += 1
            has_score = True
        if new_position[1] > self.board_real_height - 1:
            self.score_p1 += 1
            has_score = True
        if has_score and (self.score_p1 > 5 or self.score_p2 > 5):
            self.ended = True
        return has_score

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
            self.move_bat(1, MOVE_R)
        elif button == 3:
            self.move_bat(1, MOVE_L)
        elif button == 4:
            self.move_bat(2, MOVE_R)
        elif button == 7:
            self.move_bat(2, MOVE_L)

    def move_bat(self, bat, direction):
        position = self.bats_position[bat - 1]
        if direction == MOVE_R:
            mv = -1
        else:
            mv = 1
        if position + mv >= 0 \
           and position + self.bat_width + mv < self.board['width']:
            self.bats_position[bat - 1] = position + mv
        self.draw_bats()

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
                new_ball_position = self.get_next_ball_position()
                log.debug("New Ball: %s", new_ball_position)
                if self.hits_bat(new_ball_position):
                    log.debug("Hit Bat")
                    self.draw_bats()
                elif self.hits_wall(new_ball_position):
                    log.debug("Hit wall")
                elif self.scores_at_end(new_ball_position):
                    self.new_level()
                else:
                    self.move_ball(new_ball_position)
            if event.type == USEREVENT+1:
                for button in self.buttons_pressed(controls.get_buttons()):
                    log.debug("Button pressed %s", button)
                    self.button_event(button)
            if event.type == KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.move_bat(1, MOVE_L)
                if event.key == pygame.K_RIGHT:
                    self.move_bat(1, MOVE_R)
                if event.key == pygame.K_z:
                    self.move_bat(2, MOVE_L)
                if event.key == pygame.K_x:
                    self.move_bat(2, MOVE_R)
                if event.key == pygame.K_q:
                    self.running = False
        if self.ended:
            print("Thanks for playing")
            print("Level: ", self.level)
            print("Score Player 1: ", self.score_p1)
            print("Score Player 2: ", self.score_p2)


def main():
    """Start the main game"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
