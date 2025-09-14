import os.path

from PySide2 import QtGui

import Code
from Code import Util
from Code.Base.Constantes import (
    KIB_GAVIOTA,
    KIB_INDEXES,
    KIB_POLYGLOT,
    KIB_AFTER_MOVE,
    KIB_THREATS,
    KIB_BEFORE_MOVE,
    KIB_CANDIDATES,
    KIB_BESTMOVE_ONELINE,
    KIB_BESTMOVE,
    KIB_STOCKFISH,
    KIB_DATABASES,
)
from Code.Books import Books
from Code.Engines import Engines
from Code.Engines import Priorities
from Code.QT import Iconos


def cb_pointofview_options():
    li_options = [(_("Before current move"), KIB_BEFORE_MOVE), (_("After current move"), KIB_AFTER_MOVE)]
    return li_options


class Tipos:
    def __init__(self):
        self.li_tipos = (
            (KIB_CANDIDATES, _("Candidates"), Iconos.pmKibitzer().scaledToWidth(16)),
            (KIB_BESTMOVE, _("Best move"), Iconos.pmKibitzer().scaledToWidth(16)),
            (KIB_INDEXES, _("Indexes") + " - RodentII", Iconos.pmPuntoNegro()),
            (KIB_BESTMOVE_ONELINE, _("Best move in one line"), Iconos.pmKibitzer().scaledToWidth(16)),
            (KIB_STOCKFISH, _("Stockfish evaluation"), Iconos.pmPuntoAmarillo()),
            (KIB_THREATS, _("Threats"), Iconos.pmPuntoAzul()),
            (KIB_POLYGLOT, _("Polyglot book"), Iconos.pmBook().scaledToWidth(16)),
            (KIB_GAVIOTA, _("Gaviota Tablebases"), Iconos.pmFinales().scaledToWidth(16)),
            (KIB_DATABASES, _("Databases"), Iconos.pmDatabase().scaledToWidth(16)),
        )

    def combo(self):
        return [(label, key) for key, label, pm in self.li_tipos]

    def comboSinIndices(self):
        return [
            (label, key) for key, label, pm in self.li_tipos if
            key not in (KIB_INDEXES, KIB_GAVIOTA, KIB_POLYGLOT, KIB_DATABASES)
        ]

    def texto(self, tipo):
        for tp, nom, pm in self.li_tipos:
            if tp == tipo:
                return nom

    def dicDelegado(self):
        return {tp: pm for tp, txt, pm in self.li_tipos}

    def dicIconos(self):
        return {tp: QtGui.QIcon(pm) for tp, txt, pm in self.li_tipos}


class Kibitzer(Engines.Engine):
    def __init__(self):
        Engines.Engine.__init__(self)

        self.tipo = None
        self.huella = None
        self.prioridad = Priorities.priorities.normal
        self.visible = True
        self.name = None
        self.pointofview = KIB_AFTER_MOVE

    def pon_huella(self, li_engines):
        li_huellas = [en.huella for en in li_engines if en != self]
        while True:
            self.huella = Util.huella()
            if self.huella not in li_huellas:
                return

    def clonar(self, li_engines):
        otro = Kibitzer()
        otro.restore(self.save())
        otro.tipo = self.tipo
        otro.prioridad = self.prioridad
        otro.name = self.name
        otro.visible = True
        otro.pointofview = self.pointofview
        otro.pon_huella(li_engines)
        lista = [en.name for en in li_engines]
        d = 0
        while otro.name in lista:
            d += 1
            otro.name = "%s-%d" % (self.name, d)
        return otro

    def ctipo(self):
        return Tipos().texto(self.tipo)

    def cpriority(self):
        return Priorities.priorities.texto(self.prioridad)

    def cpointofview(self):
        for txt, key in cb_pointofview_options():
            if self.pointofview == key:
                return txt

    def read_uci_options(self):
        if self.tipo in (KIB_GAVIOTA, KIB_POLYGLOT):
            return
        Engines.Engine.read_uci_options(self)

    def restore(self, txt):
        Util.restore_obj_pickle(self, txt)
        ok = True
        if self.tipo in (KIB_CANDIDATES, KIB_BESTMOVE, KIB_BESTMOVE_ONELINE, KIB_THREATS, KIB_STOCKFISH):
            if not os.path.isfile(self.path_exe):
                eng = Code.configuration.buscaRival(self.alias)
                if eng:
                    self.path_exe = eng.path_exe
                else:
                    ok = False

        elif self.tipo == KIB_POLYGLOT:
            if not os.path.isfile(self.path_exe):
                lbooks = Books.ListBooks()
                book = lbooks.seek_book(self.key)
                if book:
                    self.path_exe = book.path
                else:
                    ok = False
        return ok

class Kibitzers:
    def __init__(self):
        self.file = Code.configuration.file_kibitzers()
        self.lista, self.lastfolder = self.read()

    def read(self):
        lista = []
        lastfolder = ""
        dic = Util.restore_pickle(self.file)

        if dic:
            lastfolder = dic.get("LASTFOLDER", "")
            lista_pk = dic.get("LISTA", [])
            if lista_pk:
                for txt in lista_pk:
                    kib = Kibitzer()
                    if kib.restore(txt):
                        lista.append(kib)
        return lista, lastfolder

    def number(self, huella):
        for num, kib in enumerate(self.lista):
            if kib.huella == huella:
                return num

    def save(self):
        dic = {"LISTA": [en.save() for en in self.lista], "LASTFOLDER": self.lastfolder}
        Util.save_pickle(self.file, dic)

    def nuevo_engine(self, name, engine, tipo, prioridad, pointofview, fixed_time, fixed_depth):
        kib = Kibitzer()
        kib.pon_huella(self.lista)
        eng = Code.configuration.buscaRival(engine)
        kib.restore(eng.save())
        kib.key = name
        kib.name = name
        kib.tipo = tipo
        kib.prioridad = prioridad
        kib.pointofview = pointofview
        kib.max_time = fixed_time
        kib.max_depth = fixed_depth
        self.lista.append(kib)
        self.save()
        return len(self.lista) - 1

    def nuevo_polyglot(self, book):
        kib = Kibitzer()
        kib.pon_huella(self.lista)
        kib.name = "%s: %s" % (_("Book"), book.name)
        kib.key = book.name
        kib.tipo = KIB_POLYGLOT
        kib.path_exe = book.path
        self.lista.append(kib)
        self.save()
        return len(self.lista) - 1

    def nuevo_gaviota(self):
        for kib in self.lista:
            if kib.tipo == KIB_GAVIOTA:
                return
        kib = Kibitzer()
        kib.pon_huella(self.lista)
        kib.name = _("Gaviota Tablebases")
        kib.key = kib.name
        kib.tipo = KIB_GAVIOTA
        kib.autor = "Miguel A. Ballicora"
        self.lista.append(kib)
        self.save()
        return len(self.lista) - 1

    def nuevo_index(self):
        for kib in self.lista:
            if kib.tipo == KIB_INDEXES:
                return
        kib = Kibitzer()
        eng = Code.configuration.buscaRival("rodentii")
        kib.restore(eng.save())
        kib.pon_huella(self.lista)
        kib.name = _("Indexes") + " - RodentII"
        kib.key = kib.name
        kib.tipo = KIB_INDEXES
        kib.autor = "Michele Tumbarello"
        self.lista.append(kib)
        self.save()
        return len(self.lista) - 1

    def nuevo_database(self, path_database):
        kib = Kibitzer()
        kib.pon_huella(self.lista)
        kib.name = _("Database") + ": " + os.path.basename(path_database)[:-5]
        kib.path_exe = path_database
        kib.key = kib.name
        kib.tipo = KIB_DATABASES
        kib.autor = ""
        self.lista.append(kib)
        self.save()
        return len(self.lista) - 1

    def __len__(self):
        return len(self.lista)

    def kibitzer(self, num):
        return self.lista[num]

    def remove(self, num):
        del self.lista[num]
        self.save()

    def up(self, num):
        if num > 0:
            self.lista[num], self.lista[num - 1] = self.lista[num - 1], self.lista[num]
            self.save()
            return num - 1
        return None

    def down(self, num):
        if num < (len(self.lista) - 1):
            self.lista[num], self.lista[num + 1] = self.lista[num + 1], self.lista[num]
            self.save()
            return num + 1
        return None

    def clonar(self, num):
        kib = self.lista[num].clonar(self.lista)
        self.lista.append(kib)
        self.save()
        return len(self.lista) - 1

    def lista_menu(self):
        d_ico = Tipos().dicIconos()
        li = []
        for kib in self.lista:
            if (kib.tipo in (KIB_CANDIDATES, KIB_BESTMOVE, KIB_BESTMOVE_ONELINE, KIB_POLYGLOT,
                             KIB_THREATS, KIB_STOCKFISH, KIB_DATABASES) and not os.path.isfile(kib.path_exe)):
                continue
            li.append((kib.huella, kib.name, d_ico[kib.tipo]))
        return li
