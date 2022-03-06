#include <string.h>

#include "defs.h"
#include "protos.h"
#include "globals.h"


char * xx[] = { "c4", "e5", "e3", "Nf6", "b3", "d5", "cxd5", "Nxd5", "Bb2", "Bd6", "d3", "c5", "Nf3", "Nc6", "Nbd2", "Qe7", "Be2", "O-O", "O-O",
                "f5", "Qc2", "Kh8", "Rfe1", "b6", "a3", "Bb7", "Bf1", "Nf6", "Rad1", "Rae8", "g3", "Bb8", "Nh4", "Ng4", "Bg2", "Qf6", "h3",
                "Nh6", "Qb1", "Qf7", "Bc3", "g5", "Nhf3", "Qh5", "b4", "cxb4", "axb4", "g4", "Nh4", "gxh3", "Bxh3", "Nd8", "d4", "f4", "exf4",
                "Rxf4", "dxe5", "Rxh4", "gxh4", "Ne6", "Re3", "Qxh4", "Ne4", "Ng4", "Bxg4", "Qxg4+", "Ng3", "Qh3", "Ne4", "Rg8+", "Rg3",
                "Rxg3+", "fxg3", "Bxe4", "Qxe4", "Qxg3+", "Kf1", "Qxc3", "Rd7", "Qh3+", "Ke1", "Kg8", "Re7", "Kf8", "Rxh7", "Qc3+", "Kd1",
                "Qxe5", "Qxe5", "Bxe5", "Rxa7", "Bc7", "Kc2", "Ke7", "Kc3", "Kd6", "Kc4", "Kc6", "b5+", "Kd7", "Ra1", "Bd6", "Rh1", "Nc7",
                "Rh7+", "Be7", "Rh1", "Ne8", "Kd5", "Nf6+", "Ke5", "Ng4+", "Kf4", "Nf2", "Rh7", "Ke6", "Rh6+", "Bf6", "Rh5", "Nd3+", "Ke3",
                "Nc5", "Kf4", "Bd4", "Rg5", "Kd6", "Rh5", "Nd7", "Rf5", "Be5+", "Ke4", "Nc5+", "Ke3", "Kd5", "Rh5", "Ne6", "Rf5", "Nd4", "Rh5",
                "Nxb5", "Kd3", "Nd6", "Kc2", "Nc4", "Kb3", "Kc5", "Rg5", "Na5+", "Kc2", "Nc6", "Rg8", "b5", "Rc8", "b4", "Kb3", "Bc3", "Rc7",
                "Kd6", "Rc8", "Kd5", "Rc7", "Nd4+", "Ka2", "Ke4", "Rh7", "Kd3", "Kb1", "b3", "Rb7", "Kc4", "Rc7+", "Kb4", "Rh7", "Nb5", "Rh4+",
                "Bd4", "Rh2", "Na3+", "Kc1", "Nc4", "Kb1", "Ka3", "Rh3", "Be3", "Rh1", "Nd2+", "Kc1", "Ka2", "Kd1", "Nc4", "Ke2", "b2", "Kd3",
                "Bc1", "Rh2", "Nd2"};


#define NELEMS(x)  (sizeof(x) / sizeof((x)[0]))

int pgn2pv(char *pgn, char * pv);

int main() {
    int i, tam, resp;
    char pv[10];
    char fen[100];

    init_data();
    init_board();
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);

    tam = NELEMS(xx);


    for(i = 0;i < tam;i++) {
        movegen();

        resp = pgn2pv(xx[i], pv);
        printf("%d. %s %s (%d)\n", i+1, xx[i], pv, resp);

        if( resp == 9999) break;

        printf("\nAntes: %s",board_fen(fen));
        make_nummove(resp);
        printf("\nDesp.: %s\n",board_fen(fen));
    }
    getchar();


    return 0;
}
