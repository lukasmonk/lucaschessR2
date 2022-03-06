import os
import subprocess

from PySide2 import QtCore, QtWidgets

import Code
from Code.Polyglots import Books
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import QTUtil2, SelectFiles
from Code.QT import QTVarios
from Code import Util


class WBooksCrear(QtWidgets.QDialog):
    def __init__(self, w_parent):

        QtWidgets.QDialog.__init__(self, w_parent)

        self.w_parent = w_parent

        self.file = ""

        self.setWindowTitle(_("Create a new book"))
        self.setWindowIcon(Iconos.Libros())
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        f = Controles.TipoLetra(puntos=9, peso=75)

        self.configuration = Code.configuration
        fvar = self.configuration.file_books
        self.list_books = Books.ListBooks()
        self.list_books.restore_pickle(fvar)

        lbFichero = Controles.LB(self, _("Book to create") + ":").ponFuente(f)
        self.btFichero = Controles.PB(self, "", self.buscaFichero, False).anchoMinimo(450).ponFuente(f)
        lbMaxPly = Controles.LB(self, _("Maximum movements") + ":").ponFuente(f)
        self.sbMaxPly = Controles.SB(self, 0, 0, 999).tamMaximo(50)
        lbMinGame = Controles.LB(self, _("Minimum number of games") + ":").ponFuente(f)
        self.sbMinGame = Controles.SB(self, 3, 1, 999).tamMaximo(50)
        lbMinScore = Controles.LB(self, _("Minimum score") + ":").ponFuente(f)
        self.sbMinScore = Controles.SB(self, 0, 0, 100).tamMaximo(50)
        self.chbOnlyWhite = Controles.CHB(self, _("White only"), False).ponFuente(f)
        self.chbOnlyBlack = Controles.CHB(self, _("Black only"), False).ponFuente(f)
        self.chbUniform = Controles.CHB(self, _("Uniform distribution"), False).ponFuente(f)

        lyf = Colocacion.H().control(lbFichero).control(self.btFichero)
        ly = Colocacion.G().margen(15)
        ly.otroc(lyf, 0, 0, 1, 2)
        ly.controld(lbMaxPly, 1, 0).control(self.sbMaxPly, 1, 1)
        ly.controld(lbMinGame, 2, 0).control(self.sbMinGame, 2, 1)
        ly.controld(lbMinScore, 3, 0).control(self.sbMinScore, 3, 1)
        ly.controlc(self.chbOnlyWhite, 4, 0, 1, 2)
        ly.controlc(self.chbOnlyBlack, 5, 0, 1, 2)
        ly.controlc(self.chbUniform, 6, 0, 1, 2)

        # Toolbar
        li_acciones = [(_("Accept"), Iconos.Aceptar(), "aceptar"), None, (_("Cancel"), Iconos.Cancelar(), "cancelar"), None]
        tb = Controles.TB(self, li_acciones)

        # Layout
        layout = Colocacion.V().control(tb).otro(ly).margen(3)
        self.setLayout(layout)

    def buscaFichero(self):
        fbin = SelectFiles.salvaFichero(self, _("Polyglot book"), self.list_books.path, "bin", True)
        if fbin:
            self.list_books.path = os.path.dirname(fbin)
            self.file = fbin
            self.btFichero.set_text(self.file)

    def process_toolbar(self):
        accion = self.sender().key
        if accion == "aceptar":
            self.aceptar()
        elif accion == "cancelar":
            self.reject()

    def aceptar(self):
        if not self.file:
            return

        # Creamos el pgn
        fichTemporal = self.w_parent.damePGNtemporal(self)
        if not fichTemporal:
            return

        me = QTUtil2.unMomento(self)

        # Creamos la linea de ordenes
        exe = "%s/_tools/polyglot/polyglot" % Code.folder_engines
        li = [os.path.abspath(exe), "make-book", "-pgn", fichTemporal, "-bin", self.file]
        Util.remove_file(self.file)

        maxPly = self.sbMaxPly.valor()
        minGame = self.sbMinGame.valor()
        minScore = self.sbMinScore.valor()
        onlyWhite = self.chbOnlyWhite.valor()
        onlyBlack = self.chbOnlyBlack.valor()
        uniform = self.chbUniform.valor()
        if maxPly:
            li.append("-max-ply")
            li.append("%d" % maxPly)
        if minGame and minGame != 3:
            li.append("-min-game")
            li.append("%d" % minGame)
        if minScore:
            li.append("-min-score")
            li.append("%d" % minScore)
        if onlyBlack:
            li.append("-only-black")
        if onlyWhite:
            li.append("-only-white")
        if uniform:
            li.append("-uniform")

        # Ejecutamos
        process = subprocess.Popen(li, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Mostramos el resultado
        txt = process.stdout.read()
        if os.path.isfile(self.file):
            txt += "\n" + _X(_("Book created : %1"), self.file)
        me.final()
        QTUtil2.message_bold(self, txt)

        Util.remove_file(fichTemporal)

        name = os.path.basename(self.file)[:-4]
        b = Books.Book("P", name, self.file, False)
        self.list_books.nuevo(b)
        fvar = self.configuration.file_books
        self.list_books.save_pickle(fvar)

        self.accept()


def polyglotCrear(owner):
    w = WBooksCrear(owner)
    w.exec_()


def polyglotUnir(owner):
    lista = [(None, None)]

    dict1 = {"FICHERO": "", "EXTENSION": "bin", "SISAVE": False}
    lista.append((_("File") + " 1 :", dict1))
    dict2 = {"FICHERO": "", "EXTENSION": "bin", "SISAVE": False}
    lista.append((_("File") + " 2 :", dict2))
    dictr = {"FICHERO": "", "EXTENSION": "bin", "SISAVE": True}
    lista.append((_("Book to create") + ":", dictr))

    while True:
        resultado = FormLayout.fedit(lista, title=_("Merge two books in one"), parent=owner, anchoMinimo=460, icon=Iconos.Libros())
        if resultado:
            resultado = resultado[1]
            error = None
            f1 = resultado[0]
            f2 = resultado[1]
            fr = resultado[2]

            if (not f1) or (not f2) or (not fr):
                error = _("Not indicated all files")
            elif f1 == f2:
                error = _("File") + " 1 = " + _("File") + " 2"
            elif f1 == fr:
                error = _("File") + " 1 = " + _("Book to create")
            elif f2 == fr:
                error = _("File") + " 2 = " + _("Book to create")

            if error:
                dict1["FICHERO"] = f1
                dict2["FICHERO"] = f2
                dictr["FICHERO"] = fr
                QTUtil2.message_error(owner, error)
                continue
        else:
            return

        exe = "%s/_tools/polyglot/polyglot" % Code.folder_engines

        li = [os.path.abspath(exe), "merge-book", "-in1", f1, "-in2", f2, "-out", fr]
        try:
            os.remove(fr)
        except:
            pass

        # Ejecutamos
        me = QTUtil2.unMomento(owner)

        process = subprocess.Popen(li, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Mostramos el resultado
        txt = process.stdout.read()
        if os.path.isfile(fr):
            txt += "\n" + _X(_("Book created : %1"), fr)
        me.final()
        QTUtil2.message_bold(owner, txt)

        return


def eligeJugadaBooks(main_window, li_moves, is_white, siSelectSiempre=True):
    main_window.cursorFueraBoard()
    menu = QTVarios.LCMenu(main_window)
    f = Controles.TipoLetra(name=Code.font_mono, puntos=10)
    menu.ponFuente(f)

    titulo = _("White") if is_white else _("Black")
    icono = Iconos.Carpeta()

    menu.opcion(None, titulo, icono)
    menu.separador()

    icono = Iconos.PuntoNaranja() if is_white else Iconos.PuntoNegro()

    for from_sq, to_sq, promotion, pgn, peso in li_moves:
        menu.opcion((from_sq, to_sq, promotion), pgn, icono)
        menu.separador()

    resp = menu.lanza()
    if resp:
        return resp
    else:
        if siSelectSiempre:
            from_sq, to_sq, promotion, pgn, peso = li_moves[0]
            return from_sq, to_sq, promotion
        else:
            return None


def saltaJugadaBooks(manager, li_moves, move):
    is_white = move.position_before.is_white
    menu = QTVarios.LCMenu(manager.main_window)
    f = Controles.TipoLetra(name=Code.font_mono, puntos=10)
    menu.ponFuente(f)

    icono = Iconos.PuntoNaranja() if is_white else Iconos.PuntoNegro()
    iconoActual = Iconos.Mover()

    for from_sq, to_sq, promotion, pgn, peso in li_moves:
        ico = iconoActual if from_sq == move.from_sq and to_sq == move.to_sq else icono
        menu.opcion((from_sq, to_sq, promotion), pgn, ico)
        menu.separador()

    menu.opcion((None, None, None), _("Edit data"), Iconos.PuntoVerde())

    return menu.lanza()
