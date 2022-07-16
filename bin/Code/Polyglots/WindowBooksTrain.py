import os

import Code
from Code import Util
from Code.Polyglots import Books
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTUtil2, SelectFiles
from Code.QT import QTVarios
from Code.QT import LCDialog


class WBooksTrain(LCDialog.LCDialog):
    ISWHITE, BOOK_PLAYER, BOOK_RIVAL, ALWAYS_HIGHEST, RESP_RIVAL, SHOW_MENU = range(6)

    def __init__(self, procesador):
        w_parent = procesador.main_window
        self.configuration = procesador.configuration
        self.procesador = procesador

        titulo = _("Training with a book")
        icono = Iconos.Libros()

        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, "bookstrain")

        self.setMinimumWidth(450)

        flb = Controles.TipoLetra(puntos=10)

        # Variables antiguas
        dic_data = self.restore()

        # Toolbar
        liAcciones = [
            (_("Accept"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
        ]
        tb = QTVarios.LCTB(self, liAcciones)

        # Side
        self.rb_white = Controles.RB(self, _("White"))
        self.rb_white.setChecked(dic_data.get(self.ISWHITE, True))
        self.rb_black = Controles.RB(self, _("Black"))
        self.rb_black.setChecked(not dic_data.get(self.ISWHITE, True))

        hbox = Colocacion.H().relleno().control(self.rb_white).espacio(10).control(self.rb_black).relleno()
        gb_side = Controles.GB(self, _("Side you play with"), hbox).ponFuente(flb)

        # Books
        fvar = self.configuration.file_books
        self.list_books = Books.ListBooks()
        self.list_books.restore_pickle(fvar)
        self.list_books.check()
        li = [(x.name, x) for x in self.list_books.lista]

        # Player
        book_player = li[0][1] if li else None

        nom_book_player = dic_data.get(self.BOOK_PLAYER)
        if nom_book_player:
            for nom, book in li:
                if nom == nom_book_player:
                    book_player = book
                    break
        self.cb_player = Controles.CB(self, li, book_player)

        btNuevo = Controles.PB(self, "", self.nuevo, plano=False).ponIcono(Iconos.Nuevo(), icon_size=16)
        btBorrar = Controles.PB(self, "", self.borrar, plano=False).ponIcono(Iconos.Borrar(), icon_size=16)

        self.chb_highest = Controles.CHB(
            self, _("Always the highest percentage"), dic_data.get(self.ALWAYS_HIGHEST, False)
        )

        lybook = Colocacion.H().relleno().control(self.cb_player).control(btNuevo).control(btBorrar).relleno()
        ly_select = Colocacion.H().relleno().control(self.chb_highest).relleno()

        ly = Colocacion.V().otro(lybook).espacio(10).otro(ly_select)
        gb_player = Controles.GB(self, _("Player's book"), ly).ponFuente(flb)

        # Rival
        book_rival = book_player

        nom_book_rival = dic_data.get(self.BOOK_RIVAL)
        if nom_book_rival:
            for nom, book in li:
                if nom == nom_book_rival:
                    book_rival = book
                    break
        self.cb_rival = Controles.CB(self, li, book_rival)

        li = (
            (_("Selected by the player"), "su"),
            (_("Uniform random"), "au"),
            (_("Proportional random"), "ap"),
            (_("Always the highest percentage"), "mp"),
        )
        self.cb_resp_rival = Controles.CB(self, li, dic_data.get(self.RESP_RIVAL, "au"))

        ly = Colocacion.V().controlc(self.cb_rival).espacio(10).controlc(self.cb_resp_rival)
        gb_rival = Controles.GB(self, _("Rival book"), ly).ponFuente(flb)

        self.chb_showmenu = Controles.CHB(
            self, _("Display a menu of alternatives if move is invalid"), dic_data.get(self.SHOW_MENU, True)
        )
        if Code.configuration.x_digital_board:
            self.chb_showmenu.set_value(False)
            self.chb_showmenu.hide()

        vlayout = Colocacion.V()
        vlayout.control(gb_side).espacio(5)
        vlayout.control(gb_player).espacio(5)
        vlayout.control(gb_rival).espacio(5)
        vlayout.control(self.chb_showmenu).espacio(5)
        vlayout.margen(20)

        layout = Colocacion.V().control(tb).otro(vlayout).margen(3)

        self.setLayout(layout)

        self.restore_video()

    def aceptar(self):
        self.is_white = self.rb_white.isChecked()
        self.book_player = self.cb_player.valor()
        self.player_highest = self.chb_highest.valor()
        self.book_rival = self.cb_rival.valor()
        self.rival_resp = self.cb_resp_rival.valor()
        self.show_menu = self.chb_showmenu.valor()
        self.save()

        self.save_video()
        self.accept()

    def cancelar(self):
        self.save_video()
        self.reject()

    def nuevo(self):
        fbin = SelectFiles.leeFichero(self, self.list_books.path, "bin", titulo=_("Polyglot book"))
        if fbin:
            self.list_books.path = os.path.dirname(fbin)
            nombre = os.path.basename(fbin)[:-4]
            b = Books.Book("P", nombre, fbin, False)
            self.list_books.nuevo(b)
            self.rehacer_cb(b)

    def borrar(self):
        book = self.cb_player.valor()
        if book:
            if QTUtil2.pregunta(self, _X(_("Delete from list the book %1?"), book.name)):
                self.list_books.borra(book)
                self.rehacer_cb(None)

    def rehacer_cb(self, inicial):
        fvar = self.configuration.file_books
        self.list_books.save_pickle(fvar)
        li = [(x.name, x) for x in self.list_books.lista]
        if inicial is None:
            inicial = li[0][1] if li else None
        self.cb_player.rehacer(li, inicial)
        self.cb_rival.rehacer(li, inicial)

    def restore(self):
        resp = Util.restore_pickle(self.configuration.file_train_books)
        return resp if resp else {}

    def save(self):
        dic = {
            self.ISWHITE: self.is_white,
            self.BOOK_PLAYER: self.book_player.name,
            self.ALWAYS_HIGHEST: self.player_highest,
            self.BOOK_RIVAL: self.book_rival.name,
            self.RESP_RIVAL: self.rival_resp,
            self.SHOW_MENU: self.show_menu,
        }
        Util.save_pickle(self.configuration.file_train_books, dic)


def eligeJugadaBooks(pantalla, liJugadas, is_white, siSelectSiempre=True):
    pantalla.cursorFueraTablero()
    menu = QTVarios.LCMenu(pantalla)
    f = Controles.TipoLetra(name=Code.font_mono, puntos=10)
    menu.ponFuente(f)

    titulo = _("White") if is_white else _("Black")
    icono = Iconos.Carpeta()

    menu.opcion(None, titulo, icono)
    menu.separador()

    icono = Iconos.PuntoNaranja() if is_white else Iconos.PuntoNegro()

    for xfrom, xto, promotion, pgn, peso in liJugadas:
        menu.opcion((xfrom, xto, promotion), pgn, icono)
        menu.separador()

    resp = menu.lanza()
    if resp:
        return resp
    else:
        if siSelectSiempre:
            xfrom, xto, promotion, pgn, peso = liJugadas[0]
            return xfrom, xto, promotion
        else:
            return None
