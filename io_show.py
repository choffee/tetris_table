#!/usr/bin/env python3

from Adafruit_GPIO import MCP230xx as mcs
from Adafruit_GPIO import GPIO

io = mcs.MCP23008(0x20)
for i in range(8):
    io.setup(i, GPIO.IN)
    io.pullup(i, True)

for i in range(8):
    print(io.input(i))



