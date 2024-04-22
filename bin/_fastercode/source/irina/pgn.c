#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "defs.h"
#include "protos.h"
#include "globals.h"

#define MAX_MDEPTH 1024

char pv[MAX_MDEPTH*5];
char fen[64];
int raw;
char * fens[MAX_MDEPTH];
int pos_fens;
int max_depth;


unsigned PZNAME[] =
{
    0,            0,            0,            0,            0,            0,            0,            0,            0,            0,            0,            0,
    0,            0,            0,            0,            0,            0,            0,            0,            0,            0,            0,            0,
    0,            0,            0,            0,            0,            0,            0,            0,            0,            0,            0,            0,
    0,            0,            0,            0,            0,            0,            0,            0,            0,            0,            0,            0,
    0,            0,            0,            0,            0,            0,            0,            0,            0,            0,            0,            0,
    0,            0,            0,            0,            0,            0, WHITE_BISHOP,            0,            0,            0,            0,            0,
    0,            0,            0,   WHITE_KING,            0,            0, WHITE_KNIGHT,            0,   WHITE_PAWN,  WHITE_QUEEN,   WHITE_ROOK,            0,
    0,            0,            0,            0,            0,            0,            0,            0,            0,            0,            0,            0,
    0,            0, BLACK_BISHOP,            0,            0,            0,            0,            0,            0,            0,            0,   BLACK_KING,
    0,            0, BLACK_KNIGHT,            0,   BLACK_PAWN,  BLACK_QUEEN,   BLACK_ROOK
};


void pgn_start(int depth)
{
    int i;

    if( depth > MAX_MDEPTH ) depth = MAX_MDEPTH;
    max_depth = depth;

    for( i=0; i < depth; i++)
    {
        fens[i] = (char *) malloc(128);
    }
}

void pgn_stop( void )
{
    int i;
    for( i=0; i < MAX_MDEPTH; i++)
    {
        free(fens[i]);
    }
}


int pgn_read(char * body, char * fen)
{
    char *c;
    char piece;
    char promotion;
    char from_AH, from_18;
    char to_AH, to_18;
    char *p_pv;
    int num_ok;

    int par;
    int to;
    unsigned k;
    MoveBin move, mover;

    p_pv = pv;
    *p_pv = 0;

    raw = true;

    if( *fen ) fen_board( fen );
    else init_board();

    pos_fens = 0;

    c = body;
    piece = 'P';
    from_AH = 0;
    from_18 = 0;
    to_AH = 0;
    to_18 = 0;
    promotion = 0;

    while(*c)
    {
        switch(*c)
        {
        case ' ':
        case '\r':
        case '\n':
            c++;
            break;

        case 'R':
        case 'K':
        case 'Q':
        case 'B':
        case 'N':
            piece = *c;
            promotion = 0;
            c++;
            if( *c >= '1' && *c <= '8' )
            {
                from_18 = *c;
                c++;
                if( *c == 'x' || *c == '-') c++;
                if( *c >= 'a' && *c <= 'h' )
                {
                    to_AH = *c;
                    c++;
                    if( *c >= '1' && *c <= '8' )
                    {
                        to_18 = *c;
                        c++;
                    }
                }
            }
            break;

        case 'a':
        case 'b':
        case 'c':
        case 'd':
        case 'e':
        case 'f':
        case 'g':
        case 'h':
            from_AH = *c;
            c++;
            if( *c && *c >= '1' && *c <= '8' )
            {
                from_18 = *c;
                c++;
            }
            if( *c == 'x' || *c == '-') c++;
            if( *c >= 'a' && *c <= 'h' )
            {
                to_AH = *c;
                c++;
                if( *c >= '1' && *c <= '8' )
                {
                    to_18 = *c;
                    c++;
                }
            }
            else
            {
                to_AH = from_AH;
                to_18 = from_18;
                from_AH = 0;
                from_18 = 0;
            }
            if( to_18 == 0 )
            {
                return false;
            }

            if( piece == 'P' && ( to_18 == '8' || to_18 == '1' ) )
            {
                if(*c == '=')
                {
                    c++;
                    if(*c == 'Q' || *c == 'R' || *c == 'B' || *c == 'N')
                    {
                        promotion = *c;
                        c++;
                    }
                    else if(*c == 'q' || *c == 'r' || *c == 'b' || *c == 'n')
                    {
                        promotion = *c + 'Q' - 'q';
                        c++;
                    }
                    else
                    {
                        {
                            return false;
                        }
                    }
                }
                else
                {
                    {
                        return false;
                    }
                }
            }
            break;

        case '1':
            if( *(c+1) == '-' && *(c+2) == '0' )
            {
                *p_pv = 0;
                return true;
            }
            if( *(c+1) == '/' && *(c+2) == '2' && *(c+3) == '-' && *(c+4) == '1' && *(c+5) == '/' && *(c+6) == '2')
            {
                *p_pv = 0;
                return true;
            }
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
            c++;
            while( *c >= '0' && *c <= '9' ) c++;
            while( *c == '.' ) c++;
            break;

        case '0':
            if( *(c+1) == '-' && *(c+2) == '1' )
            {
                *p_pv = 0;
                return true;
            }

        case 'O':
        case 'o':
            c++;
            if(*c == '-')
            {
                c++;
                if( *c == 'O' || *c == '0' || *c == 'o')
                {
                    c++;
                    piece = 'K';
                    from_AH = 'e';
                    from_18 = (board.color) ? '8':'1';
                    to_18 = from_18;
                    if( *c == '-' )
                    {
                        c++;
                        if( *c == 'O' || *c == '0' || *c == 'o')
                        {
                            to_AH = 'c';
                            c++;
                        }
                        else
                        {
                            return false;
                        }
                    }
                    else
                    {
                        to_AH = 'g';
                    }
                }
                else
                {
                    return false;
                }
            }
            else
            {
                return false;
            }
            break;

        case '%':
        case ';':
            while ( *c && !(*c == '\n'||*c == '\r') ) c++;
            if(raw) raw = false;
            break;

        case '(':
            par = 1;
            while ( *c && par )
            {
                c++;
                if( *c == '{' )
                {
                    while ( *c && *c != '}' ) c++;
                }
                if( *c == '(' ) par++;
                else if( *c == ')' ) par--;
            }
            if(raw) raw = false;
            break;

        case '{':
            while ( *c && *c != '}' ) c++;
            if(raw) raw = false;
            break;

        case '$':
            c++;
            if(raw) raw = false;
            break;

        case '!':
        case '?':
            c++;
            if(raw) raw = false;
            break;

        default:
            c++;
        }

        if( to_18 )
        {
            while( *c == ' ' ) c++;
            if( *c == 'e' && *(c+1) == 'p' ) c+=2;

            to = (to_AH-'a') + (to_18-'1')*8;

            if(board.color)
            {
                piece +=  'a' - 'A';
                if( promotion ) promotion += 'a' - 'A';
            }

            /*movegen();*/
            /*movegen_piece(PZNAME[piece]);*/
            movegen_piece_to((int)PZNAME[(int)piece], (unsigned)to);
            num_ok = 0;
            for (k = board.ply_moves[board.ply - 1]; k < board.ply_moves[board.ply]; k++)
            {
                move = board.moves[k];

                /*if( NAMEPZ[move.piece] == piece && move.to == to)*/
                if( move.to == to)
                {
                    if(from_AH && (move.from%8 != (from_AH-'a'))) continue;
                    if(from_18 && (move.from/8 != (from_18-'1'))) continue;
                    if( move.promotion && NAMEPZ[move.promotion] != promotion ) continue;
                    if( promotion && !move.promotion ) continue;
                    if( pv != p_pv )
                    {
                        *p_pv = ' ';
                        p_pv++;
                    }
                    strcpy(p_pv, POS_AH[move.from]);
                    p_pv += 2;
                    strcpy(p_pv, POS_AH[move.to]);
                    p_pv += 2;
                    if( promotion )
                    {
                        *p_pv = promotion;
                        p_pv++;
                    }

                    mover = move;
                    num_ok++;
                    break;
                }
            }
            if( num_ok != 1 ) return false;
            make_move(mover);
            if( pos_fens < max_depth ) board_fenM2( fens[pos_fens++] );
            piece = 'P';
            from_AH = 0;
            from_18 = 0;
            to_AH = 0;
            to_18 = 0;
            promotion = 0;
        }
    }
    *p_pv = 0;
    return true;
}


char * pgn_pv(void)
{
    return pv;
}


int pgn_raw(void)
{
    return raw;
}

char * pgn_fen(int num)
{
    return (char *)fens[num];
}

int pgn_numfens(void)
{
    return pos_fens;
}
