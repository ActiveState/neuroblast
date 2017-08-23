![NeuroBlast](neuroblast.jpg)
# Overview
NeuroBlast is a classic arcade space shooter with ML-powered AI using TensorFlow. In this short demo intended to demonstrate the accessibility of open source tools for machine learning, you can train an enemy AI using machine learning.

## How it Works

If you want to learn more about how the game works under the hood, and for a tour of the insides, see these two blog posts:

- [Building an ML-Powered AI Using TensorFlow in Go](http://gopherdata.io/post/build_ml_powered_game_ai_tensorflow/) on GopherData.io
- [Building Game AI Using Machine Learning: Working With TensorFlow, Keras, and the Intel MKL in Python](https://www.activestate.com/blog/2017/05/building-game-ai-using-machine-learning-working-tensorflow-keras-and-intel-mkl-python)

You can also [watch](https://www.youtube.com/watch?v=oiorteQg9n0) my GopherCon 2017 Lightning talk about the game or [view the slides](https://github.com/gophercon/2017-talks/tree/master/lightningtalks/PeteGarcin-BuildingMLPoweredGameAIwithTensorFlow).

## Installation - Requirements

Before you start, you will require the following external libraries/tools:

- Python 3.5 or Go 1.8
- MongoDB server [Download](https://www.mongodb.com/download-center?jmp=nav#community)
- TensorFlow C libraries for Go version [Instructions](https://www.tensorflow.org/install/install_go)

*Note: TensorFlow for Go is only available of macOS/Linux. Windows is NOT supported.*

For any package dependencies, you can either install them via pip/dep or you can also install [ActivePython 3.5.3](https://www.activestate.com/activepython/downloads) or [ActiveGo 1.8](https://www.activestate.com/activego/downloads) to have an environment with nearly all dependencies already pre-installed.

## Windows Setup Instructions

To setup the game to run on Windows in Python 3:

1. `git clone https://github.com/ActiveState/neuroblast.git`
2. `pip3 install -r requirements.txt`
3. Launch `rungame.cmd` (which will launch the Mongo server).

## MacOS/Linux Setup Instructions

To setup the game to run on MacOS/Linux in Python 3:

1. `git clone https://github.com/ActiveState/neuroblast.git`
2. `cd neuroblast`
3. `mkdir db`
2. `pip3 install -r requirements.txt`
3. Launch Mongo server: `mongod --dbpath ./db`
4. Launch the game `python3 game.py`

*Note: If you previously had Keras installed on your machine, and had run it using a different backend, make sure you configure your Keras backend to run using TensorFlow by following these [instructions](https://keras.io/backend/).*

To setup the game to run on MacOS/Linux in Go 1.8:

*Reminder: You must have the TensorFlow C libraries installed as per these [instructions](https://www.tensorflow.org/install/install_go).*

*Note: You must clone the repo into your GOPATH, or add the folder you clone into to your GOPATH in order for `dep ensure` to work.*

1. `git clone https://github.com/ActiveState/neuroblast.git`
2. `cd go`
2. `dep ensure`
3. `go build`
4. Launch the game `./go`

## Command Line Arguments

There are a number of options available when running the game from Python:

- `-n` changes the Neural Network model from using TensorFlow to using the "home grown" network model which is useful for prototyping/debugging.
- `-f` launches the game in full screen.
- `-v` changes the visualization method to use raw Keras/TensorFlow values. Warning: This is much slower!

*Note: These options are not available in the Go version.*

## Controls

### Movement

Control your ship with the arrow keys or the left-analog stick with a gamepad.

### Firing

Use either `SPACE` or the A button on your gamepad to fire. You can hold the button down for continuous fire.

## Known Issues

- Collision is not pixel-perfect
- In the Python version, being hit will slow down your rate of movement
- You can fly through the enemy ships with your ship (no collision between enemy ships/hero ship)
- Some gamepad configurations may not work
- Menu navigation with gamepad is inconsistent

## License

Copyright (C) 2017 ActiveState. Licensed under the MIT License. See LICENSE file for details.

## Credits

Written by Pete Garcin [Twitter](https://twitter.com/rawktron)/[GitHub](https://github.com/rawktron) and Tom Radcliffe.

Gopher Artwork appears courtesy of [Ashley McNamara](https://github.com/ashleymcnamara/gophers).

## Contributing

If you would like to contribute to this project, please visit the Issues tab to see what open issues are available and flagged with Help Wanted. You can also submit a Pull Request with your proposed changes. If they are in response to an issue, please reference the issue in the pull request.


