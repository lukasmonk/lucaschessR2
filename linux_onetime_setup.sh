#!/bin/bash
cd bin/_fastercode
bash linux64.sh
cd ../OS/linux/
bash RunEngines
cd Engines/stockfish/
FILE=nn-5af11540bbfe.nnue
if [ ! -f "$FILE" ]; then
    wget https://tests.stockfishchess.org/api/nn/nn-5af11540bbfe.nnue
fi

