#!/usr/bin/env python3

import os
import sys
lib_path = os.path.abspath(os.path.join('..', 'text'))
sys.path.append(lib_path)

import bitmapfont


def pixel(x, y):
    print(x, y)


with bitmapfont.BitmapFont(20, 10, pixel) as bf:
    bf.text("hi", 0, 0)
