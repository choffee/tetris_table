#!/usr/bin/env python3

import tetris
import pytest


def test_rotate_shape_test():
    tm = [[1, 0, 1], [0, 1, 0]]
    assert tetris.rotate_shape(tm) == [[1, 0], [0, 1], [1, 1]]
