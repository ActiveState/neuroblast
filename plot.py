import pygame, sys
from pygame.locals import *
import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg

dpi = 80
margin = 0.05 # (5% of the width/height of the figure...)
xpixels, ypixels = 640, 360

# Make a figure big enough to accomodate an axis of xpixels by ypixels
# as well as the ticklabels, etc...
figsize = (1 + margin) * ypixels / dpi, (1 + margin) * xpixels / dpi

fig = plt.figure(figsize=figsize, dpi=dpi)
ax = fig.add_subplot(111)

#fig, ax = plt.subplots()
canvas = agg.FigureCanvasAgg(fig)
im = ax.imshow(np.random.random((xpixels, ypixels)))

def plot(data):
   #ax.plot(data)
   im.set_data(data)
   canvas.draw()
   renderer = canvas.get_renderer()

   raw_data = renderer.tostring_rgb()
   size = canvas.get_width_height()

   return pygame.image.fromstring(raw_data, size, "RGB")