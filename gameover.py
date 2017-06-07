'''The MIT License (MIT)

Copyright (c) 2017 ActiveState Software Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

import pygame
from pygame.locals import *
import sys
from itertools import cycle
from utils import *

pressed = ""

def enter_text(eq, screen, max_length, lower = False, upper = False, title = False):
    global pressed
    BLUE = (0,0,255)
    allowed_values = [i for i in range(97, 123)] +\
                     [i for i in range(48,58)]

    BLINK_EVENT = pygame.USEREVENT + 0
    pygame.time.set_timer(BLINK_EVENT, 800)
    blinky = cycle(["_", " "])
    next_blink = next(blinky)
    displaytext('GAME OVER', 16, 320,60, WHITE, screen)        

    displaytext('Enter your name:', 16, 320,125, WHITE, screen)        

    for event in eq:
        if event.type == BLINK_EVENT:
            next_blink = next(blinky)
        # if input is in list of allowed characters, add to variable
        elif event.type == KEYUP and event.key in allowed_values \
            and len(pressed) < max_length:
            # caps entry?
            if pygame.key.get_mods() & KMOD_SHIFT or pygame.key.get_mods()\
                & KMOD_CAPS:
                pressed += chr(event.key).upper()
            # lowercase entry
            else:
                pressed += chr(event.key)
        # otherwise, only the following are valid inputs
        elif event.type == KEYUP:
            if event.key == K_BACKSPACE:
                pressed = pressed[:-1]
            elif event.key == K_SPACE:
                pressed += " "
        
    # only draw underscore if input is not at max character length
    if len(pressed) < max_length:
        displaytext(pressed + next_blink, 16, 320, 180, WHITE, screen)        
    else:
        displaytext(pressed, 15, 320, 180, WHITE, screen)        

    # perform any selected string operations
    if lower: pressed = pressed.lower()
    if upper: pressed = pressed.upper()
    if title: pressed = pressed.title()