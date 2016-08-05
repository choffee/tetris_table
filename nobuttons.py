#!/usr/bin/env python3

import time

class Buttons(object):
    def __init__(self):
        self.last_key = time.time()

    def get_buttons(self):
        if time.time() - self.last_key > 2:
            self.last_key = time.time()
            return [1]
        return []
