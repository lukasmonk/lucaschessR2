# Patricia Chess Engine
<div align="center">

  <img src="Patricia_logo.png" width="400" height="400" alt="Patricia logo">

  
  [![License][license-badge]][license-link]
  [![Release][release-badge]][release-link]
  [![Commits][commits-badge]][commits-link]
  
</div>

A killer bunny who will not hesitate to ram as many pieces as possible down your throat, Patricia is the most aggressive chess engine the world has ever seen.

<br/><br/>

## Aggression
The metric that Patricia's aggression claims are based off of is Stefan Pohl's [EAS tool (found here)](https://www.sp-cc.de/eas-ratinglist.htm), which is the most well known and well regarded tool for determining the aggressiveness of chess engines. It looks at a combination of factors, such as sacrifice rate, short win rate, and unnecessary draw rate, and outputs a score that captures how "exciting" an engine tends to play. It's not a perfect statistic but from my experience it reflects the "eye test" well.

The average engine's EAS score generally falls between 50,000 and 100,000. The most aggressive top engine is Stockfish, due to its extreme tactical ability; it has an EAS score of 190,000.

By contrast, Patricia's EAS score is <b><i>430,000</i></b> as tested by [Pohl himself](https://www.sp-cc.de/patricia_eas_engine.htm).

It's worth noting that Patricia is still well into superhuman territory, with an estimated CCRL elo of 3300-3350; she can put up a solid fight against top engines, and will crush any humans.

<br/><br/>

## What Patricia currently does to increase aggressiveness
- Default contempt of 30 centipawns for draws deemed avoidable
- Neural network using a custom training/retraining script over multiple filtered data sources that was developed over the course of a few months - this is the main source of Patricia 3's aggressiveness.
- Partially asymmetrical evaluation; Patricia doesn't care if she gets sacrificed against, so all sacrifice bonuses apply to the original side to move only.
- Bonuses for going down in material compared to original position being searched
- Bonuses for being better off than what material would suggest
- Material scaling

<br/><br/>
## Search Features
This is not a comprehensive list of search features that Patricia has.

- Alpha-Beta search with Quiescence Search and Transposition Tables
- Aspiration Windows
- Reverse Futility Pruning and Futility Pruning
- Null Move Pruning
- Late Move Reductions
- Late Move Pruning
- History Heuristic and Killer Move Heuristic
- Singular Extensions
- SEE pruning
- Countermove History, Capture History, and Follow-up History tables
- Improving
- Internal Iterative Reductions
- SIMD
- TT Replacement Schema

<br/><br/>
## Customization Options

Patricia supports a few options for users:
`Hash`: The memory alloted to the transposition table.

`Threads`: Number of threads to search with.

`UCI_LimitStrength`: Enables Patricia to be weakened using `UCI_Elo`.

`UCI_Elo`: Sets Patricia to play at a given strength range, anywhere from 500 to 3000. These ratings were calibrated by playing many matches against engines of all strengths.

`MultiPV`: Patricia searches the best X moves instead of only looking for the best line.

`Skill_Level`: Sets Patricia to play at one of 20 possible strength levels. They are:
| Skill Level | ELO |
|:---:|---|
| 1 | 500 |
| 2 | 800 |
| 3 | 1000 |
| 4 | 1200 |
| 5 | 1300 |
| 6 | 1400 |
| 7 | 1500 |
| 8 | 1600 |
| 9 | 1700 |
| 10 | 1800 |
| 11 | 1900 |
| 12 | 2000 |
| 13 | 2100 |
| 14 | 2200 |
| 15 | 2300 |
| 16 | 2400 |
| 17 | 2500 |
| 18 | 2650 |
| 19 | 2800 |
| 20 | 3000 |

`go nodes`: Search a position for a given number of nodes.

`go depth`: Search a position to a given depth.

`go movetime`: Search a position for a given number of milliseconds.

<br/><br/>

## Evaluation and Filtering
Patricia's evaluation is a neural network with a 768x2->768->1 perspective arch, trained on 2.4 billion positions of my other engine [Willow's](https://github.com/Adam-Kulju/Willow) data. It has been additionally retrained on a filtered dataset of 10 million positions specially selected for being "aggressive positions", in order to increase Patricia's understanding of them and to make her more likely to play into similar positions.

Code for filtering programs are found in the utils/ directory, and are indentified as follows:
- <b>position_filter_1:</b> Saves positions with general compensation - i.e. being down significantly in material yet still having at least a playable position. (Note: I currently do not recommend using this one.)
- <b>position_filter_2:</b> Saves positions where one side's king is exposed and under attack by enemy pieces.
- <b>position_filter_3:</b> Saves positions where one side has a major space advantage.
- <b>position_filter_4:</b> Saves opposite side castling positions with lots of material on the board and one side attempting a pawn storm.
- <b>position_filter_5:</b> Saves positions where one side is significantly behind in development.
- <b>position_filter_6:</b> Saves positions where one side can't castle and has an open king. This is somewhat similar to 2 but doesn't take into account attackers and uses a different method for calculating defensive strength.
- <b>position_filter_7:</b> Saves positions where many pieces are able to move near, are near, or are pointing at the enemy king. This uses a simple but effective ray calculator instead of a full mobility calculation.
- <b>position_filter_8:</b> Saves positions where one side has an extremely powerful minor piece that can't be traded off easily. Many such positions result from exchange sacrifices and even if they don't the dominant piece is a long term advantage that often leads to dynamics down the line.
- <b>position_filter_9:</b> Currently Patricia's best filtering script. It is a fixed version of `position_filter_1` that saves positions where we are doing much better than material balance would suggest.

Patricia currently uses positions that were filtered out by script 9.

Additionally, the `converter.cpp` file allows you to transform bullet-format data into text data, so that you can then use the filtering scripts on the resulting file.

All filtering programs are run with the command `./[exe] [input.txt] [output.txt]`. You'll have to compile the particular program that you want to run yourself, or you can ask me for a binary for a specific filtering method.

<br/><br/>

## Datagen

Patricia has support for data generation; in order to compile the datagen script, run `make datagen` in the `engines` directory. This will give you an executable named `data`; run `./data [number of threads] [optional EPD opening book]` to start datagen, and exit the process whenever you want with Ctr-C.

<br/><br/>

## Acknowledgements

- A huge shoutout to Stefan Pohl. His EAS Tool works wonderfully, makes properly and objectively testing for increase aggression possible, and is the measure by which Patricia development progressed. He was also very invested in Patricia's development and explained many features of the EAS tool to me so that I had a better understanding of what was a sacrifice and what wasn't. He has put a lot of time into quantifying style, and I am happy to have Patricia be a proof-of-concept and culmination of his ideas.

- Thanks to my friends at SweHosting as usual, for being supportive, for suggesting ideas, and for spreading Patricia propaganda in the Stockfish Discord server.

- Thanks to all the people interested in an aggressive chess engine. The support I got in my developer log on Talkchess is really nice to see. I'm glad people care about style in chess too, rather than just ELO!

<br/><br/>

## Other

Instructions for downloading/building Patricia can be found in the Releases section. If you know UCI protocol, you can run Patricia directly, otherwise she will work with any major GUI ([Arena](http://www.playwitharena.de/), [BanksiaGUI](https://banksiagui.com/), etc.)

If you think Patricia is a cool project, please spread the word! There are lots of people interested in an aggressive engine, whether it be for sparring or for analysis, and greater awareness of the undisputed queen of style would make their wish come true.

[license-badge]: https://img.shields.io/github/license/Adam-Kulju/Patricia?style=for-the-badge
[release-badge]: https://img.shields.io/github/v/release/Adam-Kulju/Patricia?style=for-the-badge
[commits-badge]: https://img.shields.io/github/commits-since/Adam-Kulju/Patricia/latest?style=for-the-badge

[license-link]: https://github.com/Adam-Kulju/Patricia/blob/main/LICENSE
[release-link]: https://github.com/Adam-Kulju/Patricia/releases/latest
[commits-link]: https://github.com/Adam-Kulju/Patricia/commits/main
