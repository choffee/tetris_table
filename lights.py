#!/usr/bin/env python3
# Wrapper for making the lights run.

import time
from neopixel import *

led_width = 10
led_height = 20
led_count = led_width * led_height

led_pin = 18
led_freq_hz = 800000
led_dma = 5
led_invert = False
led_brightness = 64

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
            color = Color(board[xpos][ypos]*10, 0, 0 )
            self.strip.setPixelColor(led, color)
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
