package main

import (
	"math"
	"math/rand"

	"github.com/faiface/pixel/pixelgl"
)

type synapse struct {
	inputNeuronIndex int
	weight           float64
	signal           float64
	x1, y1, x2, y2   float64
}

type neuron struct {
	x, y     float64
	output   float64
	synapses []synapse
	err      float64
	index    int
}

type layer struct {
	inputLayer    bool
	previousLayer *layer
	x, y          float64
	neurons       []neuron
}

type network struct {
	surface *pixelgl.Canvas
	layers  []layer
}

type example struct {
	input  []float64
	output float64
}

func sigmoid(x float64) float64 {
	return 1 / (1 + math.Exp(-x))
}

func sigmoid_derivative(x float64) float64 {
	return x * (1 - x)
}

func (s *synapse) Draw(surface *pixelgl.Canvas) {
	// TODO: Draw a line segment with width weight
}

func (n *neuron) Draw(surface *pixelgl.Canvas) {

	for _, s := range n.synapses {
		s.Draw(surface)
	}
	//        lo = parameters.left_offset
	//        to = parameters.top_offset
	//        pygame.draw.circle(nsurf,(180,180,200),(self.x+lo, self.y+to),parameters.neuron_radius)
	//        displaytext(str(round(self.output, 2)), 16, self.x + 2+lo, self.y+to, BLACK, nsurf)

}

func (n *neuron) Train(prevLayer *layer) layer {
	for _, s := range n.synapses {
		prevLayer.neurons[s.inputNeuronIndex].err += n.err * s.weight * sigmoid_derivative(n.output)
		s.weight += s.signal * n.err * sigmoid_derivative(n.output)
	}
	return *prevLayer
}

func (n *neuron) Think(prevLayer *layer) {
	activity := 0.0
	for _, s := range n.synapses {
		s.signal = prevLayer.neurons[s.inputNeuronIndex].output
		activity += s.weight * s.signal
		n.output = sigmoid(activity)
	}
}

func (l *layer) Think() {
	for _, neuron := range l.neurons {
		neuron.Think(l.previousLayer)
	}
}

func (l *layer) Draw(surface *pixelgl.Canvas) {
	for _, neuron := range l.neurons {
		neuron.Draw(surface)
	}
}

func (n *network) NewNetwork(surface *pixelgl.Canvas, requested []int) {
	n.surface = surface
	n.layers = make([]layer, len(requested))

	for i := 0; i < len(requested); i++ {
		var newLayer layer

		if i == 0 {
			newLayer.inputLayer = true
			newLayer.previousLayer = nil
			newLayer.y = 20
		} else {
			newLayer.inputLayer = false
			newLayer.previousLayer = &n.layers[i-1]
			newLayer.y = newLayer.previousLayer.y - 120
		}

		x := 10.0
		for j := 0; j < requested[i]; j++ {
			var neuron neuron
			neuron.x = x
			neuron.y = newLayer.y
			neuron.output = 0
			//neuron.synapses = make([]synapse,len(newLayer.previousLayer.neurons))
			neuron.err = 0
			index := 0
			if newLayer.previousLayer != nil {
				for _, input := range newLayer.previousLayer.neurons {
					var synapse synapse
					synapse.inputNeuronIndex = index
					synapse.weight = rand.Float64()
					synapse.signal = 0
					synapse.x1 = x
					synapse.y1 = newLayer.y
					synapse.x2 = input.x
					synapse.y2 = input.y
					neuron.synapses = append(neuron.synapses, synapse)
					index++
				}
			}

			newLayer.neurons = append(newLayer.neurons, neuron)
			x += 20
		}

		n.layers[i] = newLayer
	}
}

func (n *network) Train(data example) float64 {
	err := data.output - n.Think(data.input)
	n.ResetErrors()
	// TODO: What is -1 index in Python
	n.layers[len(n.layers)-1].neurons[0].err = err
	for i := len(n.layers) - 1; i > 0; i-- {
		for _, neuron := range n.layers[i].neurons {
			n.layers[len(n.layers)-1] = neuron.Train(&n.layers[i-1])
		}
	}
	return err
}

func (n *network) ResetErrors() {
	for _, layer := range n.layers {
		for _, neuron := range layer.neurons {
			neuron.err = 0
		}
	}
}

func (n *network) Think(inputs []float64) float64 {
	for _, layer := range n.layers {
		if layer.inputLayer {
			for i := 0; i < len(inputs); i++ {
				n.layers[0].neurons[i].output = inputs[i]
			}
		}
	}
	return n.layers[len(n.layers)-1].neurons[0].output
}

func (n *network) Draw() *pixelgl.Canvas {
	// TODO: Drawing code
	for _, layer := range n.layers {
		layer.Draw(n.surface)
	}

	return n.surface
}
