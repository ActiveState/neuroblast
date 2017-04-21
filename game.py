# game.py
# Eventually will hold all the core game functions, game loop etc.
# But none of the other stuff
# For now it will catch all everything

# Excuse the mess, it's under construction

from __future__ import division
import pygame
import pygame.freetype
import math
import gamestates

### GLOBAL GAME INIT AND MAIN LOOP
# Basic library initialization
pygame.init()

# Configure screen TODO: Should there be a config object or something to contain this?
resolution = (1280, 720)
screen = pygame.display.set_mode(resolution)

pygame.display.set_caption("Bit Blaster")

background = pygame.image.load('Cygnus_Wall.jpg')
bgsize = background.get_size()
w, h = bgsize

# TODO Get dynamic resolution but width is 1280 for now

aspect = w/h
wscale = 1280.0
hscale = wscale/aspect

bgscaled = pygame.transform.scale(background, (1280, int(hscale)))

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

init_stars(screen)
# Initial game state is menu
state = gamestates.Menu()

scrollSpeed = 1
y = -hscale+720


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
    y += scrollSpeed
    # --- Screen-clearing code goes here
    screen.blit(bgscaled, (0, y))
    # --- Drawing code should go here
    move_and_draw_stars(screen)
    ## Gamestate update
    state = state.update(screen, event_queue, clock.get_time()/1000.0)
    ## Trap exits from gamestate
    if state == None:
        done = True
    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
    # --- Limit to 60 frames per second
    clock.tick(60)

# Close the window and quit.
pygame.quit()
