// bench: 811618
// bench 12: 10210579 22,2 s 1.061
// REGEX to count all the lines under MSVC 13: ^(?([^\r\n])\s)*[^\s+?/]+[^\n]*$
// 2400 lines
// 47.4% vs Rodent 1.4, ca. 2720 Elo

enum eColor{WC, BC, NO_CL};
enum ePieceType{P, N, B, R, Q, K, NO_TP};
enum ePiece{WP, BP, WN, BN, WB, BB, WR, BR, WQ, BQ, WK, BK, NO_PC};
enum eFile {FILE_A, FILE_B, FILE_C, FILE_D, FILE_E, FILE_F, FILE_G, FILE_H};
enum eRank {RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8};
enum eMoveType {NORMAL, CASTLE, EP_CAP, EP_SET, N_PROM, B_PROM, R_PROM, Q_PROM};
enum eHashEntry{NONE, UPPER, LOWER, EXACT};
enum eMoveFlag {MV_NORMAL, MV_HASH, MV_CAPTURE, MV_KILLER, MV_BADCAPT};
enum eFactor   {F_PST, F_PAWNS, F_PASSERS, F_ATT, F_MOB, F_OUTPOST, F_LINES, F_OTHERS, N_OF_FACTORS};
enum eSquare{
  A1, B1, C1, D1, E1, F1, G1, H1,
  A2, B2, C2, D2, E2, F2, G2, H2,
  A3, B3, C3, D3, E3, F3, G3, H3,
  A4, B4, C4, D4, E4, F4, G4, H4,
  A5, B5, C5, D5, E5, F5, G5, H5,
  A6, B6, C6, D6, E6, F6, G6, H6,
  A7, B7, C7, D7, E7, F7, G7, H7,
  A8, B8, C8, D8, E8, F8, G8, H8,
  NO_SQ
};

typedef unsigned long long U64;

#define MAX_PLY         64
#define MAX_MOVES       256
#define INF             32767
#define MATE            32000
#define MAX_EVAL        29999
#define MAX_INT    2147483646

#define RANK_1_BB       (U64)0x00000000000000FF
#define RANK_2_BB       (U64)0x000000000000FF00
#define RANK_3_BB       (U64)0x0000000000FF0000
#define RANK_4_BB       (U64)0x00000000FF000000
#define RANK_5_BB       (U64)0x000000FF00000000
#define RANK_6_BB       (U64)0x0000FF0000000000
#define RANK_7_BB       (U64)0x00FF000000000000
#define RANK_8_BB       (U64)0xFF00000000000000

static const U64 bbRelRank[2][8] = { { RANK_1_BB, RANK_2_BB, RANK_3_BB, RANK_4_BB, RANK_5_BB, RANK_6_BB, RANK_7_BB, RANK_8_BB },
                                     { RANK_8_BB, RANK_7_BB, RANK_6_BB, RANK_5_BB, RANK_4_BB, RANK_3_BB, RANK_2_BB, RANK_1_BB } };

#define FILE_A_BB       (U64)0x0101010101010101
#define FILE_B_BB       (U64)0x0202020202020202
#define FILE_C_BB       (U64)0x0404040404040404
#define FILE_D_BB       (U64)0x0808080808080808
#define FILE_E_BB       (U64)0x1010101010101010
#define FILE_F_BB       (U64)0x2020202020202020
#define FILE_G_BB       (U64)0x4040404040404040
#define FILE_H_BB       (U64)0x8080808080808080

#define DIAG_A1H8_BB    (U64)0x8040201008040201
#define DIAG_A8H1_BB    (U64)0x0102040810204080
#define DIAG_B8H2_BB    (U64)0x0204081020408000

#define bbNotA          (U64)0xfefefefefefefefe // ~FILE_A_BB
#define bbNotH          (U64)0x7f7f7f7f7f7f7f7f // ~FILE_H_BB

#define ShiftNorth(x)   (x<<8)
#define ShiftSouth(x)   (x>>8)
#define ShiftWest(x)    ((x & bbNotA)>>1)
#define ShiftEast(x)    ((x & bbNotH)<<1)
#define ShiftNW(x)      ((x & bbNotA)<<7)
#define ShiftNE(x)      ((x & bbNotH)<<9)
#define ShiftSW(x)      ((x & bbNotA)>>9)
#define ShiftSE(x)      ((x & bbNotH)>>7)

#define MoreThanOne(bb) ( bb & (bb - 1) )

#define SIDE_RANDOM     (~((U64)0))

#define START_POS       "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"

#define SqBb(x)         ((U64)1 << (x))

#define Cl(x)           ((x) & 1)
#define Tp(x)           ((x) >> 1)
#define Pc(x, y)        (((y) << 1) | (x))

#define File(x)         ((x) & 7)
#define Rank(x)         ((x) >> 3)
#define Sq(x, y)        (((y) << 3) | (x))

#define Abs(x)          ((x) > 0 ? (x) : -(x))
#define Max(x, y)       ((x) > (y) ? (x) : (y))
#define Min(x, y)       ((x) < (y) ? (x) : (y))
#define Map0x88(x)      (((x) & 7) | (((x) & ~7) << 1))
#define Unmap0x88(x)    (((x) & 7) | (((x) & ~7) >> 1))
#define Sq0x88Off(x)    ((unsigned)(x) & 0x88)

#define Fsq(x)          ((x) & 63)
#define Tsq(x)          (((x) >> 6) & 63)
#define MoveType(x)     ((x) >> 12)
#define IsProm(x)       ((x) & 0x4000)
#define PromType(x)     (((x) >> 12) - 3)

#define Opp(x)          ((x) ^ 1)

#define InCheck(p)      Attacked(p, KingSq(p, p->side), Opp(p->side))
#define Illegal(p)      Attacked(p, KingSq(p, Opp(p->side)), p->side)
#define MayNull(p)      (((p)->cl_bb[(p)->side] & ~((p)->tp_bb[P] | (p)->tp_bb[K])) != 0)

#define PcBb(p, x, y)   ((p)->cl_bb[x] & (p)->tp_bb[y])
#define OccBb(p)        ((p)->cl_bb[WC] | (p)->cl_bb[BC])
#define UnoccBb(p)      (~OccBb(p))
#define TpOnSq(p, x)    (Tp((p)->pc[x]))
#define KingSq(p, x)    ((p)->king_sq[x])

#define RankIndex(o, x) (((o) >> ((070 & (x)) + 1)) & 63)
#define FileIndex(o, x) (((FILE_A_BB & ((o) >> File(x))) * DIAG_B8H2_BB) >> 58)
#define DiagIndex(o, x) ((((o) & line_mask[2][x]) * FILE_B_BB) >> 58)
#define AntiIndex(o, x) ((((o) & line_mask[3][x]) * FILE_B_BB) >> 58)

#define L1Attacks(o, x) attacks[0][x][RankIndex(o, x)]
#define L2Attacks(o, x) attacks[1][x][FileIndex(o, x)]
#define L3Attacks(o, x) attacks[2][x][DiagIndex(o, x)]
#define L4Attacks(o, x) attacks[3][x][AntiIndex(o, x)]
#define RAttacks(o, x)  (L1Attacks(o, x) | L2Attacks(o, x))
#define BAttacks(o, x)  (L3Attacks(o, x) | L4Attacks(o, x))
#define QAttacks(o, x)  (RAttacks(o, x) | BAttacks(o, x))

#define FirstOne(x)     bit_table[(((x) & (~(x) + 1)) * (U64)0x0218A392CD3D5DBF) >> 58]

#define REL_SQ(sq,cl)   ( sq ^ (cl * 56) )
#define RelSqBb(sq,cl)  ( SqBb(REL_SQ(sq,cl) ) )

enum eCastleFlag { W_KS = 1, W_QS = 2, B_KS = 4, B_QS = 8};

extern int last_sq;
extern int limit_distance;
extern bool use_book;
extern U64 BITSET[64];


typedef struct {
  int ttp;
  int castle_flags;
  int ep_sq;
  int rev_moves;
  U64 hash_key;
  U64 pawn_key;
} UNDO;

typedef class {
public:
  U64 cl_bb[2];
  U64 tp_bb[6];
  int pc[64];
  int king_sq[2];
  int mat[2];
  int mg_pst[2];
  int eg_pst[2];
  int cnt[2][6];
  int phase;
  int side;
  int castle_flags;
  int ep_sq;
  int rev_moves;
  int head;
  U64 hash_key;
  U64 pawn_key;
  U64 rep_list[256];

  void DoMove(int move, UNDO * u);
  void DoNull(UNDO * u);
  void UndoMove(int move, UNDO * u);
  void UndoNull(UNDO * u);
} POS;

typedef struct {
  POS *p;
  int phase;
  int trans_move;
  int killer1;
  int killer2;
  int *next;
  int *last;
  int move[MAX_MOVES];
  int value[MAX_MOVES];
  int *badp;
  int bad[MAX_MOVES];
} MOVES;

typedef struct {
  U64 key;
  short date;
  short move;
  short score;
  unsigned char flags;
  unsigned char depth;
} ENTRY;

void Add(int sd, int factor, int mg_bonus, int eg_bonus);
void AllocTrans(int mbsize);
int Attacked(POS *p, int sq, int side);
U64 AttacksFrom(POS *p, int sq);
U64 AttacksTo(POS *p, int sq);
int BadCapture(POS *p, int move);
void Bench(int depth);
void BuildPv(int *dst, int *src, int move);
void Check(void);
void ClearEvalHash(void);
void ClearHist(void);
void ClearTrans(void);
void DisplayPv(int score, int *pv);
int Evaluate(POS * p, int use_hash);
void EvaluateKing(POS *p, int sd);
int EvalKingFile(POS * p, int sd, U64 bbFile);
int EvalFileShelter(U64 bbOwnPawns, int sd);
int EvalFileStorm(U64 bbOppPawns, int sd);
void EvaluatePieces(POS * p, int sd);
void EvaluatePawns(POS * p, int sd);
U64 FillNorth(U64 bb);
U64 FillSouth(U64 bb);
int *GenerateCaptures(POS *p, int *list);
int *GenerateQuiet(POS *p, int *list);
int GetMS(void);
U64 GetWPControl(U64 bb);
U64 GetBPControl(U64 bb);
int GetDrawFactor(POS *p, int sd);
void UpdateHistory(POS *p, int move, int depth, int ply);
void Init(void);
void InitEval(void);
void InitSearch(void);
void InitCaptures(POS *p, MOVES *m);
void InitMoves(POS *p, MOVES *m, int trans_move, int ply);
void InitWeights(void);
int InputAvailable(void);
U64 InitHashKey(POS * p);
U64 InitPawnKey(POS * p);
void Iterate(POS *p, int *pv);
int Legal(POS *p, int move);
int Mobility(POS * p, int sd);
void MoveToStr(int move, char *move_str);
int MvvLva(POS *p, int move);
int NextCapture(MOVES *m);
int NextMove(MOVES *m, int *flag);
void ParseGo(POS *, char *);
int ParseMoves(POS *p, char *ptr);
void ParsePosition(POS *, char *);
void ParseSetoption(char *);
int Perft(POS *p, int ply, int depth);
void PrintBoard(POS *p);
char *ParseToken(char *, char *);
int PopCnt(U64);
int PopFirstBit(U64 * bb);
void PvToStr(int *, char *);
int Quiesce(POS *p, int ply, int alpha, int beta, int *pv);
U64 Random64(void);
void ReadLine(char *str, int n);
void ResetEngine(void);
int IsDraw(POS * p);
void ScoreCaptures(MOVES *);
void ScoreQuiet(MOVES *m);
int Widen(POS *p, int depth, int * pv, int lastScore);
int Search(POS *p, int ply, int alpha, int beta, int depth, int was_null, int *pv);
int SelectBest(MOVES *m);
void SetPosition(POS *p, const char *epd);
int StrToMove(POS *p, char *move_str);
int Swap(POS *p, int from, int to);
void Think(POS *p, int *pv);
int Timeout(void);
int TransRetrieve(U64 key, int *move, int *score, int alpha, int beta, int depth, int ply);
void TransStore(U64 key, int move, int score, int flags, int depth, int ply);
void UciLoop(void);

bool check_book( const char * fname, POS * p, char * move );

extern U64 line_mask[4][64];
extern U64 attacks[4][64][64];
extern U64 p_attacks[2][64];
extern U64 n_attacks[64];
extern U64 k_attacks[64];
extern U64 passed_mask[2][64];
extern U64 adjacent_mask[8];
extern int mg_pst_data[2][6][64];
extern int eg_pst_data[2][6][64];
extern int castle_mask[64];
extern const int bit_table[64];
extern const int passed_bonus[2][8];
extern const int tp_value[7];
extern const int phase_value[7];
extern int history[12][64];
extern int killer[MAX_PLY][2];
extern U64 zob_piece[12][64];
extern U64 zob_castle[16];
extern U64 zob_ep[8];
extern int pondering;
extern int root_depth;
extern U64 nodes;
extern int abort_search;
extern ENTRY *tt;
extern int tt_size;
extern int tt_mask;
extern int tt_date;
extern int weights[N_OF_FACTORS];
