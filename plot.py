import pygame, sys
from pygame.locals import *
import numpy
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg

fig = plt.figure(figsize=[3, 3])
ax = fig.add_subplot(111)
canvas = agg.FigureCanvasAgg(fig)

def plot(data):
   ax.plot(data)
   canvas.draw()
   renderer = canvas.get_renderer()

   raw_data = renderer.tostring_rgb()
   size = canvas.get_width_height()

   return pygame.image.fromstring(raw_data, size, "RGB")