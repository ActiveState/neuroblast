
from keras.models import Sequential
from keras.layers import Dense, Activation

class Brain:

    def __init__(self):
        self.mapShots = {}
        self.mapHits  = {}

    def add_shot(self, bullet, dx, dy, du, dv):
        self.mapShots[bullet] = (dx, dy, du, dv)

    def record_hit(self, bullet):
        self.mapHits[bullet] = 1

    def record_miss(self, bullet):
        self.mapHits[bullet] = 0


