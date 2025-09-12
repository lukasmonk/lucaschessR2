This is Alaric. It is absolutely freeware with a few restrictions described in the file licens.txt
No guarantee of any kind. Use Alaric on your own risk. 

This package includes:
Licens.txt   		- a few restrictions about the usage - please read it.
readme.txt   		- this file
Alaric707.exe  		- chess engine for the uci protocol 
Alaricwb707.exe		- chess engine for the wb protocol  
Alaric.ini 			- ini file for Alaricwb707.exe 
kpk.dat				- bitbase for KpK endgames. 
Place them all in the same directory as alaric. It is the easy way.
You can put the book somewhere else and give the full path in the settings.

You can download an opening books from http://alaric.fendrich.se/


Inhalt
======
1. What's new?

2. Implemantation and usage

3. Options and parameters

4. Making books

5. Thanks to... 



1. What's new?
==============

- Faster search

- Futility reduction is added

- Fixed a bug that made Alaric resign in dead draw positions

- Fixed a bug that made Shredder and maybe other GUI.s 
  offer a draw after book (Alaric sent eval=0 for every bookmove)
  
- Changed default value for option BookFile to GS_Alaric.book
  (That is Günther Simon's book for Alaric)

- Minor changes in evaluate

- Fixed what made Alaric stop if book wasn't found

- Book code bugs are fixed. Both makebook and selecting book moves.

- Inserted a Log option. Alaric.log is created if it is on

- In winboard mode the input moves are tested for legality


2. Implemantation and usage
===========================
Place the exe files, kpk.dat, alaric.ini and book in the same directory.
N.B! Do not mix the new Alaric.ini file with older versions! Use different directories.


UCI
---

Alaric707.exe  is the uci version
configuration: See Alaric.ini for explanations of the different options


WinBoard
--------

Alaricwb707.exe [-ini filename]
The -ini parameter if you want to use an ini file other than Alaric.ini.  
(For instance alaricwb -ini .\Alaric2.ini or alaricwb -ini "c:/games/alaric/alaric3.ini")
See Alaric.ini for the all the configuration options available.



Some commands in the dos-window
-------------------------------

There a few test/debug commands that can be used in console mode, such as:

d	  (display the current position)
perft x   (count all nodes until searchdepth=x)
perftm x  (count all nodes until depth x from each move in this position)
help      (see all the consol commands that can be used except uci and wb commands)
You can paste a FEN string directly into the dos-window in order to setup a position for analyze

for book makers:
bookmoves (display all bookmoves from current position)
1000test  (generates a bookmove 1000 times from current position and display the result)



3. Options and parmaters
========================
Both the UCI and winboard version are using the same options (when it is possible).

In the file Alaric.ini all the options are explained and the default values can be found.

One way to play around with different configurations for winboard is to use different alaric.ini files.
Start the program with: 
alaricwb703 -ini .\alaric2.ini    in order to use alaric2.ini instead of alaric.ini
For some reason, at my system I have to put .\ in front of the file name. You can use the full path if you prefer.

For the UCI version you can save the different configurations if the GUI have that function.



4. Making Books
===============

This is a simple book based on the much more complicated book in Terra (my previous chess engine).
I also looked at what functions the polyglot book have.
You can create a book from a pgn file. It will use the result tag in order to collect statistics for each move.
It also uses the NAGs !! = "allways use this move", ! = "strong move - use it often", ? and ?? = "never use this move"
if there are more than one !! move from the same position, one of them will be selected by random.

BTW, 2 usefule consol commands when making books: 
bookmoves (the bookmovs at the current position) and 1000test (select bookmoves 1000 times and shows the result)

To create a new book:
makebook -pgn x.pgn -book x.book [-mingames y] [-minscore z] [-maxply v] [-white|-black] 
-pgn and -book is required. All the rest are optional.
Example: makebook -pgn good.pgn -book good.book -minscore 60

-pgn  the pgn-file to use. Full path or only the file name if it is in the sam directory as alaric
-book the created book. Full path or only filename.
-mingames y: remove moves that are not in at least y games from the same position
-minscore z: a value between 0 and 100 representing win% for the move in the games the move is from.
             0 means include all moves, 50 means include moves with at least even result, 100 means all won. 
-maxply v  : exclude every move from games after ply v
-white     : include only white moves
-black     : include only black moves

To merge books:
mergebooks old1.book old2.book new.book

old1.book and old2.book are merged into new.book
If the move is in only one of old1.book and old2.book, it will be copied to new.book
if the move is in both old1 and old2 the statistics will be added into the entry in new.book
except when at lest one of them have a NAG move (!!, !, ? or ??). If so that move will be 
copied to new.book as the same NAG. (Keep the highest value if a conflict. Maybe I will change this later.)


5. Thanks
=========
I have a long list of persons to be thankful to during my long history of chess programming.
All of you who inspired me and teached me by sharing your knowledge and thoughts. 
I will not give that list here....

I would also like to thank all the rating list creators and TD's that set up good tournaments and lists.
You are the chess programmers best friends! 

A special thanks for this release to you who gave me good advices, useful feedback and found bugs:
- Eelco de Groot  
- Gábor Szots
- Ted Summers
- Günther Simon (author of a new Alaric book)

I probably forgot someone here. Please forgive my memory....
I now and then get nice letters with error reports or suggestions from alla parts of the world. 
Great! Thanks!