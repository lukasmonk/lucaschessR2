import random

import Code
from Code.Base import Position
from Code.Base.Constantes import RESULT_DRAW, RESULT_WIN_WHITE, RESULT_WIN_BLACK
from Code.SQL import UtilSQL


class DBendings:
    def __init__(self, configuration):
        self.configuration = configuration
        self.db_data = UtilSQL.DictRawSQL(self.configuration.file_endings_gtb())
        self.db_examples = UtilSQL.DictRawSQL(Code.path_resource("IntFiles", "gtb5.db"))

        self.current_key = None
        self.current_dicfen = {}
        self.current_listfen = []
        self.current_fen = None
        self.examples_auto = True  # Si tras cambiar de tipo se cargan ejemplos si no hay fens del tipo

    def set_examples_auto(self, ok):
        self.examples_auto = ok

    def test_tipo(self, key):
        lik = self.keylist()
        if key not in lik:
            key = lik[0]
        return key

    def keylist(self, examples=True, own=True):
        pzs_gaviota = Code.configuration.pieces_gaviota()
        lst = []
        if examples:
            lst.extend(self.db_examples.keys())
        if own:
            lst.extend(self.db_data.keys())
        st = set(lst)
        lst = list(st)
        lst.sort()
        return [x for x in lst if len(x) <= pzs_gaviota]

    def read_key(self, key, order):
        if not (key in self.db_data) and self.examples_auto:
            cp = Position.Position()
            lista = self.db_examples[key]
            if lista:
                d = {}
                for mt, fen in lista:
                    cp.read_fen(fen)
                    d[fen] = {"MATE": mt, "XFEN": cp.label(), "ORIGIN": "example"}
                self.db_data[key] = d
        self.current_dicfen = self.db_data.get(key, {})
        self.current_key = key
        self.current_fen = None
        self.current_listfen = list(self.current_dicfen.keys())
        self.current_order = order

        if order == "random":
            random.shuffle(self.current_listfen)
        elif order == "difficulty":
            self.current_listfen.sort(
                key=lambda x: self.current_dicfen[x]["MATE"] if self.current_dicfen[x]["MATE"] > 0 else 999
            )

        return len(self.current_listfen)

    def pos_fen(self, fenm2):
        return self.current_listfen.index(fenm2)

    def current_num_fens(self):
        return len(self.current_listfen)

    def get_current_fen(self, pos):
        self.current_fen = self.current_listfen[pos]
        return self.current_fen

    def current_fen_field(self, pos, field, default=0):
        fen = self.current_listfen[pos]
        return self.current_dicfen[fen].get(field, default)

    def set_current_fen_field(self, pos, field, value):
        fen = self.current_listfen[pos]
        dic = self.current_dicfen[fen]
        dic[field] = value
        self.db_data[self.current_key] = self.current_dicfen

    def register_try(self, pos, game, ms, moves, is_helped):
        fen = self.current_listfen[pos]
        dic_fen = self.current_dicfen[fen]

        dic_fen["TRIES"] = dic_fen.get("TRIES", 0) + 1

        mensaje = ""

        is_white = game.first_position.is_white

        mt = dic_fen["MATE"]
        result = game.resultado()
        if mt == 0:
            success = result == RESULT_DRAW
        else:
            success = (result == RESULT_WIN_WHITE) if is_white else (result == RESULT_WIN_BLACK)
        if success and not is_helped:
            dic_fen["TRIES_OK"] = dic_fen.get("TRIES_OK", 0) + 1
            ms_previo = dic_fen.get("TIMEMS")
            if (ms_previo is None) or (ms < ms_previo):
                label = _("New best time")
                dic_fen["TIMEMS"] = ms
            else:
                label = _("Time")

            mensaje += "%s: %.1f\n" % (label, ms / 1000)

            moves_previo = dic_fen.get("MOVES")
            if (moves_previo is None) or (moves < moves_previo):
                label = _("New best number of movements")
                dic_fen["MOVES"] = moves
            else:
                label = _("Number of movements")
            mensaje += "%s: %d\n" % (label, moves)
        self.db_data[self.current_key] = self.current_dicfen
        return success, mensaje

    def register_empty_try(self, pos):
        fen = self.current_listfen[pos]
        dic_fen = self.current_dicfen[fen]
        dic_fen["TRIES"] = dic_fen.get("TRIES", 0) + 1
        self.db_data[self.current_key] = self.current_dicfen

    def reset_data_pos(self, pos):
        fen = self.current_listfen[pos]
        dic_fen = self.current_dicfen[fen]
        for k in ("TRIES", "TRIES_OK", "TIMEMS", "MOVES"):
            if k in dic_fen:
                del dic_fen[k]
        self.db_data[self.current_key] = self.current_dicfen

    def close(self):
        self.db_data.close()
        self.db_examples.close()

    def insert(self, fen, mt):
        cp = Position.Position()
        cp.read_fen(fen)
        key = cp.pzs_key()
        fen_m2 = cp.fenm2()
        self.read_key(key, "initial")
        if fen_m2 not in self.current_dicfen:
            self.current_dicfen[fen_m2] = {"MATE": mt, "XFEN": cp.label(), "ORIGIN": "manual"}
            self.db_data[key] = self.current_dicfen
            self.current_listfen.append(fen_m2)
        return key, fen_m2

    def add_examples(self, key):
        cp = Position.Position()
        lista = self.db_examples[key]
        if lista:
            num_imported = 0
            d = self.db_data.get(key, {})
            for mt, fen_m2 in lista:
                if fen_m2 not in d:
                    cp.read_fen(fen_m2)
                    d[fen_m2] = {"MATE": mt, "XFEN": cp.label(), "ORIGIN": "example"}
                    num_imported += 1
            self.db_data[key] = d
            return num_imported
        else:
            return 0

    def import_lista(self, tipo, li_fens_mt):
        cp = Position.Position()
        self.db_data.set_faster_mode()
        for fen, mt in li_fens_mt:
            cp.read_fen(fen)
            key = cp.pzs_key()
            fen_m2 = cp.fenm2()
            dic = self.db_data.get(key, {})
            if fen_m2 in dic:
                dic[fen_m2]["ORIGIN"] = tipo
            else:
                dic[fen_m2] = {"MATE": mt, "XFEN": cp.label(), "ORIGIN": tipo}
            self.db_data[key] = dic
        self.db_data.set_normal_mode()

    def remove(self, pos):
        fen = self.current_listfen[pos]
        del self.current_dicfen[fen]
        if len(self.current_dicfen) == 0:
            del self.db_data[self.current_key]
            self.read_key(self.keylist()[0], self.current_order)
        else:
            self.db_data[self.current_key] = self.current_dicfen
            del self.current_listfen[pos]

    def remove_results(self, only_current_key):
        self.db_data.set_faster_mode()
        li_fields = ["TRIES", "TRIES_OK", "MOVES", "TIMEMS"]

        def haz(key):
            dic_data = self.db_data[key]
            if dic_data is None:
                return
            changed = False
            for fen_m2, dic_fenm2 in dic_data.items():
                for field in li_fields:
                    if field in dic_fenm2:
                        del dic_fenm2[field]
                        changed = True
            if changed:
                self.db_data[key] = dic_data

        if only_current_key:
            haz(self.current_key)
        else:
            for key in self.db_data.keys():
                haz(key)

        self.db_data.set_normal_mode()

    def remove_positions(self, only_current_key):
        def haz(key):
            dic_data = self.db_data[key]
            if dic_data is None:
                return
            li_borrar = [fen_m2 for fen_m2, dic_fenm2 in dic_data.items() if dic_fenm2["ORIGIN"] == "manual"]
            for fen_m2 in li_borrar:
                del dic_data[fen_m2]
            self.db_data[key] = dic_data

        if only_current_key:
            haz(self.current_key)
        else:
            for key in self.db_data.keys():
                haz(key)
