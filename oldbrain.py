
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.utils.vis_utils import model_to_dot
import numpy as np
from random import randrange
import pygame


from neuralnetwork import NeuralNetwork
from formulae import calculate_average_error, seed_random_number_generator
import parameters


class Brain:

    def __init__(self):
        self.mapShots = {}
        self.mapHits  = {}
        self.trained = False

        self.id = randrange(0,100)
        # create model
        self.model = Sequential()

        # From what I could gather from the docs, columns came first in the input shape
        self.model.add(Dense(4, input_shape=(4,), activation='relu'))
        self.model.add(Dense(1, activation='sigmoid'))
        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])        
        

    def learn(self):
        # Builds the model based on the dataset to this point
        # Create a n * 4 matrix for the input data
        #[list(item) for item in self.mapShots.it]
        x = []
        #y = np.empty((0))
        y = []
        #Step 1, build Numpy Arrays for complete data points
        for k,v in self.mapShots.iteritems():
            # Convert our tuple to a numpy array
            if k in self.mapHits:
                a = list(v)
                x.append(a)
                #y = np.append(y,self.mapHits[k])
                y.append(self.mapHits[k])
        
        #print x
        #print y
        # Fit the data to the model        
        self.model.fit(x,y,epochs=150,batch_size=10)
        scores = self.model.evaluate(x, y)
        print("\n%s: %.2f%%" % (self.model.metrics_names[1], scores[1]*100))
        self.trained = True
        

    def add_shot(self, bullet, dx, dy, du, dv):
        self.mapShots[bullet] = (dx, dy, du, dv)

    def record_hit(self, bullet):
        self.mapHits[bullet] = 1

    def record_miss(self, bullet):
        self.mapHits[bullet] = 0

    def draw(self,screen):
        #from keras.utils.layer_utils import print_summary
        #print_summary(self.model)
        for l in self.model.layers:
            for n in l.weights:
                print n

        print "------------"

        if self.trained:
            #img = model_to_dot(self.model).create(prog='dot', format='png')
            from keras.utils import plot_model
            plot_model(self.model, to_file='model.png',show_shapes=True)

            graphimg = pygame.image.load('model.png')
            #graphimg = pygame.image.frombuffer(img,(234,352),"RGBA")
        
            screen.blit(graphimg,(640,0))