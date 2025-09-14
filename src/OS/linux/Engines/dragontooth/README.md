[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)
[![Documentation](https://img.shields.io/badge/Documentation-GoDoc-green.svg)](https://godoc.org/github.com/dylhunn/dragontooth)

Dragontooth | Dylan D. Hunn
===========================

**This project is currently in beta state.**

Dragontooth is a fast, UCI-compliant chess engine written in Go. The successor to my [previous engine](https://github.com/dylhunn/sabertooth-source), Dragontooth is the first highly-parallel Go chess engine. It uses state-of-the-art techniques, including magic bitboards, fully-legal move generation, highly parallel search, and automatic parameter tuning.

Additionally, Dragontooth has some unique features. It is 100% modular, such that the [move generator and associated utilities](https://github.com/dylhunn/dragontoothmg) are packaged as a library. Moreover, the code is written with a focus on readability, so it can serve as a "reference" engine.

**Where can I download compiled binaries/executables?**
=======================================================

Compiled versions for several platforms are available in [the releases section](https://github.com/dylhunn/dragontooth/releases). This repo contains the source code.

Repo summary
============

Here is a summary of the important files and folders in the repo:

| **Package**         | **Description**                                                                                                                                         |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| main       | This is the UCI entrypoint that handles communication with the GUI. |
| evaluate       | This package handles board evaluation. |
| ttable      | This package implements the transposition table. |
| search      | This package provides the primary alpha-beta search functions. |

Building Dragontooth from source
================================

This project requires Go 1.9. As of the time of writing, 1.9 is still a pre-release version. You can get it by cloning the official [Go Repo](https://github.com/golang/go), and building it yourself.

To build Dragontooth from source, make sure your `GO_PATH` environment variable is correctly set, and install it using `go get`:

    go get github.com/dylhunn/dragontooth

Alternatively, you can clone it yourself, but this will require you to clone [the dependency](https://github.com/dylhunn/dragontoothmg) as well, and configure them at the correct paths:

    git clone https://github.com/dylhunn/dragontooth.git
    git clone https://github.com/dylhunn/dragontoothmg.git

Documentation
=============

You can find the documentation [here](https://godoc.org/github.com/dylhunn/dragontooth).