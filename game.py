# game.py
# Eventually will hold all the core game functions, game loop etc.
# But none of the other stuff
# For now it will catch all everything

# Excuse the mess, it's under construction

from __future__ import division
import pygame
import pygame.freetype
import math
import numpy as np
import gamestates
from utils import *
import plot
import sys

### GLOBAL GAME INIT AND MAIN LOOP
# Basic library initialization
pygame.init()
loadfont(24)

# Configure screen TODO: Should there be a config object or something to contain this?
resolution = (1280, 720)
flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
if (len(sys.argv) > 1) and (sys.argv[1] == '-f'):
    flags = pygame.DOUBLEBUF
screen = pygame.display.set_mode(resolution, flags)
screen.set_alpha(None)

pygame.display.set_caption("Bit Blaster")

background = pygame.image.load('Cygnus_Wall.jpg')
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

init_stars(screen)
# Initial game state is menu
state = gamestates.Menu()

scrollSpeed = -1
#y = -hscale+720

# Optimized method for scrolling background continuously
topY = hscale-720       # As soon as topY because -720, next frame, flip it back to hscale-720

plotUpdateRate = 1/10.0
plotCounter = 0.0

# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    event_queue = pygame.event.get()
    for event in event_queue:
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True

    # --- Game logic should go here
    topY += scrollSpeed
    # --- Screen-clearing code goes here
    #screen.blit(bgscaled, (0, y))
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
    # --- Drawing code should go here
    move_and_draw_stars(screen)
    ## Gamestate update
    state = state.update(screen, event_queue, clock.get_time()/1000.0, clock)
    ## Trap exits from gamestate
    if state == None:
        done = True
        
    plotCounter+= clock.get_time()/1000.0
    if plotCounter>plotUpdateRate:
        # Get the plotted data and display it on screen
        surf = plot.plot(np.random.random((640, 360)))
        screen.blit(surf,(640,0))
        plotCounter = 0.0
    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
    # --- Limit to 60 frames per second
    clock.tick(30)

# Close the window and quit.
pygame.quit()
