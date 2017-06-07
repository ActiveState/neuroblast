from keras.models import Sequential
from keras.layers import Dense, Activation
import numpy as np
from random import randrange
import pygame

from neuralnetwork import NeuralNetwork
from formulae import calculate_average_error, seed_random_number_generator
import parameters

class TrainingExample():
    def __init__(self, inputs, output):
        self.inputs = inputs
        self.output = output

class Brain:

    def __init__(self):
        self.mapShots = {}
        self.mapHits  = {}
        self.trained = False

        self.id = randrange(0,100)
        # create model
        self.model = NeuralNetwork([4, 6, 4, 4, 1])

        # create model
        self.keras = Sequential()

        # Configure the Keras Model
        self.keras.add(Dense(4, input_shape=(4,), activation='relu'))
        self.keras.add(Dense(6, activation='relu'))
        self.keras.add(Dense(4, activation='relu'))
        self.keras.add(Dense(4, activation='relu'))
        self.keras.add(Dense(1, activation='sigmoid'))
        self.keras.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])        
        

    # Keras version of learning
    def train(self):
        # Builds the model based on the dataset to this point
        # Create a n * 4 matrix for the input data
        x = []
        y = []
        for k,v in self.mapShots.iteritems():
            if k in self.mapHits:
                a = list(v)
                x.append(a)
                y.append(self.mapHits[k])
        
        # Fit the data to the model        
        self.keras.fit(x,y,epochs=150,batch_size=10)
        scores = self.keras.evaluate(x, y)
        print("\n%s: %.2f%%" % (self.keras.metrics_names[1], scores[1]*100))

    # "Home grown" Neural Net implementation
    def learn(self):
        # Builds the model based on the dataset to this point
        # Create a n * 4 matrix for the input data
        x = []
        y = []
        cumulative_error = 0
        for k,v in self.mapShots.iteritems():
            # Convert our tuple to a numpy array
            if k in self.mapHits:
                a = list(v)
                cumulative_error += self.model.train(TrainingExample(a,self.mapHits[k]))
        
        # Fit the data to the model        
        self.trained = True        

    def add_shot(self, bullet, dx, dy, du, dv):
        self.mapShots[bullet] = (dx, dy, du, dv)

    def record_hit(self, bullet):
        self.mapHits[bullet] = 1

    def record_miss(self, bullet):
        self.mapHits[bullet] = 0

    def draw(self,screen):
        self.model.draw(screen)