******************************************************************************

CT800 project - an ARM Cortex M4 based chess computer

This project is licenced under the GNU General Public License version 3
or any later version of the License. See COPYING.txt for the full text
of the License.

******************************************************************************

Supported platforms:
- STM32 embedded system microcontroller (dedicated hardware)
- Windows  (UCI)
- PC-Linux (UCI)
- Android  (4.1 or higher running on ARMv7-A or higher; UCI)
- RaspPi   (UCI)
- macOS    (UCI, for both x86 and ARM based Macs)

Note: unfortunately, Apple iOS cannot enjoy support because the terms of the
app store are incompatible with the GPL, and iOS does not allow installations
without app store. This would also apply to potential third party iOS ports
of the CT800 engine.

Note: UCI means "Universal Chess Interface", which is a widespread protocol
that connects chess engines and chess GUIs (Graphical User Interface). The
CT800 UCI version features complete UCI support except for pondering.

******************************************************************************

The contents of the different directories within this project:

binaries/       contains pre-built binaries.

                STM32: the CT800 firmware for the embedded target platform in
                .hex and .bin format.

                The UCI engine binaries are supplied for:
                Windows (x86-64, x86, ARM-64 and ARM-32)
                Android-ARM (32 and 64 bit)
                Android-x86 (32 and 64 bit)

                No pre-built binary supplied for:
                PC-Linux, Rasberry Pi, macOS

                The PNG files in the Logo-Images directory are for logo use
                e.g. in the Arena GUI.

documentation/  contains relevant project documentation, including build
                and installation instructions for the software (in
                doc_software), top level diagrams of the software and build
                instructions for the dedicated hardware.

source/         contains the source text and build directory (GPLv3+).
                for the book data text file itself, see the book tool.

source/application/
                contains the version for STM32 bare metal.

source/application-uci/
                contains the UCI version for Windows, Linux and Android.

tools/          contains tools that are either necessary for a firmware
                build or for modifying certain parts of the firmware:

tools/crctool/  contains the CRC tool that appends a CRC32 to a successful
                STM32 firmware build (GPLv3+).
tools/booktool/ contains the opening book compiler that generates the
                binary opening book format from the line based text file
                and the book data text file itself (GPLv3+).
tools/kpk/      contains the endgame table generator that generates the
                binary endgame table for "king+pawn vs. king"
                (BSD 2-clause).

******************************************************************************

Necessary tool chain for generating the UCI compatible PC/Android version:
- Windows: GCC for the host system.
- Linux:   GCC (including pthreads) for the host system. Use the build scripts
           under source/application-uci/ . Tested under Knoppix-64 8.6.1.
- Andoid:  Clang ARM cross-compiler (Android NDK).
- Raspi:   GCC on Raspberry Pi and using the Linux build scripts or cross
           compile from Windows using the Windows toolchain for Raspberry Pi.
- macOS:   Clang for the host system.

******************************************************************************

Necessary tool chain for generating the STM32 bare metal firmware:

Windows: GCC-ARM-NONE-EABI; CoIDE is optional. If you want to compile
the book tool and the CRC tool yourself, you will also need e.g. MingW,
but the EXE files are already supplied.

Linux: GCC-ARM-NONE-EABI. Besides, also GCC-x86 for the host system,
and that one should generate 32 bit binaries (use multilib) in order to
be as close to the target build as possible.

Target system installation of the firmware using the JTAG interface of
the target board (not scope of this project):

Windows: OpenOCD (GPLv2+) or CoIDE v1.78 (propietary, without charge)

Linux: OpenOCD (GPLv2+)
(see e.g. http://regalis.com.pl/en/arm-cortex-stm32-gnulinux/ )

******************************************************************************

Note: the firmware source code, the tools and the documentation in this
project ZIP archive are matching each other. However, you cannot mix
different versions of the project ZIP file. E.g. the opening book compiler
supplied with V1.01 of this project is not compatible with V1.20 and vice
versa.


Rasmus Althoff, August 2023

******************************************************************************
