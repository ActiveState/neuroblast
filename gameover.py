import pygame
from pygame.locals import *
import sys
from itertools import cycle
from utils import *

pressed = ""

def enter_text(eq, screen, max_length, lower = False, upper = False, title = False):
    """
    returns user name input of max length "max length and with optional
    string operation performed
    """

    #print "listening for input"
    
    global pressed
    BLUE = (0,0,255)
    # create list of allowed characters using ascii values
    # numbers 1-9, letters a-z
    allowed_values = [i for i in range(97, 123)] +\
                     [i for i in range(48,58)]

    # create blinking underscore
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