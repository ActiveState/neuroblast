'''The MIT License (MIT)

Copyright (c) 2017 ActiveState Software Inc.
Copyright (c) 2015 Milo Spencer-Harper

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


import pygame
from math import fabs
from formulae import sigmoid, sigmoid_derivative, random_weight, get_synapse_colour, adjust_line_to_perimeter_of_circle, layer_left_margin
import parameters
from utils import *
import keras.backend as K

# From: https://github.com/philipperemy/keras-visualize-activations
def get_activations(model, model_inputs, print_shape_only=False, layer_name=None):
    activations = []
    inp = model.input

    model_multi_inputs_cond = True
    if not isinstance(inp, list):
        # only one input! let's wrap it in a list.
        inp = [inp]
        model_multi_inputs_cond = False

    outputs = [layer.output for layer in model.layers if
               layer.name == layer_name or layer_name is None]  # all layer outputs

    funcs = [K.function(inp + [K.learning_phase()], [out]) for out in outputs]  # evaluation functions

    if model_multi_inputs_cond:
        list_inputs = []
        list_inputs.extend(model_inputs)
        list_inputs.append(1.)
    else:
        list_inputs = [model_inputs, 1.]

    # Learning phase. 1 = Test mode (no dropout or batch normalization)
    # layer_outputs = [func([model_inputs, 1.])[0] for func in funcs]
    layer_outputs = [func(list_inputs)[0] for func in funcs]
    for layer_activations in layer_outputs:
        activations.append(layer_activations)
    return activations


## Global vars used for vizmodel == 1
surf = pygame.Surface((640,720))
nsurf = pygame.Surface((640,720))
nsurf.fill((255,0,255))
nsurf.set_colorkey((255,0,255))

# Draws a network using the live weights/activations from Keras/Tensorflow
def draw_network(screen, model, model_inputs, weights):
        surf.fill((0,0,0))
        nsurf.fill((255,0,255))
        graph = get_activations(model, model_inputs)
        y = parameters.bottom_margin
        for layer in range(len(graph)):
            x = layer_left_margin(len(graph[layer][0]))
            for node in range(len(graph[layer][0])):
                if (layer+1 != len(graph)):
                    for synapse in range(len(weights[layer+1][node])):
                        lo = parameters.left_offset
                        to = parameters.top_offset
                        x2 = synapse * parameters.horizontal_distance_between_neurons + layer_left_margin(len(graph[layer+1][0]))
                        y2 = y+parameters.vertical_distance_between_layers
                        pygame.draw.line(surf,get_synapse_colour(weights[layer+1][node][synapse]),(int(x+lo), int(y+to)), (int(x2+lo), int(y2+to)),max(1,int(fabs(weights[layer+1][node][synapse]))))
                lo = parameters.left_offset
                to = parameters.top_offset
                pygame.draw.circle(nsurf,(180,180,200),(int(x+lo), int(y+to)),parameters.neuron_radius)
                displaytext(str(round(graph[layer][0][node], 2)), 16, x + 2+lo, y+to, BLACK, nsurf)
                x += parameters.horizontal_distance_between_neurons
            y += parameters.vertical_distance_between_layers
        screen.blit(surf,(640,0))
        screen.blit(nsurf,(640,0)) 

# This home grown neural net was an initial version of the visualization as a POC
# It is convenient for dumping debug data and prototyping, so included here for completeness
# However this code is no longer used.

class Synapse():
    def __init__(self, input_neuron_index, x1, x2, y1, y2):
        self.input_neuron_index = input_neuron_index
        self.weight = random_weight()
        self.signal = 0
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        
    def dump(self,f):
        f.write(str(self.weight)+"\n")

    def draw(self,screen):
        lo = parameters.left_offset
        to = parameters.top_offset
        pygame.draw.line(screen,get_synapse_colour(self.weight),(int(self.x1+lo), int(self.y1+to)), (int(self.x2+lo), int(self.y2+to)),max(1,int(fabs(self.weight))))

class Neuron():
    def __init__(self, x, y, previous_layer):
        self.x = x
        self.y = y
        self.output = 0
        self.synapses = []
        self.error = 0
        index = 0
        if previous_layer:
            for input_neuron in previous_layer.neurons:
                synapse = Synapse(index, x, input_neuron.x, y, input_neuron.y)
                self.synapses.append(synapse)
                index += 1

    def train(self, previous_layer):
        for synapse in self.synapses:
            # Propagate the error back down the synapse to the neuron in the layer below
            previous_layer.neurons[synapse.input_neuron_index].error += self.error * sigmoid_derivative(self.output) * synapse.weight
            # Adjust the synapse weight
            synapse.weight += synapse.signal * self.error * sigmoid_derivative(self.output)
        return previous_layer

    def think(self, previous_layer):
        activity = 0
        for synapse in self.synapses:
            synapse.signal = previous_layer.neurons[synapse.input_neuron_index].output
            activity += synapse.weight * synapse.signal
        self.output = sigmoid(activity)

    def dump(self,f):
        for synapse in self.synapses:
            synapse.dump(f)

    def draw(self,screen,nsurf):
        for synapse in self.synapses:
            synapse.draw(screen)
        
        lo = parameters.left_offset
        to = parameters.top_offset
        pygame.draw.circle(nsurf,(180,180,200),(int(self.x+lo), int(self.y+to)),parameters.neuron_radius)
        displaytext(str(round(self.output, 2)), 16, self.x + 2+lo, self.y+to, BLACK, nsurf)



class Layer():
    def __init__(self, network, number_of_neurons):
        if len(network.layers) > 0:
            self.is_input_layer = False
            self.previous_layer = network.layers[-1]
            self.y = self.previous_layer.y + parameters.vertical_distance_between_layers
        else:
            self.is_input_layer = True
            self.previous_layer = None
            self.y = parameters.bottom_margin
        self.neurons = []
        x = layer_left_margin(number_of_neurons)
        for iteration in range(number_of_neurons):
            neuron = Neuron(x, self.y, self.previous_layer)
            self.neurons.append(neuron)
            x += parameters.horizontal_distance_between_neurons

    def think(self):
        for neuron in self.neurons:
            neuron.think(self.previous_layer)

    def draw(self,screen,nsurf):
        for neuron in self.neurons:
            neuron.draw(screen,nsurf)

    def dump(self,f):
        for neuron in self.neurons:
            neuron.dump(f)

class NeuralNetwork():
    def __init__(self, requested_layers):
        self.surf = pygame.Surface((640,720))
        self.nsurf = pygame.Surface((640,720))
        self.nsurf.fill((255,0,255))
        self.nsurf.set_colorkey((255,0,255))

        self.layers = []
        for number_of_neurons in requested_layers:
            self.layers.append(Layer(self, number_of_neurons))

    def train(self, example):
        error = example.output - self.think(example.inputs)
        self.reset_errors()
        self.layers[-1].neurons[0].error = error
        for l in range(len(self.layers) - 1, 0, -1):
            for neuron in self.layers[l].neurons:
                self.layers[l - 1] = neuron.train(self.layers[l - 1])
        return fabs(error)

    def do_not_think(self):
        for layer in self.layers:
            for neuron in layer.neurons:
                neuron.output = 0
                for synapse in neuron.synapses:
                    synapse.signal = 0

    def think(self, inputs):
        for layer in self.layers:
            if layer.is_input_layer:
                for index, value in enumerate(inputs):
                    self.layers[0].neurons[index].output = value
            else:
                layer.think()
        return self.layers[-1].neurons[0].output

    def dump(self,f):
        for layer in self.layers:
            layer.dump(f)

    def draw(self,screen):
        self.surf.fill((0,0,0))
        self.nsurf.fill((255,0,255))
        for layer in self.layers:
            layer.draw(self.surf,self.nsurf)

        screen.blit(self.surf,(640,0))
        screen.blit(self.nsurf,(640,0))

    def reset_errors(self):
        for layer in self.layers:
            for neuron in layer.neurons:
                neuron.error = 0