#!/usr/bin/env python3

from Adafruit_GPIO import MCP230xx as mcs
from Adafruit_GPIO import GPIO

interupt_pin = 18
i2c_address = 0x20

class Buttons(object):

    def __init__(self):
        self.buttons = mcs.MCP23008(i2c_address)
        for i in range(8):
            self.buttons.setup(i, GPIO.IN)
            self.buttons.pullup(i, True)

    def add_callback(self, callback):
        # Setup interupt
        gpio = GPIO.get_platform_gpio()
      
        gpio.setup(interupt_pin, GPIO.IN)
        gpio.add_event_detect(interupt_pin, GPIO.FALLING, callback=callback, bouncetime=5)
         

    def get_buttons(self):
        return self.buttons.input_pins(range(8))

if __name__ == "__main__":
    butts = Buttons()
    print(butts.get_buttons())
    butts.add_callback(lambda x: print(butts.get_buttons()))



