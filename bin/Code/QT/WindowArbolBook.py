from PySide2 import QtWidgets, QtCore

import Code
from Code.Base import Game, Position
from Code.Board import Board
from Code.Books import Books, WBooks
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTVarios


class UnMove:
    def __init__(self, listaMovesPadre, book, fenBase, movBook):

        self.listaMovesPadre = listaMovesPadre
        self.listaMovesHijos = None
        self.book = book
        self.fenBase = fenBase
        self.from_sq, self.to_sq, self.promotion, label, self.ratio = movBook
        label = label.replace(" - ", " ").strip()
        while "  " in label:
            label = label.replace("  ", " ")
        self.pgn, self.porcentaje, self.absoluto = label.split(" ")
        self.porcentaje += "  " * listaMovesPadre.nivel
        self.absoluto += "  " * listaMovesPadre.nivel

        pv = self.from_sq + self.to_sq + self.promotion

        self.game = listaMovesPadre.gameBase.copia()
        self.game.read_pv(pv)

        self.item = None

        self.current_position = len(self.game) - 1

    def row(self):
        return self.listaMovesPadre.liMoves.index(self)

    def analysis(self):
        return self.listaMovesPadre.analisisMov(self)

    def conHijosDesconocidos(self, dbCache):
        if self.listaMovesHijos:
            return False
        fenm2 = self.game.last_position.fenm2()
        return fenm2 in dbCache

    def etiPuntos(self, siExten):
        pts = self.listaMovesPadre.etiPuntosUnMove(self, siExten)
        if not siExten:
            return pts
        nom = self.listaMovesPadre.nomAnalisis()
        if nom:
            return nom + ": " + pts
        else:
            return ""

    def creaHijos(self):
        self.listaMovesHijos = ListaMoves(self, self.book, self.game.last_position.fen())
        return self.listaMovesHijos

    def start(self):
        self.current_position = -1

    def atras(self):
        self.current_position -= 1
        if self.current_position < -1:
            self.start()

    def adelante(self):
        self.current_position += 1
        if self.current_position >= len(self.game):
            self.final()

    def final(self):
        self.current_position = len(self.game) - 1

    def numVariations(self):
        return len(self.variantes)

    def damePosicion(self):
        if self.current_position == -1:
            position = self.game.first_position
            from_sq, to_sq = None, None
        else:
            move = self.game.move(self.current_position)
            position = move.position
            from_sq = move.from_sq
            to_sq = move.to_sq
        return position, from_sq, to_sq

    def ponValoracion(self, valoracion):
        self.valoracion = valoracion

    def ponComentario(self, comment):
        self.comment = comment


class ListaMoves:
    def __init__(self, moveOwner, book, fen):

        if not moveOwner:
            self.nivel = 0
            cp = Position.Position()
            cp.read_fen(fen)
            self.gameBase = Game.Game(cp)
        else:
            self.nivel = moveOwner.listaMovesPadre.nivel + 1
            self.gameBase = moveOwner.game.copia()

        self.book = book
        self.fen = fen
        self.moveOwner = moveOwner
        book.polyglot()
        liMovesBook = book.get_list_moves(fen)
        self.liMoves = []
        for uno in liMovesBook:
            self.liMoves.append(UnMove(self, book, fen, uno))

    def change_book(self, book):
        self.book = book
        book.polyglot()
        liMovesBook = book.get_list_moves(self.fen)
        self.liMoves = []
        for uno in liMovesBook:
            self.liMoves.append(UnMove(self, book, self.fen, uno))

    def siEstaEnLibro(self, book):
        book.polyglot()
        liMovesBook = book.get_list_moves(self.fen)
        return len(liMovesBook) > 0


class TreeMoves(QtWidgets.QTreeWidget):
    def __init__(self, owner):
        QtWidgets.QTreeWidget.__init__(self)
        self.owner = owner
        self.setAlternatingRowColors(True)
        self.listaMoves = owner.listaMoves
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.menu_context)

        self.setHeaderLabels((_("Moves"), "", _("Games"), "", ""))
        self.setColumnHidden(3, True)

        ftxt = Controles.FontType(puntos=9)

        self.setFont(ftxt)

        self.currentItemChanged.connect(self.seleccionado)
        self.itemDoubleClicked.connect(self.owner.aceptar)

        self.dicItemMoves = {}
        self.ponMoves(self.listaMoves)

        self.sortItems(4, QtCore.Qt.AscendingOrder)

    def ponMoves(self, listaMoves):

        liMoves = listaMoves.liMoves
        if liMoves:
            moveOwner = listaMoves.moveOwner
            padre = self if moveOwner is None else moveOwner.item
            for n, mov in enumerate(liMoves):
                item = QtWidgets.QTreeWidgetItem(
                    padre, [mov.pgn, mov.porcentaje, mov.absoluto, "%07d" % int(mov.absoluto)]
                )
                item.setTextAlignment(1, QtCore.Qt.AlignRight)
                item.setTextAlignment(2, QtCore.Qt.AlignRight)

                mov.item = item
                self.dicItemMoves[str(item)] = mov

            x = 0
            for t in range(3):
                x += self.columnWidth(t)
                self.resizeColumnToContents(t)

            mov = listaMoves.liMoves[0]
            self.setCurrentItem(mov.item)

            nv = 0
            for t in range(3):
                nv += self.columnWidth(t)

            dif = nv - x
            if dif > 0:
                sz = self.owner.splitter.sizes()
                sz[1] += dif
                self.owner.resize(self.owner.width() + dif, self.owner.height())
                self.owner.splitter.setSizes(sz)

    def menu_context(self, position):
        if hasattr(self.owner.wmoves, "menu_context"):
            self.owner.wmoves.menu_context()

    def goto(self, mov):
        mov = mov.listaMovesPadre.buscaMovVisibleDesde(mov)
        self.setCurrentItem(mov.item)
        self.owner.muestra(mov)
        self.setFocus()

    def seleccionado(self, item, itemA):
        if item:
            self.owner.muestra(self.dicItemMoves[str(item)])
            self.setFocus()

    def keyPressEvent(self, event):
        resp = QtWidgets.QTreeWidget.keyPressEvent(self, event)
        k = event.key()
        if k == 43:
            self.mas()

        return resp

    def mas(self, mov=None):
        if mov is None:
            item = self.currentItem()
            mov = self.dicItemMoves[str(item)]
        else:
            item = mov.item
        if mov.listaMovesHijos is None:
            item.setText(0, mov.pgn)
            listaMovesHijos = mov.creaHijos()
            self.ponMoves(listaMovesHijos)

    def currentMov(self):
        item = self.currentItem()
        if item:
            mov = self.dicItemMoves[str(item)]
        else:
            mov = None
        return mov


class WMoves(QtWidgets.QWidget):
    def __init__(self, owner, siEnviar):
        QtWidgets.QWidget.__init__(self)

        self.owner = owner

        # Tree
        self.tree = TreeMoves(owner)

        # ToolBar
        tb = Controles.TBrutina(self, icon_size=20, with_text=False)
        if siEnviar:
            tb.new(_("Accept"), Iconos.Aceptar(), self.owner.aceptar)
            tb.new(_("Cancel"), Iconos.Cancelar(), self.owner.cancelar)
        else:
            tb.new(_("Close"), Iconos.MainMenu(), self.owner.cancelar)
        tb.new(_("Open new branch"), Iconos.Mas(), self.rama)
        tb.new(_("Books"), Iconos.Libros(), self.owner.menu_books)
        tb.new(_("Registered books"), Iconos.Book(), self.registered_books)

        layout = Colocacion.V().control(tb).control(self.tree).margen(1)

        self.setLayout(layout)

    def rama(self):
        if self.tree.currentMov():
            QTUtil.send_key_widget(self.tree, QtCore.Qt.Key_Plus, "+")

    def registered_books(self):
        WBooks.registered_books(self)
        self.owner.list_books.restore()


class InfoMove(QtWidgets.QWidget):
    def __init__(self, is_white_bottom, fenActivo):
        QtWidgets.QWidget.__init__(self)

        config_board = Code.configuration.config_board("INFOMOVE", 32)
        self.board = Board.Board(self, config_board)
        self.board.crea()
        self.board.set_side_bottom(is_white_bottom)

        self.cpDefecto = Position.Position()
        self.cpDefecto.read_fen(fenActivo)
        self.porDefecto()

        btInicio = Controles.PB(self, "", self.start).ponIcono(Iconos.MoverInicio())
        btAtras = Controles.PB(self, "", self.atras).ponIcono(Iconos.MoverAtras())
        btAdelante = Controles.PB(self, "", self.adelante).ponIcono(Iconos.MoverAdelante())
        btFinal = Controles.PB(self, "", self.final).ponIcono(Iconos.MoverFinal())

        self.lbTituloLibro = Controles.LB(self, "")

        lybt = Colocacion.H().relleno()
        for x in (btInicio, btAtras, btAdelante, btFinal):
            lybt.control(x)
        lybt.relleno()

        lyt = Colocacion.H().relleno().control(self.board).relleno()

        lya = Colocacion.H().relleno().control(self.lbTituloLibro).relleno()

        layout = Colocacion.V()
        layout.otro(lyt)
        layout.otro(lybt)
        layout.otro(lya)
        layout.relleno()
        self.setLayout(layout)

        self.movActual = None

    def porDefecto(self):
        self.board.set_position(self.cpDefecto)

    def cambioBoard(self):
        pass

    def ponValores(self):
        if self.movActual:
            position, from_sq, to_sq = self.movActual.damePosicion()
            self.board.set_position(position)

            if from_sq:
                self.board.put_arrow_sc(from_sq, to_sq)

    def ponTituloLibro(self, titulo):
        self.lbTituloLibro.set_text("<h2>" + titulo + "</h2>")

    def start(self):
        if self.movActual:
            self.movActual.start()
        self.ponValores()

    def atras(self):
        if self.movActual:
            self.movActual.atras()
        self.ponValores()

    def adelante(self):
        if self.movActual:
            self.movActual.adelante()
        self.ponValores()

    def final(self):
        if self.movActual:
            self.movActual.final()
        self.ponValores()

    def muestra(self, mov):
        self.movActual = mov
        self.ponValores()


class WindowArbolBook(LCDialog.LCDialog):
    def __init__(self, manager, siEnVivo):

        titulo = _("Consult a book")
        icono = Iconos.Libros()
        extparam = "treebook"
        LCDialog.LCDialog.__init__(self, manager.main_window, titulo, icono, extparam)

        # Se lee la lista de libros1
        self.list_books = Books.ListBooks()

        self.book = self.list_books.porDefecto()

        # fens
        fenActivo = manager.fenActivoConInicio()  # Posicion en el board
        fenUltimo = manager.last_fen()
        self.siEnviar = siEnVivo and (fenActivo == fenUltimo)

        self.listaMoves = ListaMoves(None, self.book, fenActivo)

        self.infoMove = InfoMove(manager.board.is_white_bottom, fenActivo)

        self.wmoves = WMoves(self, self.siEnviar)

        self.splitter = splitter = QtWidgets.QSplitter(self)
        splitter.addWidget(self.infoMove)
        splitter.addWidget(self.wmoves)

        ly = Colocacion.H().control(splitter).margen(0)

        self.setLayout(ly)

        self.wmoves.tree.setFocus()

        anchoBoard = self.infoMove.board.width()

        self.resize(600 - 278 + anchoBoard, anchoBoard + 30)
        self.splitter.setSizes([296 - 278 + anchoBoard, 290])
        for col, ancho in enumerate((100, 59, 87, 0, 38)):
            self.wmoves.tree.setColumnWidth(col, ancho)

        self.set_title(self.book)

    def muestra(self, mov):
        self.infoMove.muestra(mov)

    def aceptar(self):
        if self.siEnviar:
            mov = self.wmoves.tree.currentMov()
            if mov:
                li = []
                while True:
                    nv = mov.listaMovesPadre.nivel
                    li.append((mov.from_sq, mov.to_sq, mov.promotion))
                    if nv == 0:
                        break
                    mov = mov.listaMovesPadre.moveOwner
                self.resultado = li
                self.accept()
            else:
                self.reject()
        else:
            self.reject()
        self.save_video()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F3:
            self.buscaSiguiente()

    def cancelar(self):
        self.save_video()
        self.reject()

    def closeEvent(self, event):
        self.save_video()

    def change_book(self, book):
        self.listaMoves.change_book(book)
        self.wmoves.tree.clear()
        self.wmoves.tree.ponMoves(self.listaMoves)
        self.list_books.porDefecto(book)
        self.list_books.save()
        self.set_title(book)
        self.book = book

    def set_title(self, book):
        titulo = book.name
        self.infoMove.ponTituloLibro(titulo)
        self.setWindowTitle(_("Consult a book") + " [%s]" % titulo)

    def menu_books(self):
        menu = QTVarios.LCMenu(self)
        nBooks = len(self.list_books.lista)

        for book in self.list_books.lista:
            ico = Iconos.PuntoVerde() if book == self.book else Iconos.PuntoNaranja()
            menu.opcion(("x", book), book.name, ico)

        if nBooks > 1:
            menu.separador()
            menu.opcion(("1", None), _("Next book") + " <F3>", Iconos.Buscar())

        resp = menu.lanza()
        if resp:
            orden, book = resp
            if orden == "x":
                self.change_book(book)

            elif orden == "b":
                self.list_books.borra(book)
                self.list_books.save()
            elif orden == "1":
                self.buscaSiguiente()

    def buscaSiguiente(self):
        # del siguiente al final
        si = False
        for book in self.list_books.lista:
            if si:
                if self.listaMoves.siEstaEnLibro(book):
                    self.change_book(book)
                    return
            if book == self.book:
                si = True
        # del principio al actual
        for book in self.list_books.lista:
            if self.listaMoves.siEstaEnLibro(book):
                self.change_book(book)
                return
            if book == self.book:
                return
