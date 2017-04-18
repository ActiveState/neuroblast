# game.py
# Eventually will hold all the core game functions, game loop etc.
# But none of the other stuff
# For now it will catch all everything

from __future__ import division
import pygame
import pygame.freetype
from random import randrange, choice


class Killable(object):
    def __init__(self):
        self.health = 100
        self.active = True
    def TakeDamage(self, damage):
        #Take damage fuc tion
        self.health -= damage
        if self.health < 0:
            # DEAD
            self.Die()
    def Die(self):
        # DO something
        # Trigger Particle or something
        self.active = False

class Enemy(Killable):
    def __init__(self):
        # Enemy specific stuff here
        self.BulletLayer = 1

class Player(Killable):
    def __init__(self):
        # Plauer specifc init stuff here
        self.BulletLayer = 2

 
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0,0,255)
RED = (255, 0, 0)

## Constants
MAX_STARS  = 250
STAR_SPEED = 2

# GameState object will return a new state object if it transitions
class GameState(object):
    def update(self, screen, event_queue):
        return self

def displaytext(
    text,
    fontsize,
    x,
    y,
    color,
    ):

    #font = pygame.font.SysFont('sawasdee', fontsize, True)
    font = pygame.freetype.Font('./De Valencia (beta).otf', fontsize)
    texcol = pygame.Color(*color)
    text = font.render(text, texcol)
    textpos = text[0].get_rect(centerx=x, centery=y)
    screen.blit(text[0], textpos)

class Play(GameState):
    def update(self,screen,event_queue):
        return self

# Draws the menu on screen.
# This is a class that is just instantiated
# While that object exists, it processes stuff
# Only one "GameState" object can exist at one time
class Menu(GameState):
    def update(self,screen,event_queue):
        nextState = self
        global menu_selection
        displaytext('Play', 32, screen.get_width() / 2 - 20, screen.get_height() * 3 / 4
                    - 40, WHITE)
        displaytext('Exit', 32, screen.get_width() / 2 - 20, screen.get_height() * 3 / 4,
                    WHITE)
        displaytext('Bit Blaster v1.0', 12, screen.get_width() - 80, screen.get_height() - 20,
                    WHITE)
        displaytext('Copyright (C) 2017 ActiveState Software Inc.', 12, screen.get_width() - 80, screen.get_height() - 10,
                    WHITE)
        displaytext(u'\u00bb', 32, screen.get_width() / 2 - 60, screen.get_height() * 3 / 4
                    - 40*menu_selection, WHITE)
        
        # Each game state processes its own input queue in its own way to avoid messy input logic
        for event in event_queue:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                    if menu_selection == 0:
                        menu_selection = 1
                    else:
                        menu_selection = 0
                if event.key == pygame.K_RETURN:
                    if menu_selection == 1:
                        nextState = Play()
                    else:
                        nextState = None
    
        
        return nextState
    


def init_stars(screen):
    """ Create the starfield """
    global stars
    stars = []
    for i in range(MAX_STARS):
    # A star is represented as a list with this format: [X,Y,speed]
        star = [randrange(0,screen.get_width() - 1),
                randrange(0,screen.get_height() - 1),
                choice([1,2,3])]
        stars.append(star)

def move_and_draw_stars(screen):
  """ Move and draw the stars in the given screen """
  global stars
  for star in stars:
    star[1] += star[2]
    # If the star hit the bottom border then we reposition
    # it in the top of the screen with a random X coordinate.
    if star[1] >= screen.get_height():
      star[1] = 0
      star[0] = randrange(0,1279)
      star[2] = choice([1,2,3])
 
    # Adjust the star color acording to the speed.
    # The slower the star, the darker should be its color.
    if star[2] == 1:
      color = (100,100,100)
    elif star[2] == 2:
      color = (190,190,190)
    elif star[2] == 3:
      color = (255,255,255)
 
    # Draw the star as a rectangle.
    # The star size is proportional to its speed.
    screen.fill(color,(star[0],star[1],star[2],star[2]))

# Basic library initialization 
pygame.init()
 
# Configure screen TODO: Should there be a config object or something to contain this?
resolution = (1280, 720)
screen = pygame.display.set_mode(resolution)
 
pygame.display.set_caption("Bit Blaster")

background = pygame.image.load('Cygnus_Wall.jpg')
bgsize = background.get_size()
w,h = bgsize

print w,h

# TODO Get dynamic resolution but width is 1280 for now

aspect = w/h

print aspect
wscale = 1280.0
hscale = wscale/aspect

bgscaled = pygame.transform.scale(background, (1280, int(hscale)))

# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
 
init_stars(screen)

state = Menu()

scrollSpeed = 1
y = -hscale+720
menu_selection = 1

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
    screen.blit(bgscaled,(0,y))
 
    # Here, we clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
 
    # If you want a background image, replace this clear with blit'ing the
    # background image.
 
    # --- Drawing code should go here
    move_and_draw_stars(screen)
 
    state = state.update(screen,event_queue)

    if (state == None):
        done = True
    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
pygame.quit()