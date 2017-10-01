#!/usr/bin/env python3
"""
    This is my tetris table game.
    Copyright John Cooper - 2016

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import logging
import os
import signal
from games import tetris

"""
Handle the fact that systemd sends us a HUP at the start.
"""


def handler(signum, frame):
    """Ignore the signal for now"""
    pass


signal.signal(signal.SIGHUP, handler)


try:
    os.putenv('SDL_FBDEV', '/dev/fb0')
    os.putenv('SDL_VIDEODRIVER', 'fbcons')
    os.putenv('SDL_NOMOUSE', '1')
    os.putenv('SDL_NOSOUND', '1')
    import lights
    import buttons
except ImportError:
    os.unsetenv('SDL_FBDEV')
    os.unsetenv('SDL_VIDEODRIVER')
    os.unsetenv('SDL_NOMOUSE')
    os.unsetenv('SDL_NOSOUND')
    import nolights as lights
    import nobuttons as buttons


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

board_width = 10
board_height_hidden = 2
board_height = 20 + board_height_hidden


def new_board():
    pixels = [[0 for _ in range(board_width)] for _ in range(board_height)]
    return {
        "pixels": pixels,
        "height": board_height,
        "width": board_width,
        "height_hidden": board_height_hidden,
    }


def main():
    """Start the main game"""
    light_board = lights.Board()
    board = new_board()
    table_buttons = buttons.Buttons()
    game = tetris.Tetris(board, light_board, table_buttons)
    game.run()


if __name__ == "__main__":
    main()
