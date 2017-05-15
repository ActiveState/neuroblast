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
 
    def learn(self):
        # Builds the model based on the dataset to this point
        # Create a n * 4 matrix for the input data
        #[list(item) for item in self.mapShots.it]
        x = []
        #y = np.empty((0))
        y = []
        #Step 1, build Numpy Arrays for complete data points
        cumulative_error = 0
        for k,v in self.mapShots.iteritems():
            # Convert our tuple to a numpy array
            if k in self.mapHits:
                a = list(v)
                cumulative_error += self.model.train(TrainingExample(a,self.mapHits[k]))
        
        #print x
        #print y
        print "Finished training, cumulative error was "+str(cumulative_error)
        # Fit the data to the model        
        self.trained = True
        

    def add_shot(self, bullet, dx, dy, du, dv):
        self.mapShots[bullet] = (dx, dy, du, dv)

    def record_hit(self, bullet):
        self.mapHits[bullet] = 1
        #self.learn()

    def record_miss(self, bullet):
        self.mapHits[bullet] = 0
        #self.learn()

    def draw(self,screen):
        #from keras.utils.layer_utils import print_summary
        #print_summary(self.model)
        self.model.draw(screen)