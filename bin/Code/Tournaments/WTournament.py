import os
import time

from PySide2 import QtWidgets, QtCore

import Code
from Code import Util
from Code import XRun
from Code.Base import Game, Position
from Code.Base.Constantes import FEN_INITIAL, BOOK_BEST_MOVE, BOOK_RANDOM_UNIFORM, BOOK_RANDOM_PROPORTIONAL
from Code.Books import Books
from Code.Databases import DBgames, WDB_Games
from Code.Engines import Engines, WEngines
from Code.Engines import SelectEngines
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import SelectFiles
from Code.QT import WindowSavePGN
from Code.Tournaments import Tournament
from Code.Voyager import Voyager

GRID_ALIAS, GRID_VALUES, GRID_GAMES_QUEUED, GRID_GAMES_FINISHED, GRID_RESULTS = range(5)


class WTournament(LCDialog.LCDialog):
    def __init__(self, w_parent, nombre_torneo):

        torneo = self.torneo = Tournament.Tournament(nombre_torneo)

        titulo = nombre_torneo
        icono = Iconos.Torneos()
        extparam = "untorneo_v1"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        self.configuration = Code.configuration
        self.internal_engines = SelectEngines.SelectEngines(w_parent)

        # Datos

        self.liEnActual = []
        self.xjugar = None
        self.liResult = None
        self.last_change = Util.today()
        self.li_results = []

        # Toolbar
        tb = Controles.TBrutina(self, icon_size=24)
        tb.new(_("Close"), Iconos.MainMenu(), self.terminar)
        tb.new(_("Launch workers"), Iconos.Lanzamiento(), self.gm_launch)

        # Tabs
        self.tab = tab = Controles.Tab()

        # Tab-configuration --------------------------------------------------
        w = QtWidgets.QWidget()

        # Adjudicator
        lb_resign = Controles.LB(self, "%s (%s): " % (_("Minimum centipawns to assign winner"), "0=%s" % _("Disable")))
        self.ed_resign = Controles.ED(self).tipoInt(torneo.resign()).anchoFijo(30)
        bt_resign = Controles.PB(self, "", rutina=self.borra_resign).ponIcono(Iconos.Reciclar())

        # Draw-plys
        lb_draw_min_ply = Controles.LB(self,
                                       "%s (%s): " % (_("Minimum movements to assign draw"), "0=%s" % _("Disable")))
        self.ed_draw_min_ply = Controles.ED(self).ponInt(torneo.draw_min_ply()).anchoFijo(30).align_right()
        # Draw-puntos
        lb_draw_range = Controles.LB(self, _("Maximum centipawns to assign draw") + ": ")
        self.ed_draw_range = Controles.ED(self).tipoInt(torneo.draw_range()).anchoFijo(30)
        bt_draw_range = Controles.PB(self, "", rutina=self.borra_draw_range).ponIcono(Iconos.Reciclar())

        # adjudicator
        self.list_engines = self.configuration.combo_engines_multipv10()
        self.cbJmotor, self.lbJmotor = QTUtil2.combobox_lb(self, self.list_engines, torneo.adjudicator(), _("Engine"))
        self.edJtiempo = Controles.ED(self).tipoFloat(torneo.adjudicator_time()).anchoFijo(50)
        self.lbJtiempo = Controles.LB2P(self, _("Time in seconds"))
        layout = Colocacion.G()
        layout.controld(self.lbJmotor, 3, 0).control(self.cbJmotor, 3, 1)
        layout.controld(self.lbJtiempo, 4, 0).control(self.edJtiempo, 4, 1)
        self.gbJ = Controles.GB(self, _("Adjudicator"), layout)
        self.gbJ.setCheckable(True)
        self.gbJ.setChecked(torneo.adjudicator_active())

        lb_book = Controles.LB(self, _("Opening book") + ": ")
        self.list_books = Books.ListBooks()
        li = [(x.name, x.path) for x in self.list_books.lista]
        li.insert(0, ("* " + _("None"), "-"))
        self.cbBooks = Controles.CB(self, li, torneo.book())
        bt_nuevo_book = Controles.PB(self, "", self.new_book, plano=False).ponIcono(Iconos.Nuevo(), icon_size=16)
        ly_book = Colocacion.H().control(self.cbBooks).control(bt_nuevo_book).relleno()

        lb_book_depth = Controles.LB(self, _("Max depth of book (0=Maximum)") + ": ")
        self.sbBookDepth = Controles.SB(self, torneo.book_depth(), 0, 200)

        lb_slow = Controles.LB(self, _("Slow down the movement of pieces") + ": ")
        self.chb_slow = Controles.CHB(self, " ", self.torneo.slow_pieces())

        # Posicion inicial
        lb_fen = Controles.LB(self, _("Initial position") + ": ")
        self.fen = torneo.fen()
        self.btPosicion = Controles.PB(self, " " * 5 + _("Change") + " " * 5, self.position_edit).ponPlano(False)
        self.btPosicionQuitar = Controles.PB(self, "", self.position_remove).ponIcono(Iconos.Motor_No())
        self.btPosicionPegar = (
            Controles.PB(self, "", self.position_paste).ponIcono(Iconos.Pegar16()).ponToolTip(_("Paste FEN position"))
        )
        ly_fen = (
            Colocacion.H()
            .control(self.btPosicionQuitar)
            .control(self.btPosicion)
            .control(self.btPosicionPegar)
            .relleno()
        )

        # Norman Pollock
        lb_norman = Controles.LB(
            self,
            '%s(<a href="http://www.nk-qy.info/40h/">?</a>): '
            % _("Initial position from Norman Pollock openings database"),
        )
        self.chbNorman = Controles.CHB(self, " ", self.torneo.norman())

        # Layout
        layout = Colocacion.G()
        ly_res = Colocacion.H().control(self.ed_resign).control(bt_resign).relleno()
        ly_dra = Colocacion.H().control(self.ed_draw_range).control(bt_draw_range).relleno()
        layout.controld(lb_resign, 0, 0).otro(ly_res, 0, 1)
        layout.controld(lb_draw_range, 1, 0).otro(ly_dra, 1, 1)
        layout.controld(lb_draw_min_ply, 2, 0).control(self.ed_draw_min_ply, 2, 1)
        layout.controld(lb_book, 3, 0).otro(ly_book, 3, 1)
        layout.controld(lb_book_depth, 4, 0).control(self.sbBookDepth, 4, 1)
        layout.controld(lb_fen, 5, 0).otro(ly_fen, 5, 1)
        layout.controld(lb_norman, 6, 0).control(self.chbNorman, 6, 1)
        layout.controld(lb_slow, 7, 0).control(self.chb_slow, 7, 1)
        layout_v = Colocacion.V().relleno().otro(layout).control(self.gbJ).relleno()
        layout_h = Colocacion.H().relleno().otro(layout_v).relleno()

        # Creamos
        w.setLayout(layout_h)
        tab.new_tab(w, _("Configuration"))

        # Tab-engines --------------------------------------------------
        self.splitterEngines = QtWidgets.QSplitter(self)
        self.register_splitter(self.splitterEngines, "engines")
        # TB
        li_acciones = [
            (_("New"), Iconos.TutorialesCrear(), self.eng_new),
            None,
            (_("Modify"), Iconos.Modificar(), self.eng_modify),
            None,
            (_("Remove"), Iconos.Borrar(), self.eng_remove),
            None,
            (_("Copy"), Iconos.Copiar(), self.eng_copy),
            None,
            (_("Import"), Iconos.MasDoc(), self.eng_import),
            None,
        ]
        tb_en_a = Controles.TBrutina(self, li_acciones, icon_size=16, style=QtCore.Qt.ToolButtonTextBesideIcon)

        # Grid engine
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUM", _("N."), 50, align_center=True)
        o_columns.nueva("ALIAS", _("Alias"), 209)
        self.gridEnginesAlias = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True, xid=GRID_ALIAS)
        self.register_grid(self.gridEnginesAlias)

        w = QtWidgets.QWidget()
        ly = Colocacion.V().control(self.gridEnginesAlias).margen(0)
        w.setLayout(ly)
        self.splitterEngines.addWidget(w)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("CAMPO", _("Label"), 200, align_right=True)
        o_columns.nueva("VALOR", _("Value"), 286)
        self.gridEnginesValores = Grid.Grid(self, o_columns, siSelecFilas=False, xid=GRID_VALUES)
        self.register_grid(self.gridEnginesValores)

        w = QtWidgets.QWidget()
        ly = Colocacion.V().control(self.gridEnginesValores).margen(0)
        w.setLayout(ly)
        self.splitterEngines.addWidget(w)

        self.splitterEngines.setSizes([250, 520])  # por defecto

        w = QtWidgets.QWidget()
        ly = Colocacion.V().control(tb_en_a).control(self.splitterEngines)
        w.setLayout(ly)
        tab.new_tab(w, _("Engines"))

        # Creamos

        # Tab-games queued--------------------------------------------------
        w = QtWidgets.QWidget()
        # TB
        li_acciones = [
            (_("New"), Iconos.TutorialesCrear(), self.gm_crear_queued),
            None,
            (_("Remove"), Iconos.Borrar(), self.gm_borrar_queued),
            None,
        ]
        tb_en_g = Controles.TBrutina(self, li_acciones, icon_size=16, style=QtCore.Qt.ToolButtonTextBesideIcon)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUM", _("N."), 50, align_center=True)
        o_columns.nueva("WHITE", _("White"), 190, align_center=True)
        o_columns.nueva("BLACK", _("Black"), 190, align_center=True)
        o_columns.nueva("TIME", _("Time"), 170, align_center=True)
        # o_columns.nueva("STATE", _("State"), 190, align_center=True)
        self.gridGamesQueued = Grid.Grid(
            self, o_columns, siSelecFilas=True, siSeleccionMultiple=True, xid=GRID_GAMES_QUEUED
        )
        self.register_grid(self.gridGamesQueued)
        # Layout
        layout = Colocacion.V().control(tb_en_g).control(self.gridGamesQueued)

        # Creamos
        w.setLayout(layout)
        tab.new_tab(w, _("Games queued"))

        # Tab-games terminados--------------------------------------------------
        w = QtWidgets.QWidget()
        # TB
        li_acciones = [
            (_("Remove"), Iconos.Borrar(), self.gm_borrar_finished),
            None,
            (_("Show"), Iconos.PGN(), self.gm_show_finished),
            None,
            (_("Save") + "(%s)" % _("PGN"), Iconos.GrabarComo(), self.gm_save_pgn),
            None,
            (_("Save") + "(%s)" % _("Database"), Iconos.GrabarComo(), self.gm_save_database),
            None,
        ]
        tb_en_gt = Controles.TBrutina(self, li_acciones, icon_size=16, style=QtCore.Qt.ToolButtonTextBesideIcon)

        self.cache_games_finished = {}
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUM", _("N."), 50, align_center=True)
        o_columns.nueva("WHITE", _("White"), 190, align_center=True)
        o_columns.nueva("BLACK", _("Black"), 190, align_center=True)
        o_columns.nueva("TIME", _("Time"), 170, align_center=True)
        o_columns.nueva("RESULT", _("Result"), 190, align_center=True)
        o_columns.nueva("PLYCOUNT", _("Movements"), 100, align_center=True)
        self.gridGamesFinished = Grid.Grid(
            self, o_columns, siSelecFilas=True, siSeleccionMultiple=True, xid=GRID_GAMES_FINISHED
        )
        self.register_grid(self.gridGamesFinished)
        # Layout
        layout = Colocacion.V().control(tb_en_gt).control(self.gridGamesFinished)

        # Creamos
        w.setLayout(layout)
        tab.new_tab(w, _("Games finished"))

        # Tab-resultado --------------------------------------------------
        w = QtWidgets.QWidget()

        # Grid
        wh = _("W ||White")
        bl = _("B ||Black")
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUM", _("N."), 35, align_center=True)
        o_columns.nueva("ENGINE", _("Engine"), 120, align_center=True)
        o_columns.nueva("SCORE", _("Score") + "%", 50, align_center=True)
        o_columns.nueva("WIN", _("Wins"), 50, align_center=True)
        o_columns.nueva("DRAW", _("Draws"), 50, align_center=True)
        o_columns.nueva("LOST", _("Losses"), 50, align_center=True)
        o_columns.nueva("WIN-WHITE", "%s %s" % (wh, _("Wins")), 60, align_center=True)
        o_columns.nueva("DRAW-WHITE", "%s %s" % (wh, _("Draws")), 60, align_center=True)
        o_columns.nueva("LOST-WHITE", "%s %s" % (wh, _("Losses")), 60, align_center=True)
        o_columns.nueva("WIN-BLACK", "%s %s" % (bl, _("Wins")), 60, align_center=True)
        o_columns.nueva("DRAW-BLACK", "%s %s" % (bl, _("Draws")), 60, align_center=True)
        o_columns.nueva("LOST-BLACK", "%s %s" % (bl, _("Losses")), 60, align_center=True)
        o_columns.nueva("GAMES", _("Games"), 50, align_center=True)
        self.gridResults = Grid.Grid(self, o_columns, siSelecFilas=True, xid=GRID_RESULTS)
        self.register_grid(self.gridResults)

        self.qtColor = {
            "WHITE": QTUtil.qtColorRGB(255, 250, 227),
            "BLACK": QTUtil.qtColorRGB(221, 255, 221),
            "SCORE": QTUtil.qtColorRGB(170, 170, 170),
        }

        # Layout
        layout = Colocacion.V().control(self.gridResults)

        # Creamos
        w.setLayout(layout)
        tab.new_tab(w, _("Results"))

        # Layout
        # tab.set_position("W")
        layout = Colocacion.V().control(tb).espacio(-3).control(tab).margen(2)
        self.setLayout(layout)

        self.restore_video(siTam=True, anchoDefecto=800, altoDefecto=430)

        self.gridEnginesAlias.gotop()

        self.ed_resign.setFocus()

        self.show_position()

        QtCore.QTimer.singleShot(5000, self.comprueba_cambios)
        self.rotulos_tabs()

    def closeEvent(self, event):
        self.cerrar()

    def terminar(self):
        self.cerrar()
        self.accept()

    def cerrar(self):
        if self.torneo:
            self.grabar()
            self.torneo = None
        self.save_video()

    def rotulos_tabs(self):
        self.tab.set_value(1, "%d %s" % (self.torneo.num_engines(), _("Engines")))
        self.tab.set_value(2, "%d %s" % (self.torneo.num_games_queued(), _("Games queued")))
        self.tab.set_value(3, "%d %s" % (self.torneo.num_games_finished(), _("Games finished")))
        self.calc_results()

    def calc_results(self):
        self.li_results = []
        for num in range(self.torneo.num_engines()):
            eng = self.torneo.engine(num)
            ww, wb, dw, db, lw, lb = (
                len(eng.win_white),
                len(eng.win_black),
                len(eng.draw_white),
                len(eng.draw_black),
                len(eng.lost_white),
                len(eng.lost_black),
            )
            tt = ww + wb + dw + db + lw + lb
            p = (ww + wb) * 2 + (dw + db) * 1
            score = (p * 50 / tt) if tt > 0 else 0
            self.li_results.append((eng.key, score, ww, wb, dw, db, lw, lb))
        self.li_results.sort(key=lambda x: x[1], reverse=True)
        self.gridResults.refresh()

    def borra_resign(self):
        previo = self.ed_resign.textoInt()
        self.ed_resign.tipoInt(0 if previo else 350)

    def borra_draw_range(self):
        previo = self.ed_draw_range.textoInt()
        self.ed_draw_range.tipoInt(0 if previo else 10)
        self.ed_draw_min_ply.tipoInt(0 if previo else 50)

    def show_position(self):
        if self.fen:
            label = self.fen
            self.btPosicionQuitar.show()
            self.btPosicionPegar.show()
            self.chbNorman.set_value(False)
        else:
            label = _("Change")
            self.btPosicionQuitar.hide()
            self.btPosicionPegar.show()
        label = " " * 5 + label + " " * 5
        self.btPosicion.set_text(label)

    def position_edit(self):
        cp = Position.Position()
        cp.read_fen(self.fen)
        position, is_white_bottom = Voyager.voyager_position(self, cp)
        if position is not None:
            self.fen = position.fen()
            self.show_position()

    def position_remove(self):
        self.fen = ""
        self.show_position()

    def position_paste(self):
        texto = QTUtil.get_txt_clipboard()
        if texto:
            cp = Position.Position()
            try:
                cp.read_fen(texto.strip())
                self.fen = cp.fen()
                if self.fen == FEN_INITIAL:
                    self.fen = ""
                self.show_position()
            except:
                pass

    def new_book(self):
        fbin = SelectFiles.leeFichero(self, self.list_books.path, "bin", titulo=_("Polyglot book"))
        if fbin:
            self.list_books.path = os.path.dirname(fbin)
            name = os.path.basename(fbin)[:-4]
            b = Books.Book("P", name, fbin, False)
            self.list_books.nuevo(b)
            li = [(x.name, x.path) for x in self.list_books.lista]
            li.insert(0, ("* " + _("By default"), "*"))
            self.cbBooks.rehacer(li, b.path)

    def grid_num_datos(self, grid):
        gid = grid.id
        if gid == GRID_ALIAS:
            return self.torneo.num_engines()
        elif gid == GRID_VALUES:
            return len(self.liEnActual)
        elif gid == GRID_GAMES_QUEUED:
            return self.torneo.num_games_queued()
        elif gid == GRID_GAMES_FINISHED:
            return self.torneo.num_games_finished()
        elif gid == GRID_RESULTS:
            return self.torneo.num_engines()

    def grid_dato(self, grid, row, o_column):
        column = o_column.key
        gid = grid.id
        if gid == GRID_ALIAS:
            return self.grid_dato_engines_alias(row, column)
        elif gid == GRID_VALUES:
            return self.grid_dato_engines_values(row, column)
        elif gid == GRID_RESULTS:
            return self.grid_dato_result(row, column)
        elif gid == GRID_GAMES_QUEUED:
            return self.grid_dato_games_queued(row, column)
        elif gid == GRID_GAMES_FINISHED:
            return self.grid_dato_games_finished(row, column)

    def grid_dato_engines_alias(self, row, column):
        me = self.torneo.engine(row)
        if column == "ALIAS":
            return me.key
        elif column == "NUM":
            return str(row + 1)

    def grid_dato_engines_values(self, row, column):
        li = self.liEnActual[row]
        if column == "CAMPO":
            return li[0]
        else:
            return str(li[1])

    def grid_dato_result(self, row, column):
        key, score, ww, wb, dw, db, lw, lb = self.li_results[row]
        if column == "NUM":
            return str(row + 1)
        elif column == "ENGINE":
            return key
        elif column == "SCORE":
            return "%.1f" % score if score > 0 else "0"
        elif column == "WIN":
            return "%d" % (ww + wb)
        elif column == "LOST":
            return "%d" % (lw + lb)
        elif column == "DRAW":
            return "%d" % (dw + db)
        elif column == "WIN-WHITE":
            return "%d" % ww
        elif column == "LOST-WHITE":
            return "%d" % lw
        elif column == "DRAW-WHITE":
            return "%d" % dw
        elif column == "WIN-BLACK":
            return "%d" % wb
        elif column == "LOST-BLACK":
            return "%d" % lb
        elif column == "DRAW-BLACK":
            return "%d" % db
        elif column == "GAMES":
            return "%s" % (ww + wb + lw + lb + dw + db)

    def grid_dato_games_queued(self, row, column):
        gm = self.torneo.game_queued(row)
        if column == "NUM":
            return str(row + 1)
        elif column == "WHITE":
            en = self.torneo.search_hengine(gm.hwhite)
            return en.key if en else "???"
        elif column == "BLACK":
            en = self.torneo.search_hengine(gm.hblack)
            return en.key if en else "???"
        # elif column == "STATE":
        #     return _("Working...") if gm.worker else ""
        elif column == "TIME":
            return gm.etiTiempo()

    def grid_dato_games_finished(self, row, column):
        gm: Tournament.GameTournament = self.torneo.game_finished(row)
        if gm.id_game not in self.cache_games_finished:
            self.cache_games_finished[gm.id_game] = gm.game()
        game = self.cache_games_finished[gm.id_game]

        if column == "NUM":
            return str(row + 1)
        elif column == "WHITE":
            en = self.torneo.search_hengine(gm.hwhite)
            return en.key if en else "???"
        elif column == "BLACK":
            en = self.torneo.search_hengine(gm.hblack)
            return en.key if en else "???"
        elif column == "RESULT":
            return gm.result + " (%s)" % game.get_tag("Termination")
        elif column == "TIME":
            return gm.etiTiempo()
        elif column == "PLYCOUNT":
            return str(len(game))


    def grid_cambiado_registro(self, grid, row, column):
        if grid.id == GRID_ALIAS:
            me = self.torneo.engine(row)
            self.act_engine(me)
            self.gridEnginesValores.refresh()

    def act_engine(self, me):
        self.liEnActual = []
        row = self.gridEnginesAlias.recno()
        if row < 0:
            return

        # tipo, key, label, valor
        self.liEnActual.append((_("Engine"), me.name))
        self.liEnActual.append((_("Author"), me.autor))
        self.liEnActual.append((_("File"), Util.relative_path(me.path_exe)))
        self.liEnActual.append((_("Information"), me.id_info.replace("\n", " - ")))
        self.liEnActual.append(("ELO", me.elo))
        self.liEnActual.append((_("Max depth"), me.depth))
        self.liEnActual.append((_("Maximum seconds to think"), me.time))
        pbook = me.book
        if pbook in ("-", None):
            pbook = "* " + _("Engine book")
        else:
            if pbook == "*":
                pbook = "* " + _("By default")
            dic = {BOOK_RANDOM_UNIFORM: _("Uniform random"), BOOK_RANDOM_PROPORTIONAL: _("Proportional random"),
                   BOOK_BEST_MOVE: _("Always the highest percentage")}
            pbook += "   (%s)" % dic.get(me.bookRR, BOOK_BEST_MOVE)

        self.liEnActual.append((_("Opening book"), pbook))

        for opcion in me.li_uci_options():
            self.liEnActual.append((opcion.name, str(opcion.valor)))

    def gm_launch(self):
        if self.torneo.num_games_queued() == 0:
            QTUtil2.message(self, _("You must create some games (Queued Games tab/ New)"))
            return
        self.grabar()

        resp = QTVarios.launch_workers(self)

        if resp:
            with QTUtil2.OneMomentPlease(self):
                last = 0
                for num in range(resp):
                    worker_plant = Util.opj(self.configuration.folder_tournaments_workers(), "worker.%05d")
                    pos = last + 1
                    while True:
                        wfile = worker_plant % pos
                        if Util.exist_file(wfile):
                            if not Util.remove_file(wfile):
                                pos += 1
                                continue
                        last = pos
                        break
                    XRun.run_lucas("-tournament", self.torneo.file, wfile)
                    time.sleep(1.0)

    def comprueba_cambios(self):
        if self.torneo:
            changed = (
                    self.torneo.resign() != self.ed_resign.textoInt()
                    or self.torneo.draw_min_ply() != self.ed_draw_min_ply.textoInt()
                    or self.torneo.draw_range() != self.ed_draw_range.textoInt()
                    or self.torneo.fen() != self.fen
                    or self.torneo.norman() != self.chbNorman.valor()
                    or self.torneo.slow_pieces() != self.chb_slow.valor()
                    or self.torneo.book() != self.cbBooks.valor()
                    or self.torneo.book_depth() != self.sbBookDepth.valor()
                    or self.torneo.adjudicator_active() != self.gbJ.isChecked()
                    or self.torneo.adjudicator() != self.cbJmotor.valor()
                    or self.torneo.adjudicator_time() != self.edJtiempo.textoFloat()
            )
            if changed:
                self.grabar()

            last_change_saved = self.torneo.get_last_change()
            if last_change_saved and last_change_saved > self.last_change:
                self.last_change = Util.today()
                self.torneo.dbs_reread()
                self.gridGamesFinished.refresh()
                self.gridGamesQueued.refresh()
                self.gridResults.refresh()
                self.rotulos_tabs()

            QtCore.QTimer.singleShot(5000, self.comprueba_cambios)

    def grabar(self):
        if self.torneo:
            self.torneo.resign(self.ed_resign.textoInt())
            self.torneo.draw_min_ply(self.ed_draw_min_ply.textoInt())
            self.torneo.draw_range(self.ed_draw_range.textoInt())
            self.torneo.fen(self.fen)
            self.torneo.norman(self.chbNorman.valor())
            self.torneo.slow_pieces(self.chb_slow.valor())
            self.torneo.book(self.cbBooks.valor())
            self.torneo.book_depth(self.sbBookDepth.valor())
            self.torneo.adjudicator_active(self.gbJ.isChecked())
            self.torneo.adjudicator(self.cbJmotor.valor())
            self.torneo.adjudicator_time(self.edJtiempo.textoFloat())

    def eng_new(self):
        # Pedimos el ejecutable
        exe_motor = SelectFiles.leeFichero(self, self.torneo.ultCarpetaEngines(), "*", _("Engine"))
        if not exe_motor:
            return
        self.torneo.ultCarpetaEngines(os.path.dirname(exe_motor))

        # Leemos el UCI
        me = Engines.read_engine_uci(exe_motor)
        if not me:
            QTUtil2.message_bold(self, _X(_("The file %1 does not correspond to a UCI engine type."), exe_motor))
            return
        eng = Tournament.EngineTournament()
        eng.restore(me.save())
        eng.pon_huella(self.torneo)
        self.torneo.save_engine(eng)
        self.gridEnginesAlias.refresh()
        self.gridEnginesAlias.gobottom(0)

        self.gridResults.refresh()

        self.rotulos_tabs()

    # def enImportarTodos(self):
    #     lista = self.configuration.combo_engines()
    #     for name, key in lista:
    #         for depth in range(1, 5):
    #             me = Tournament.EngineTournament()
    #             me.pon_huella(self.torneo)
    #             me.read_exist_engine(key)
    #             me.key = key + " - depth %d" % depth
    #             me.depth = depth
    #             me.elo = 1500
    #             self.torneo.save_engine(me)
    #     self.gridEnginesAlias.refresh()
    #     self.gridEnginesAlias.gobottom(0)
    #     self.gridResults.refresh()
    #     self.rotulos_tabs()

    def eng_import(self):
        resp = self.internal_engines.menu(self)
        if not resp:
            return

        me = Tournament.EngineTournament()
        me.pon_huella(self.torneo)
        me.restore(resp.save())
        me.alias = me.key = me.name
        me.depth = me.max_depth

        self.torneo.save_engine(me)
        self.gridEnginesAlias.refresh()
        self.gridEnginesAlias.gobottom(0)

        self.gridResults.refresh()

        self.rotulos_tabs()

    def grid_tecla_control(self, grid, k, is_shift, is_control, is_alt):
        if k in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
            if grid == self.gridGamesQueued:
                self.gm_borrar_queued()
            elif grid == self.gridEnginesAlias:
                self.eng_remove()
            elif grid == self.gridGamesFinished:
                self.gm_borrar_finished()

    def grid_doble_click(self, grid, row, column):
        if grid in [self.gridEnginesAlias, self.gridEnginesValores]:
            self.eng_modify()
        elif grid == self.gridGamesFinished:
            self.gm_show_finished()

    def grid_color_fondo(self, grid, nfila, ocol):
        if grid == self.gridResults:
            key = ocol.key
            if "WHITE" in key:
                return self.qtColor["WHITE"]
            elif "BLACK" in key:
                return self.qtColor["BLACK"]
            elif "SCORE" in key:
                return self.qtColor["SCORE"]

    def eng_modify(self):
        row = self.gridEnginesAlias.recno()
        if row < 0:
            return
        me = self.torneo.engine(row)

        w = WEngines.WEngineExtend(self, self.torneo.list_engines(), me, is_tournament=True)
        if w.exec_():
            self.act_engine(me)
            self.torneo.save_engine(me)
            self.gridEnginesAlias.refresh()
            self.gridEnginesValores.refresh()
            self.gridResults.refresh()

    def eng_remove(self):
        li = self.gridEnginesAlias.recnosSeleccionados()
        if li:
            clista = ",".join([self.torneo.engine(pos).name for pos in li])
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?") + "\n\n%s" % clista):
                self.torneo.remove_engines(li)
                self.gridEnginesAlias.refresh()
                if self.torneo.num_engines() > 0:
                    self.grid_cambiado_registro(self.gridEnginesAlias, 0, None)
                else:
                    self.liEnActual = []
                self.gridEnginesValores.refresh()
                self.gridGamesQueued.refresh()
                self.gridEnginesAlias.setFocus()
                self.gridResults.refresh()
                self.rotulos_tabs()

    def eng_copy(self):
        row = self.gridEnginesAlias.recno()
        if row >= 0:
            me = self.torneo.engine(row)
            self.torneo.copy_engine(me)
            self.calc_results()
            self.gridEnginesAlias.refresh()
            self.gridEnginesAlias.gobottom(0)
            self.gridResults.refresh()
            self.rotulos_tabs()

    def gm_crear_queued(self):
        li_engines = self.torneo.list_engines()
        n_engines = len(li_engines)
        if n_engines < 2:
            QTUtil2.message_error(self, _("You must use at least two engines"))
            return

        dic_valores = self.configuration.read_variables("crear_torneo")

        get = dic_valores.get

        form = FormLayout.FormLayout(self, _("Games"), Iconos.Torneos())

        form.separador()
        form.spinbox(_("Rounds"), 1, 999, 50, get("ROUNDS", 1))

        form.separador()
        form.float(_("Total minutes"), get("MINUTES", 10.00))

        form.separador()
        form.float(_("Seconds added per move"), get("SECONDS", 0.0))

        form.add_tab(_("Options"))

        li_groups = Util.div_list(li_engines, 20)
        for ngroup, group in enumerate(li_groups):
            for en in group:
                form.checkbox(en.key, get(en.huella, True))
            form.add_tab(_("Engines"))

        resp = form.run()
        if resp is None:
            return

        accion, li_resp = resp

        options = li_resp[0]

        dic_valores["ROUNDS"] = rounds = options[0]
        dic_valores["MINUTES"] = minutos = options[1]
        dic_valores["SECONDS"] = seconds = options[2]

        li_resp_engines = []
        for group in li_resp[1:]:
            li_resp_engines.extend(group)
        li_sel = []
        for num in range(self.torneo.num_engines()):
            en = li_engines[num]
            dic_valores[en.huella] = si = li_resp_engines[num]
            if si:
                li_sel.append(en.huella)

        self.configuration.write_variables("crear_torneo", dic_valores)

        n_sel = len(li_sel)
        if n_sel < 2:
            QTUtil2.message_error(self, _("You must use at least two engines"))
            return

        tr = 0
        for x in range(n_sel - 1):
            for y in range(x + 1, n_sel):
                tr += 2

        tt = rounds * tr
        pb = QTUtil2.BarraProgreso1(self, _("Games"), show_time=tt > 20)
        pb.set_total(tt)
        pb.mostrar()
        pos = 0
        for r in range(rounds):
            for x in range(n_sel - 1):
                for y in range(x + 1, n_sel):
                    self.torneo.new_game(li_sel[x], li_sel[y], minutos, seconds)
                    pos += 1
                    pb.pon(pos)
                    self.torneo.new_game(li_sel[y], li_sel[x], minutos, seconds)
                    pos += 1
                    pb.pon(pos)
                    if pb.is_canceled():
                        break
                if pb.is_canceled():
                    break
            if pb.is_canceled():
                break
            self.torneo.new_game_commit()
        pb.close()
        self.torneo.new_game_commit()

        self.gridGamesQueued.refresh()
        self.gridGamesQueued.gobottom()
        self.rotulos_tabs()

    def gm_borrar_queued(self):
        li = self.gridGamesQueued.recnosSeleccionados()
        if li:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                with QTUtil2.OneMomentPlease(self):
                    self.torneo.remove_games_queued(li)
                    self.gridGamesQueued.refresh()
                    self.gridResults.refresh()
                    self.rotulos_tabs()

    def gm_borrar_finished(self):
        li = self.gridGamesFinished.recnosSeleccionados()
        if li:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                with QTUtil2.OneMomentPlease(self):
                    self.torneo.remove_games_finished(li)
                    self.gridGamesFinished.refresh()
                    self.rotulos_tabs()

    def gm_show_finished(self):
        li = self.gridGamesFinished.recnosSeleccionados()
        if li:
            pos = li[0]
            um = QTUtil2.one_moment_please(self, _("Reading the game"))
            game = self.torneo.game_finished(pos).game()
            um.final()
            game = Code.procesador.manager_game(self, game, True, False, None)
            if game is not None:
                self.torneo.save_game_finished(pos, game)
                self.gridGamesFinished.refresh()
                self.rotulos_tabs()

    def gm_save_pgn(self):
        if self.torneo.num_games_finished() > 0:
            w = WindowSavePGN.WSaveVarios(self)
            if w.exec_():
                ws = WindowSavePGN.FileSavePGN(self, w.dic_result)
                if ws.open():
                    ws.um()
                    if not ws.is_new:
                        ws.write("\n\n")
                    for gm in self.torneo.db_games_finished:
                        game = Game.Game()
                        game.restore(gm.game_save)
                        ws.write(game.pgn())
                        ws.write("\n\n\n")
                    ws.close()
                    ws.um_final()

    def gm_save_database(self):
        if self.torneo.num_games_finished() > 0:
            dbpath = QTVarios.select_db(self, self.configuration, True, True, remove_autosave=True)
            if dbpath is None:
                return
            if dbpath == ":n":
                dbpath = WDB_Games.new_database(self, self.configuration)
                if dbpath is None:
                    return
            um = QTUtil2.one_moment_please(self, _("Saving..."))
            db = DBgames.DBgames(dbpath)
            for gm in self.torneo.db_games_finished:
                game = Game.Game()
                game.restore(gm.game_save)
                db.insert(game)
            um.final()
            db.close()
            QTUtil2.temporary_message(self, _("Saved"), 1.2)
