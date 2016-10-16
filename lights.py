#!/usr/bin/env python3
# Wrapper for making the lights run.

import time
from neopixel import *
import logging as log

led_width = 10
led_height = 20
led_count = led_width * led_height

led_pin = 18
led_freq_hz = 800000
led_dma = 5
led_invert = False
led_brightness = 64

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

def strip_pos_to_board(led_num):
    xpos = int(led_num % led_height)
    ypos = int(led_num / led_height)
    if ypos % 2 == 0:
        xpos = led_height - xpos -1
    return (xpos, ypos)

class Board(object):
    def __init__(self):
        """Setup a board"""
        self.strip = Adafruit_NeoPixel(led_count, led_pin, led_freq_hz, led_dma, led_invert, led_brightness)
        self.strip.begin()

    def show_board(self, board):
        """Show a board on the lights"""
        for led in range(led_count -1):
            xpos, ypos = strip_pos_to_board(led)
            try:
                led_rgb = colors[board[xpos][ypos]]
            except IndexError:
                log.error("Ivalid color ID %s", board[xpos][ypos])
                led_rgb = [255, 255, 255]
            led_color = Color(led_rgb[0], led_rgb[1], led_rgb[2])
            self.strip.setPixelColor(led, led_color)
        self.strip.show()




def main():
    strip = Adafruit_NeoPixel(led_count, led_pin, led_freq_hz, led_dma, led_invert, led_brightness)
    strip.begin()
    colour = Color(64, 128, 64)
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, colour)
        strip.show()
        time.sleep(10/1000.0)


if __name__ == "__main__":
    main()
