#!/usr/bin/env python3

import time
import logging as log
import random

class Buttons(object):
    def __init__(self):
        self.last_key = time.time()

    def get_buttons(self):
        return []
        """ Used to return random buttons """
        if time.time() - self.last_key > 1:
            buttons = [True, True, True, True, True, True, True, True]
            log.debug("Random Button time")
            self.last_key = time.time()
            buttons[random.randrange(4,8)] = False
            return buttons
