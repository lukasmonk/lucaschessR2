# This code is a translation to python from pg_key.c and pg_show.c released in the public domain by Michel Van den Bergh.
# http://alpha.uhasselt.be/Research/Algebra/Toga

import os
import random

import Code
from Code import Util
from Code.Base import Position
from Code.Base.Constantes import BOOK_BEST_MOVE, BOOK_RANDOM_UNIFORM, BOOK_RANDOM_PROPORTIONAL
from Code.Books import Polyglot


class ListBooks:
    def __init__(self):
        self.lista = []
        self.path = ""

        # S = Manager solo
        # P = PGN
        # M = EntMaquina
        # T = Tutor
        self._modoAnalisis = ""

        self.restore()

    def restore_pickle(self, file):
        dic_booklist = Util.restore_pickle(file)
        if dic_booklist:
            self.lista = []
            for dic_book in dic_booklist["lista"]:
                b = Book("P", "", "", False)
                b.from_dic(dic_book)
                self.lista.append(b)
            self.path = dic_booklist["path"]
            if not os.path.isdir(self.path):
                self.path = Code.configuration.folder_userdata()
            self._modoAnalisis = dic_booklist["_modoAnalisis"]
            self.at_least_one()

    def save_pickle(self, file):
        dic = {"path": self.path, "_modoAnalisis": self._modoAnalisis, "lista": [book.to_dic() for book in self.lista]}
        Util.save_pickle(file, dic)

    def restore(self):
        self.restore_pickle(Code.configuration.file_books)
        self.verify()

    def save(self):
        self.save_pickle(Code.configuration.file_books)

    def at_least_one(self):
        if len(self.lista) > 0:
            return
        ok_gm = False
        ok_rd = False

        engine_rodent = Code.configuration.buscaRival("rodentii")
        path_rodent = Util.opj(os.path.dirname(engine_rodent.path_exe), "books", "rodent.bin")

        for book in self.lista:
            if Util.same_path(book.path, Code.tbook):
                ok_gm = True
            if Util.same_path(book.path, path_rodent):
                ok_rd = True

        if not ok_gm:
            bookdef = Code.tbook
            b = Book("P", os.path.basename(bookdef)[:-4], bookdef, True)
            self.lista.append(b)
        if not ok_rd:
            b = Book("P", "Rodent", path_rodent, False)
            self.lista.append(b)

    def modoAnalisis(self, apli):
        return apli in self._modoAnalisis

    def porDefecto(self, book=None):
        if book:
            for book1 in self.lista:
                book1.pordefecto = False
            book.pordefecto = True
        else:
            self.at_least_one()
            for book in self.lista:
                if book.pordefecto:
                    return book
            return self.lista[0]

    def seek_book(self, name):
        for book in self.lista:
            if book.name == name:
                return book
        return None

    def verify(self):
        for x in range(len(self.lista) - 1, -1, -1):
            book = self.lista[x]
            if not book.existe():
                del self.lista[x]
        self.at_least_one()

    def nuevo(self, book):
        for libroA in self.lista:
            if libroA.igualque(book):
                return
        self.lista.append(book)
        self.save()

    def borra(self, book):
        for n, libroL in enumerate(self.lista):
            if libroL == book:
                del self.lista[n]


class Book:
    def __init__(self, tipo, name, path, pordefecto, extras=None):
        self.tipo = tipo
        self.name = name
        self.path = Util.norm_path(path)
        self.pordefecto = pordefecto
        self.orden = 100  # futuro ?
        self.extras = extras  # futuro ?

    def clone(self):
        return Book(self.tipo, self.name, self.path, self.pordefecto, self.extras)

    def to_dic(self):
        dic = {
            "tipo": self.tipo,
            "name": self.name,
            "path": self.path,
            "pordefecto": self.pordefecto,
            "orden": self.orden,
            "extras": self.extras,
        }
        return dic

    def from_dic(self, dic):
        self.tipo = dic["tipo"]
        self.name = dic["name"]
        self.path = dic["path"]
        self.pordefecto = dic["pordefecto"]
        self.orden = dic["orden"]
        self.extras = dic["extras"]

    def __eq__(self, other):
        return isinstance(other, Book) and self.igualque(other)

    def igualque(self, otro):
        return self.tipo == otro.tipo and self.name == otro.name and self.path == otro.path

    def existe(self):
        return os.path.isfile(self.path)

    def polyglot(self):
        self.book = Polyglot.Polyglot(self.path)

    def get_list_moves(self, fen):
        li = self.book.lista(self.path, fen)
        position = Position.Position()
        position.read_fen(fen)

        total = 0
        maxim = 0
        for entry in li:
            w = entry.weight
            total += w
            if w > maxim:
                maxim = w

        lista_jugadas = []
        for entry in li:
            pv = entry.pv()
            w = entry.weight
            pc = w * 100.0 / total if total else "?"
            from_sq, to_sq, promotion = pv[:2], pv[2:4], pv[4:]
            pgn = position.pgn_translated(from_sq, to_sq, promotion)
            lista_jugadas.append([from_sq, to_sq, promotion, "%-5s -%7.02f%% -%7d" % (pgn, pc, w), 1.0 * w / maxim])
        return lista_jugadas

    def alm_list_moves(self, fen):
        li = self.book.lista(self.path, fen)
        position = Position.Position()
        position.read_fen(fen)

        total = 0
        maxim = 0
        for entry in li:
            w = entry.weight
            total += w
            if w > maxim:
                maxim = w

        lista_jugadas = []
        st_pvs_included = set()
        for entry in li:
            w = entry.weight
            alm = Util.Record()
            pv = alm.pv = entry.pv()
            st_pvs_included.add(pv.lower())
            alm.from_sq, alm.to_sq, alm.promotion = pv[:2], pv[2:4], pv[4:]
            alm.pgn = position.pgn_translated(alm.from_sq, alm.to_sq, alm.promotion)
            alm.pgnRaw = position.pgn(alm.from_sq, alm.to_sq, alm.promotion)
            alm.fen = fen
            alm.porc = "%0.02f%%" % (w * 100.0 / total,) if total else ""
            alm.weight = w
            lista_jugadas.append(alm)

        # if extended:
        #     for exmove in position.get_exmoves():
        #         pv = exmove.move()
        #         if pv not in st_pvs_included:
        #             FasterCode.set_fen(fen)
        #             from_sq, to_sq, promotion = pv[:2], pv[2:4], pv[4:]
        #             FasterCode.move_pv(from_sq, to_sq, promotion)
        #             new_fen = FasterCode.get_fen()
        #             li = self.book.lista(self.path, new_fen)
        #             if len(li) > 0:
        #                 alm = Util.Record()
        #                 alm.from_sq, alm.to_sq, alm.promotion = from_sq, to_sq, promotion
        #                 alm.pgn = position.pgn_translated(from_sq, to_sq, promotion)
        #                 alm.pgnRaw = position.pgn(from_sq, to_sq, promotion)
        #                 alm.fen = fen
        #                 alm.porc = ""
        #                 alm.weight = 0
        #                 listaJugadas.append(alm)

        return lista_jugadas

    def eligeJugadaTipo(self, fen, tipo):
        maxim = 0
        li_max = []
        li = self.book.lista(self.path, fen)
        nli = len(li)
        if nli == 0:
            return None

        elif nli == 1:
            pv = li[0].pv()

        elif tipo == BOOK_BEST_MOVE:  # Mejor position
            for entry in li:
                w = entry.weight
                if w > maxim:
                    maxim = w
                    li_max = [entry]
                elif w == maxim:
                    li_max.append(entry)
            pos = random.randint(0, len(li_max) - 1) if len(li_max) > 1 else 0
            pv = li_max[pos].pv()

        elif tipo == BOOK_RANDOM_UNIFORM:  # Aleatorio uniforme
            pos = random.randint(0, len(li) - 1)
            pv = li[pos].pv()

        elif tipo == BOOK_RANDOM_PROPORTIONAL:  # Aleatorio proporcional
            liW = [x.weight for x in li]
            t = sum(liW)
            num = random.randint(1, t)
            pos = 0
            t = 0
            for n, x in enumerate(liW):
                t += x
                if num <= t:
                    pos = n
                    break
            pv = li[pos].pv()

        else:
            return None

        return pv.lower()

    def miraListaPV(self, fen, siMax, onlyone=True):
        li = self.book.lista(self.path, fen)

        li_resp = []
        if siMax:
            maxim = -1
            for entry in li:
                w = entry.weight
                if w > maxim:
                    maxim = w
                    li_resp = [entry.pv()]
                elif w == maxim and not onlyone:
                    li_resp.append(entry.pv())
        else:
            for entry in li:
                li_resp.append(entry.pv())

        return li_resp


class Libro(Book):  # Cambio de denominación, error en restore wplayagainst engine
    pass


class BookGame(Book):
    def __init__(self, path):
        name = os.path.basename(path)[:-4]
        Book.__init__(self, "P", name, path, True)
        self.polyglot()
        self.activo = True

    def activar(self):
        self.activo = True

    def si_esta(self, fen, move):
        if self.activo:
            lista_jugadas = self.get_list_moves(fen)
            if lista_jugadas:
                for apdesde, aphasta, appromotion, nada, nada1 in lista_jugadas:
                    mx = apdesde + aphasta + appromotion
                    if mx.strip().lower() == move:
                        return True
            else:
                self.activo = False
        return False
