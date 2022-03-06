## stash-bot

Stash is a UCI-compliant chess engine developed from scratch. Preferably used
with a GUI like Arena, CuteChess, Fritz, etc.

## Files

The repository consists of the following files:

  * Readme.md, the file you are currently reading.
  * LICENSE, a text file containing the GNU General Public License version 3.
  * src, the directory containing all the source code + a Makefile that can be
    used to compile Stash on Unix-like systems (or Windows if you installed
    MinGW).
  * utils\\unix\_build.sh and utils\\windows\_build.sh, two shell scripts that
    can generate profiled builds for your architecture.
  * utils\\release\_build.sh, a shell script mainly intended for the
    contributors to automatically generate all binaries when creating releases.

## UCI Parameters

Stash supports for now all these UCI options:

  * #### Threads
    Sets the number of cores used for searching a position (defaults to 1).

  * #### Hash
    Sets the hash table size in MB (defaults to 16).

  * #### Clear Hash
    Clears the hash table.

  * #### MultiPV
    Output the best N lines (principal variations) when searching.
    Leave at 1 for best performance.

  * #### Move Overhead
    Assumes a time delay of x milliseconds due to network and GUI overheads.
    Increase it if the engine often loses games on time. The default value
    of 100 ms should be sufficient for all chess GUIs.

## Frequently Asked Questions

  * #### How do I compile this project for my computer ?
    If you are on a Unix-like system, simply go to the src directory from a
    terminal and type:
    ```
    make
    ```
    Special architecture optimizations may be applied by typing:
    ```
    make ARCH=arch_name
    ```
    with `arch_name` being one of the following: x86-64, x86-64-modern or
    x86-64-bmi2. Use `ARCH=unknown` if you don't know your CPU architecture,
    or if you're compiling on a 32-bit machine.

  * #### I do not have a compiler on my machine: how do I do ?
    Compiled binaries for Linux and Windows are available from the "releases"
    page of the project. You can download the binary corresponding to your
    operating system and architecture.

  * #### Which binary should I choose ?
    The latest release should always be the best. The different architecture
    builds are:
      - 64: generic 64-bit build. Should work on all 64-bit processors
        of your operating system.

      - x86_64: x86_64 build. Same as previous one, but enables use of the
        `prefetch` instruction, which places RAM addresses in cache for faster
        access. Should work on almost all 64-bit processors.

      - x86_64-modern: same as previous one, but also enables use of the
        `popcnt` (Population Count) instruction. Should work on all > 2006
        64-bit processors.

      - x86_64-bmi2: same as previous one, but also enables use of the `pext`
        (Parallel Bit Extract) instruction. Should work on all AMD
        processors with Excavator arch or newer, and all Intel processors with
        Haswell arch or newer.
