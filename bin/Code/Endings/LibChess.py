import random

import FasterCode
import chess
import chess.gaviota


class T4:
    def __init__(self, configuration):
        self.tb = chess.gaviota.open_tablebase(configuration.folder_gaviota())

    def better_moves(self, fen, move):
        dic = self.checkFen(fen)
        max_dtm = move_dtm = dic[move] if move else -1
        for pv, dtm in dic.items():
            if dtm < 0:
                if max_dtm < 0:
                    if dtm < max_dtm:
                        max_dtm = dtm
            elif dtm == 0:
                if max_dtm < 0:
                    max_dtm = dtm
            else:
                if max_dtm <= 0 or dtm < max_dtm:
                    max_dtm = dtm
        if move and max_dtm == move_dtm:
            return []
        else:
            return [pv for pv, dtm in dic.items() if dtm == max_dtm]

    def best_move(self, fen):
        li = self.better_moves(fen, None)
        if li:
            return random.choice(li)
        else:
            return None

    def best_moves_game(self, game):
        lifens = [move.position_before.fen().split(" ")[0] for move in game.li_moves]

        fen = game.last_position.fen()
        lifens.append(fen.split(" ")[0])

        FasterCode.set_fen(fen)

        li_moves = FasterCode.get_moves()
        lista_win = []
        lista_draw = []
        lista_lost = []
        for xpv in li_moves:
            pv = xpv[1:]
            FasterCode.set_fen(fen)
            FasterCode.move_pv(pv[:2], pv[2:4], pv[4:])
            xfen = FasterCode.get_fen()
            dtm = -self.dtm(xfen)
            if dtm is not None:
                fen_base = xfen.split(" ")[0]
                num = lifens.count(fen_base)
                if num >= 2:
                    dtm = 0
                if dtm > 0:
                    lista_win.append((pv, dtm, xfen))
                elif dtm == 0:
                    wdl = -self.wdl(xfen)
                    if wdl > 0:
                        lista_win.append((pv, dtm, xfen))
                    else:
                        lista_draw.append((pv, dtm, xfen))
                else:
                    lista_lost.append((pv, dtm, xfen))
        if lista_win:
            lista_win.sort(key=lambda x: x[1])
            buscar = lista_win[0][1]
            lista = [x[0] for x in lista_win if x[1] == buscar]
        elif lista_draw:
            lista = [x[0] for x in lista_draw]
        elif lista_lost:
            lista_lost.sort(key=lambda x: x[1])
            buscar = lista_lost[0][1]
            lista = [x[0] for x in lista_lost if x[1] == buscar]
        else:
            lista = []

        # if len(lista) > 1:
        #     cp = Position()
        #     min_ch = 99999
        #     pos_ch = -1
        #     for pos, mv in enumerate(lista):
        #         cp.read_fen(fen)
        #         cp.play(mv[:2], mv[2:4], mv[4:])
        #         ch = cp.cohesion()
        #         if ch < min_ch:
        #             pos_ch = pos
        #             min_ch = ch
        #     lista = [lista[pos_ch]]
        return lista

    def dtm(self, fen):
        try:
            board = chess.Board(fen)
        except:
            return None
        if len(board.piece_map()) > 5:
            return None
        try:
            dtm = self.tb.probe_dtm(board)
        except:
            dtm = None
        return dtm

    def wdl(self, fen):
        board = chess.Board(fen)
        if len(board.piece_map()) > 5:
            return None
        try:
            wdl = self.tb.probe_wdl(board)
        except:
            wdl = None
        return wdl

    def checkFen(self, fen):
        FasterCode.set_fen(fen)
        liMoves = FasterCode.get_moves()
        dic = {}
        for xpv in liMoves:
            pv = xpv[1:]
            FasterCode.set_fen(fen)
            FasterCode.move_pv(pv[:2], pv[2:4], pv[4:])
            xfen = FasterCode.get_fen()
            dtm = self.dtm(xfen)
            if dtm is not None:
                dic[pv] = -dtm
        return dic

    def listFen(self, fen):
        FasterCode.set_fen(fen)
        liMoves = FasterCode.get_exmoves()
        li = []
        for move in liMoves:
            from_sq = move.xfrom()
            to_sq = move.xto()
            promotion = move.promotion()
            FasterCode.set_fen(fen)
            FasterCode.move_pv(from_sq, to_sq, promotion)
            xfen = FasterCode.get_fen()
            board = chess.Board(xfen)
            try:
                dtm = -self.tb.probe_dtm(board)
                if dtm == 0:
                    if board.is_checkmate():
                        xdtm = "#"
                        orden = 999999
                    else:
                        xdtm = _("Draw")
                        orden = 0
                elif dtm < 0:
                    xdtm = str(dtm)
                    orden = -(999999 + dtm)
                else:
                    xdtm = str(dtm)
                    orden = 999999 - dtm
            except:
                xdtm = "?"
                orden = -999999

            li.append((move.san(), xdtm, orden, from_sq, to_sq, promotion))
        li.sort(key=lambda x: -x[2])
        return li

    def best_mvs(self, fen):
        FasterCode.set_fen(fen)
        liMoves = FasterCode.get_exmoves()
        li = []
        for move in liMoves:
            from_sq = move.xfrom()
            to_sq = move.xto()
            promotion = move.promotion()
            FasterCode.set_fen(fen)
            FasterCode.move_pv(from_sq, to_sq, promotion)
            xfen = FasterCode.get_fen()
            board = chess.Board(xfen)
            try:
                dtm = -self.tb.probe_dtm(board)
                if dtm == 0:
                    if board.is_checkmate():
                        orden = 999999
                    else:
                        orden = 0
                elif dtm < 0:
                    orden = -(999999 + dtm)
                else:
                    orden = 999999 - dtm
            except:
                orden = -999999

            li.append((from_sq, to_sq, orden))
        li.sort(key=lambda x: -x[2])
        if li:
            obase = li[0][2]
            for pos, (f, t, o) in enumerate(li):
                if o != obase:
                    return li[:pos]
        return li

    def wdl_move(self, fen, move):
        FasterCode.set_fen(fen)
        liMoves = FasterCode.get_moves()
        liMoves = map(lambda x: x[1:], liMoves)

        if move in liMoves:
            FasterCode.move_pv(move[:2], move[2:4], move[4:])
            xfen = FasterCode.get_fen()
            wdl = self.wdl(xfen)
            if wdl:
                wdl = -wdl
            return wdl
        else:
            return None

    def close(self):
        if self.tb:
            self.tb.close()
            self.tb = None
