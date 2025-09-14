1. Introduction
---------------

Rocinante is a free UCI chess engine. 
Rocinante is a program to experiment with different visions and 
algorithms applied to the game of chess.
The main purpose of this engine is not the attainment of the highest 
Elo rating possible, but to provide alternative algorithms that could 
be attractive to other uses of a chess program.
After publishing a new engine based on a new algorithm, 
inevitably, it becomes the reference for that algorithm.
That's why I will try to improve on each delivery.

Rocinante 1 was the first approach to this idea by using the algorithm 
probability based B star (PB*). Delivery was made as soon as it was able 
to fight with minimal success with TSCP. When I write these words,
TSCP 1.81 has a rating of 1707 and Rocinante 1.01 of 1560. (CCRL 40/4)
The evaluation function (UFO) is the simplest possible.
(Material + Piece square tables). And implemented as originally 
posted by Tomasz Michniewski on the Polish chess programming discussion 
list (progszach). This first version already includes MP. And it has been 
successfully migrated to linux, android, and in 64 bits platforms win64, linux.

Rocinante 2.0 is a cuasi complete rewrite of Rocinante.
There have been some refactoring and changes to optimize the 
execution of the program without significantly altering the 
underlying algorithms.
The version 1.01 was bitboard and this new release uses mailbox.
Some code has been stolen from Simplex (Zobrist, hashtable, PVS etc).
A new algorithm has been added. MCTS_AB: Monte Carlo Tree Search alpha beta.
Monte Carlo programs are successful in the game of Go, but are notoriously 
ineffective in chess. I intend to add this algorithm to verify the veracity
of these claims.
I've added a new evaluation function. And a SeeEval that replaces a quiesce search.
This is configured using UCI protocol options.

2. UCI Options.
---------------
>uci
id name Rocinante 2.0
id author Antonio Torrecillas
option name cpus type spin default 1 min 0 max 256
option name threads type spin default 1 min 0 max 256
option name klevel type spin default 1 min 0 max 1
option name mcts_ab type check default true
option name probedepth type spin default 1 min -1 max 10
uciok

Option cpus and threads control the number of worker threads.

Option mcts_ab control the main algorithm.
    true -> use of mcts_ab Monte Carlo Tree Search
	false -> use PB* Probability Based B star.

Option klevel control the evaluation function
	0 -> UFO material + Piece square tables.
	1 -> Material + development + PST + Mobility + ...

Option probedepth
Both MCTS_AB and PB* have an alpha beta algorithm as a replacement 
for a static evaluation. Probe Depth control the depth of this alpha beta.
	-1 -> no alpha beta is used. Instead a static exchange evaluation is used.
	0  -> quiesce evaluation. (MVLA).No checks.
	1  -> one ply + quiesce.
	2  -> two ply alpha beta + quiesce.
	3  -> 3 plys AB+quiesce.
	4 and up -> iterative deepening + LMR + nullmove etc.

The limiting factor here is the fact that the refinements that characterize modern 
programs are only visible beyond the third ply.(ID, IID, LMR, Null Move).

As a general rule the greater depth probe better.But there is a minimum number 
of expand by time control. (112 expands for PB*).

3. UCI Output.
--------------

Both PB* as MCTS are characterized by touring the search tree to a leaf and expand
this node. The algorithm moves through successive Expands. In a program with Iterative 
Deepening we have two parameters: the depth and the visited nodes. In Rocinante only 
expands. In Rocinante output, nodes correspond to the number of performed Expands.
The depth and seldepth are computed by the number of moves in the PV.

For example
>position startpos
>go movetime 1000
info depth 1 seldepth 1 pv d2d4  score cp 11 nodes 1 nps 500 hashfull 0 time 2
info depth 2 seldepth 2 pv e2e4 d7d5  score cp 21 nodes 4 nps 500 hashfull 0 time 8
info depth 2 seldepth 2 pv g1f3 d7d5  score cp 19 nodes 8 nps 444 hashfull 0 time 18
info depth 3 seldepth 3 pv e2e4 d7d5 b1c3  score cp 13 nodes 9 nps 450 hashfull 0 time 20
info depth 2 seldepth 2 pv b1c3 e7e5  score cp 19 nodes 10 nps 454 hashfull 0 time 22
info depth 3 seldepth 3 pv e2e4 d7d5 b1c3  score cp 13 nodes 11 nps 458 hashfull 0 time 24

an NPS of 500 means 500 expands per second. We can see that the depth can go up and down
as the engine think. There is no depth/iteration concept.

4.UCI: go fixed depth.
----------------------
To emulate the go depth command of UCI Rocinante 2 use the following rule:

   go depth 1 -> 18 expands.
   go depth 2 -> 54 expands.
   ...
   go depth n -> 6 * 3^n


5. Known bugs
-------------
The MP in linux platform is broken.

6. Web Home
-----------
for updates please visit
http://sites.google.com/site/barajandotrebejos/

//    Copyright 2009-2012 Antonio Torrecillas Gonzalez
//
//    This file is part of Rocinante.
//
//    Rocinante is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    Rocinante is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with Rocinante.  If not, see <http://www.gnu.org/licenses/>
//
