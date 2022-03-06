#ifndef IRINA_HASH_H
#define IRINA_HASH_H
#include "defs.h"

#define    HASH_EXACT   0
#define    HASH_ALPHA   1
#define    HASH_BETA    2

typedef struct
{
   Bitmap   hashkey;
   int      depth;
   int      val;
   int      flags;
   MoveBin     move;
} HASH_reg;

#endif
