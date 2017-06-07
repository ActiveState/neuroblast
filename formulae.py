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

from numpy import exp, random
from math import atan, sin, cos
import parameters


def sigmoid(x):
    return 1 / (1 + exp(-x))


def sigmoid_derivative(x):
    return x * (1 - x)


def seed_random_number_generator():
    random.seed(1)


def random_weight():
    return 2 * random.random() - 1


def get_synapse_colour(weight):
    if weight > 0:
        return 0, 255, 0
    else:
        return 255, 0, 0


def adjust_line_to_perimeter_of_circle(x1, x2, y1, y2):
    angle = atan((x2 - x1) / float(y2 - y1))
    x_adjustment = parameters.neuron_radius * sin(angle)
    y_adjustment = parameters.neuron_radius * cos(angle)
    return x1 - x_adjustment, x2 + x_adjustment, y1 - y_adjustment, y2 + y_adjustment


def layer_left_margin(number_of_neurons):
    return parameters.left_margin + parameters.horizontal_distance_between_neurons * (parameters.number_of_neurons_in_widest_layer - number_of_neurons) / 2


def calculate_average_error(cumulative_error, number_of_examples):
    if cumulative_error:
        return round(cumulative_error * 100 / number_of_examples, 2)
    else:
        return None