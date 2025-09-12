#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "defs.h"
#include "protos.h"
#include "hash.h"
#include "globals.h"

Bitmap HASH_keys[64][16];
Bitmap HASH_ep[64];
Bitmap HASH_wk = 0;
Bitmap HASH_wq;
Bitmap HASH_bk;
Bitmap HASH_bq;
Bitmap HASH_side;

Bitmap register_max;


Bitmap rand64()
{
    return rand() ^ ((Bitmap) rand() << 15) ^ ((Bitmap) rand() << 30) ^ ((Bitmap) rand() << 45) ^ ((Bitmap) rand() << 60);
}

void init_hash()
{
    int i, j;

    srand((unsigned int) get_ms());

    for (i = 0; i < 64; i++)
    {
        HASH_ep[i] = rand64();
        for (j = 0; j < 16; j++)
        {
            HASH_keys[i][j] = rand64();
        }
    }
    HASH_side = rand64();
    HASH_wk = rand64();
    HASH_wq = rand64();
    HASH_bk = rand64();
    HASH_bq = rand64();

}
