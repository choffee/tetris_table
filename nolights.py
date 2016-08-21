#!/usr/bin/env python3
import pygame
from bitcolors import colors

MAX_X=424
MAX_Y=600
BLOCK_SIZE=20

def make_square(x, y):
    b_size = BLOCK_SIZE
    return (x * b_size + 1, MAX_Y - (y + 1) * b_size - 2, b_size, b_size)

def make_color(num):
    return colors[num]

class Board(object):
    def __init__(self):
        self.screen = pygame.display.set_mode((MAX_X, MAX_Y))
        top = MAX_Y - ( 20 * BLOCK_SIZE) - 3
        pygame.draw.rect(self.screen, (255, 255, 255), (0, top, 10 * BLOCK_SIZE + 2, BLOCK_SIZE * 20 + 2), 1)

    def show_board(self, board):
        for line_no, line in enumerate(board):
            for cell_no, cell in enumerate(line):
                pygame.draw.rect(self.screen, make_color(cell), make_square(cell_no, line_no))

        pygame.display.update()
