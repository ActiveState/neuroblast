# Overview
NeuroBlast is a classic arcade space shooter with ML-powered AI using TensorFlow. In this short demo intended to demonstrate the accessibility of open source tools for machine learning, you can train an enemy AI using machine learning.

## Installation - Requirements

Before you start, you will require the following external libraries/tools:

- Python 3.5 or Go 1.8
- MongoDB server [Download](https://www.mongodb.com/download-center?jmp=nav#community)
- TensorFlow C libraries for Go version [Instructions](https://www.tensorflow.org/install/install_go)

*Note: TensorFlow for Go is only available of macOS/Linux. Windows is NOT supported.*

For any package dependencies, you can either install them via pip/dep or you can also install [ActivePython 3.5.3](https://www.activestate.com/activepython/downloads) or [ActiveGo 1.8](https://www.activestate.com/activego/downloads) to have an environment with nearly all dependencies already pre-installed.

## Windows Setup Instructions

To setup the game to run on Windows in Python 3:

1. `git clone https://github.com/ActiveState/boothgame.git`
2. `pip3 install -r requirements.txt`
3. Launch `rungame.cmd` (which will launch the Mongo server).

## MacOS/Linux Setup Instructions

To setup the game to run on MacOS/Linux in Python 3:

1. `git clone https://github.com/ActiveState/boothgame.git`
2. `pip3 install -r requirements.txt`
3. Launch Mongo server: `mongod --dbpath <path to data/db>`
4. Launch the game `python3 game.py`

To setup the game to run on MaOS/Linux in Go 1.8:

*Reminder: You must have the TensorFlow C libraries installed as per these [instructions](https://www.tensorflow.org/install/install_go).*

1. `git clone https://github.com/ActiveState/boothgame.git`
2. `cd go`
2. `dep ensure`
3. `go build`
4. Launch the game `./go`

## Command Line Arguments



## Controls

## License

## Contributing
