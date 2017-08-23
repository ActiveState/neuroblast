![NeuroBlast](../neuroblast.jpg)
# Overview
NeuroBlast is a classic arcade space shooter with ML-powered AI using TensorFlow. In this short demo intended to demonstrate the accessibility of open source tools for machine learning, you can train an enemy AI using machine learning.

## How it Works

If you want to learn more about how the game works under the hood, and for a tour of the insides, see these two blog posts:

- [Building an ML-Powered AI Using TensorFlow in Go](http://gopherdata.io/post/build_ml_powered_game_ai_tensorflow/) on GopherData.io
- [Building Game AI Using Machine Learning: Working With TensorFlow, Keras, and the Intel MKL in Python](https://www.activestate.com/blog/2017/05/building-game-ai-using-machine-learning-working-tensorflow-keras-and-intel-mkl-python)

You can also [watch](https://www.youtube.com/watch?v=oiorteQg9n0) my GopherCon 2017 Lightning talk about the game or [view the slides](https://github.com/gophercon/2017-talks/tree/master/lightningtalks/PeteGarcin-BuildingMLPoweredGameAIwithTensorFlow).

## Installation - Requirements

Before you start, you will require the following external libraries/tools:

- TensorFlow C libraries for Go version [Instructions](https://www.tensorflow.org/install/install_go)

*Note: TensorFlow for Go is only available of macOS/Linux. Windows is NOT supported.*

For any package dependencies you can either use `dep` or install [ActiveGo 1.8](https://www.activestate.com/activego/downloads) to have an environment with nearly all dependencies already pre-installed.

## MacOS/Linux Setup Instructions

To setup the game to run on MacOS/Linux in Go 1.8:

*Reminder: You must have the TensorFlow C libraries installed as per these [instructions](https://www.tensorflow.org/install/install_go).*

*Note: You must clone the repo into your GOPATH, or add the folder you clone into to your GOPATH in order for `dep ensure` to work.*

1. `git clone https://github.com/ActiveState/neuroblast.git`
2. `cd go`
2. `dep ensure`
3. `go build`
4. Launch the game `./go`

## License

Copyright (C) 2017 ActiveState. Licensed under the MIT License. See LICENSE file for details.

## Credits

Written by Pete Garcin [Twitter](https://twitter.com/rawktron)/[GitHub](https://github.com/rawktron) and Tom Radcliffe.

Gopher Artwork appears courtesy of [Ashley McNamara](https://github.com/ashleymcnamara/gophers).

## Contributing

If you would like to contribute to this project, please visit the Issues tab to see what open issues are available and flagged with Help Wanted. You can also submit a Pull Request with your proposed changes. If they are in response to an issue, please reference the issue in the pull request.


