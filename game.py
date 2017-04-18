# game.py
# Eventually will hold all the core game functions, game loop etc.
# But none of the other stuff
# For now it will catch all everything

# Excuse the mess, it's under construction

from __future__ import division
import pygame
import pygame.freetype
from random import randrange, choice
import math

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, color, direction, speed, container):
        pygame.sprite.Sprite.__init__(self, container)
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.col = list(color)
        for i in range(5, 0, -1):
            self.col[0] = color[0] * float(i) / 5
            self.col[1] = color[1] * float(i) / 5
            self.col[2] = color[2] * float(i) / 5
            pygame.draw.circle(self.image, tuple(self.col), (5, 5), i,
                               0)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  # + direction[1]*20)
        self.direction = direction
        self.speed = speed

    def update(self):
        (x, y) = self.rect.center
        y += self.direction[1] * self.speed
        x += self.direction[0] * self.speed
        self.rect.center = (x, y)
        # TODO make the bounds constants or dynamic
        if y <= 0 or y >= 720 or x <= 0 or x >= 1280:
            self.kill()

class Killable(pygame.sprite.Sprite):
    def __init__(self):
        super(Killable, self).__init__()

        self.health = 100
    def TakeDamage(self, damage):
        #Take damage fuc tion
        self.health -= damage
        if self.health < 0:
            # DEAD
            self.Die()
    def Die(self):
        # DO something
        # Trigger Particle or something
        self.kill()

class Enemy(Killable):
    def __init__(self):
        # Enemy specific stuff here
        self.BulletLayer = 1
        self.x = 640
        self.y = 0
        self.velx = 0
        self.vely = 1       # wish there was a vector class
        self.bullets = pygame.sprite.Group()
    def update(self, screen, event_queue, dt):
        global spritesheet

        self.x = 600+math.sin(self.y/45) * 80

        self.y += self.vely

        rect = pygame.Rect((380, 0, 94, 100))
        screen.blit(spritesheet, (self.x, self.y), rect)

        self.bullets.update()
        self.bullets.draw(screen)


class Player(Killable):
    def __init__(self):
        # Plauer specifc init stuff here
        self.BulletLayer = 2
        self.x = 500
        self.y = 500
        self.velx = 0
        self.vely = 0       # wish there was a vector class
        self.bullets = pygame.sprite.Group()

    def update(self, screen, event_queue, dt):
        global spritesheet

        rect = pygame.Rect((0, 0, 94, 100))
        screen.blit(spritesheet, (self.x, self.y), rect)

        self.bullets.update()
        self.bullets.draw(screen)

        keys=pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.velx = -SHIP_ACC
        if keys[pygame.K_RIGHT]:
            self.velx = SHIP_ACC
        if keys[pygame.K_UP]:
            self.vely = -SHIP_ACC
        if keys[pygame.K_DOWN]:
            self.vely = SHIP_ACC
        if keys[pygame.K_SPACE]:
            bul = Bullet(self.x,self.y,BLUE,(0,-1),20,self.bullets)

        '''        # Cap speed
        if self.velx > SHIP_MAX:
            self.velx = SHIP_MAX
        elif self.velx<-SHIP_MAX:
            self.velx = -SHIP_MAX
        if self.vely > SHIP_MAX:
            self.vely = SHIP_MAX
        elif self.vely<-SHIP_MAX:
            self.vely = -SHIP_MAX

        # Decelerate
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and self.velx != 0:
            sign = 1
            if (self.velx<0):
                sign = -1
            self.velx -= SHIP_ACC * 2 * sign
            if (sign==1 and self.velx<0):
                self.velx = 0
            elif (sign==-1 and self.velx>0):
                self.velx = 0

        if not (keys[pygame.K_UP] or keys[pygame.K_DOWN]) and self.vely != 0:
            sign = 1
            if (self.vely<0):
                sign = -1
            self.vely -= SHIP_ACC * 2 * sign
            if (sign==1 and self.vely<0):
                self.vely = 0
            elif (sign==-1 and self.vely>0):
                self.vely = 0
            
        '''
        if not (keys[pygame.K_UP] or keys[pygame.K_DOWN]):
            self.vely = 0
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            self.velx = 0

        self.x += self.velx
        self.y += self.vely


 
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

## Constants
MAX_STARS = 250

# Acceleration in pixels per second
SHIP_ACC = 25

# Utility functions
def displaytext(text, fontsize, x, y, color, surface):
    font = pygame.freetype.Font('./De Valencia (beta).otf', fontsize)
    texcol = pygame.Color(*color)
    text = font.render(text, texcol)
    textpos = text[0].get_rect(centerx=x, centery=y)
    surface.blit(text[0], textpos)

def init_stars(screen):
    """ Create the starfield """
    global stars
    stars = []
    for i in range(MAX_STARS):
    # A star is represented as a list with this format: [X,Y,speed]
        star = [randrange(0,screen.get_width() - 1),
                randrange(0,screen.get_height() - 1),
                choice([2,3,4])]
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
      star[2] = choice([2,3,4])
 
    # Adjust the star color acording to the speed.
    # The slower the star, the darker should be its color.
    if star[2] == 2:
      color = (100,100,255)
    elif star[2] == 3:
      color = (190,190,190)
    elif star[2] == 4:
      color = (255,255,255)
 
    # Draw the star as a rectangle.
    # The star size is proportional to its speed.
    screen.fill(color,(star[0],star[1],star[2],star[2]))

### -------------------------------------

### GAME ENTITY CLASSES

# GameState object will return a new state object if it transitions
class GameState(object):
    def update(self, screen, event_queue, dt):
        return self


class Play(GameState):
    def __init__(self):
        self.player = Player()
        self.enemy = Enemy()

    def update(self, screen, event_queue, dt):
        self.player.update(screen, event_queue, dt)
        self.enemy.update(screen, event_queue, dt)
        return self

# Draws the menu on screen.
# This is a class that is just instantiated
# While that object exists, it processes stuff
# Only one "GameState" object can exist at one time
class Menu(GameState):
    def update(self, screen, event_queue, dt):
        nextState = self
        global menu_selection
        displaytext('Play', 32, screen.get_width() / 2 - 20, screen.get_height() * 3 / 4
                    - 40, WHITE, screen)
        displaytext('Exit', 32, screen.get_width() / 2 - 20, screen.get_height() * 3 / 4,
                    WHITE, screen)
        displaytext('Bit Blaster v1.0', 12, screen.get_width() - 80, screen.get_height() - 20,
                    WHITE, screen)
        displaytext('Copyright (C) 2017 ActiveState Software Inc.', 12, screen.get_width() - 80, screen.get_height() - 10,
                    WHITE, screen)
        displaytext(u'\u00bb', 32, screen.get_width() / 2 - 60, screen.get_height() * 3 / 4
                    - 40*menu_selection, WHITE, screen)

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

## --------------------------------

### GLOBAL GAME INIT AND MAIN LOOP
# Basic library initialization
pygame.init()

# Configure screen TODO: Should there be a config object or something to contain this?
resolution = (1280, 720)
screen = pygame.display.set_mode(resolution)

pygame.display.set_caption("Bit Blaster")

spritesheet = pygame.image.load("spaceship_sprite_package_by_kryptid.png")
spritesheet.set_colorkey(spritesheet.get_at((0, 0)))

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
