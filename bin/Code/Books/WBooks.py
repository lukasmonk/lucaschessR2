import os
import os.path
import time

import Code
from Code import Util
from Code.Books import Books
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import SelectFiles


def select_move_books(main_window, li_moves, is_white, always_select):
    main_window.cursorFueraBoard()
    menu = QTVarios.LCMenu(main_window)
    f = Controles.FontType(name=Code.font_mono, puntos=10)
    menu.set_font(f)

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
        if always_select:
            time.sleep(0.2)
            QTUtil.refresh_gui()
            return li_moves[0][0], li_moves[0][1], li_moves[0][2]
        else:
            return None


class WRegisteredBooks(LCDialog.LCDialog):
    def __init__(self, owner):
        self.procesador = Code.procesador
        self.configuration = Code.procesador.configuration
        self.resultado = None

        LCDialog.LCDialog.__init__(self, owner, _("Registered books"), Iconos.Book(), "registered_books")

        self.list_books = Books.ListBooks()

        o_columnas = Columnas.ListaColumnas()
        o_columnas.nueva("NAME", _("Name"), 240)
        o_columnas.nueva("MTIME", _("Last modification"), 130, align_center=True)
        o_columnas.nueva("SIZE", _("Moves"), 100, align_right=True)
        o_columnas.nueva("FOLDER", _("Folder"), 240)
        self.glista = Grid.Grid(self, o_columnas, siSelecFilas=True, siSeleccionMultiple=True)

        tb = QTVarios.LCTB(self)
        tb.new(_("Close"), Iconos.MainMenu(), self.terminar)
        tb.new(_("New"), Iconos.Nuevo(), self.new)
        tb.new(_("Internal books"), Iconos.Import8(), self.importar)
        tb.new(_("Unregister"), Iconos.Borrar(), self.unregister)
        tb.new(_("Up"), Iconos.Arriba(), self.go_up)
        tb.new(_("Down"), Iconos.Abajo(), self.go_down)

        ly = Colocacion.V().control(tb).control(self.glista).margen(4)
        self.setLayout(ly)

        self.register_grid(self.glista)
        self.restore_video(anchoDefecto=742, altoDefecto=329)

        self.glista.gotop()

    def go_up(self):
        row = self.glista.recno()
        if row > 0:
            lista = self.list_books.lista
            lista[row], lista[row - 1] = lista[row - 1], lista[row]
            self.list_books.save()
            self.glista.goto(row - 1, 0)
            self.glista.refresh()

    def go_down(self):
        row = self.glista.recno()
        lista = self.list_books.lista
        if row < len(lista) - 1:
            lista[row], lista[row + 1] = lista[row + 1], lista[row]
            self.glista.goto(row + 1, 0)
            self.glista.refresh()

    def grid_dato(self, grid, row, o_columna):
        col = o_columna.key
        book: Books.Book = self.list_books.lista[row]
        if col == "MTIME":
            return Util.localDateT(Util.datefile(book.path))
        elif col == "NAME":
            return book.name
        elif col == "SIZE":
            return "{:,}".format(Util.filesize(book.path) // 16).replace(",", ".")
        elif col == "FOLDER":
            return Code.relative_root(os.path.dirname(book.path))

    def grid_num_datos(self, grid):
        return len(self.list_books.lista)

    def closeEvent(self, event):  # Cierre con X
        self.save_video()

    def terminar(self):
        self.save_video()
        self.accept()

    def new(self):
        fbin = SelectFiles.leeFichero(self, self.list_books.path, "bin", titulo=_("Polyglot book"))
        if fbin:
            self.list_books.path = os.path.dirname(fbin)
            name = os.path.basename(fbin)[:-4]
            book = Books.Book("P", name, fbin, True)
            self.list_books.nuevo(book)
            self.glista.refresh()

    def unregister(self):
        li = self.glista.recnosSeleccionados()
        if len(li) > 0:
            mens = _("Do you want to unregister all selected records?")
            mens += "\n"
            for num, row in enumerate(li, 1):
                mens += "\n%d. %s" % (num, self.list_books.lista[row].name)
            if QTUtil2.pregunta(self, mens):
                li.sort(reverse=True)
                for row in li:
                    del self.list_books.lista[row]
                self.list_books.save()
                self.glista.refresh()

    def importar(self):
        dic_books = self.configuration.dic_books

        def divide(k, path):
            path = Code.relative_root(path)
            li = path.split(os.sep)
            path0 = li[0]
            name = li[-1]
            resto = os.sep.join(li[1:-1])
            return (path, k, path0, resto, name)

        li_books = [divide(k, v) for k, v in dic_books.items()]
        li_books.sort(key=lambda x: x[1])
        li_books.sort(key=lambda x: x[2])
        li_books.sort(key=lambda x: x[3])
        menu = QTVarios.LCMenuRondo(self)
        previo0 = None
        for (path, k, path0, resto, name) in li_books:
            if path0 != previo0:
                submenu = menu.submenu(path0, menu.rondo.otro())
                previo0 = path0
                previo_resto = None
            if resto != previo_resto:
                subsubmenu = submenu.submenu(resto, menu.rondo.otro())
                previo_resto = resto
            subsubmenu.opcion(k, name, menu.rondo.otro())
        resp = menu.lanza()
        if resp:
            fbin = dic_books[resp]
            name = os.path.basename(fbin)[:-4]
            book = Books.Book("P", name, fbin, True)
            self.list_books.nuevo(book)
            self.glista.refresh()


def registered_books(owner):
    w = WRegisteredBooks(owner)
    w.exec()
