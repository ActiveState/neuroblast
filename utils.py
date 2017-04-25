import pygame
import pygame.freetype
from random import randrange, choice

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Acceleration in pixels per second
SHIP_ACC = 400

## Constants
MAX_STARS = 250

def loadfont(size):
    global font
    font = pygame.freetype.Font('./De Valencia (beta).otf', size)


# Utility functions
def displaytext(text, fontsize, x, y, color, surface):
    global font
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
        star = [randrange(0,screen.get_width()/2 - 4),
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
      star[0] = randrange(0,636)
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
