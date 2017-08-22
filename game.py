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

# game.py
# Core game initialization, main game loop, etc.

from __future__ import division
import pygame
import pygame.freetype
import math
import numpy as np
import gamestates
from utils import *
import sys
import argparse

### GLOBAL GAME INIT AND MAIN LOOP
# Basic library initialization
pygame.init()
loadfont(24)
parser = argparse.ArgumentParser()
parser.add_argument('-f',action='store_true')
parser.add_argument('-n',action='store_true')
parser.add_argument('-v',action='store_true')

args = parser.parse_args()

# 0 is internal neural net, 1 is keras/tensorflow (default)
netmodel = 1

# VizModel is which viz method, direct Keras (1) or simulated neural net (0) (faster)
vizmodel = 0

# Configure screen TODO: Should there be a config object or something to contain this?
resolution = (1280, 720)
flags = pygame.DOUBLEBUF

if (args.f == True):
    flags |= pygame.FULLSCREEN

# Netmodel = 1 means Keras/Tensorflow, 0 = internal simple neural net for prototyping
if (args.n == True):
    netmodel = 0

if (args.v == True):
    vizmodel = 1

screen = pygame.display.set_mode(resolution, flags)
screen.set_alpha(None)

pygame.display.set_caption("Neuro/Blast")

background = pygame.image.load('art/python-game_background.png')
bgsize = background.get_size()
w, h = bgsize

# TODO Get dynamic resolution but width is 1280 for now

aspect = w/h
wscale = 640
hscale = wscale/aspect

bgscaled = pygame.transform.scale(background, (640, int(hscale)))

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Init gamepads
# Initialize the joystick control, get the first one
pygame.joystick.init()
if (pygame.joystick.get_count()>0):
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
else:
    joystick = None

init_stars(screen)
# Initial game state is menu
state = gamestates.Menu(None)

scrollSpeed = -1

# Optimized method for scrolling background continuously
topY = hscale-720       # As soon as topY because -720, next frame, flip it back to hscale-720

plotUpdateRate = 1/10.0
plotCounter = 0.0

while not done:
    event_queue = pygame.event.get()
    for event in event_queue:
        if event.type == pygame.QUIT:
            done = True

    topY += scrollSpeed
    offset = hscale+topY    # If topY becomes negative, we use this to seamlessly blit until it clears itself up
    y = topY
    blitStartY = 0
    height = 720
    if (topY<0):
        blitStartY = -topY
        height = 720+topY
        y = 0
        screen.blit(bgscaled,(0,0),(0,offset,640,720-height))
    screen.blit(bgscaled,(0,blitStartY),(0,y,640,height+1))
    
    if topY<=-720:
        topY = hscale-720     
    move_and_draw_stars(screen)
    ## Gamestate update
    state = state.update(screen, event_queue, clock.get_time()/1000.0, clock, joystick, netmodel,vizmodel)
    ## Trap exits from gamestate
    if state == None:
        done = True
        
    pygame.display.flip()
    clock.tick(30)

# Close the window and quit.
pygame.quit()
