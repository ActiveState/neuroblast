import pygame
from pygame.locals import *
import sys
from itertools import cycle

def enter_text(max_length, lower = False, upper = False, title = False):
    """
    returns user name input of max length "max length and with optional
    string operation performed
    """
    BLUE = (0,0,255)
    pressed = ""
    finished = False
    # create list of allowed characters using ascii values
    # numbers 1-9, letters a-z
    allowed_values = [i for i in range(97, 123)] +\
                     [i for i in range(48,58)]

    # create blinking underscore
    BLINK_EVENT = pygame.USEREVENT + 0
    pygame.time.set_timer(BLINK_EVENT, 800)
    blinky = cycle(["_", " "])
    next_blink = next(blinky)

    while not finished:
        screen.fill((0,0,0))
        pygame.draw.rect(screen, BLUE, (125,175,150,50))
        print_text(font, 125, 150, "Enter Name:")

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
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
                elif event.key == K_RETURN:
                    finished = True
        # only draw underscore if input is not at max character length
        if len(pressed) < max_length:
            print_text(font, 130, 180, pressed + next_blink)
        else:
            print_text(font, 130, 180, pressed)
        pygame.display.update()

    # perform any selected string operations
    if lower: pressed = pressed.lower()
    if upper: pressed = pressed.upper()
    if title: pressed = pressed.title()

    return pressed


def print_text(font, x, y, text, color = (255,255,255)):
    """Draws a text image to display surface"""
    text_image = font.render(text, True, color)
    screen.blit(text_image, (x,y))

pygame.init()
screen = pygame.display.set_mode((400,400))
font = pygame.font.SysFont(None, 25)
fpsclock = pygame.time.Clock()
fps = 30
BLUE = (0,0,255)
# name entered?
name = False

while True:
    fpsclock.tick(fps)
    pressed = None
    for event in pygame.event.get():
        if event.type == KEYUP:
            print(pygame.key.name(event.key))
            print(ord(pygame.key.name(event.key)))
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # key polling
    keys = pygame.key.get_pressed()
    screen.fill((0,0,0))

    if not name:
        name = enter_text(3,False,True)

    print_text(font, 130, 180, name)
    pygame.display.update()