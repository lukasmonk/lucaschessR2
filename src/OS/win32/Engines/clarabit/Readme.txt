 Clarabit Chess Engine by Salvador Pallares, Spain.
http://sapabe.googlepages.com


License and Warrranty
=====================
Clarabit  is free to be used and freely distributed without any restriction except modifying
its content. It has been heavily tested without causing any problem. 
Use this program as your own risk. It came with absolutely no warranties. 
In no event will the author be held liable for any damages arising from the use of this program.


Configuration
=============
Engine configuration is mostly do by command line parameters: 

 UCI mode parameters (hash, pawns hash, use own book and pondering) will be configured by the GUI.

 Xboard mode command line parameters are:

        hash XX       where XX(1-4096) is the numer of MegaBytes in the Main Transposition Table.

        phash YY      where YY(1-256) is the numer of MegaBytes in the Pawns Transposition Table.

        bookoff       to disable use of own Opening Book.

  General Command Line parameters for both xboard and UCI:

        egbbdir DD     where DD is the directory containig endgame bitbase dll and files.

        egbbcache MM   where MM(1-32) is the number of MegaBytes for endgame bitbase cache. 

        egbboff        to disable Endgame Bitbases.

        ics            to enable ICC/FICS  kibitz.


Acknowledgements
================
    * Pradu Kannan for introducing me to Magic bitboards. 
    * Ed Schroder for his opensource opening book code.
    * Olivier Deville and Fonzy Bluemers  for their  revised  opening book.
    * Daniel Shawul for his opensource egbb access code.


More info in the Web site.


I would like to receive your feedbacks.

Hope you enjoy it!



