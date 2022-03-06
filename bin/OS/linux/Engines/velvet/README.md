## :chess_pawn: Velvet Chess Engine

![Release](https://img.shields.io/github/v/release/mhonert/velvet-chess)
![Test](https://img.shields.io/github/workflow/status/mhonert/velvet-chess/Test?label=Test&logo=github)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**Velvet Chess Engine** is a UCI chess engine written in [Rust](https://www.rust-lang.org).
> It is based upon my other web-based chess engine [Wasabi](https://github.com/mhonert/chess), which is written in AssemblyScript.

It is currently ranked in the range of 2600-2700 ELO in the Computer Chess Rating Lists (CCRL).

### Usage

In order to play against Velvet, you need a Chess Client with support for the UCI protocol.
The engine was tested with **cutechess-cli** and **PyChess** on Linux and **Arena** and **Banksia** on Windows, but
should also work with other UCI compatible clients.

Alternatively you can also play against my web-based chess engine [Wasabi](https://mhonert.github.io/chess).

### Installation
- Download the suitable executable for your platform (Linux or Windows) and CPU generation from the Releases page
  - *x86_64-modern* - recommended for most recent CPUs from **2013** onwards (requires a CPU with support for the [BMI1](https://en.wikipedia.org/wiki/Bit_Manipulation_Instruction_Sets) instruction sets)
  - *x86_64-popcnt* - for older 64-Bit CPUs, which support the POPCNT instruction, but not BMI1
  - *x86_64-vintage* - for older 64-Bit CPUs, which support neither POPCNT nor BMI1

### License
This project is licensed under the GNU General Public License - see the [LICENSE](LICENSE) for details.

### Attributions
- The [Chess Programming Wiki (CPW)](https://www.chessprogramming.org/Main_Page) has excellent articles and descriptions
- The testers from the [Computer Chess Rating Lists (CCRL)](https://www.computerchess.org.uk/ccrl/) are doing a great job testing lots
  of chess engines for the rating lists
