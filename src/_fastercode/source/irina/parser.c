#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "defs.h"
#include "protos.h"
#include "globals.h"

extern unsigned PZNAME[];


char x[1000];

char * limpia(char *c)
{
    for(; *c; c++ )
    {
        if(!isspace((int) (*c))) break;
    }
    return c;
}

int parse_pgn( char * pgn, char * resp )
{
    char *c;
    char *r;
    char * r_ini;
    char fen[256];
    char label[256];
    char value[256];
    int tam;
    int pos;

    fen[0] = 0;
    c = pgn;
    r = resp;
    r_ini = r;

    c = limpia(c);
    while( *c == '[' ) {
        pos = 0;
        while( *c && *c != '"' )     // hasta las "
        {
            if( *c != ' ' )
            {
                label[pos++] = *c;
                *r++ = *c;
            }
            c++;
        }
        if( *c == '"' && pos )
        {
            label[pos] = 0;
            pos = 0;
            c++;
            *r++ = ' ';
            while( *c && *c != '"' )
            {
                if( *c == '\\' )
                {
                    c++;
                    if( ! *c ) break;
                }
                value[pos++] = *c;
                *r++ = *c;
                c++;
            }
            value[pos] = 0;
            *r++ = '\n';
        }
        if(strstr(label, "FEN") != NULL)
        {
            strcpy(fen, value);
        }
        c = limpia(++c);
        if(*c == ']') {
            c = limpia(++c);
        }
    }
    tam = r - r_ini;

    return parse_body(fen, c, r) + tam;
}

int parse_body( char * fen, char * body, char * resp )
{
    char * c;
    char * r_ini;
    char * r;
    char piece;
    char promotion;
    char from_AH, from_18;
    char to_AH, to_18;
    int par;
    int to;
    int num_ok;
    unsigned k;
    MoveBin move, mover;

    c = body;
    r = resp;
    r_ini = r;

    if( *fen ) fen_board( fen );
    else init_board();

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
                if( *c == 'x' ) c++;
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
            if( *c == 'x' ) c++;
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
                *r++ = 'R';
                *r++ = '1';
                *r = 0;
                return r-r_ini;
            }
            if( *(c+1) == '/' && *(c+2) == '2' && *(c+3) == '-' && *(c+4) == '1' && *(c+5) == '/' && *(c+6) == '2')
            {
                *r++ = 'R';
                *r++ = '2';
                *r = 0;
                return r-r_ini;
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
                *r++ = 'R';
                *r++ = '3';
                *r = 0;
                return r-r_ini;
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
            *r++ = '{';
            while ( *c && !(*c == '\n'||*c == '\r') ) {
                *r++ = *c;
                c++;
            }
            *r++ = '\n';
            break;

        case '(':
            *r++ = '(';
            par = 1;
            while ( *c && par )
            {
                c++;
                if( *c == '\r' || *c == '\n') *r++ = ' ';
                else *r++ = *c;
                if( *c == '{' )
                {
                    while ( *c && *c != '}' ) {
                        c++;
                        if( *c == '\r' || *c == '\n') *r++ = ' ';
                        else *r++ = *c;
                    }
                }
                if( *c == '(' ) {
                    par++;
                }
                else if( *c == ')' ) par--;
            }
            *r++ = '\n';
            break;

        case '{':
            *r++ = '{';
            while ( *c && *c != '}' ) {
                c++;
                if( *c == '\r' || *c == '\n') *r++ = ' ';
                else *r++ = *c;
            }
            *r++ = '\n';
            break;

        case '$':
            *r++ = '$';
            c++;
            if (*c >= '1' && *c <= '9') {
                *r++ = *c;
                c++;
                if (*c >= '0' && *c <= '9') {
                    *r++ = *c;
                    c++;
                    if (*c >= '0' && *c <= '9') {
                        *r++ = *c;
                        c++;
                    }
                }
            }
            *r++ = '\n';
            break;

        case '?':
            *r++ = '?';
            c++;
            if (*c == '?') {
                *r++ = '?';
                c++;
            }
            else {
                if (*c == '!') {
                    *r++ = '!';
                    c++;
                }
            }
            *r++ = '\n';
            break;

        case '!':
            *r++ = '!';
            c++;
            if (*c == '!') {
                *r++ = '!';
                c++;
            }
            else {
                if (*c == '?') {
                    *r++ = '?';
                    c++;
                }
            }
            *r++ = '\n';
            break;

        case '*':
            *r++ = 'R';
            *r++ = '0';
            *r = 0;
            return r-r_ini;

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
                    *r++ = 'M';
                    strcpy(r, POS_AH[move.from]);
                    r += 2;
                    strcpy(r, POS_AH[move.to]);
                    r += 2;
                    if( promotion )
                    {
                        *r++ = promotion;
                    }
                    *r++ = '\n';

                    mover = move;
                    num_ok ++;
                }
            }
            if(num_ok != 1) return false;
            make_move(mover);
            piece = 'P';
            from_AH = 0;
            from_18 = 0;
            to_AH = 0;
            to_18 = 0;
            promotion = 0;
        }
    }
    *r = 0;
    return r-r_ini;
}

