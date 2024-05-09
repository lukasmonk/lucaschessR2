import collections

import FasterCode
from PySide2 import QtWidgets, QtCore

import Code
import Code.Nags.Nags
from Code.Analysis import WindowAnalysisParam
from Code.Base import Game, Position
from Code.Base.Constantes import GOOD_MOVE, VERY_GOOD_MOVE, NO_RATING, INTERESTING_MOVE, INACCURACY, MISTAKE, BLUNDER
from Code.Board import Board
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.SQL import UtilSQL


class UnMove:
    def __init__(self, listaMovesPadre, pv, dicCache):

        self.listaMovesPadre = listaMovesPadre
        self.listaMovesHijos = None

        self.pv = pv

        self.game = listaMovesPadre.gameBase.copia()
        self.game.read_pv(self.pv)

        self.titulo = self.game.last_jg().pgn_translated()

        if dicCache:
            dic = dicCache.get(self.pv, {})
        else:
            dic = {}

        self.valoracion = dic.get("VAL", 0)
        self.comment = dic.get("COM", "")
        self.variantes = dic.get("VAR", [])
        self.siOculto = dic.get("OCU", False)

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
        self.listaMovesHijos = ListaMoves(self, self.game.last_position.fen(), self.listaMovesPadre.dbCache)
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

    def guardaCache(self, dicCache):
        dic = {}
        if self.valoracion != "-":
            dic["VAL"] = self.valoracion
        if self.comment:
            dic["COM"] = self.comment
        if self.variantes:
            dic["VAR"] = self.variantes
        if self.siOculto:
            dic["OCU"] = True
        if dic:
            dicCache[self.pv] = dic

        if self.listaMovesHijos:
            self.listaMovesHijos.guardaCache()


class ListaMoves:
    def __init__(self, moveOwner, fen, dbCache):
        self.moveOwner = moveOwner
        self.dbCache = dbCache

        if not moveOwner:
            self.nivel = 0
            cp = Position.Position()
            cp.read_fen(fen)
            self.gameBase = Game.Game(cp)
        else:
            self.nivel = self.moveOwner.listaMovesPadre.nivel + 1
            self.gameBase = self.moveOwner.game.copia()

        self.fenm2 = self.gameBase.last_position.fenm2()

        dicCache = self.dbCache[self.fenm2]

        FasterCode.set_fen(self.fenm2 + " 0 1")
        liMov = [pv_pz for pv_pz in FasterCode.get_moves()]
        liMov.sort()
        liMov = [pv_pz[1:] for pv_pz in liMov]
        liMoves = []
        for pv in liMov:
            um = UnMove(self, pv, dicCache)
            liMoves.append(um)

        self.liMoves = liMoves
        self.liMovesInicial = liMoves[:]
        self.li_analysis = dicCache.get("ANALISIS", []) if dicCache else []

        # self.analisisActivo
        # self.dicAnalisis
        self.ponAnalisisActivo(dicCache.get("ANALISIS_ACTIVO", None) if dicCache else None)

    def guardaCache(self):
        dicCache = {}
        for um in self.liMoves:
            um.guardaCache(dicCache)

        if self.li_analysis:
            dicCache["ANALISIS"] = self.li_analysis
            dicCache["ANALISIS_ACTIVO"] = self.analisisActivo

        if dicCache:
            self.dbCache[self.fenm2] = dicCache

    def etiPuntosUnMove(self, mov, siExten):
        if self.analisisActivo is None:
            return ""

        if mov.pv in self.dicAnalisis:
            rm = self.dicAnalisis[mov.pv]
            resp = rm.abbrev_text() if siExten else rm.abbrev_text_base()
        else:
            resp = "?"
        if self.nivel % 2:
            resp += " "
        return resp

    def numVisiblesOcultos(self):
        n = 0
        for mov in self.liMoves:
            if mov.siOculto:
                n += 1
        return len(self.liMoves) - n, n

    def nomAnalisis(self):
        if self.analisisActivo is None or len(self.li_analysis) <= self.analisisActivo:
            return ""
        mrm = self.li_analysis[self.analisisActivo]
        return mrm.label

    def quitaAnalisis(self, num):
        if num == self.analisisActivo:
            self.ponAnalisisActivo(None)
        del self.li_analysis[num]

    def analisisMov(self, mov):
        return self.dicAnalisis.get(mov.pv, None)

    def reordenaSegunValoracion(self):
        li = []
        dnum = {
            VERY_GOOD_MOVE: 0,
            GOOD_MOVE: 1000,
            INTERESTING_MOVE: 1300,
            INACCURACY: 1700,
            MISTAKE: 2000,
            BLUNDER: 3000,
            NO_RATING: 4000,
        }
        for mov in self.liMovesInicial:
            v = mov.valoracion
            num = dnum[v]
            dnum[v] += 1
            li.append((mov, num))
        li.sort(key=lambda x: x[1])
        liMov = []
        for mov, num in li:
            liMov.append(mov)
        self.liMoves = liMov

    def ponAnalisisActivo(self, num):

        if num is not None and num >= len(self.li_analysis):
            if len(self.li_analysis) > 0:
                num = len(self.li_analysis) - 1
            else:
                num = None

        self.analisisActivo = num

        if num is None:
            self.dicAnalisis = {}
            self.reordenaSegunValoracion()
            return

        dic = collections.OrderedDict()

        dicPos = {}

        mrm = self.li_analysis[num]

        for n, rm in enumerate(mrm.li_rm):
            a1h8 = rm.movimiento()
            dic[a1h8] = rm
            dicPos[a1h8] = n + 1

        li = []
        for mov in self.liMoves:
            pos = dicPos.get(mov.pv, 999999)
            li.append((mov, pos))

        li.sort(key=lambda x: x[1])

        self.liMoves = []
        for mov, pos in li:
            self.liMoves.append(mov)

        self.dicAnalisis = dic

    def listaMovsSiguientes(self, mov):
        pos = self.liMoves.index(mov)
        li = [self.liMoves[x] for x in range(pos + 1, len(self.liMoves))]
        return li

    def listaMovsValoracionVisibles(self, valoracion):
        li = [mov for mov in self.liMoves if mov.valoracion == valoracion and not mov.siOculto]
        return li

    def buscaMovVisibleDesde(self, mov):
        pos = self.liMoves.index(mov)
        li = list(range(pos, len(self.liMoves)))
        if pos:
            li.extend(range(pos, -1, -1))
        for x in li:
            mv = self.liMoves[x]
            if not mv.siOculto:
                return mv
        mov.siOculto = False  # Por si acaso
        return mov


class TreeMoves(QtWidgets.QTreeWidget):
    def __init__(self, owner, procesador):
        QtWidgets.QTreeWidget.__init__(self)
        self.owner = owner
        self.dbCache = owner.dbCache
        self.setAlternatingRowColors(True)
        self.listaMoves = owner.listaMoves
        self.procesador = procesador

        self.setHeaderLabels((_("Moves"), _("Score"), _("Comments"), "T"))
        self.setColumnHidden(3, True)

        dic_nags = Code.Nags.Nags.dic_nags()
        self.dicValoracion = collections.OrderedDict()
        self.dicValoracion["1"] = (VERY_GOOD_MOVE, dic_nags[3].text, Iconos.NAG_3())
        self.dicValoracion["2"] = (GOOD_MOVE, dic_nags[1].text, Iconos.NAG_1())
        self.dicValoracion["3"] = (MISTAKE, dic_nags[2].text, Iconos.NAG_2())
        self.dicValoracion["4"] = (BLUNDER, dic_nags[4].text, Iconos.NAG_4())
        self.dicValoracion["5"] = (INTERESTING_MOVE, dic_nags[5].text, Iconos.NAG_5())
        self.dicValoracion["6"] = (INACCURACY, dic_nags[6].text, Iconos.NAG_6())
        self.dicValoracion["0"] = (NO_RATING, _("No rating"), Iconos.NAG_0())

        self.currentItemChanged.connect(self.seleccionado)
        self.itemDoubleClicked.connect(self.edited)

        hitem = self.header()
        hitem.setSectionsClickable(True)
        hitem.sectionDoubleClicked.connect(self.editedH)

        self.dicItemMoves = {}
        self.ponMoves(self.listaMoves)

        self.sortItems(3, QtCore.Qt.AscendingOrder)

    def editedH(self, col):
        item = self.currentItem()
        if not item:
            return
        mov = self.dicItemMoves[str(item)]
        lm = mov.listaMovesPadre

        if col == 0:
            lm.reordenaSegunValoracion()
            self.ordenaMoves(lm)
        elif col == 1:
            lm.ponAnalisisActivo(lm.analisisActivo)
            self.ordenaMoves(lm)

    def ponMoves(self, listaMoves):
        liMoves = listaMoves.liMoves
        if liMoves:
            moveOwner = listaMoves.moveOwner
            padre = self if moveOwner is None else moveOwner.item
            for n, mov in enumerate(liMoves):
                titulo = mov.titulo
                if mov.conHijosDesconocidos(self.dbCache):
                    titulo += " ^"
                item = QtWidgets.QTreeWidgetItem(padre, [titulo, mov.etiPuntos(False), mov.comment])
                item.setTextAlignment(1, QtCore.Qt.AlignRight)
                item.setTextAlignment(3, QtCore.Qt.AlignCenter)
                item.setToolTip(2, mov.comment)
                if mov.siOculto:
                    qm = self.indexFromItem(item, 0)
                    self.setRowHidden(qm.row(), qm.parent(), True)

                self.ponIconoValoracion(item, mov.valoracion)
                mov.item = item
                self.dicItemMoves[str(item)] = mov

            x = 0
            for t in range(3):
                x += self.columnWidth(t)

            mov = listaMoves.buscaMovVisibleDesde(liMoves[0])
            self.setCurrentItem(mov.item)

            x = self.columnWidth(0)
            self.resizeColumnToContents(0)
            dif = self.columnWidth(0) - x
            if dif > 0:
                sz = self.owner.splitter.sizes()
                sz[1] += dif
                self.owner.resize(self.owner.width() + dif, self.owner.height())
                self.owner.splitter.setSizes(sz)

    def edited(self, item, col):
        mov = self.dicItemMoves.get(str(item), None)
        if mov is None:
            return

        if col == 0:
            self.editValoracion(item, mov)

        elif col == 1:
            self.editAnalisis(item, mov)

        elif col == 2:
            self.edit_comment(item, mov)

    def edit_comment(self, item, mov):
        form = FormLayout.FormLayout(self, ("Comments") + " " + mov.titulo, Iconos.ComentarioEditar(), anchoMinimo=400)

        form.separador()

        form.editbox(_("Comments"), mov.comment, alto=5, init_value=mov.comment)
        form.separador()

        resultado = form.run()
        if resultado is None:
            return

        accion, li_resp = resultado
        mov.comment = li_resp[0].rstrip()

        item.setText(2, mov.comment)
        item.setToolTip(2, mov.comment)

    def editValoracion(self, item, mov):
        menu = QTVarios.LCMenu(self)
        for k in self.dicValoracion:
            cl, titulo, icono = self.dicValoracion[k]
            menu.opcion(cl, titulo, icono)
            menu.separador()

        resp = menu.lanza()
        if resp is None:
            return None

        mov.valoracion = resp
        self.ponIconoValoracion(item, resp)

    def editAnalisis(self, item, mov):
        # Hay un analysis -> se muestra en variantes
        # Analisis.show_analysis( self.procesador, self.xtutor, move, is_white, pos )
        fen = mov.game.last_position.fen()

        rm = mov.analysis()
        if rm is None:
            return

        game = Game.Game(mov.game.last_position)
        game.read_pv(rm.pv)
        linea_pgn = game.pgnBaseRAW()
        wowner = self.owner
        board = wowner.infoMove.board
        import Code.Variations as Variations

        game_resp = Variations.edit_variation_moves(
            self.procesador,
            wowner,
            board.is_white_bottom,
            fen,
            linea_pgn,
            titulo=mov.titulo + " - " + mov.etiPuntos(True),
        )
        if game_resp:
            if game_resp.pv() != rm.pv and game_resp.first_position.fen() == game.first_position.fen():
                rm.pv = game_resp.pv()

    def mostrarOcultar(self, item, mov):
        lm = mov.listaMovesPadre
        n_visibles, n_ocultos = lm.numVisiblesOcultos()
        if n_visibles <= 1 and n_ocultos == 0:
            return

        lista_movs_siguientes = lm.listaMovsSiguientes(mov)

        menu = QTVarios.LCMenu(self)

        if n_visibles > 1:
            smenu = menu.submenu(_("Hide"), Iconos.Ocultar())
            smenu.opcion("actual", _("Selected move"), Iconos.PuntoNaranja())
            smenu.separador()
            if lista_movs_siguientes:
                smenu.opcion("siguientes", _("Next moves"), Iconos.PuntoRojo())
                smenu.separador()

            for k in self.dicValoracion:
                valoracion, titulo, icono = self.dicValoracion[k]
                if lm.listaMovsValoracionVisibles(valoracion):
                    smenu.opcion("val_%d" % valoracion, titulo, icono)
                    smenu.separador()

        if n_ocultos:
            menu.opcion("mostrar", _("Show what is hidden"), Iconos.Mostrar())

        resp = menu.lanza()
        if resp is None:
            return

        if resp == "actual":
            mov.siOculto = True

        elif resp == "siguientes":
            for mv in lista_movs_siguientes:
                mv.siOculto = True

        elif resp.startswith("val_"):
            valoracion = int(resp[4])
            for mv in lm.listaMovsValoracionVisibles(valoracion):
                if n_visibles == 1:
                    break
                mv.siOculto = True
                n_visibles -= 1

        elif resp == "mostrar":
            for mv in lm.liMoves:
                mv.siOculto = False

        qmParent = self.indexFromItem(item, 0).parent()
        for nFila, mv in enumerate(lm.liMoves):
            self.setRowHidden(nFila, qmParent, mv.siOculto)

        self.goto(mov)

    def menu_context(self, position):
        self.owner.wmoves.menu_context()

    def iconoValoracion(self, valoracion):
        return Iconos.icono("NAG_%d" % valoracion)

    def ponIconoValoracion(self, item, valoracion):
        item.setIcon(0, self.iconoValoracion(valoracion))

    def ordenaMoves(self, listaMoves):
        for n, mov in enumerate(listaMoves.liMoves):
            c_ord = "%02d" % (n + 1)
            mov.item.setText(3, c_ord)
        self.sortItems(3, QtCore.Qt.AscendingOrder)

    def goto(self, mov):
        mov = mov.listaMovesPadre.buscaMovVisibleDesde(mov)
        self.setCurrentItem(mov.item)
        self.owner.muestra(mov)
        self.setFocus()

    def seleccionado(self, item, itemA):
        self.owner.muestra(self.dicItemMoves[str(item)])
        self.setFocus()

    def keyPressEvent(self, event):
        resp = QtWidgets.QTreeWidget.keyPressEvent(self, event)
        k = event.key()
        if k == QtCore.Qt.Key_Plus:
            self.mas()
        elif k in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
            self.menos()
        elif 48 <= k <= 54:
            item = self.currentItem()
            if item:
                cl, titulo, icono = self.dicValoracion[chr(k)]
                self.ponIconoValoracion(item, cl)
                mov = self.dicItemMoves[str(item)]
                mov.valoracion = cl

        return resp

    def mas(self, mov=None):
        if mov is None:
            item = self.currentItem()
            mov = self.dicItemMoves[str(item)]
        else:
            item = mov.item
        if mov.listaMovesHijos is None:
            item.setText(0, mov.titulo)
            listaMovesHijos = mov.creaHijos()
            self.ponMoves(listaMovesHijos)

    def menos(self, mov=None):
        if mov is None:
            item = self.currentItem()
            mov = self.dicItemMoves[str(item)]

        lm = mov.listaMovesPadre
        n_visibles, n_ocultos = lm.numVisiblesOcultos()
        if n_visibles <= 1:
            return

        qm = self.currentIndex()
        self.setRowHidden(qm.row(), qm.parent(), True)
        mov.siOculto = True

        self.goto(mov)

    def currentMov(self):
        item = self.currentItem()
        if item:
            mov = self.dicItemMoves[str(item)]
        else:
            mov = None
        return mov


class WMoves(QtWidgets.QWidget):
    def __init__(self, owner, procesador):
        QtWidgets.QWidget.__init__(self)

        self.owner = owner

        # Tree
        self.tree = TreeMoves(owner, procesador)

        # ToolBar
        self.tb = Controles.TBrutina(self, with_text=False, icon_size=24)
        self.tb.new(_("Open new branch"), Iconos.Mas(), self.rama)
        self.tb.new(_("Show") + "/" + _("Hide"), Iconos.Mostrar(), self.mostrar)
        self.tb.new(_("Rating"), self.tree.iconoValoracion(0), self.valorar)
        self.tb.new(_("Analyze"), Iconos.Analizar(), self.analizar)
        self.tb.new(_("Comments"), Iconos.ComentarioEditar(), self.comment)

        layout = Colocacion.V().control(self.tb).control(self.tree).margen(1)

        self.setLayout(layout)

    def rama(self):
        mov = self.tree.currentMov()
        if not mov:
            return
        self.tree.mas()

    def analizar(self):
        mov = self.tree.currentMov()
        if not mov:
            return
        self.owner.analizar(mov)

    def valorar(self):
        mov = self.tree.currentMov()
        if not mov:
            return
        self.tree.editValoracion(mov.item, mov)

    def comment(self):
        mov = self.tree.currentMov()
        if not mov:
            return
        self.tree.edit_comment(mov.item, mov)

    def mostrar(self):
        mov = self.tree.currentMov()
        if not mov:
            return
        self.tree.mostrarOcultar(mov.item, mov)


class InfoMove(QtWidgets.QWidget):
    def __init__(self, is_white_bottom):
        QtWidgets.QWidget.__init__(self)

        config_board = Code.configuration.config_board("INFOMOVE", 32)
        self.main_window = self
        self.board = Board.Board(self, config_board)
        self.board.crea()
        self.board.set_side_bottom(is_white_bottom)

        btInicio = Controles.PB(self, "", self.start).ponIcono(Iconos.MoverInicio())
        btAtras = Controles.PB(self, "", self.atras).ponIcono(Iconos.MoverAtras())
        btAdelante = Controles.PB(self, "", self.adelante).ponIcono(Iconos.MoverAdelante())
        btFinal = Controles.PB(self, "", self.final).ponIcono(Iconos.MoverFinal())

        self.lbAnalisis = Controles.LB(self, "")

        lybt = Colocacion.H().relleno()
        for x in (btInicio, btAtras, btAdelante, btFinal):
            lybt.control(x)
        lybt.relleno()

        lyt = Colocacion.H().relleno().control(self.board).relleno()

        lya = Colocacion.H().relleno().control(self.lbAnalisis).relleno()

        layout = Colocacion.V()
        layout.otro(lyt)
        layout.otro(lybt)
        layout.otro(lya)
        layout.relleno()
        self.setLayout(layout)

        self.movActual = None

    def ponValores(self):
        position, from_sq, to_sq = self.movActual.damePosicion()
        self.board.set_position(position)

        if from_sq:
            self.board.put_arrow_sc(from_sq, to_sq)

        self.lbAnalisis.set_text("<b>" + self.movActual.etiPuntos(True) + "</b>")

    def start(self):
        self.movActual.start()
        self.ponValores()

    def atras(self):
        self.movActual.atras()
        self.ponValores()

    def adelante(self):
        self.movActual.adelante()
        self.ponValores()

    def final(self):
        self.movActual.final()
        self.ponValores()

    def muestra(self, mov):
        self.movActual = mov
        self.ponValores()


class WindowArbol(LCDialog.LCDialog):
    def __init__(self, w_parent, game, nj, procesador):

        main_window = w_parent
        parent_board = main_window.board

        self.procesador = procesador

        titulo = _("Moves tree")
        icono = Iconos.Arbol()
        extparam = "moves"
        LCDialog.LCDialog.__init__(self, main_window, titulo, icono, extparam)

        dicVideo = self.restore_dicvideo()

        self.dbCache = UtilSQL.DictSQL(Code.configuration.ficheroMoves)
        if nj >= 0:
            position = game.move(nj).position
        else:
            position = game.first_position
        self.listaMoves = ListaMoves(None, position.fen(), self.dbCache)

        tb = QTVarios.LCTB(self)
        tb.new(_("Save"), Iconos.Grabar(), self.grabar)
        tb.new(_("Cancel"), Iconos.Cancelar(), self.cancelar)

        self.infoMove = InfoMove(parent_board.is_white_bottom)

        w = QtWidgets.QWidget(self)
        ly = Colocacion.V().control(tb).control(self.infoMove).margen(3)
        w.setLayout(ly)

        self.splitter = splitter = QtWidgets.QSplitter(self)

        self.wmoves = WMoves(self, procesador)

        splitter.addWidget(w)
        splitter.addWidget(self.wmoves)

        ly = Colocacion.H().control(splitter).margen(0)

        self.setLayout(ly)

        self.wmoves.tree.setFocus()

        anchoBoard = self.infoMove.board.width()

        self.restore_video(anchoDefecto=869 - 242 + anchoBoard)
        if not dicVideo:
            dicVideo = {
                "TREE_3": 27,
                "SPLITTER": [260 - 242 + anchoBoard, 617],
                "TREE_1": 49,
                "TREE_2": 300,
                "TREE_4": 25,
            }
        sz = dicVideo.get("SPLITTER", None)
        if sz:
            self.splitter.setSizes(sz)
        for x in range(1, 2):
            w = dicVideo.get("TREE_%d" % x, None)
            if w:
                self.wmoves.tree.setColumnWidth(x, w)

    def muestra(self, mov):
        self.infoMove.muestra(mov)

    def save_video(self):
        dic_extended = {"SPLITTER": self.splitter.sizes()}
        for x in range(1, 6):
            dic_extended["TREE_%d" % x] = self.wmoves.tree.columnWidth(x)

        LCDialog.LCDialog.save_video(self, dic_extended)

    def grabar(self):
        self.listaMoves.guardaCache()
        self.dbCache.close()

        self.accept()

    def cancelar(self):
        self.dbCache.close()
        self.reject()

    def closeEvent(self, event):
        self.dbCache.close()
        self.save_video()

    def analizar(self, mov):
        if mov.listaMovesPadre:
            lm = mov.listaMovesPadre
        else:
            lm = self.listaMoves

        # Si tiene ya analysis, lo pedimos o nuevo
        menu = QTVarios.LCMenu(self)
        if lm.li_analysis:
            for n, mrm in enumerate(lm.li_analysis):
                menu.opcion(n, mrm.label, Iconos.PuntoVerde())
            menu.separador()

            menu.opcion(-999999, _("New analysis"), Iconos.Mas())
            menu.separador()

            if lm.analisisActivo is not None:
                menu.opcion(-999998, _("Hide analysis"), Iconos.Ocultar())
                menu.separador()

            menu1 = menu.submenu(_("Delete analysis of"), Iconos.Delete())
            for n, mrm in enumerate(lm.li_analysis):
                menu1.opcion(-n - 1, mrm.label, Iconos.PuntoRojo())
                menu1.separador()

            resp = menu.lanza()
            if resp is None:
                return

            if resp >= 0:
                self.ponAnalisis(lm, resp)
                return

            elif resp == -999999:
                self.nuevoAnalisis(lm)
                return

            elif resp == -999998:
                self.ponAnalisis(lm, None)
                return

            else:
                num = -resp - 1
                mrm = lm.li_analysis[num]
                if QTUtil2.pregunta(self, _X(_("Delete analysis of %1?"), mrm.label)):
                    self.quitaAnalisis(lm, num)
                return

        else:
            self.nuevoAnalisis(lm)

    def nuevoAnalisis(self, lm):
        fen = lm.gameBase.last_position.fen()
        alm = WindowAnalysisParam.analysis_parameters(self, False, all_engines=True)
        if alm is None:
            return
        if alm.engine == "default":
            xengine = self.procesador.analyzer_clone(alm.vtime, alm.depth, alm.multiPV)
        else:
            confMotor = Code.configuration.buscaRival(alm.engine)
            confMotor.update_multipv(alm.multiPV)
            xengine = self.procesador.creaManagerMotor(confMotor, alm.vtime, alm.depth, has_multipv=True)

        me = QTUtil2.analizando(self, True)

        def test_me(rm):
            if me.cancelado():
                xengine.stop()
            return True

        xengine.set_gui_dispatch(test_me)

        mrm = xengine.analiza(fen)
        xengine.terminar()
        cancelado = me.cancelado()
        me.final()
        if not cancelado:
            mrm.vtime = alm.vtime / 1000.0
            mrm.depth = alm.depth

            tipo = "%s=%d" % (_("Depth"), mrm.depth) if mrm.depth else '%.0f"' % mrm.vtime
            mrm.label = "%s %s" % (mrm.name, tipo)
            lm.li_analysis.append(mrm)
            self.ponAnalisis(lm, len(lm.li_analysis) - 1)

    def ponAnalisis(self, lm, num):

        lm.ponAnalisisActivo(num)

        for um in lm.liMoves:
            um.item.setText(1, um.etiPuntos(False))

        self.wmoves.tree.ordenaMoves(lm)
        self.wmoves.tree.goto(lm.liMoves[0])
        #
        # self.infoMove.ponValores()

    def quitaAnalisis(self, lm, num):

        lm.quitaAnalisis(num)

        for um in lm.liMoves:
            um.item.setText(1, um.etiPuntos(False))

        self.wmoves.tree.ordenaMoves(lm)
        self.wmoves.tree.goto(lm.liMoves[0])

        self.infoMove.ponValores()
