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

import pygame
from pygame.locals import *
from pygame.color import *

width = 10
height = 20

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

def show_board(board):
    for y in board:
        print(y)

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

    def new_shape(self):
        """Select a new shape and position it"""
        self.shape = shapes[randrange(len(shapes))]
        self.shape_pos_x = randrange(width - len(self.shape))
        self.shape_pos_y = height
        self.last_drop_time = pygame.time.get_ticks()

    def time_till_next_drop(self):
        """Return number of milliseconds to next move, can be negative"""
        next_time = self.last_drop_time + self.drop_interval
        return next_time - pygame.time.get_ticks()

    def make_drop(self):
        """Move the shape down one"""
        self.last_drop_time = pygame.time.get_ticks()
        self.shape_pos_y = self.shape_pos_y - 1
        self.check_collisions()

    def check_colliions(self):
        """Check the block is not bumping into anything"""
        pass

    def run(self):
        """Run the game"""
        print("Run the game")
        show_board(self.board)
        print(self.shape)
        self.running = True
        pygame.time.event(USEREVENT, 100) # every 100 miliseconds
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                if event.type == pygame.USEREVENT:
                    if self.time_till_next_drop < 0:
                        make_drop

def main():
    """Start the main game"""
    game = Tetris()
    game.run()

if __name__ == "__main__":
    main()
