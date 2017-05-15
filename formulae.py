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