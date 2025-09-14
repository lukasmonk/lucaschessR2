import Code
from Code import Util
from Code.Base.Constantes import BOOK_BEST_MOVE, BOOK_RANDOM_UNIFORM, BOOK_RANDOM_PROPORTIONAL, SELECTED_BY_PLAYER
from Code.Books import Books, WBooks
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTVarios


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

        flb = Controles.FontType(puntos=10)

        # Variables antiguas
        dic_data = self.restore()

        # Toolbar
        tb = QTVarios.LCTB(self)
        tb.new(_("Accept"), Iconos.Aceptar(), self.aceptar)
        tb.new(_("Cancel"), Iconos.Cancelar(), self.cancelar)
        tb.new(_("Books"), Iconos.Book(), self.register_books)

        # Side
        self.rb_white = Controles.RB(self, _("White"))
        self.rb_white.setChecked(dic_data.get(self.ISWHITE, True))
        self.rb_black = Controles.RB(self, _("Black"))
        self.rb_black.setChecked(not dic_data.get(self.ISWHITE, True))

        hbox = Colocacion.H().relleno().control(self.rb_white).espacio(10).control(self.rb_black).relleno()
        gb_side = Controles.GB(self, _("Side you play with"), hbox).set_font(flb)

        # Books
        self.list_books = Books.ListBooks()
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

        self.chb_highest = Controles.CHB(
            self, _("Always the highest percentage"), dic_data.get(self.ALWAYS_HIGHEST, False)
        )

        lybook = Colocacion.H().relleno().control(self.cb_player).relleno()
        ly_select = Colocacion.H().relleno().control(self.chb_highest).relleno()

        ly = Colocacion.V().otro(lybook).espacio(10).otro(ly_select)
        gb_player = Controles.GB(self, _("Player's book"), ly).set_font(flb)

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
            (_("Always the highest percentage"), BOOK_BEST_MOVE),
            (_("Proportional random"), BOOK_RANDOM_PROPORTIONAL),
            (_("Uniform random"), BOOK_RANDOM_UNIFORM),
            (_("Selected by the player"), SELECTED_BY_PLAYER),
        )
        self.cb_resp_rival = Controles.CB(self, li, dic_data.get(self.RESP_RIVAL, BOOK_RANDOM_UNIFORM))

        ly = Colocacion.V().controlc(self.cb_rival).espacio(10).controlc(self.cb_resp_rival)
        gb_rival = Controles.GB(self, _("Rival book"), ly).set_font(flb)

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

    def register_books(self):
        WBooks.registered_books(self)
        self.list_books = Books.ListBooks()
        self.list_books.save()
        li = [(x.name, x) for x in self.list_books.lista]
        self.cb_player.rehacer(li, self.cb_player.valor())
        self.cb_rival.rehacer(li, self.cb_rival.valor())

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
