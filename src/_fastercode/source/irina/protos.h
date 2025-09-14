#ifndef IRINA_PROTOS_H
#define IRINA_PROTOS_H

#include "defs.h"
#include "hash.h"

// util.c
unsigned int bit_count(Bitmap bitmap);
unsigned int first_one(Bitmap bitmap);
int ah_pos(char *ah);
Bitmap get_ms(void);
bool bioskey(void);
char *move2str(MoveBin move, char *str_dest);
int is_bmi2(void);

// test.c
void test(void);
char *strip(char *txt);

void xmove(MoveBin move);
void xbitmap(Bitmap bm);
void xfen(void);

void xm(const char *fmt, ...);
void xl(void);
void xt(int num);

void show_move(MoveBin move);
int move_num(MoveBin move);
MoveBin num_move(int num);
void show_bitmap(Bitmap bm);
void show_4bitmap(Bitmap bm1, Bitmap bm2, Bitmap bm3, Bitmap bm4);
void show_move(MoveBin move);
bool equal_boards(Board b0, Board b1, Board b2, MoveBin mv);
Bitmap calc_perft(char *fen, int depth);
void perft(int depth);
void perft_file(char * file);

// eval.c
int eval(void);
void set_level(int lv);

// loop.c
void begin(void);
void loop(void);
void set_position(char *line);
void go(char *line);

// data.c
void init_data(void);

// board.c
void init_board(void);
void board_reset(void);
void fen_board(char *fen);
void bitmap_pz(unsigned pz[], Bitmap bm, int piece);
char *board_fen(char *fen);
char *board_fenM2(char *fen);
Bitmap board_hashkey(void);

// movegen.c
int movegen(void);
void addMove(MoveBin move);
bool isAttacked(Bitmap targetBitmap, int fromSide);
bool incheck(void);
bool incheckOther(void);
unsigned int movegenCaptures(void);

int movegen_piece(unsigned piece);
int movegen_piece_to(int piece, unsigned xto);

// makemove.c
void make_move(MoveBin move);
void unmake_move(void);

// search.c
char * play(int depth, int time);
int alphaBeta(int alpha, int beta, int depthleft, int ply);
int quiescence(int alpha, int beta, int ply);


// hash.c
Bitmap rand64();
void init_hash();

void set_ext_fen_body(char * ext_fen, char * ext_body, char * ext_pv );

// lc.c
int pgn2pv(char *pgn, char * pv);
int make_nummove(int num);
char * playFen( char * fen, int depth, int time );
int numMoves( void );
void getMove( int num, char * pv );
int numBaseMove( void );
int searchMove( char *desde, char *hasta, char * promotion );
void getMoveEx( int num, char * info );
char * toSan(int num, char *sanMove);

// parser.c
int parse_body( char * fen, char * body, char * resp );
int parse_pgn( char * pgn, char * resp );

// pgn.c
void pgn_start(int depth);
void pgn_stop( void );
int pgn_read(char * body, char * fen);
char * pgn_pv(void);
int pgn_raw(void);
char * pgn_fen(int num);
int pgn_numfens(void);

// polyglot.c
Bitmap hash_from_fen(char *fen);
void open_poly_w(char * name);
void close_poly();
void write_integer(int size, unsigned long long n);
unsigned int move_from_string(char move_s[6]);
int move_to_string(char move_s[6], unsigned int move);


#endif
