'''The MIT License (MIT)

Copyright (c) 2017 ActiveState Software Inc.

Written by Tom Radcliffe, Pete Garcin @rawktron

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


from keras.models import Sequential
from keras.layers import Dense, Activation
import numpy as np
from random import randrange
import pygame

from neuralnetwork import NeuralNetwork
from neuralnetwork import *
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
        self.currentState = np.array([list((0,0,0,0))])
        self.weights = []

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
        self.keras.compile(loss='mean_squared_error', optimizer='sgd', metrics=['accuracy'])        

        # Initialize weights array
        for layer in self.keras.layers:
            self.weights.append(layer.get_weights()[0])
        

    # Keras version of learning
    def train(self):
        # Builds the model based on the dataset to this point
        # Create a n * 4 matrix for the input data
        x = []
        y = []
        for k,v in self.mapShots.items():
            # Convert our tuple to a numpy array
            if k in self.mapHits:
                a = list(v)
                x.append(a)
                y.append(self.mapHits[k])
        
        # Fit the data to the model        
        self.keras.fit(x,y,nb_epoch=150,batch_size=10)
        scores = self.keras.evaluate(x, y)
        print("\n%s: %.2f%%" % (self.keras.metrics_names[1], scores[1]*100))

        # Cache trained weights for visualization
        # Element 0 is weights, 1 is biases
        for layer in self.keras.layers:
            self.weights.append(layer.get_weights()[0])

    # "Home grown" Neural Net implementation
    def learn(self):
        # Builds the model based on the dataset to this point
        # Create a n * 4 matrix for the input data
        x = []
        y = []
        cumulative_error = 0
        for k,v in self.mapShots.items():
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

    def draw(self,screen,vizmodel):
        if (vizmodel == 1):
            draw_network(screen, self.keras,self.currentState, self.weights)
        else:
            self.model.draw(screen)