.........|.........|.........|.........|.........|.........|.........|.........|

Gaviota Chess Engine
Copyright (c) 2000-2014 Miguel A. Ballicora
-------------------------------------------------------------------------------

Gaviota (Spanish word for Seagull) is a chess engine available for Windows, 
Linux, MacOSX, and Android. The code has been written as portable as possible, 
so Gaviota could support other OS in the future.

Gaviota is only an engine, so it needs to be plugged to a proper chess GUI
(Graphic user interface). Current version fully supports the latest Winboard/
Xboard with all its new features. Gaviota also supports the UCI (Universal 
Chess Interface) protocol. Gaviota can be used with some free interfaces such 
as Arena (Windows), Winboard/Xboard, ChessGUI, Scid, and any commercial 
interface that supports those protocols.

Please follow the instructions of your favorite GUI on how to connect engines.

Gaviota is one of the chess engines with more features. It has its own book, 
learning, own endgame table bases, and can use up to sixty four processors or 
cores (SMP), and as mentioned above, supports most OSs all features of 
Winboard II and most of the features of UCI, including MultiPV.

---- Compiles --------------------------------------------------------------------

gaviota-1.0-windows/gaviota-v1.0-win64-general.exe (for 64 bit systems)
gaviota-1.0-windows/gaviota-v1.0-win32.exe (for 32 bit systems)
gaviota-1.0-windows/gaviota-v1.0-win64-AVX.exe (64 bit with AVX capable systems
for instance Sandybridge and up in Intel and Bulldozers and up for AMD)

You can check which is works and it is faster for you with the --benchmark switch
(see below)

---- License for the Engine ---------------------------------------------------

Copyright (C) 2000-2013, Miguel A. Ballicora
 
This software is provided 'as-is', without any express or implied warranty of 
any kind. In no event or circumstance will the author be held liable for any 
damages arising from the use of this software. Anyone is permitted to use this
software, but its distribution is not allowed without the consent of the
author. The origin of this software must not be misrepresented and you must
not claim that you wrote the original software. Modification of the software
is not permitted. (mails to the gmail account: mballicora)

---- Usage --------------------------------------------------------------------

Gaviota can also be executed from the console to be used as an analysis tool,
generate tablebases, or opening books. The following examples assume that 
the name of the engine program is "gaviota" or has been renamed to "gaviota". 
Some of the distributions may have the files named as gaviota-linux32, 
gaviota-win64 etc. to indicate what operating system they are targeting.

If from console the program is executed (do not forget to precede it 
with ./ if you are running in Linux and not installed in /usr/local/bin)

gaviota -v

You will obtain the version number

gaviota

will run as a winboard or UCI engine.

gaviota -x

will be forced to be run as winboard engine

gaviota -s

will be more friendly if you want to use it as a analysis tool from console.
type 'help', and you will get all the available commands. For instance, you
will get

Gaviota v1.0
Copyright (c) 2000-2014 Miguel A. Ballicora
There is NO WARRANTY of any kind
# mode = winboard/xboard
# Type 'screen' for a better output in console mode
# Type 'help' for a list of useful commands

help
use:
help <command>
for more information

?           accepted    adjudicate  analyze     bk          black       
book        bookpgn     bookpgnwb   bookpopmin  clearbrain  clearlearn  
cores       d           display     easy        egtbpath    egtpath     
enddups     epdtest     evaltest    exclude     fen         force       
fritz       go          hard        hasha       hashl       hashp       
hinfo       hint        include     items       kibitz      learnf      
level       log         memory      name        new         nopost      
nowait      nps         option      otim        pause       perft       
perftdiv    ping        playother   post        protover    quit        
ram         random      rejected    remove      reset       result      
score       screen      screenwidth script      sd          see         
set         setboard    smpdepth    smpwidth    sn          st          
stats       tb          tbgen       tbtest      tbuse       tbval       
tbvali      testbail    time        traceroot   transp      uci         
undo        usermove    wait        white       xboard 

---- Command line options -----------------------------------------------------

 -h, --help          print this help
 -v, --version       print version number and exit
 -L, --license       display license information
 -x, --xboard        start engine in xboard/winboard (CECP) mode
 -u, --uci           start engine in UCI mode
 -s, --screen        start engine in optimized screen/console mode
 -i, --ini=FILE      initialization FILE, overrides gaviota.ini.txt
 -S, --script=FILE   script FILE to execute commands in batch
 -e, --test=FILE     test, input is FILE in epd format
 -d, --depth=NUM     test each position with a NUM depth limit
 -n, --nodes=NUM     test each position with with a NUM nodes limit
 -t, --time=NUM      test each position with a search limited to NUM seconds
 -c, --cores=NUM     test with NUM cores/threads
 -r, --relieve=NUM   stop test when NUM consecutive plies agree (default=64)
 -b, --benchmark     run an internal benchmark test

---- Benchmark ----------------------------------------------------------------

gaviota --benchmark or gaviota -b will run a set of 24 positions (Bratko-Kopec
test) and measure the number of nodes and speed in nodes per seconds.
This is important for comparison between different versions and compiles.

---- Book building and special help -------------------------------------------

Then, if you need more help about a specific command you type help <command>
For instance, to know more about bookpgnwb, which is one of the tools to
build books, you type

help bookpgnwb

bookpgnwb <ply_limit> <white_input> <black_input> <bookfile_ouput>
creates a book with the name bookfile_output from the files
white_input (white repertoire) and black_input (black repertoire).
These two input files should be in pgn format. The maximum length
the variations is limited by the number ply_limit
For example:
bookpgnwb 30 white.pgn black.pgn book.bin
Aftewards, the file book.bin should be registered in the ini file

---- Configuration-------------------------------------------------------------

As many native Winboard/Xboard engines, Gaviota can be configured by
modifying a special text file. In this case, it is "gaviota.ini.txt"
The options in this file are self-explanatory. In addition, if you use 
Winboard or Xboard, you can configure the engine options directly from the 
graphical interface. 

If you use Gaviota as a UCI engine, most likely the GUI will provide a menu for
you to change the options.

---- Acknowledgments ----------------------------------------------------------

You can find an updated acknowledgement note at

http://sites.google.com/site/gaviotachessengine/Home/acknowledgments

Enjoy Gaviota, and you may find more support at

http://sites.google.com/site/gaviotachessengine/

Miguel A. Ballicora






 


