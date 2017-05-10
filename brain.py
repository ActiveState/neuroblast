
from keras.models import Sequential
from keras.layers import Dense, Activation
import numpy as np

class Brain:

    def __init__(self):
        self.mapShots = {}
        self.mapHits  = {}
        # create model
        self.model = Sequential()
        # From what I could gather from the docs, columns came first in the input shape
        self.model.add(Dense(6, input_shape=(4,), activation='relu'))
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
        

    def add_shot(self, bullet, dx, dy, du, dv):
        self.mapShots[bullet] = (dx, dy, du, dv)

    def record_hit(self, bullet):
        self.mapHits[bullet] = 1

    def record_miss(self, bullet):
        self.mapHits[bullet] = 0

