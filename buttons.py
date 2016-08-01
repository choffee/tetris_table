#!/usr/bin/env python3

from Adafruit_GPIO import MCP230xx as mcs
from Adafruit_GPIO import GPIO

class Buttons(object):

    def __init__(self):
        self.buttons = mcs.MCP23008(0x20)
        for i in range(8):
            self.buttons.setup(i, GPIO.IN)
            self.buttons.pullup(i, True)

    def get_buttons(self):
        return self.buttons.input_pins(range(8))

if __name__ == "__main__":
    butts = Buttons()
    print(butts.get_buttons())



