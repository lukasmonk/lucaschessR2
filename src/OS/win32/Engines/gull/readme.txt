Gull 3 @ 17.04.2014
	Further optimization of evaluation weights.
	Nonlinear king shelter evaluation.
	More endgame knowledge. 
	Minor search tweaks.
	SMP rewrite, the code is simplified.

Gull 2.9 alpha @ 26.01.2014
	This version is a base for Gull 3 development. It has no multi-cpu support, since I haven't yet decided 
	whether to implement SMP via processes or threads. 
	Maximum hash table size is 1Gb.
	Should be slightly stronger than 2.8 beta at ultra short time controls due to minor differences in move generation algorithm.
	At blitz and long time controls the ELO difference is likely to be well within error margins of most rating lists. 

Gull 2.8 beta @ 26.01.2014
	Full evaluation rewrite. Gull is back to being an original engine.
	Minor search tweaks.

	Beta status due to unrefined source code (the evaluation function was just copy-pasted from Gull 2.9 alpha)
	BMI2 build provides a small speedup on CPUs with BMI2 instruction set support (Intel Haswell).
	For testing under ChessGUI it may be better to use the version with automatic affinity turned off.

Gull 2.3 @ 17.10.2013
	Minor search tweaks.

Gull 2.2 @ 17.08.2013
	Improved king safety evaluation.
	Quadratic PST optimized with the use of automated tuning.
	Several SMP bugs fixed.
	Time management bug (pondering mode) fixed.

Gull 2.1 @ 17.06.2013
	Evaluation weights are optimized with the use of automated tuning (source code included). 
	Gull's evaluation is no longer almost identical to that of Ivanhoe. 
	Minor search & time management & SMP efficiency enhancements.

	On SMP & Hyper-Threading:
		By default Gull limits the number of processes to the number of physical CPU cores availible.
		This is done in order to avoid ELO drop due to significant SMP search overhead at bullet time controls. 
		However for long games & analysis it is recommended to turn HT on and manually set the number of processes (UCI option "Threads")  
		to equal the number of logical CPUs.

	On the automated tuning (technical):
		Tuning is done in two steps:
		1. an estimate of the gradient is calculated;
		2. line search is performed.
	 	SPSA (just move a bit along the gradient direction instead of performing a line search) may also be quite effective, 
		though it's difficult to pick good parameters.
		Fairly simple exit criteria are used for the line search. I don't employ SPRT because it's guaranteed to be optimal only for 
		elo=elo1 vs elo=elo0 hypothesis, whereas in this case we are interested in elo>elo0 vs elo<=elo0 test. However it's still possible
		for SPRT (or some other test) to be better for some elo-elo0 values. Shouldn't be very difficult to run a numerical comparision
		between various tests.	  

Gull II @ 20.12.2012
	Slightly modified eval & search. 
	Significantly improved parallel search efficiency at long time controls.   

Gull II beta2 @ 17.07.2012
	Compatibility with XP finally fixed. +Knight underpromotion bug fixed. 
	The change in playing strength should be negligible.

Gull II beta xp @ 17.07.2012
	Compatibility with Windows XP fixed. No need for update if you use Vista/7/8.
	Still Gull will not run under any Windows older than XP.

Gull II beta @ 16.07.2012
	A derivative of Gull 1.2 (program structure, board representation, move generators etc.) & Ivanhoe (versions 63 & 46: evaluation). 
	Whether future versions will retain Ivanhoe's evaluation is still undecided. 

	Gull II beta supports multi-core CPUs. For now parallel algorithms are pretty basic, and performance gain isn't very good. 
	P.S. Gull employs processes instead of threads for the sake of code simplicity.

	P.P.S. This version may be buggy (tested only on my home PC). That's why it is a beta :) 


