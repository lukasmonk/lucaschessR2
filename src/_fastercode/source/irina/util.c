#include <sys/types.h>
#include <sys/timeb.h>
#include <string.h>
#include <ctype.h>
#include "defs.h"
#include "protos.h"
#include "globals.h"


#ifdef WIN32
int is_bmi2()
{
    int info[4];
    __cpuidex(info, 0x00000007, 0);
    return (info[1] & ((int)1 <<  8)) != 0;
}
#else
#include <stdint.h>
int is_bmi2()
{
    // change by: https://github.com/jlrdh
    #ifdef __aarch64__
        return 0;
    #else
        __builtin_cpu_init ();
        return __builtin_cpu_supports("bmi2");
    #endif
}
#endif

unsigned int bit_count(Bitmap bitmap) {
    // MIT HAKMEM algorithm, see http://graphics.stanford.edu/~seander/bithacks.html

    static const Bitmap M1 = 0x5555555555555555; // 1 zero,  1 one ...
    static const Bitmap M2 = 0x3333333333333333; // 2 zeros,  2 ones ...
    static const Bitmap M4 = 0x0f0f0f0f0f0f0f0f; // 4 zeros,  4 ones ...
    static const Bitmap M8 = 0x00ff00ff00ff00ff; // 8 zeros,  8 ones ...
    static const Bitmap M16 = 0x0000ffff0000ffff; // 16 zeros, 16 ones ...
    static const Bitmap M32 = 0x00000000ffffffff; // 32 zeros, 32 ones

    bitmap = (bitmap & M1) + ((bitmap >> 1) & M1); //put count of each  2 bits into those  2 bits
    bitmap = (bitmap & M2) + ((bitmap >> 2) & M2); //put count of each  4 bits into those  4 bits
    bitmap = (bitmap & M4) + ((bitmap >> 4) & M4); //put count of each  8 bits into those  8 bits
    bitmap = (bitmap & M8) + ((bitmap >> 8) & M8); //put count of each 16 bits into those 16 bits
    bitmap = (bitmap & M16) + ((bitmap >> 16) & M16); //put count of each 32 bits into those 32 bits
    bitmap = (bitmap & M32) + ((bitmap >> 32) & M32); //put count of each 64 bits into those 64 bits
    return (int) bitmap;
}

/**
 * @author Kim Walisch (2012)
 * @param bb bitboard to scan
 * @precondition bb != 0
 * @return index (0..63) of least significant one bit
 */
unsigned int first_one(Bitmap bb) {
    static const int index64[64] ={
        0, 47, 1, 56, 48, 27, 2, 60,
        57, 49, 41, 37, 28, 16, 3, 61,
        54, 58, 35, 52, 50, 42, 21, 44,
        38, 32, 29, 23, 17, 11, 4, 62,
        46, 55, 26, 59, 40, 36, 15, 53,
        34, 51, 20, 43, 31, 22, 10, 45,
        25, 39, 14, 33, 19, 30, 9, 24,
        13, 18, 8, 12, 7, 6, 5, 63
    };
    static const Bitmap debruijn64 = 0x03f79d71b4cb0a89;

    return index64[((bb ^ (bb - 1)) * debruijn64) >> 58];
}

Bitmap get_ms() {
    struct timeb buffer;

    ftime(&buffer);
    return (buffer.time * 1000) +buffer.millitm;
}

int ah_pos(char *ah) {
    if ((ah[0] < 'a') || (ah[0] > 'h') || (ah[1] < '0') || (ah[1] > '9')) {
        return 0;
    }
    return (int) (ah[0] - 'a') + 8 * (int) (ah[1] - '1');
}

char *strip(char *txt) {
    int tam;

    for (tam = strlen(txt) - 1; tam && (txt[tam] == '\n' || txt[tam] == '\r'); tam--) {
        txt[tam] = '\0';
    }
    return txt;
}

char *move2str(MoveBin move, char *str_dest) {
    sprintf(str_dest, "%s%s", POS_AH[move.from], POS_AH[move.to]);
    if (move.promotion) {
        sprintf(str_dest + 4, "%c", tolower(NAMEPZ[move.promotion]));
    }
    return str_dest;
}


/*
 * From Beowulf, from Olithink () (via glaurung)
 */
#ifndef _WIN32

/* Linux */
bool bioskey() {
    fd_set readfds;
    struct timeval timeout;

    FD_ZERO(&readfds);
    FD_SET(fileno(stdin), &readfds);
    /* Set to timeout immediately */
    timeout.tv_sec = 0;
    timeout.tv_usec = 0;
    select(16, &readfds, 0, 0, &timeout);

    return (FD_ISSET(fileno(stdin), &readfds));
}


#else
/* Windows */
#include <windows.h>
#include <conio.h>

bool bioskey() {
    return _kbhit();
}
#endif
