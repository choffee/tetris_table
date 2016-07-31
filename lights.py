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
