             Ufim Version 8.02 (July 2006) by N.Khasanov

  Ufim 8.02 is a chess program ("engine") that works with Winboard.
Winboard is a known free Windows program providing graphic user interface (GUI)
for chess programs. Winboard was written by Tim Mann and can be downloaded
from http://www.tim-mann.org/chess.html
 
  Ufim 8.02 supports both Winboard protocol and UCI protocol.
Therefore Ufim can also be used in many other GUIs. In Winboard mode Ufim
works with Arena, Winboard, Chessmaster etc. In UCI mode Ufim works with Fritz,
Shredder etc.  Of course, Ufim can work alone, but it is not recommended.

  In UCI mode Ufim 8.02 also supports Chess960 (Fischer Random Chess).

  Ufim 8.02 has many possibilities such as various time levels, "move now", 
editing of positions, analyze mode, resign mode, retraction of moves etc.
It recognizes threefold repetition, 50-move rule, draw by insufficient 
material etc. Ufim 8.02 can think ("ponder") at the opponent's time.
Ufim was written in Pascal language.

  The strength rating of Ufim 8.02 is higher than 2500 Elo points.
You can weaken Ufim using the "weak" parameter in the configuration file.
In UCI mode you can set any Elo rating in the range 700..2000 for weakening.

  Ufim 8.02 uses a very small "opening book" and does not use such huge files
as endgame table bases. Therefore the system requirements are small:
any computer with Windows'95 or later, 300 kb of memory and 120 kb on disk.
Of course, your GUI needs memory too.

  Ufim 8.02 may use a configuration file (ufim802.ini) for Winboard mode.
If you want to get a special log file, you can write log=1 in that file. 
If Ufim 8.02 must not resign, write resign=0.
Also if your computer has enough memory, you can set the hash size to
a non-zero value to increase the thinking strength of Ufim.
If Ufim802.ini does not exist, log=0, resign=1, book=1, learn=1, weak=0,
weakdelay=1 and hashsize=0 are assumed.

  If you want to use Winboard, it is necessary to install Winboard and read
its helpfile before the installation of Ufim 8.02. The Ufim802.zip archive
contains four files:
       ufim802.exe - the program
       ufim802.bok - the opening book
       ufim802.ini - the configuration file
       readme.txt - this file.
Extract these files to your Winboard directory (or to another directory,
for example, C:\UFIMDIR\ ). Add to winboard.ini file the following lines:
     ufim802 /fd="c:\ufimdir"
     ufim802 /sd="c:\ufimdir"
into the sections /firstChessProgramNames=" " and
/secondChessProgramNames=" " correspondingly.
Run winboard.exe and enjoy!

  Ufim 8.02 can be freely used for all non-commercial purposes.

  UFIM 8.02 IS DISTRIBUTED "AS IS".  NO WARRANTY OF ANY
KIND IS EXPRESSED OR IMPLIED.  YOU USE AT YOUR OWN RISK.
THE AUTHOR WILL NOT BE LIABLE FOR DATA LOSS, DAMAGES, LOSS
OF PROFITS OR ANY OTHER KIND OF LOSS WHILE USING OR MISUSING
THIS SOFTWARE.

  Acknowledgments.
  I used many ideas from Bob Hyatt, Tom Kerrigan, Dusan Dobes, Fabien Letouzey
and other programmers.  Also big thanks to Leo Dijksman, Sergey Kudryavtsev,
Frank Quisinsky, Heinz van Kempen, George Lyapko, Slobodan R. Stojanovic,
Igor Gorelikov, Odd Gunnar Malin, Anton Maydell, Claude Dubois, Milorad Madjar,
Dieter Buerssner and other people who kindly helped me in improving this engine.

  If you find an error or a bug, please write to salavata@mail.ru
