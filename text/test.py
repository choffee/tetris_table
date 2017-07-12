#!/usr/bin/env python3

import bitmapfont


def pixel(x, y):
  print(x, y)


with bitmapfont.BitmapFont(20, 10, pixel) as bf:
    bf.text("hi", 0, 0)
