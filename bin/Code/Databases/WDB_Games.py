import csv
import os
import shutil
import time

from PySide2 import QtWidgets, QtCore

import Code
from Code import Util, XRun
from Code.Analysis import AnalysisGame, WindowAnalysisParam, RunAnalysisControl
from Code.Base import Game, Position
from Code.Base.Constantes import WHITE, BLACK, FEN_INITIAL, TACTICTHEMES, DBSHOW_INITIAL_POSITION, DBSHOW_FIRST_MOVE, DBSHOW_LAST_MOVE
from Code.Books import PolyglotImportExports
from Code.Databases import DBgames, WDB_Utils, DBgamesMov, RemoveCommentsVariations, WebExternalImporter
from Code.Databases import WDB_GUtils
from Code.GM import GM
from Code.LearnGame import WindowPlayGame, WindowLearnGame
from Code.Odt import WOdt
from Code.Openings import OpeningsStd
from Code.Openings import WindowOpenings
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import GridEditCols
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import SelectFiles
from Code.QT import WindowSavePGN
from Code.SQL import UtilSQL
from Code.Themes import WDB_Theme_Analysis
from Code.Translations import TrListas
from Code.Voyager import Voyager


class WGames(QtWidgets.QWidget):
    def __init__(self, wb_database, db_games, wsummary, si_select):
        QtWidgets.QWidget.__init__(self)

        self.wb_database = wb_database
        self.db_games = db_games  # <--setdbGames
        self.procesador = Code.procesador
        self.configuration = Code.configuration

        self.key_columns = "columns_database"

        self.wsummary = wsummary
        self.infoMove = None  # <-- setInfoMove
        self.summaryActivo = None  # movimiento activo en summary
        self.movenum = 0  # Se usa para indicarla al mostrar el pgn en infoMove

        self.si_select = si_select

        self.is_temporary = wb_database.is_temporary
        self.changes = False
        self.toolbar_save = False

        self.terminado = False  # singleShot

        self.ap = OpeningsStd.ap

        self.li_filter = []
        self.where = None

        self.last_opening = None

        # Grid
        o_columns = self.lista_columnas()
        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, altoFila=self.configuration.x_databases_rowheight,
                              siSeleccionMultiple=True, xid="wgames")
        self.grid.set_tooltip_header(
            _("For a numerical sort, press Ctrl (Alt or Shift) while double-clicking on the header."))

        # Status bar
        self.status = QtWidgets.QStatusBar(self)
        self.status.setFixedHeight(Controles.calc_fixed_width(22))

        # ToolBar
        self.tbWork = QTVarios.LCTB(self)
        self.set_toolbar()

        ly_tb = Colocacion.H().control(self.tbWork)

        layout = Colocacion.V().otro(ly_tb).control(self.grid).control(self.status).margen(1)

        self.setLayout(layout)

    def set_toolbar(self):
        self.tbWork.clear()
        add_tb = self.tbWork.new
        if self.si_select:
            add_tb(_("Accept"), Iconos.Aceptar(), self.wb_database.tw_aceptar)
            add_tb(_("Cancel"), Iconos.Cancelar(), self.wb_database.tw_cancelar)
            add_tb(_("First"), Iconos.Inicio(), self.tw_gotop)
            add_tb(_("Last"), Iconos.Final(), self.tw_gobottom)
            add_tb(_("Filter"), Iconos.Filtrar(), self.tw_filtrar)
        else:
            add_tb(_("Close"), Iconos.MainMenu(), self.wb_database.tw_terminar)
            if self.changes and self.is_temporary:
                add_tb(_("Save"), Iconos.Grabar(), self.tw_exportar_pgn)

            add_tb(_("Edit"), Iconos.Modificar(), self.tw_edit)
            add_tb(_("New"), Iconos.Nuevo(), self.tw_nuevo, _("Add a new game"))
            add_tb(_("Filter"), Iconos.Filtrar(), self.tw_filtrar)
            add_tb(_("First"), Iconos.Inicio(), self.tw_gotop)
            add_tb(_("Last"), Iconos.Final(), self.tw_gobottom)
            add_tb(_("Up"), Iconos.Arriba(), self.tw_up)
            add_tb(_("Down"), Iconos.Abajo(), self.tw_down)
            add_tb(_("Remove"), Iconos.Borrar(), self.tw_remove)
            add_tb(_("Config"), Iconos.Configurar(), self.tw_configure)
            add_tb(_("Utilities"), Iconos.Utilidades(), self.tw_utilities)
            add_tb(_("Import"), Iconos.Import8(), self.tw_import)
            add_tb(_("Export"), Iconos.Export8(), self.tw_export)
            add_tb(_("Train"), Iconos.TrainStatic(), self.tw_train)

    def set_changes(self, ok):
        if self.changes == ok:
            return
        self.changes = ok
        if self.is_temporary:
            self.set_toolbar()

    def tw_train(self):
        menu = QTVarios.LCMenu(self)
        submenu = menu.submenu(_("Learn a game"), Iconos.School())
        submenu.opcion(self.tw_memorize, _("Memorizing their moves"), Iconos.LearnGame())
        submenu.separador()
        submenu.opcion(self.tw_play_against, _("Playing against"), Iconos.Law())
        menu.separador()

        submenu = menu.submenu(_("Create trainings"), Iconos.Entrenamiento())
        eti = '"' + _("Play like a Grandmaster") + '"'
        submenu.opcion(self.tw_gm, _X(_("Create training to %1"), eti), Iconos.GranMaestro())
        submenu.separador()
        eti = '"' + _("Learn tactics by repetition") + '"'
        submenu.opcion(self.tw_uti_tactic, _X(_("Create training to %1"), eti), Iconos.Tacticas())
        if self.db_games.has_positions():
            submenu.separador()
            eti = '"' + _("Training positions") + '"'
            submenu.opcion(self.tw_training_positions, _X(_("Create training to %1"), eti), Iconos.Carpeta())

        resp = menu.lanza()
        if resp:
            resp()

    def tw_play_against(self):
        li = self.grid.recnosSeleccionados()
        if li:
            db_play = WindowPlayGame.DBPlayGame(self.configuration.file_play_game())
            recno = li[0]
            game = self.db_games.read_game_recno(recno)
            game.remove_info_moves()
            h = hash(game.xpv())
            recplay = db_play.recnoHash(h)
            if recplay is None:
                db_play.appendHash(h, game)
                recplay = db_play.recnoHash(h)
            db_play.close()

            XRun.run_lucas("-playagainst", str(recplay))

    def tw_memorize(self):
        li = self.grid.recnosSeleccionados()
        if li:
            with WindowLearnGame.DBLearnGame() as db_learn:
                um = QTUtil2.one_moment_please(self.wb_database)
                recno = li[0]
                game = self.db_games.read_game_recno(recno)
                db_learn.append_game(game)
                um.final()

                w = WindowLearnGame.WLearn1(self, db_learn, 0)
                w.exec_()

    def lista_columnas(self):
        drots = DBgames.drots
        dcabs = self.db_games.read_config("dcabs", drots.copy())
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("__num__", _("N."), 60, align_center=True)
        li_tags = self.db_games.li_tags()
        st100 = {"Event", "Site", "White", "Black"}
        for tag in li_tags:
            label = TrListas.pgn_label(tag)
            if label == tag:
                label = dcabs.get(tag, drots.get(label.upper(), label))
            align_center = tag not in ("EVENT", "SITE")
            ancho = 100 if tag in st100 else 80
            o_columns.nueva(tag, label, ancho, align_center=align_center)
        o_columns.nueva("rowid", _("Row ID"), 60, align_center=True)
        return o_columns

    def rehaz_columnas(self):
        li_tags = self.db_games.li_tags()
        o_columns = self.grid.o_columns
        si_cambios = False

        li_remove = []
        for n, col in enumerate(o_columns.li_columns):
            key = col.key
            if key not in li_tags and key not in ("__num__", "rowid"):
                li_remove.append(n)
        if li_remove:
            si_cambios = True
            li_remove.sort(reverse=True)
            for n in li_remove:
                del o_columns.li_columns[n]

        drots = DBgames.drots
        dcabs = self.db_games.read_config("dcabs", drots.copy())
        st100 = {"Event", "Site", "White", "Black"}
        st_actual = {col.key for col in self.grid.o_columns.li_columns}
        for tag in li_tags:
            if tag not in st_actual:
                label = TrListas.pgn_label(tag)
                if label == tag:
                    label = dcabs.get(label, drots.get(label.upper(), label))
                o_columns.nueva(tag, label, 100 if tag in st100 else 70, align_center=tag not in ("Event", "Site"))
                si_cambios = True

        if si_cambios:
            self.db_games.reset_cache()
            self.grid.releerColumnas()

    def setdbGames(self, db_games):
        self.db_games = db_games

    def setInfoMove(self, infoMove):
        self.infoMove = infoMove
        self.graphicBoardReset()

    def updateStatus(self):
        if self.terminado:
            return
        recs = self.db_games.reccount()
        if self.summaryActivo:
            game = self.summaryActivo.get("game", Game.Game())
            nj = len(game)
            if nj > 1:
                p = game.copia(nj - 2)
                txt = "%s | " % p.pgn_base_raw()
            else:
                txt = ""
            si_pte = self.db_games.if_there_are_records_to_read()
            if not si_pte:
                if recs:
                    txt += f'{_("Games")}: {recs:,}'
            else:
                txt += _("Reading") + "..."
            if self.where:
                where = self.where
                wxpv = 'XPV LIKE "'
                while wxpv in where:
                    pos = where.index(wxpv)
                    otro = where[pos + len(wxpv):]
                    pos_apos = otro.index('"')
                    xpv = otro[: pos_apos - 1]
                    g = Game.Game()
                    g.read_xpv(xpv)
                    pgn = g.pgn_base_raw(translated=True)
                    where = where[:pos] + pgn + where[pos + len(wxpv) + pos_apos + 1:]
                txt += " | %s: %s" % (_("Filter"), where)
        else:
            si_pte = self.db_games.if_there_are_records_to_read()
            txt = ""
            if not si_pte:
                if recs:
                    txt += "%s: %d" % (_("Games"), recs)
            else:
                txt += f'{_("Working...")}'

        if si_pte:
            QtCore.QTimer.singleShot(500, self.updateStatus)

        self.grid.refresh()

        self.status.showMessage(txt, 0)

    def grid_num_datos(self, grid):
        return self.db_games.reccount()

    def grid_dato(self, grid, nfila, ocol):
        key = ocol.key
        if key == "__num__":
            return str(nfila + 1)
        elif key == "rowid":
            return str(self.db_games.get_rowid(nfila))
        elif key == "__opening__":
            xpv = self.db_games.field(nfila, "XPV")
            if xpv[0] != "|":
                return self.ap.xpv(xpv)
            return ""
        return self.db_games.field(nfila, key)

    def grid_right_button(self, grid, row, col, modif):
        key = col.key
        if key.upper() in ("ROWID", "PLYCOUNT") or key.startswith("__"):
            return

        value = self.db_games.field(row, key)
        new_value = QTUtil2.read_simple(self, _("Edit"), col.head, value, width=300, in_cursor=True)
        if new_value is None:
            return
        new_value = new_value.strip()
        self.set_changes(True)

        for row in self.grid.recnosSeleccionados():
            self.db_games.set_field(row, key, new_value)

        self.grid.refresh()

    def grid_doble_click(self, grid, fil, col):
        if self.si_select:
            self.wb_database.tw_aceptar()
        else:
            self.tw_edit()

    def grid_doubleclick_header(self, grid, col):
        key = col.key
        if key in ("__num__"):
            return
        is_shift, is_control, is_alt = QTUtil.keyboard_modifiers()
        is_numeric = is_shift or is_control or is_alt
        li_order = self.db_games.get_order()
        if key == "opening":
            key = "XPV"
        is_already = False
        for n, (cl, tp, is_num) in enumerate(li_order):
            if cl == key:
                is_already = True
                if tp == "ASC":
                    li_order[n] = (key, "DESC", is_numeric)
                    col.head = col.head.strip("+-") + "-"
                    if n:
                        del li_order[n]
                        li_order.insert(0, (key, "DESC", is_numeric))

                elif tp == "DESC":
                    del li_order[n]
                    col.head = col.head[:-1]
                break
        if not is_already:
            li_order.insert(0, (key, "ASC", is_numeric))
            col.head += "+"
        self.db_games.put_order(li_order)
        self.grid.refresh()
        self.grid.gotop()
        self.updateStatus()
        self.grid_cambiado_registro(None, 0, None)

    def grid_tecla_control(self, grid, k, is_shift, is_control, is_alt):
        if k in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            self.tw_edit()
        elif k in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Right):
            self.infoMove.tecla_pulsada(k)
            row, col = self.grid.posActualN()
            if QtCore.Qt.Key_Right:
                if col > 0:
                    col -= 1
            elif QtCore.Qt.Key_Left:
                if col < len(self.grid.columnas().li_columns) - 1:
                    col += 1
            self.grid.goto(row, col)
        elif k == QtCore.Qt.Key_Home:
            self.tw_gotop()
        elif k == QtCore.Qt.Key_End:
            self.tw_gobottom()
        elif k == QtCore.Qt.Key_G and is_control:
            self.goto_registro()
        elif k == QtCore.Qt.Key_R and is_alt:
            self.tw_resize_columns()
        elif k == QtCore.Qt.Key_Delete:
            self.tw_remove()
        elif is_alt and k == QtCore.Qt.Key_C:
            self.tw_menu_columns()

        else:
            return True  # que siga con el resto de teclas

    def goto_registro(self):
        total = self.db_games.reccount()
        if total:
            registro = QTUtil2.read_simple(self, self.db_games.get_name(), _("Go to the record"), "")
            if registro and registro.isdigit():
                num_registro = min(max(int(registro) - 1, 0), total - 1)
                self.grid.goto(num_registro, 0)

    def closeEvent(self, event):
        self.tw_terminar()

    def tw_terminar(self):
        if self.is_temporary and self.changes:
            if QTUtil2.pregunta(self, _("Changes have been made, do you want to export them to a PGN file?")):
                self.tw_exportar_pgn(False)
        self.terminado = True
        self.db_games.close()

    def actualiza(self, siObligatorio=False):
        def pvSummary(summary):
            if summary is None:
                return ""
            xlipv = summary.get("pv", "").split(" ")
            return " ".join(xlipv[:-1])

        if self.wsummary:
            summary_activo = self.wsummary.movActivo()
            if siObligatorio or pvSummary(self.summaryActivo) != pvSummary(summary_activo) or self.li_filter:
                self.where = None
                self.summaryActivo = summary_activo
                pv = ""
                if self.summaryActivo:
                    pv = self.summaryActivo.get("pv")
                    if pv:
                        lipv = pv.split(" ")
                        pv = " ".join(lipv[:-1])
                    else:
                        pv = ""
                self.db_games.filter_pv(pv)
                self.updateStatus()
                self.movenum = pv.count(" ")
                self.grid.refresh()
                self.grid.gotop()
        else:
            if siObligatorio or self.li_filter:
                self.where = None
                self.db_games.filter_pv("")
                self.updateStatus()
                self.grid.refresh()
                self.grid.gotop()

        self.show_current()

    def show_current(self):
        recno = self.grid.recno()
        if recno >= 0:
            self.grid_cambiado_registro(None, recno, None)
        else:
            self.infoMove.game_mode(Game.Game(), 0)

    def grid_cambiado_registro(self, grid, row, oCol):
        if self.grid_num_datos(grid) > row >= 0:
            self.setFocus()
            self.grid.setFocus()
            fen, pv = self.db_games.get_pv(row)
            if fen:
                p = Game.Game(fen=fen)
                p.read_pv(pv)
                p.is_finished()
                option = self.configuration.x_dbshow_positions
            else:
                p = Game.Game()
                p.read_pv(pv)
                p.assign_opening()
                p.is_finished()
                option = self.configuration.x_dbshow_completegames

            if option == DBSHOW_LAST_MOVE:
                pos = len(p)-1
            elif option == DBSHOW_INITIAL_POSITION:
                pos = -1
            else:
                pos = 0

            if fen:
                self.infoMove.fen_mode(p, fen, pos)
            else:
                self.infoMove.game_mode(p, pos)

    def tw_gobottom(self):
        self.grid.gobottom()

    def tw_gotop(self):
        self.grid.gotop()

    def tw_up(self):
        row = self.grid.recno()
        if row >= 0:
            fila_nueva = self.db_games.interchange(row, True)
            self.set_changes(True)
            if fila_nueva is not None:
                self.grid.goto(fila_nueva, 0)
                self.grid.refresh()

    def tw_down(self):
        row = self.grid.recno()
        if row >= 0:
            fila_nueva = self.db_games.interchange(row, False)
            self.set_changes(True)
            if fila_nueva is not None:
                self.grid.goto(fila_nueva, 0)
                self.grid.refresh()

    def edit_save(self, recno, game):
        if game is not None:
            resp = self.db_games.save_game_recno(recno, game)
            if resp.ok:
                if not resp.changed:
                    return

                if self.wsummary and resp.summary_changed:
                    self.wsummary.rehazActual()

                if resp.inserted:
                    self.updateStatus()

                if recno is None:
                    self.grid.gobottom()
                else:
                    resp.recno = recno
                    self.grid.goto(recno, 0)
                    self.grid_cambiado_registro(self, recno, None)
                self.rehaz_columnas()
                self.grid.refresh()
                self.set_changes(True)
                return resp

            else:
                QTUtil2.message_error(self, resp.mens_error)
        return None

    def edit_previous_next(self, order, game):
        if not hasattr(game, "recno"):
            game.recno = self.grid.recno()
        if order == "save":
            self.edit_save(game.recno, game)
        elif order == "with_previous_next":
            return game.recno > 0, game.recno < self.grid_num_datos(self.grid)
        elif order == "previous":
            recno = game.recno - 1
            if recno >= 0:
                self.grid.goto(recno, 0)
                game, recno = self.current_game()
                game.recno = recno
            return game
        elif order == "next":
            recno = game.recno + 1
            if recno < len(self.db_games):
                self.grid.goto(recno, 0)
                game, recno = self.current_game()
                if game:
                    game.recno = recno
            return game

    def edit(self, recno, game):
        if recno is None:
            with_previous_next = None
        else:
            with_previous_next = self.edit_previous_next
        game.recno = recno
        game = self.procesador.manager_game(self, game, not self.db_games.allows_positions, False, self.infoMove.board,
            with_previous_next=with_previous_next, save_routine=self.edit_save, )
        if game:
            self.set_changes(True)
            self.edit_save(game.recno, game)

    def tw_nuevo(self):
        recno = None
        pc = self.db_games.blank_game()
        self.edit(recno, pc)

    def tw_edit(self):
        if self.grid.recno() >= 0:
            um = QTUtil2.one_moment_please(self.wb_database, _("Reading the game"))
            game, recno = self.current_game()
            um.final()
            if game is not None:
                self.edit(recno, game)
            elif recno is not None:
                QTUtil2.message_bold(self, _("This game is wrong and can not be edited"))

    def current_game(self):
        li = self.grid.recnosSeleccionados()
        if li:
            recno = li[0]

            game = self.db_games.read_game_recno(recno)
        else:
            recno = None
            game = None
        return game, recno

    def tw_filtrar(self):
        xpv = None
        if self.summaryActivo and "pv" in self.summaryActivo:
            li = self.summaryActivo["pv"].split(" ")
            if len(li) > 1:
                xpv = " ".join(li[:-1])

        def refresh():
            self.grid.refresh()
            self.grid.gotop()
            self.updateStatus()
            self.grid_cambiado_registro(None, 0, 0)

        def standard():
            w = WDB_Utils.WFiltrar(self, self.li_filter, self.db_games.path_file)
            if w.exec_():
                self.li_filter = w.li_filter

                self.where = w.where()
                self.db_games.filter_pv(xpv, self.where)
                refresh()

        def raw_sql():
            w = WDB_Utils.WFiltrarRaw(self, self.grid.o_columns, self.where)
            if w.exec_():
                self.where = w.where
                self.db_games.filter_pv(xpv, self.where)
                refresh()

        def opening():
            me = QTUtil2.one_moment_please(self.wb_database)

            w = WindowOpenings.WOpenings(self.wb_database, self.last_opening)
            me.final()
            if w.exec_():
                self.last_opening = ap = w.resultado()
                pv = getattr(ap, "a1h8", "")
                self.db_games.filter_pv(pv)
                self.where = self.db_games.filter
                self.movenum = pv.count(" ")
                refresh()

        def remove_filter():
            self.db_games.filter_pv("")
            self.where = None
            if self.summaryActivo:
                self.summaryActivo["game"] = Game.Game()
                self.wsummary.start()
            refresh()

        menu = QTVarios.LCMenu(self)
        menu.opcion(standard, _("Standard"), Iconos.Filtrar())
        menu.separador()
        menu.opcion(raw_sql, _("Advanced"), Iconos.SQL_RAW())
        menu.separador()
        menu.opcion(opening, _("Opening"), Iconos.Opening())
        menu.separador()
        menu.opcion(self.filter_position, _("By position"), Iconos.Board())
        if self.db_games.filter is not None and self.db_games.filter:
            menu.separador()
            menu.opcion(remove_filter, _("Remove filter"), Iconos.Cancelar())

        resp = menu.lanza()
        if resp:
            resp()

    def generate_positions_file(self):
        pb = QTUtil2.BarraProgreso1(self, _("Indexing..."), formato1="%p%", show_time=True)
        pb.mostrar()
        pb.set_total(self.db_games.reccount())
        fp = DBgamesMov.DBgamesMov(self.db_games)
        resp = fp.generate(pb)
        pb.close()
        return resp

    def update_positions_file(self):
        fp = DBgamesMov.DBgamesMov(self.db_games)
        total = fp.pending()
        pb = QTUtil2.BarraProgreso1(self, _("Indexing..."), formato1="%p%", show_time=True)
        pb.mostrar()
        pb.set_total(total)
        resp = fp.update(pb)
        pb.close()
        return resp

    def filter_position(self):
        fp = DBgamesMov.DBgamesMov(self.db_games)
        if fp.need_generate():
            if not QTUtil2.pregunta(self,
                                    _("A position index file needs to be created, which can be a lengthy process, shall we continue?")):
                return
            if not self.generate_positions_file():
                return
        elif fp.pending() > 0:
            if not self.update_positions_file():
                return

        key = "LAST_FEN_SEARCHED"
        last_fen_searched = self.db_games.read_config(key, FEN_INITIAL)
        position = Position.Position()
        position.read_fen(last_fen_searched)
        position, is_white = Voyager.voyager_position(self, position)
        if position is None:
            return
        fen = position.fen()
        self.db_games.save_config(key, fen)
        resp = fp.filter(fen)
        if resp is None:
            QTUtil2.message_bold(self, _("No game has been found with this position"))
            return
        li_seq, li_games = resp
        self.db_games.filter_positions(li_seq, [rowid for rowid, pos in li_games])
        self.grid.refresh()
        self.grid_cambiado_registro(None, 0, None)
        txt = "%s: %d | %s: %s" % (_("Games"), self.db_games.reccount(), _("Filter"), fen)
        self.status.showMessage(txt, 0)

    def tw_remove(self):
        li = self.grid.recnosSeleccionados()
        if li:
            if not QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                return

            um = QTUtil2.working(self)
            self.set_changes(True)
            self.db_games.remove_list_recnos(li)
            if self.summaryActivo:
                self.summaryActivo["games"] -= len(li)
                self.wsummary.reset()
            self.grid.refresh()
            self.updateStatus()

            self.show_current()
            recno = self.grid.recno()
            if recno >= 0:
                self.grid.goto(recno, 0)

            um.final()

    def tw_import(self):
        menu = QTVarios.LCMenu(self)
        submenu = menu.submenu(_("From a PGN file"), Iconos.FichPGN())
        submenu.opcion(self.tw_importar_pgn, _("Complete"), Iconos.PuntoVerde())
        submenu.separador()
        submenu.opcion(self.tw_importar_pgn_rem, _("Remove comments and variations"), Iconos.PuntoRojo())
        menu.separador()
        menu.opcion(self.tw_importar_db, _("From other database"), Iconos.Database())
        menu.separador()
        submenu = menu.submenu(_("Paste PGN"), Iconos.Pegar16())
        submenu.opcion(self.tw_paste_pgn, _("Complete"), Iconos.PuntoVerde())
        submenu.separador()
        submenu.opcion(self.tw_paste_pgn_rem, _("Remove comments and variations"), Iconos.PuntoRojo())
        menu.separador()
        menu.opcion(self.tw_importar_db, _("From other database"), Iconos.Database())
        menu.separador()
        if self.db_games.allows_positions and (self.db_games.reccount() == 0 or not self.db_games.allows_duplicates):
            menu.opcion(self.tw_importar_lichess_puzzles, _("From the Lichess Puzzle Database"), Iconos.Lichess())
        menu.separador()
        submenu = menu.submenu(_("Games of a user in"), Iconos.Usuarios())
        submenu.opcion(self.tw_importar_lichess_user, "lichess.org", Iconos.Lichess())
        submenu.separador()
        submenu.opcion(self.tw_importar_chesscom_user, "chess.com", Iconos.ChessCom())
        resp = menu.lanza()
        if resp:
            resp()

    def tw_export(self):
        li_all = range(self.db_games.reccount())
        if not li_all:
            return None
        li_sel = self.grid.recnosSeleccionados()

        menu = QTVarios.LCMenu(self)

        submenu = menu.submenu(_("To a PGN file"), Iconos.FichPGN())
        submenu.opcion((self.tw_exportar_pgn, False), _("All registers"), Iconos.PuntoVerde())
        if li_sel:
            submenu.separador()
            submenu.opcion((self.tw_exportar_pgn, True), "%s [%d]" % (_("Only selected games"), len(li_sel)),
                Iconos.PuntoAzul())

        menu.separador()
        submenu = menu.submenu(_("To a CSV file"), Iconos.CSV())
        submenu.opcion((self.tw_exportar_csv, False), _("All registers"), Iconos.PuntoVerde())
        if li_sel:
            submenu.separador()
            submenu.opcion((self.tw_exportar_csv, True), "%s [%d]" % (_("Only selected games"), len(li_sel)),
                Iconos.PuntoAzul())

        menu.separador()
        submenu = menu.submenu(_("To other database"), Iconos.Database())
        submenu.opcion((self.tw_exportar_db, li_all), _("All registers"), Iconos.PuntoVerde())
        if li_sel:
            submenu.separador()
            submenu.opcion((self.tw_exportar_db, li_sel), "%s [%d]" % (_("Only selected games"), len(li_sel)),
                Iconos.PuntoAzul())

        if self.db_games.has_positions():
            menu.separador()
            menu.opcion((self.tw_odt, None), _("To a position sheet in ODF format"), Iconos.ODT())

        menu.separador()

        resp = menu.lanza()
        if resp:
            funcion, lista = resp
            if lista is not None:
                funcion(lista)
            else:
                funcion()

    def tw_odt(self):
        key_var = "ODT"
        dic = self.configuration.read_variables(key_var)
        folder = dic.get("FOLDER_SAVE", self.configuration.carpeta)
        path = os.path.join(folder, self.db_games.get_name() + ".odt")

        form = FormLayout.FormLayout(self, _("Export"), Iconos.ODT(), anchoMinimo=640)
        form.separador()
        form.file(_("Save as"), "odt", True, path)
        form.separador()
        form.checkbox(_("Skip the first move"), False)
        form.separador()

        li_registros_selected = self.grid.recnosSeleccionados()
        li_registros_total = list(range(self.db_games.reccount()))
        nreg_selected = len(li_registros_selected)
        if nreg_selected > 1:
            form.checkbox(f'{_("Only selected games")} ({nreg_selected})', True)
            form.separador()

        resultado = form.run()
        if not resultado:
            return

        accion, li_gen = resultado

        path_odt = li_gen[0]
        if not path_odt:
            return
        dic["FOLDER_SAVE"] = os.path.dirname(path)
        self.configuration.write_variables(key_var, dic)

        skip_first = li_gen[1]
        if nreg_selected > 1:
            li_registros = li_registros_selected if li_gen[2] else li_registros_total
        else:
            li_registros = li_registros_total

        um = QTUtil2.working(self)
        li_fens_pgn = self.db_games.get_fens_pgn(li_registros, skip_first)
        total = len(li_fens_pgn)
        um.final()
        if total == 0:
            return

        dic = {"POS": 0, "TOTAL": total}

        wodt = WOdt.WOdt(self, path_odt)
        board = wodt.board
        tname = "Table3x2"
        wodt.create_document("", False, margins=(1.0, 1.0, 1.0, 1.0))
        wodt.odt_doc.register_table(tname, 2)
        dic["TABLE"] = wodt.odt_doc.create_table(tname)

        def run_data(wodt):
            current_pos = dic["POS"]

            table = dic["TABLE"]

            wodt.set_cpos("%d/%d" % (current_pos + 1, total))

            odt_doc = wodt.odt_doc

            row = None

            for posx in range(current_pos, min(current_pos + 6, total)):
                fen, pgn = li_fens_pgn[posx]
                position = Position.Position()
                position.read_fen(fen)

                board.set_position(position)
                # if board.is_white_bottom != position.is_white:
                #     board.rotate_board()
                path_img = self.configuration.temporary_file("png")
                board.save_as_img(path_img, "png", False, True)

                if posx % 2 == 0:
                    row = odt_doc.add_row(table)
                cell = odt_doc.add_cell(row)
                odt_doc.add_png(path_img, 6.6, align_center=True, parent=cell)
                odt_doc.add_linebreak(parent=cell)
                side = "_" if position.is_white else '■'
                odt_doc.add_paragraph(f"{posx + 1:3d} {side}___________________________", align_center=True,
                                      parent=cell)
                odt_doc.add_linebreak(parent=cell)

                dic["POS"] = posx + 1
            return dic["POS"] < total

        wodt.set_routine(run_data)
        if wodt.exec_():
            wodt.odt_doc.add_pagebreak()
            for pos, (fen, pgn) in enumerate(li_fens_pgn, 1):
                if pgn:
                    wodt.odt_doc.add_paragraph(f"{pos:3d}:   {pgn}")
                    wodt.odt_doc.add_linebreak()

            wodt.odt_doc.create(path_odt)

    def tw_configure(self):
        menu = QTVarios.LCMenu(self)

        if not self.is_temporary:
            menu.opcion(self.tw_options, _("Database options"), Iconos.Opciones())
            menu.separador()

        menu.opcion(self.tw_edit_columns, _("Configure the columns"), Iconos.EditColumns(), shortcut="ALT+C")
        menu.separador()

        menu.opcion(self.tw_resize_columns, _("Resize all columns to contents"), Iconos.ResizeAll(), shortcut="ALT+R")
        menu.separador()

        menu.opcion(self.tw_change_height, _("Change the height of each row"), Iconos.Height())
        menu.separador()

        submenu = menu.submenu(_("Graphic elements (Director)"), Iconos.Script())

        si_show = self.db_games.read_config("GRAPHICS_SHOW_ALLWAYS", False)
        submenu.opcion(self.tw_dir_show_change, _("Show always"), is_checked=si_show)
        submenu.separador()

        si_graphics_specific = self.db_games.read_config("GRAPHICS_SPECIFIC", False)
        submenu.opcion(self.tw_locale_change, _("Specific to this database"), Iconos.PuntoAzul(),
                       is_checked=si_graphics_specific)
        menu.separador()

        submenu = menu.submenu(_("First display on the board"), Iconos.Board())

        def add_subsubmenu(label, ico, key, option):
            subsubmenu = submenu.submenu(label, ico)
            subsubmenu.opcion((key, DBSHOW_INITIAL_POSITION), _("Initial position"), is_checked= option == DBSHOW_INITIAL_POSITION)
            subsubmenu.separador()
            subsubmenu.opcion((key, DBSHOW_FIRST_MOVE), _("First movement"), is_checked= option == DBSHOW_FIRST_MOVE)
            subsubmenu.separador()
            subsubmenu.opcion((key, DBSHOW_LAST_MOVE), _("Last movement"), is_checked= option == DBSHOW_LAST_MOVE)
            submenu.separador()

        add_subsubmenu(_("Positions"), Iconos.Board(), "show_positions", self.configuration.x_dbshow_positions)
        add_subsubmenu(_("Complete games"), Iconos.Training_Games(), "show_completegames", self.configuration.x_dbshow_completegames)

        resp = menu.lanza()
        if resp:
            if isinstance(resp, tuple):
                key, option = resp
                if key == "show_positions":
                    self.configuration.x_dbshow_positions = option
                else:
                    self.configuration.x_dbshow_completegames = option
                self.configuration.graba()
                if self.grid.recno() > -1:
                    self.grid_cambiado_registro(None, self.grid.recno(), None)
            else:
                resp()

    def tw_options(self):
        db = self.db_games
        dic_data = {"NAME": db.get_name(), "LINK_FILE": db.link_file, "FILEPATH": db.path_file,
            "EXTERNAL_FOLDER": db.external_folder, "SUMMARY_DEPTH": db.depth_stat(),
            "ALLOWS_DUPLICATES": db.read_config("ALLOWS_DUPLICATES", True),
            "ALLOWS_POSITIONS": db.read_config("ALLOWS_POSITIONS", True),
            "ALLOWS_COMPLETE_GAMES": db.read_config("ALLOWS_COMPLETE_GAMES", True),
            "ALLOWS_ZERO_MOVES": db.read_config("ALLOWS_ZERO_MOVES", True), }
        w = WDB_GUtils.WOptionsDatabase(self, self.configuration, dic_data)
        if not w.exec_():
            return None

        dic_data = w.dic_data_resp
        db.save_config("ALLOWS_DUPLICATES", dic_data["ALLOWS_DUPLICATES"])
        db.save_config("ALLOWS_POSITIONS", dic_data["ALLOWS_POSITIONS"])
        db.save_config("ALLOWS_COMPLETE_GAMES", dic_data["ALLOWS_COMPLETE_GAMES"])
        db.save_config("ALLOWS_ZERO_MOVES", dic_data["ALLOWS_ZERO_MOVES"])

        db.read_options()

        # Comprobamos depth
        new_depth = dic_data["SUMMARY_DEPTH"]
        if new_depth != self.db_games.depth_stat():
            self.wsummary.reindexar_question(new_depth, False)
            db.save_config("SUMMARY_DEPTH", new_depth)

        # Si ha cambiado la localización, se cierra, se mueve y se reabre en la nueva
        # Internal -> Internal
        old_is_internal = Util.same_path(self.db_games.path_file, self.db_games.link_file)
        old_is_external = not old_is_internal
        new_is_internal = len(dic_data["EXTERNAL_FOLDER"]) == 0
        new_is_external = not new_is_internal

        path_old_data = self.db_games.path_file
        path_new_data = dic_data["FILEPATH_WITH_DATA"]

        reinit = False
        must_close = True

        if new_is_external and old_is_external:
            new_link = dic_data["FILEPATH"]
            old_link = self.db_games.link_file
            if not Util.same_path(new_link, old_link):
                self.configuration.set_last_database(new_link)
                Util.remove_file(old_link)
                reinit = True
                must_close = True

        if new_is_internal and old_is_external:
            os.remove(self.db_games.link_file)

        if not Util.same_path(path_old_data, path_new_data):
            self.db_games.close()
            shutil.move(path_old_data, path_new_data)
            shutil.move(path_old_data + ".st1", path_new_data + ".st1")
            self.configuration.set_last_database(dic_data["FILEPATH"])
            reinit = True
            must_close = False

        if reinit:
            self.wb_database.reinit_sinsalvar(must_close)  # para que no cree de nuevo al salvar configuración

    def tw_tags(self):
        w = WDB_GUtils.WTags(self, self.db_games)
        if w.exec_():
            dic_cambios = w.dic_cambios

            um = QTUtil2.working(self)

            dcabs = self.db_games.read_config("dcabs", {})
            reinit = False

            # Primero CREATE
            for dic in dic_cambios["CREATE"]:
                self.db_games.add_column(dic["KEY"])
                dcabs[dic["KEY"]] = dic["LABEL"]
                reinit = True

            # Segundo FILL
            li_field_value = []
            for dic in dic_cambios["FILL"]:
                li_field_value.append((dic["KEY"], dic["VALUE"]))
            if li_field_value:
                self.db_games.fill(li_field_value)

            # Segundo FILL_PGN
            li_fill_pgn = []
            for dic in dic_cambios["FILL_PGN"]:
                li_fill_pgn.append(dic["KEY"])
            if li_fill_pgn:
                for key in li_fill_pgn:
                    um.label("%s: %s" % (key, w.fill_pgn))
                    self.db_games.fill_pgn(key)

            # Tercero RENAME_LBL
            for dic in dic_cambios["RENAME"]:
                dcabs[dic["KEY"]] = dic["LABEL"]
                reinit = True

            self.db_games.save_config("dcabs", dcabs)

            # Cuarto REMOVE
            lir = dic_cambios["REMOVE"]
            if len(lir) > 0:
                um = QTUtil2.working(self)
                lista = [x["KEY"] for x in lir]
                self.db_games.remove_columns(lista)
                self.set_changes(True)
                reinit = True
                um.final()

            if reinit:
                self.wb_database.reinit_sinsalvar()  # para que no cree de nuevo al salvar configuración

            else:
                self.db_games.reset_cache()
                self.grid.refresh()

            um.final()

    def readVarsConfig(self):
        show_always = self.db_games.read_config("GRAPHICS_SHOW_ALLWAYS")
        specific = self.db_games.read_config("GRAPHICS_SPECIFIC")
        return show_always, specific

    def graphicBoardReset(self):
        show_always, specific = self.readVarsConfig()
        fich_graphic = self.db_games.path_file if specific else None
        self.infoMove.board.dbvisual_set_file(fich_graphic)
        self.infoMove.board.dbvisual_set_show_always(show_always)

    def tw_dir_show_change(self):
        previo = self.db_games.read_config("GRAPHICS_SHOW_ALLWAYS", False)
        self.db_games.save_config("GRAPHICS_SHOW_ALLWAYS", not previo)
        self.graphicBoardReset()

    def tw_locale_change(self):
        previo = self.db_games.read_config("GRAPHICS_SPECIFIC", False)
        self.db_games.save_config("GRAPHICS_SPECIFIC", not previo)
        self.graphicBoardReset()

    def tw_resize_columns(self):
        um = QTUtil2.one_moment_please(self.wb_database, _("Resizing"))
        self.grid.resizeColumnsToContents()
        um.final()

    def tw_change_height(self):
        cheight = QTUtil2.read_simple(self, _("Databases"), _("Height"), str(self.configuration.x_databases_rowheight),
                                      mas_info=f'{_("By default")} = 24')
        if cheight:
            if cheight.isdigit():
                height = int(cheight)
                if height > 0:
                    self.configuration.x_databases_rowheight = height
                    self.configuration.graba()
                    self.grid.ponAltoFila(height)

    def tw_utilities(self):
        is_empty = self.db_games.is_empty()

        menu = QTVarios.LCMenu(self)
        if not is_empty:
            menu.opcion(self.tw_massive_analysis, _("Mass analysis"), Iconos.Analizar())
            menu.separador()
            menu.opcion(self.goto_registro, f'{_("Go to the record")} ({_("CTRL")}-G)', Iconos.GoToNext())
            menu.separador()
            menu.opcion(self.tw_polyglot, _("Create a polyglot book"), Iconos.Book())
            menu.separador()
            menu.opcion(self.tw_themes, _("Statistics on tactical themes"), Iconos.Tacticas())
            menu.separador()
            menu.opcion(self.tw_remove_duplicates, _("Remove duplicates"), Iconos.Remove1())
            menu.separador()
            submenu = menu.submenu(_("Remove comments/ratings/analysis"), Iconos.DeleteColumn())
            submenu1 = submenu.submenu(_("All elements"), Iconos.Borrar())
            submenu1.opcion(self.tw_remove_comments_all, _("All registers"), Iconos.PuntoVerde())
            li_sel = self.grid.recnosSeleccionados()
            submenu1.separador()
            submenu1.opcion(self.tw_remove_comments_selected, "%s [%d]" % (_("Only selected games"), len(li_sel)),
                            Iconos.PuntoAzul())
            submenu.separador()
            submenu2 = submenu.submenu(_("Certain elements"), Iconos.Director())
            submenu2.opcion(self.tw_remove_comments_partial_all, _("All registers"), Iconos.PuntoVerde())
            submenu2.separador()
            submenu2.opcion(self.tw_remove_comments_partial_selected,
                            "%s [%d]" % (_("Only selected games"), len(li_sel)), Iconos.PuntoAzul())
            menu.separador()
            menu.opcion(self.generate_positions_file, _("Regenerate index positions file"), Iconos.Board())
            menu.separador()

        menu.opcion(self.tw_tags, _("Update tags"), Iconos.Tags())
        menu.separador()
        menu.opcion(self.tw_pack, _("Pack database"), Iconos.Pack())

        resp = menu.lanza()
        if resp:
            resp()

    def tw_gm(self):
        name = ""
        player = ""
        li_selected = self.grid.recnosSeleccionados()
        selected = len(li_selected) > 1
        side = ""
        result = ""

        while True:
            title = _("Play like a Grandmaster")
            title = _X(_("Create training to %1"), title)
            form = FormLayout.FormLayout(self, title, Iconos.GranMaestro(), anchoMinimo=640)

            form.separador()

            form.edit(_("Training name"), name)
            form.separador()

            form.edit_np('<div align="right">%s:<br>%s</div>' % (_("Only the following players"),
                                                                 _("(You can add multiple aliases separated by ; and wildcards with *)"),),
                player, )
            form.separador()

            form.checkbox(_("Only selected games"), selected)
            form.separador()

            li = [(_("White & Black"), None), (_("White"), WHITE), (_("Black"), BLACK)]
            form.combobox(_("Side"), li, side)
            form.separador()

            li = [(_("Any"), None), (_("Win"), "Win"), (f'{_("Win")}+{_("Draw")}', "Win+Draw"), (_("Loss"), "Lost"),
                (f'{_("Loss")}+{_("Draw")}', "Lost+Draw"), ]
            form.combobox(_("Result"), li, result)
            form.separador()

            resultado = form.run()

            if resultado is None:
                return

            accion, li_gen = resultado
            name, player, selected, side, result = li_gen

            if not name:
                QTUtil2.message_error(self, _("Name missing"))
                continue

            name = Util.valid_filename(name)

            li_players = player.upper().split(";") if player else None

            fgm = GM.FabGM(name, li_players, side, result)

            if not selected:
                li_selected = range(self.db_games.reccount())
            nregs = len(li_selected)
            mensaje = _("Game") + "  %d/" + str(nregs)
            tmp_bp = QTUtil2.BarraProgreso(self, title, "", nregs).mostrar()

            for n, recno in enumerate(li_selected):
                if tmp_bp.is_canceled():
                    break

                game: Game.Game = self.db_games.read_game_recno(recno)
                if n:
                    tmp_bp.pon(n)
                tmp_bp.mensaje(mensaje % (n + 1,))

                if game.is_fen_initial():
                    fgm.other_game(game)

            is_canceled = tmp_bp.is_canceled()
            tmp_bp.cerrar()

            if not is_canceled:
                is_created = fgm.xprocesa()

                if is_created:
                    li_created = [name]
                    li_not_created = None
                else:
                    li_not_created = [name]
                    li_created = None
                WDB_Utils.message_creating_trainings(self, li_created, li_not_created)

            return

    def tw_uti_tactic(self):
        def rutina_datos(recno, skip_first):
            dic = {}
            for key in self.db_games.li_fields:
                dic[key] = self.db_games.field(recno, key)
            p: Game.Game = self.db_games.read_game_recno(recno)
            if skip_first:
                dic["PGN_REAL"] = p.pgn()
                p.skip_first()
            p.remove_bad_variations()
            fen = dic["FEN"] = p.first_position.fen()
            p.set_tag("FEN", fen)
            try:
                dic["PGN"] = p.pgn()
            except TypeError:
                return None
            dic["PLIES"] = len(p)
            return dic

        li_registros_selected = self.grid.recnosSeleccionados()
        li_registros_total = range(self.db_games.reccount())

        WDB_Utils.create_tactics(self.procesador, self, li_registros_selected, li_registros_total, rutina_datos,
            self.db_games.get_name())

    def tw_training_positions(self):
        def rutina_datos(recno, skip_first):
            try:
                dic = {}
                for key in self.db_games.li_fields:
                    dic[key] = self.db_games.field(recno, key)
                p = self.db_games.read_game_recno(recno)
                if skip_first:
                    dic["PGN_REAL"] = p.pgn()
                    p.skip_first()
                    dic["FEN"] = p.get_tag("FEN")
                p.remove_bad_variations()
                dic["PGN"] = p.pgn()
                dic["PLIES"] = len(p)
            except TypeError:
                QTUtil2.message_error(self, _("Error") + f": {recno + 1}")
                return {}
            return dic

        li_registros_selected = self.grid.recnosSeleccionados()
        li_registros_total = range(self.db_games.reccount())

        WDB_Utils.create_training_positions(self.procesador, self, li_registros_selected, li_registros_total,
            rutina_datos, self.db_games.get_name())

    def tw_pack(self):
        um = QTUtil2.one_moment_please(self.wb_database)
        self.db_games.pack()
        um.final()

    def tw_massive_analysis(self):
        li_seleccionadas = self.grid.recnosSeleccionados()
        n_seleccionadas = len(li_seleccionadas)

        alm = WindowAnalysisParam.massive_analysis_parameters(self, self.configuration, n_seleccionadas > 1,
            is_database=True)
        if not alm:
            return

        if alm.multiple_selected:
            nregs = n_seleccionadas
        else:
            nregs = self.db_games.reccount()
            li_seleccionadas = None

        if alm.workers == 1:
            self.tw_massive_analysis_1_worker(alm, nregs, li_seleccionadas)
        else:
            self.tw_massive_analysis_n_workers(alm, nregs, li_seleccionadas)

    def tw_massive_analysis_n_workers(self, alm, nregs, li_seleccionadas):
        rac = RunAnalysisControl.AnalysisMassiveWithWorkers(self, alm, nregs, li_seleccionadas)
        rac.run()

        if alm.accuracy_tags or alm.themes_tags:
            self.rehaz_columnas()

        self.procesador.entrenamientos.menu = None

    def tw_massive_analysis_1_worker(self, alm, nregs, li_seleccionadas):
        self.grid.setDisabled(True)
        self.tbWork.setDisabled(True)

        tmp_bp = QTUtil2.BarraProgreso2(self, _("Mass analysis"), formato2="%p%", with_pause=True)
        tmp_bp.set_total(1, nregs)
        tmp_bp.put_label(1, _("Game"))
        tmp_bp.put_label(2, _("Moves"))
        tmp_bp.mostrar()

        if alm.num_moves:
            lni = Util.ListaNumerosImpresion(alm.num_moves)
        else:
            lni = None

        ap = AnalysisGame.AnalyzeGame(alm, True)

        ap.cached_begin()

        for n in range(nregs):

            if tmp_bp.is_canceled():
                break
            tmp_bp.pon(1, n + 1)

            if alm.multiple_selected:
                recno = li_seleccionadas[n]
            else:
                recno = n

            game = self.db_games.read_game_recno(recno)
            self.grid.goto(recno, 0)
            #
            if lni:
                n_movs = len(game)
                li_movs = []
                if n_movs:
                    for nmov in range(n_movs):
                        nmove = nmov // 2 + 1
                        if lni.siEsta(nmove):
                            li_movs.append(nmov)
                ap.li_selected = li_movs
                if len(li_movs) == 0:
                    continue
            else:
                ap.li_selected = None
            ap.xprocesa(game, tmp_bp)

            self.db_games.save_game_recno(recno, game)
            self.set_changes(True)

        ap.cached_end()

        if not tmp_bp.is_canceled():
            ap.terminar(True)

            li_creados = []
            li_no_creados = []

            if alm.tacticblunders:
                if ap.siTacticBlunders:
                    li_creados.append(alm.tacticblunders)
                else:
                    li_no_creados.append(alm.tacticblunders)

            for x in (alm.pgnblunders, alm.fnsbrilliancies, alm.pgnbrilliancies):
                if x:
                    if Util.exist_file(x):
                        li_creados.append(x)
                    else:
                        li_no_creados.append(x)

            if alm.bmtblunders:
                if ap.si_bmt_blunders:
                    li_creados.append(alm.bmtblunders)
                else:
                    li_no_creados.append(alm.bmtblunders)
            if alm.bmtbrilliancies:
                if ap.si_bmt_brilliancies:
                    li_creados.append(alm.bmtbrilliancies)
                else:
                    li_no_creados.append(alm.bmtbrilliancies)
            if li_creados:
                WDB_Utils.message_creating_trainings(self, li_creados, li_no_creados)
                self.procesador.entrenamientos.rehaz()

        else:
            ap.terminar(False)

        if alm.accuracy_tags or alm.themes_tags:
            self.rehaz_columnas()

        tmp_bp.cerrar()

        self.grid.setDisabled(False)
        self.tbWork.setDisabled(False)

    def tw_themes(self):
        with QTUtil2.OneMomentPlease(self.wb_database, _("Analyzing tactical themes"), with_cancel=True) as um:
            a = WDB_Theme_Analysis.SelectedGameThemeAnalyzer(self, um)
            if a.is_canceled:
                return

        if len(a.dic_themes) == 0:
            QTUtil2.message(self, _("No themes were found in selected games!"))
            return
        wma = WDB_Theme_Analysis.WDBMoveAnalysis(self, a.li_output_dic, a.title, a.missing_tags_output)
        wma.exec_()

    def tw_remove_duplicates(self):
        if not QTUtil2.pregunta(self, "%s\n%s" % (_("Remove duplicates"), _("Are you sure?"))):
            return

        um = QTUtil2.one_moment_please(self.wb_database, _("Remove duplicates"))
        self.db_games.remove_duplicates()
        um.final()

        self.grid.refresh()
        self.updateStatus()

    def tw_remove_comments_all(self):
        self.tw_remove_comments(None)

    def tw_remove_comments_selected(self):
        self.tw_remove_comments(self.grid.recnosSeleccionados())

    def tw_remove_comments(self, li_regs):
        if not QTUtil2.pregunta(self, "%s\n%s" % (_("Remove comments/ratings/analysis"), _("Are you sure?"))):
            return

        with QTUtil2.OneMomentPlease(self.wb_database, _("Remove comments/ratings/analysis")):
            self.db_games.remove_data(li_regs)

        QTUtil2.temporary_message_without_image(self, _("Done"), 0.8)

    def tw_remove_comments_partial_all(self):
        self.tw_remove_comments_partial(None)

    def tw_remove_comments_partial_selected(self):
        self.tw_remove_comments_partial(self.grid.recnosSeleccionados())

    def tw_remove_comments_partial(self, li_regs):
        w = RemoveCommentsVariations.WRemoveCommentsVariations(self.wb_database, "databases_partial_remove2", False)
        if w.exec_():
            if li_regs is None:
                li_regs = range(self.db_games.reccount())

            if len(li_regs) == 0:
                return

            rem_themes = w.rem.rem_themes if self.db_games.has_field(TACTICTHEMES) else False

            pb = QTUtil2.BarraProgreso1(self, _("Remove comments and variations"), show_time=True)
            pb.set_total(len(li_regs))
            pb.mostrar()
            for pos, recno in enumerate(li_regs):
                if pb.is_canceled():
                    break
                pb.pon(pos)
                game = self.db_games.read_data(recno)
                if game is not None:
                    game, changed = w.run_game(game)
                    if changed:
                        self.set_changes(True)
                        if rem_themes:
                            game.del_tag(TACTICTHEMES)
                            self.db_games.modify(recno, game)
                        else:
                            self.db_games.save_data(recno, game)
            pb.close()
            self.grid.refresh()
            QTUtil2.temporary_message_without_image(self, _("Done"), 0.8)

    def tw_polyglot(self):
        titulo = self.db_games.get_name() + ".bin"
        resp = PolyglotImportExports.export_polyglot_config(self, self.configuration, titulo)
        if resp is None:
            return
        path_bin, uniform = resp
        resp = PolyglotImportExports.import_polyglot_config(self, self.configuration, os.path.basename(path_bin), False)
        if resp is None:
            return
        plies, st_side, st_results, ru, min_games, min_score, li_players, calc_weight, save_score = resp
        db = UtilSQL.DictBig()

        def fsum(keymove, pt):
            num, pts = db.get(keymove, (0, 0))
            num += 1
            pts += pt
            db[keymove] = num, pts

        dltmp = PolyglotImportExports.ImportarPGNDB(self, titulo)
        dltmp.show()

        ok = PolyglotImportExports.add_db(self.db_games, plies, st_results, st_side, li_players, ru, time.time, 1.2,
            dltmp.dispatch, fsum)
        dltmp.close()

        if ok:
            PolyglotImportExports.create_bin_from_dbbig(self, path_bin, db, min_games, min_score, calc_weight,
                save_score, uniform)

    def tw_exportar_db(self, lista):
        dbpath = QTVarios.select_db(self, self.configuration, False, True)
        if not dbpath:
            return
        if dbpath == ":n":
            name = os.path.basename(self.db_games.path_file) if self.is_temporary else ""
            dbpath = WDB_GUtils.new_database(self, self.configuration, name=name)
            if dbpath is None:
                return

        dl_tmp = QTVarios.ImportarFicheroDB(self)
        dl_tmp.ponExportados()
        dl_tmp.show()

        dbn = DBgames.DBgames(dbpath)
        if dbn.allows_duplicates:
            dl_tmp.hide_duplicates()
        dbn.append_db(self.db_games, lista, dl_tmp)
        dbn.close()
        if not self.is_temporary:
            self.changes = False

    def tw_exportar_pgn(self, only_selected=False):
        w = WindowSavePGN.WSaveVarios(self, with_remcomments=True)
        if w.exec_():
            dic_result = w.dic_result
            remove_comments = dic_result["REMCOMMENTSVAR"]
            with_seventags = dic_result["SEVENTAGS"]
            ws = WindowSavePGN.FileSavePGN(self, dic_result)
            if ws.open():
                pb = QTUtil2.BarraProgreso1(self, _("Saving..."), formato1="%v/%m (%p%)")
                pb.mostrar()
                if only_selected:
                    li_sel = self.grid.recnosSeleccionados()
                else:
                    li_sel = list(range(self.db_games.reccount()))
                pb.set_total(len(li_sel))
                for n, recno in enumerate(li_sel):
                    pb.pon(n)
                    try:
                        game = self.db_games.read_game_recno(recno)
                    except AttributeError:
                        return
                    if pb.is_canceled():
                        break
                    if game is None:
                        continue
                    if remove_comments:
                        game.remove_info_moves()
                    if with_seventags:
                        game.add_seventags()
                    pgn = game.pgn()
                    result = game.resultado()
                    if n > 0 or not ws.is_new:
                        ws.write("\n\n")
                    if result in ("*", "1-0", "0-1", "1/2-1/2"):
                        if not pgn.endswith(result):
                            pgn += " " + result
                    ws.write(pgn + "\n")

                if not pb.is_canceled():
                    self.set_changes(False)
                pb.close()
                ws.close()
                QTUtil2.temporary_message(self, _("Saved"), 1.2)

    def tw_exportar_csv(self, only_selected):
        dic_csv = self.configuration.read_variables("CSV")
        path_csv = SelectFiles.salvaFichero(self, _("Export") + " - " + _("To a CSV file"),
                                            dic_csv.get("FOLDER", self.configuration.carpeta), "csv")
        if not path_csv:
            return
        if not path_csv.lower().endswith(".csv"):
            path_csv = path_csv.strip() + ".csv"
        dic_csv["FOLDER"] = os.path.dirname(path_csv)
        self.configuration.write_variables("CSV", dic_csv)
        pb = QTUtil2.BarraProgreso1(self, _("Saving..."))
        pb.setFixedWidth(360)
        pb.mostrar()
        if only_selected:
            li_sel = self.grid.recnosSeleccionados()
        else:
            li_sel = list(range(self.db_games.reccount()))
        pb.set_total(len(li_sel))
        li_fields = []
        for col in self.grid.oColumnasR.li_columns:
            key = col.key
            if key.startswith("__") or key.upper() == "ROWID":
                continue
            li_fields.append((key, col.head))

        with open(path_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            li_data = []
            for key, head in li_fields:
                li_data.append(head)
            li_data.append("PGN")
            writer.writerow(li_data)

            for n, recno in enumerate(li_sel):
                pb.pon(n)
                if pb.is_canceled():
                    break
                li_data = []
                for key, head in li_fields:
                    li_data.append(self.db_games.field(recno, key))
                game = self.db_games.read_game_recno_base(recno)
                pgn = game.pgn_base_raw()
                li_data.append(pgn)
                writer.writerow(li_data)

        canceled = pb.is_canceled()
        if not canceled :
            QTUtil2.temporary_message(self, _("Saved"), 0.8)
            if not self.is_temporary:
                self.changes = False
        pb.close()
        if not canceled:
            Code.startfile(path_csv)

    def tw_paste_pgn_rem(self):
        w = RemoveCommentsVariations.WRemoveCommentsVariations(self, "databases_remove_comvar", True)
        if w.exec_():
            self.tw_paste_pgn(rem_comvar_run=w.run)

    def tw_paste_pgn(self, rem_comvar_run=None):
        texto = QTUtil.get_txt_clipboard()
        if texto:
            path_temp = self.configuration.temporary_file("pgn")
            try:
                with open(path_temp, "wt", encoding="utf-8") as q:
                    q.write(texto)
                self.tw_importar_pgn(path_temp, rem_comvar_run)
                return
            except:
                pass
        QTUtil2.message_error(self, _("The text from the clipboard does not contain a chess game in PGN format"))

    def tw_importar_pgn(self, path_pgn=None, rem_comvar_run=None):
        if path_pgn is None:
            files = SelectFiles.select_pgns(self)
            if not files:
                return
        else:
            files = [path_pgn, ]

        dl_tmp = QTVarios.ImportarFicheroPGN(self)
        if self.db_games.allows_duplicates:
            dl_tmp.hide_duplicates()
        dl_tmp.show()
        self.db_games.import_pgns(files, dl_tmp, rem_comvar_run=rem_comvar_run)
        self.set_changes(True)

        self.rehaz_columnas()
        self.actualiza(True)
        if self.wsummary:
            self.wsummary.reset()

    def tw_importar_pgn_rem(self):
        w = RemoveCommentsVariations.WRemoveCommentsVariations(self, "databases_remove_comvar", True)
        if w.exec_():
            self.tw_importar_pgn(rem_comvar_run=w.run)

    def tw_importar_db(self):
        path = QTVarios.select_db(self, self.configuration, False, False)
        if not path:
            return
        dl_tmp = QTVarios.ImportarFicheroDB(self)
        if self.db_games.allows_duplicates:
            dl_tmp.hide_duplicates()
        dl_tmp.show()

        dbn = DBgames.DBgames(path)
        self.db_games.append_db(dbn, range(dbn.all_reccount()), dl_tmp)
        self.set_changes(True)

        self.rehaz_columnas()
        self.actualiza(True)
        if self.wsummary is not None:
            self.wsummary.reset()

    def tw_importar_lichess_puzzles(self):
        mens_base = _("You must follow the next steps")
        mens_puzzles = _("Download the puzzles in csv format from LiChess website")
        link_puzzles = "https://database.lichess.org/#puzzles"

        mens_7z = _("Uncompress this file with a tool like PeaZip")
        link_7z = "https://peazip.github.io/"
        mens_unzip = _("Uncompress this file")

        mens_eco = _(
            "If you want to include a field with the opening, you have to download and unzip in the same folder as the puzzle file, the file indicated below")
        link_eco = ("https://sourceforge.net/projects/lucaschessr/files/Version_R2/lichess_dict_pv_ids.zip/download")
        idea = _("Original idea and more information")
        link_idea = "https://cshancock.netlify.app/post/2021-06-23-lichess-puzzles-by-eco"

        mensaje = "%s:" % mens_base
        mensaje += "<ol>"

        mensaje += "<li>%s" % mens_puzzles
        mensaje += '<ul><li><a href="%s">%s</a></li></ul>' % (link_puzzles, link_puzzles)
        mensaje += "</li>"

        if Code.is_windows:
            mensaje += "<li>%s" % mens_7z
            mensaje += '<ul><li><a href="%s">%s</a></li></ul>' % (link_7z, link_7z)
            mensaje += "</li>"
        else:
            mensaje += "<li>%s</li>" % mens_unzip

        mensaje += "<li>%s" % mens_eco
        mensaje += "<ul>"
        mensaje += '<li><a href="%s">%s</a></li>' % (link_eco, link_eco)
        mensaje += '<li>%s: <a href="%s">%s</a></li>' % (idea, link_idea, link_idea)
        mensaje += "</ul>"
        mensaje += "</li>"

        mensaje += "</ol>"
        mensaje += "<br>%s" % _("The import takes a long time.")

        if not QTUtil2.pregunta(self, mensaje, label_yes=_("Continue"), label_no=_("Cancel")):
            return

        path = SelectFiles.leeFichero(self, self.configuration.carpetaBase, "csv",
            _("From the Lichess Puzzle Database"))
        if not path:
            return

        tam = Util.filesize(path)
        if tam < 10:
            return

        dic_gid_pv = {}
        path_eco = Util.opj(os.path.dirname(path), "lichess_dict_pv_ids.sqlite")
        if Util.exist_file(path_eco):
            um = QTUtil2.working(self)
            with UtilSQL.DictTextSQL(path_eco) as db_sqltext:
                dic = db_sqltext.as_dictionary()
                for pv, txt in dic.items():
                    opening = OpeningsStd.ap.assign_pv(pv)
                    if opening:
                        gids = txt.split("|")
                        for gid in gids:
                            dic_gid_pv[gid] = opening
            um.final()

        def url_id(url):
            liu = url.split("/")
            key = liu[-1]
            if "black" in key:
                key = liu[-2]
            if "#" in key:
                key = key.split("#")[0]
            return key

        with open(path, "r") as f:
            pb = QTUtil2.BarraProgreso1(self, _("Importing"), formato1="%p%", show_time=False)
            pb.setFocus()
            pb.set_total(tam)
            pb.show()
            csv_reader = csv.reader(f)
            pos_ftell = 0
            for pos, row in enumerate(csv_reader):
                if len(row) < 9:
                    continue

                pos_ftell += sum(len(tag) for tag in row) + 1 + len(row)

                if pos == 0:
                    li_tags = [tag.upper() for tag in row]
                    pos_fen = li_tags.index("FEN")
                    pos_gameurl = li_tags.index("GAMEURL")
                    pos_moves = li_tags.index("MOVES")
                    del row[pos_moves]
                    if dic_gid_pv:
                        row.append("Opening")
                        row.append("ECO")
                    li_tags = [tag.upper() for tag in row]
                    sql = self.db_games.create_sql_insert(li_tags)
                    self.db_games.check_columns(row)
                    continue
                fen = row[pos_fen]
                pv = row[pos_moves]
                if dic_gid_pv:
                    gid = url_id(row[pos_gameurl])
                    opening = dic_gid_pv.get(gid)
                    if opening:
                        name = opening.tr_name
                        eco = opening.eco
                    else:
                        name = ""
                        eco = ""
                    row.append(name)
                    row.append(eco)
                del row[pos_moves]

                with_commit = pos % 100000 == 0
                self.db_games.add_reg_lichess(sql, fen, pv, row, with_commit)

                if pos % 10 == 0:
                    pb.pon(pos_ftell)
                    if pb.is_canceled():
                        break
            pb.cerrar()
        self.db_games.commit()
        self.set_changes(True)

        self.rehaz_columnas()
        self.actualiza(True)

    def tw_importar_lichess_user(self):
        iext = WebExternalImporter.Lichess(self, self.db_games)
        if iext.params():
            if iext.import_games():
                self.rehaz_columnas()
                self.grid.refresh()
                self.updateStatus()
                self.grid.gotop()

    def tw_importar_chesscom_user(self):
        iext = WebExternalImporter.ChessCom(self, self.db_games)
        if iext.params():
            if iext.import_games():
                self.rehaz_columnas()
                self.grid.refresh()
                self.updateStatus()
                self.grid.gotop()

    def tw_menu_columns(self):
        dic_conf = self.configuration.read_variables(self.key_columns)
        menu = QTVarios.LCMenu(self)
        menu.opcion(self.tw_edit_columns, _("Configure the columns"), Iconos.EditColumns())
        menu.separador()

        st_letters = set()

        def set_name(x):
            for pos, c in enumerate(x):
                if c.upper() not in st_letters:
                    st_letters.add(c.upper())
                    return x[:pos] + "&" + x[pos:]
            return x

        for name in dic_conf:
            menu.opcion(name, set_name(name), Iconos.PuntoAzul())
        menu.separador()
        menu.opcion(self.tw_reinit_columns, _("Reinit"), Iconos.Reiniciar())
        resp = menu.lanza()
        if resp is None:
            return
        if isinstance(resp, str):
            conf = dic_conf.get(resp)
            self.grid.o_columns.restore_dic(conf, self.grid)
            dcabs = self.db_games.read_config("dcabs", {})
            for col in self.grid.o_columns.li_columns:
                dcabs[col.key] = col.head
            self.db_games.save_config("dcabs", dcabs)
            self.grid.releerColumnas()
        else:
            resp()

    def tw_reinit_columns(self):
        self.grid.o_columns = self.lista_columnas()
        self.grid.releerColumnas()

    def tw_edit_columns(self):
        w = GridEditCols.EditCols(self.grid, self.key_columns, self.lista_columnas())
        if w.exec_():
            o_columns = self.grid.o_columns
            dcabs = self.db_games.read_config("dcabs", {})
            for col in o_columns.li_columns:
                dcabs[col.key] = col.head
            self.db_games.save_config("dcabs", dcabs)
            self.grid.releerColumnas()
