import os
import shutil
import time

from PySide2 import QtWidgets, QtCore

import Code
import Code.Openings.WindowOpenings as WindowOpenings
from Code import Util
from Code.Analysis import AnalysisGame, WindowAnalysisParam
from Code.Base import Game
from Code.Base.Constantes import WHITE, BLACK
from Code.Databases import DBgames, WDB_Utils
from Code.GM import GM
from Code.Openings import OpeningsStd
from Code.Polyglots import PolyglotImportExports
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import GridEditCols
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import SelectFiles
from Code.QT import WindowPlayGame
from Code.QT import WindowLearnGame
from Code.QT import WindowSavePGN
from Code.SQL import UtilSQL
from Code.Themes import WDB_Theme_Analysis
from Code.Translations import TrListas
from Code.QT import LCDialog


class WGames(QtWidgets.QWidget):
    def __init__(self, procesador, wb_database, dbGames, wsummary, si_select):
        QtWidgets.QWidget.__init__(self)

        self.wb_database = wb_database
        self.dbGames = dbGames  # <--setdbGames
        self.procesador = procesador
        self.configuration = procesador.configuration

        self.wsummary = wsummary
        self.infoMove = None  # <-- setInfoMove
        self.summaryActivo = None  # movimiento activo en summary
        self.numJugada = 0  # Se usa para indicarla al mostrar el pgn en infoMove

        self.si_select = si_select

        self.is_temporary = wb_database.is_temporary
        self.changes = False

        self.terminado = False  # singleShot

        self.ap = OpeningsStd.ap

        self.liFiltro = []
        self.where = None

        self.last_opening = None

        # Grid
        o_columns = self.lista_columnas()
        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, altoFila=24, siSeleccionMultiple=True, xid="wgames")
        self.grid.set_tooltip_header(
            _("For a numerical sort, press Ctrl (Alt or Shift) while double-clicking on the header.")
        )

        # Status bar
        self.status = QtWidgets.QStatusBar(self)
        self.status.setFixedHeight(22)

        # ToolBar
        if si_select:
            liAccionesWork = [
                (_("Accept"), Iconos.Aceptar(), wb_database.tw_aceptar),
                None,
                (_("Cancel"), Iconos.Cancelar(), wb_database.tw_cancelar),
                None,
                (_("First"), Iconos.Inicio(), self.tw_gotop),
                None,
                (_("Last"), Iconos.Final(), self.tw_gobottom),
                None,
                (_("Filter"), Iconos.Filtrar(), self.tw_filtrar),
                None,
            ]
        else:
            liAccionesWork = [
                (_("Close"), Iconos.MainMenu(), wb_database.tw_terminar),
                None,
                (_("Edit"), Iconos.Modificar(), self.tw_edit),
                None,
                (_("New"), Iconos.Nuevo(), self.tw_nuevo, _("Add a new game")),
                None,
                (_("Filter"), Iconos.Filtrar(), self.tw_filtrar),
                None,
                (_("First"), Iconos.Inicio(), self.tw_gotop),
                None,
                (_("Last"), Iconos.Final(), self.tw_gobottom),
                None,
                (_("Up"), Iconos.Arriba(), self.tw_up),
                None,
                (_("Down"), Iconos.Abajo(), self.tw_down),
                None,
                (_("Remove"), Iconos.Borrar(), self.tw_borrar),
                None,
                (_("Config"), Iconos.Configurar(), self.tw_configure),
                None,
                (_("Utilities"), Iconos.Utilidades(), self.tw_utilities),
                None,
                (_("Import"), Iconos.Import8(), self.tw_import),
                None,
                (_("Export"), Iconos.Export8(), self.tw_export),
                None,
                (_("Train"), Iconos.TrainStatic(), self.tw_train),
                None,
            ]

        self.tbWork = QTVarios.LCTB(self, liAccionesWork)

        lyTB = Colocacion.H().control(self.tbWork)

        layout = Colocacion.V().otro(lyTB).control(self.grid).control(self.status).margen(1)

        self.setLayout(layout)

    def tw_train(self):
        menu = QTVarios.LCMenu(self)
        submenu = menu.submenu(_("Learn a game"), Iconos.School())
        submenu.opcion(self.tw_memorize, _("Memorizing their moves"), Iconos.LearnGame())
        submenu.separador()
        submenu.opcion(self.tw_play_against, _("Playing against"), Iconos.Law())
        menu.separador()
        menu.opcion(self.tw_uti_tactic, _("Create tactics training"), Iconos.Tacticas())
        menu.separador()
        eti = _("Play like a Grandmaster")
        menu.opcion(self.tw_gm, _X(_("Create training to %1"), eti), Iconos.GranMaestro())
        menu.separador()

        resp = menu.lanza()
        if resp:
            resp()

    def tw_play_against(self):
        li = self.grid.recnosSeleccionados()
        if li:
            dbPlay = WindowPlayGame.DBPlayGame(self.configuration.file_play_game())
            for recno in li:
                game = self.dbGames.read_game_recno(recno)
                h = hash(game.xpv())
                recplay = dbPlay.recnoHash(h)
                if recplay is None:
                    reg = {"GAME": game.save()}
                    dbPlay.appendHash(h, reg)
                    recplay = dbPlay.recnoHash(h)
            dbPlay.close()

            if len(li) == 1:
                self.wb_database.tw_terminar()
                self.procesador.play_game_show(recplay)

    def tw_memorize(self):
        li = self.grid.recnosSeleccionados()
        if li:
            db = WindowLearnGame.DBLearnGame(self.configuration.file_learn_game())
            li.sort(reverse=True)
            for recno in li:
                game = self.dbGames.read_game_recno(recno)
                reg = {"GAME": game.save()}
                db.append(reg)
            db.close()

            self.wb_database.tw_terminar()
            self.procesador.learn_game()

    def lista_columnas(self):
        dcabs = self.dbGames.read_config("dcabs", DBgames.drots.copy())
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("__num__", _("N."), 60, align_center=True)
        li_tags = self.dbGames.li_tags()
        st100 = {"Event", "Site", "White", "Black"}
        for tag in li_tags:
            label = TrListas.pgnLabel(tag)
            if label == tag:
                label = dcabs.get(label, label)
            align_center = not (tag in ("Event", "Site"))
            ancho = 100 if tag in st100 else 80
            o_columns.nueva(tag, label, ancho, align_center=align_center)
        o_columns.nueva("rowid", _("Row ID"), 60, align_center=True)
        return o_columns

    def rehaz_columnas(self):
        li_tags = self.dbGames.li_tags()
        o_columns = self.grid.o_columns
        si_cambios = False

        li_remove = []
        for n, col in enumerate(o_columns.li_columns):
            key = col.key
            if not (key in li_tags) and not (key in ("__num__", "rowid")):
                li_remove.append(n)
        if li_remove:
            si_cambios = True
            li_remove.sort(reverse=True)
            for n in li_remove:
                del o_columns.li_columns[n]

        dcabs = self.dbGames.read_config("dcabs", DBgames.drots.copy())
        st100 = {"Event", "Site", "White", "Black"}
        stActual = {col.key for col in self.grid.o_columns.li_columns}
        for tag in li_tags:
            if not (tag in stActual):
                label = TrListas.pgnLabel(tag)
                if label == tag:
                    label = dcabs.get(label, label)
                o_columns.nueva(tag, label, 100 if tag in st100 else 70, align_center=not (tag in ("Event", "Site")))
                si_cambios = True

        if si_cambios:
            self.dbGames.reset_cache()
            self.grid.releerColumnas()

    def setdbGames(self, dbGames):
        self.dbGames = dbGames

    def setInfoMove(self, infoMove):
        self.infoMove = infoMove
        self.graphicBoardReset()

    def updateStatus(self):
        if self.terminado:
            return
        if not self.summaryActivo:
            txt = ""
        else:
            game = self.summaryActivo.get("game", Game.Game())
            nj = len(game)
            if nj > 1:
                p = game.copia(nj - 2)
                txt = "%s | " % p.pgnBaseRAW()
            else:
                txt = ""
            siPte = self.dbGames.if_there_are_records_to_read()
            if not siPte:
                recs = self.dbGames.reccount()
                if recs:
                    txt += "%s: %d" % (_("Games"), recs)
            if self.where:
                txt += " | %s: %s" % (_("Filter"), self.where)
            if siPte:
                QtCore.QTimer.singleShot(1000, self.updateStatus)

        self.status.showMessage(txt, 0)

    def grid_num_datos(self, grid):
        return self.dbGames.reccount()

    def grid_dato(self, grid, nfila, ocol):
        key = ocol.key
        if key == "__num__":
            return str(nfila + 1)
        elif key == "rowid":
            return str(self.dbGames.get_rowid(nfila))
        elif key == "__opening__":
            xpv = self.dbGames.field(nfila, "XPV")
            if xpv[0] != "|":
                return self.ap.xpv(xpv)
            return ""
        return self.dbGames.field(nfila, key)

    def grid_doble_click(self, grid, fil, col):
        if self.si_select:
            self.wb_database.tw_aceptar()
        else:
            self.tw_edit()

    def grid_doubleclick_header(self, grid, col):
        key = col.key
        if key in ("__num__"):
            return
        is_shift, is_control, is_alt = QTUtil.kbdPulsado()
        is_numeric = is_shift or is_control or is_alt
        li_order = self.dbGames.get_order()
        if key == "opening":
            key = "XPV"
        is_already = False
        for n, (cl, tp, is_num) in enumerate(li_order):
            if cl == key:
                is_already = True
                if tp == "ASC":
                    li_order[n] = (key, "DESC", is_numeric)
                    col.head = col.antigua + "-"
                    if n:
                        del li_order[n]
                        li_order.insert(0, (key, "DESC", is_numeric))

                elif tp == "DESC":
                    del li_order[n]
                    col.head = col.head[:-1]
                break
        if not is_already:
            li_order.insert(0, (key, "ASC", is_numeric))
            col.antigua = col.head
            col.head = col.antigua + "+"
        self.dbGames.put_order(li_order)
        self.grid.refresh()
        self.updateStatus()

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
        else:
            return True  # que siga con el resto de teclas

    def closeEvent(self, event):
        self.tw_terminar()

    def tw_terminar(self):
        if self.is_temporary and self.changes:
            if QTUtil2.pregunta(self, _("Changes have been made, do you want to export them to a PGN file?")):
                self.tw_exportar_pgn(False)
        self.terminado = True
        self.dbGames.close()

    def actualiza(self, siObligatorio=False):
        def pvSummary(summary):
            if summary is None:
                return ""
            lipv = summary.get("pv", "").split(" ")
            return " ".join(lipv[:-1])

        if self.wsummary:
            summaryActivo = self.wsummary.movActivo()
            if siObligatorio or pvSummary(self.summaryActivo) != pvSummary(summaryActivo) or self.liFiltro:
                self.where = None
                self.summaryActivo = summaryActivo
                pv = ""
                if self.summaryActivo:
                    pv = self.summaryActivo.get("pv")
                    if pv:
                        lipv = pv.split(" ")
                        pv = " ".join(lipv[:-1])
                    else:
                        pv = ""
                self.dbGames.filter_pv(pv)
                self.updateStatus()
                self.numJugada = pv.count(" ")
                self.grid.refresh()
                self.grid.gotop()
        else:
            if siObligatorio or self.liFiltro:
                self.where = None
                self.dbGames.filter_pv("")
                self.updateStatus()
                self.grid.refresh()
                self.grid.gotop()

        recno = self.grid.recno()
        if recno >= 0:
            self.grid_cambiado_registro(None, recno, None)

    def grid_cambiado_registro(self, grid, row, oCol):
        if self.grid_num_datos(grid) > row >= 0:
            self.setFocus()
            self.grid.setFocus()
            fen, pv = self.dbGames.get_pv(row)
            if fen:
                p = Game.Game(fen=fen)
                p.read_pv(pv)
                p.is_finished()
                self.infoMove.modoFEN(p, fen, -1)
            else:
                p = Game.Game()
                p.read_pv(pv)
                p.assign_opening()
                p.is_finished()
                self.infoMove.modoPartida(p, 0)

    def tw_gobottom(self):
        self.grid.gobottom()

    def tw_gotop(self):
        self.grid.gotop()

    def tw_up(self):
        row = self.grid.recno()
        if row >= 0:
            filaNueva = self.dbGames.interchange(row, True)
            self.changes = True
            if filaNueva is not None:
                self.grid.goto(filaNueva, 0)
                self.grid.refresh()

    def tw_down(self):
        row = self.grid.recno()
        if row >= 0:
            filaNueva = self.dbGames.interchange(row, False)
            self.changes = True
            if filaNueva is not None:
                self.grid.goto(filaNueva, 0)
                self.grid.refresh()

    def edit_save(self, recno, game):
        if game is not None:
            resp = self.dbGames.save_game_recno(recno, game)
            if resp.ok:
                if not resp.changed:
                    return

                if resp.summary_changed:
                    self.wsummary.rehazActual()

                if resp.inserted:
                    self.updateStatus()

                if recno is None:
                    self.grid.gobottom()
                else:
                    self.grid.goto(recno, 0)
                    self.grid_cambiado_registro(self, recno, None)
                self.rehaz_columnas()
                self.grid.refresh()
                self.changes = True

            else:
                QTUtil2.message_error(self, resp.mens_error)

    def edit_previous_next(self, order, game):
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
            if recno < len(self.dbGames):
                self.grid.goto(recno, 0)
                game, recno = self.current_game()
                game.recno = recno
            return game

    def edit(self, recno, game):
        if recno is None:
            with_previous_next = None
        else:
            with_previous_next = self.edit_previous_next
        game.recno = recno
        game = self.procesador.manager_game(
            self,
            game,
            not self.dbGames.allows_positions,
            False,
            self.infoMove.board,
            with_previous_next=with_previous_next,
            save_routine=self.edit_save,
        )
        if game:
            self.changes = True
            self.edit_save(game.recno, game)

    def tw_nuevo(self):
        recno = None
        pc = self.dbGames.blank_game()
        self.edit(recno, pc)

    def tw_edit(self):
        if self.grid.recno() >= 0:
            um = QTUtil2.unMomento(self, _("Reading the game"))
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
            game = self.dbGames.read_game_recno(recno)
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
            w = WDB_Utils.WFiltrar(self, self.grid.o_columns, self.liFiltro, self.dbGames.nom_fichero)
            if w.exec_():
                self.liFiltro = w.liFiltro

                self.where = w.where()
                self.dbGames.filter_pv(xpv, self.where)
                refresh()

        def raw_sql():
            w = WDB_Utils.WFiltrarRaw(self, self.grid.o_columns, self.where)
            if w.exec_():
                self.where = w.where
                self.dbGames.filter_pv(xpv, self.where)
                refresh()

        def opening():
            me = QTUtil2.unMomento(self)

            w = WindowOpenings.WOpenings(self, self.configuration, self.last_opening)
            me.final()
            if w.exec_():
                self.last_opening = ap = w.resultado()
                pv = getattr(ap, "a1h8", "")
                self.dbGames.filter_pv(pv)
                self.where = self.dbGames.filter
                self.numJugada = pv.count(" ")
                refresh()

        def remove_filter():
            self.dbGames.filter_pv("")
            self.where = None
            self.summaryActivo["game"] = Game.Game()
            self.wsummary.start()
            refresh()

        menu = QTVarios.LCMenu(self)
        menu.opcion(standard, _("Standard"), Iconos.Filtrar())
        menu.separador()
        menu.opcion(raw_sql, _("Advanced"), Iconos.SQL_RAW())
        menu.separador()
        menu.opcion(opening, _("Opening"), Iconos.Opening())
        if self.dbGames.filter is not None and self.dbGames.filter:
            menu.separador()
            menu.opcion(remove_filter, _("Remove filter"), Iconos.Cancelar())

        resp = menu.lanza()
        if resp:
            resp()

    def tw_borrar(self):
        li = self.grid.recnosSeleccionados()
        if li:
            if not QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                return

            um = QTUtil2.unMomento(self, _("Working..."))
            self.changes = True
            self.dbGames.remove_list_recnos(li)
            if self.summaryActivo:
                self.summaryActivo["games"] -= len(li)
                self.wsummary.reset()
            self.grid.refresh()
            self.updateStatus()

            um.final()

    def tw_import(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion(self.tw_importar_PGN, _("From a PGN file"), Iconos.FichPGN())
        menu.separador()
        menu.opcion(self.tw_importar_DB, _("From other database"), Iconos.Database())
        menu.separador()
        if self.dbGames.allows_positions and (self.dbGames.reccount() == 0 or not self.dbGames.allows_duplicates):
            menu.opcion(self.tw_importar_lichess, _("From the Lichess Puzzle Database"), Iconos.Lichess())
        resp = menu.lanza()
        if resp:
            resp()

    def tw_export(self):
        li_all = range(self.dbGames.reccount())
        if not li_all:
            return None
        li_sel = self.grid.recnosSeleccionados()

        menu = QTVarios.LCMenu(self)

        submenu = menu.submenu(_("To a PGN file"), Iconos.FichPGN())
        submenu.opcion((self.tw_exportar_pgn, False), _("All registers"), Iconos.PuntoVerde())
        if li_sel:
            submenu.separador()
            submenu.opcion(
                (self.tw_exportar_pgn, True), "%s [%d]" % (_("Only selected games"), len(li_sel)), Iconos.PuntoAzul()
            )

        menu.separador()
        submenu = menu.submenu(_("To other database"), Iconos.Database())
        submenu.opcion((self.tw_exportar_db, li_all), _("All registers"), Iconos.PuntoVerde())
        if li_sel:
            submenu.separador()
            submenu.opcion(
                (self.tw_exportar_db, li_sel), "%s [%d]" % (_("Only selected games"), len(li_sel)), Iconos.PuntoAzul()
            )

        resp = menu.lanza()
        if resp:
            funcion, lista = resp
            funcion(lista)

    def tw_configure(self):
        menu = QTVarios.LCMenu(self)

        if not self.is_temporary:
            menu.opcion(self.tw_options, _("Database options"), Iconos.Opciones())
            menu.separador()

        menu.opcion(self.tw_tags, _("Tags"), Iconos.Tags())
        menu.separador()

        submenu = menu.submenu(_("Appearance"), Iconos.Appearance())

        dico = {True: Iconos.Aceptar(), False: Iconos.PuntoRojo()}
        submenu.opcion(self.tw_resize_columns, _("Resize all columns to contents"), Iconos.ResizeAll())
        submenu.separador()
        submenu.opcion(self.tw_edit_columns, _("Configure the columns"), Iconos.EditColumns())
        submenu.separador()

        si_show = self.dbGames.read_config("GRAPHICS_SHOW_ALLWAYS", False)
        si_graphics_specific = self.dbGames.read_config("GRAPHICS_SPECIFIC", False)
        menu1 = submenu.submenu(_("Graphic elements (Director)"), Iconos.Script())
        menu2 = menu1.submenu(_("Show always"), Iconos.PuntoAzul())
        menu2.opcion(self.tw_dir_show_yes, _("Yes"), dico[si_show])
        menu2.separador()
        menu2.opcion(self.tw_dir_show_no, _("No"), dico[not si_show])
        menu1.separador()
        menu2 = menu1.submenu(_("Specific to this database"), Iconos.PuntoAzul())
        menu2.opcion(self.tw_locale_yes, _("Yes"), dico[si_graphics_specific])
        menu2.separador()
        menu2.opcion(self.tw_locale_no, _("No"), dico[not si_graphics_specific])
        menu.separador()

        resp = menu.lanza()
        if resp:
            resp()

    def tw_options(self):
        db = self.dbGames
        dic_data = {
            "NAME": db.get_name(),
            "LINK_FILE": db.link_file,
            "FILEPATH": db.nom_fichero,
            "EXTERNAL_FOLDER": db.external_folder,
            "SUMMARY_DEPTH": db.depth_stat(),
            "ALLOWS_DUPLICATES": db.read_config("ALLOWS_DUPLICATES", True),
            "ALLOWS_POSITIONS": db.read_config("ALLOWS_POSITIONS", True),
            "ALLOWS_COMPLETE_GAMES": db.read_config("ALLOWS_COMPLETE_GAMES", True),
            "ALLOWS_ZERO_MOVES": db.read_config("ALLOWS_ZERO_MOVES", True),
        }
        w = WOptionsDatabase(self, self.configuration, dic_data)
        if not w.exec_():
            return None

        dic_data = w.dic_data_resp
        self.dbGames.read_options()

        # Comprobamos depth
        new_depth = dic_data["SUMMARY_DEPTH"]
        if new_depth != self.dbGames.depth_stat():
            self.wsummary.reindexar_question(new_depth, False)
            self.dbGames.save_config("SUMMARY_DEPTH", new_depth)

        # Si ha cambiado la localización, se cierra, se mueve y se reabre en la nueva
        # Internal -> Internal
        old_is_internal = Util.same_path(self.dbGames.nom_fichero, self.dbGames.link_file)
        old_is_external = not old_is_internal
        new_is_internal = len(dic_data["EXTERNAL_FOLDER"]) == 0
        new_is_external = not new_is_internal

        path_old_data = self.dbGames.nom_fichero
        path_new_data = dic_data["FILEPATH_WITH_DATA"]

        reinit = False
        must_close = True

        if new_is_external and old_is_external:
            new_link = dic_data["FILEPATH"]
            old_link = self.dbGames.link_file
            if not Util.same_path(new_link, old_link):
                self.configuration.set_last_database(new_link)
                Util.remove_file(old_link)
                reinit = True
                must_close = True

        if new_is_internal and old_is_external:
            os.remove(self.dbGames.link_file)

        if not Util.same_path(path_old_data, path_new_data):
            self.dbGames.close()
            shutil.move(path_old_data, path_new_data)
            shutil.move(path_old_data + ".st1", path_new_data + ".st1")
            self.configuration.set_last_database(dic_data["FILEPATH"])
            reinit = True
            must_close = False

        if reinit:
            self.wb_database.reinit_sinsalvar(must_close)  # para que no cree de nuevo al salvar configuración

    def tw_tags(self):
        w = WTags(self, self.dbGames)
        if w.exec_():
            dic_cambios = w.dic_cambios

            dcabs = self.dbGames.read_config("dcabs", {})
            reinit = False

            # Primero CREATE
            for dic in dic_cambios["CREATE"]:
                self.dbGames.add_column(dic["KEY"])
                dcabs[dic["KEY"]] = dic["LABEL"]
                reinit = True

            # Segundo FILL
            li_field_value = []
            for dic in dic_cambios["FILL"]:
                li_field_value.append((dic["KEY"], dic["VALUE"]))
            if li_field_value:
                self.dbGames.fill(li_field_value)

            # Tercero RENAME_LBL
            for dic in dic_cambios["RENAME"]:
                dcabs[dic["KEY"]] = dic["LABEL"]

            self.dbGames.save_config("dcabs", dcabs)

            # Cuarto REMOVE
            lir = dic_cambios["REMOVE"]
            if len(lir) > 0:
                um = QTUtil2.unMomento(self, _("Working..."))
                lista = [x["KEY"] for x in lir]
                self.dbGames.remove_columns(lista)
                self.changes = True
                reinit = True
                um.final()

            if reinit:
                self.wb_database.reinit_sinsalvar()  # para que no cree de nuevo al salvar configuración

            else:
                self.dbGames.reset_cache()
                self.grid.refresh()

    def tw_edit_columns(self):
        w = GridEditCols.EditCols(self.grid, self.configuration, "columns_database")
        if w.exec_():
            self.grid.releerColumnas()

    def readVarsConfig(self):
        show_always = self.dbGames.read_config("GRAPHICS_SHOW_ALLWAYS")
        specific = self.dbGames.read_config("GRAPHICS_SPECIFIC")
        return show_always, specific

    def graphicBoardReset(self):
        show_always, specific = self.readVarsConfig()
        fichGraphic = self.dbGames.nom_fichero if specific else None
        self.infoMove.board.dbvisual_set_file(fichGraphic)
        self.infoMove.board.dbvisual_set_show_always(show_always)

    def tw_dir_show_yes(self):
        self.dbGames.save_config("GRAPHICS_SHOW_ALLWAYS", True)
        self.graphicBoardReset()

    def tw_dir_show_no(self):
        self.dbGames.save_config("GRAPHICS_SHOW_ALLWAYS", False)
        self.graphicBoardReset()

    def tw_locale_yes(self):
        self.dbGames.save_config("GRAPHICS_SPECIFIC", True)
        self.graphicBoardReset()

    def tw_locale_no(self):
        self.dbGames.save_config("GRAPHICS_SPECIFIC", False)
        self.graphicBoardReset()

    def tw_resize_columns(self):
        um = QTUtil2.unMomento(self, _("Resizing"))
        self.grid.resizeColumnsToContents()
        um.final()

    def tw_utilities(self):
        si_games = len(self.dbGames) > 0

        menu = QTVarios.LCMenu(self)
        if si_games:
            menu.opcion(self.tw_massive_analysis, _("Mass analysis"), Iconos.Analizar())
            menu.separador()
            menu.opcion(self.tw_polyglot, _("Create a polyglot book"), Iconos.Book())
            menu.separador()
            menu.opcion(self.tw_themes, _("Statistics on tactical themes"), Iconos.Tacticas())
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

            form.edit_np(
                '<div align="right">%s:<br>%s</div>'
                % (
                    _("Only the following players"),
                    _("(You can add multiple aliases separated by ; and wildcards with *)"),
                ),
                player,
            )
            form.separador()

            form.checkbox(_("Only selected games"), selected)
            form.separador()

            li = [(_("Both sides"), None), (_("White"), WHITE), (_("Black"), BLACK)]
            form.combobox(_("Which side"), li, side)
            form.separador()

            li = [
                (_("Any"), None),
                (_("Win"), "Win"),
                (_("Win+Draw"), "Win+Draw"),
                (_("Loss"), "Lost"),
                (_("Loss+Draw"), "Lost+Draw"),
            ]
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
                li_selected = range(self.dbGames.reccount())
            nregs = len(li_selected)
            mensaje = _("Game") + "  %d/" + str(nregs)
            tmpBP = QTUtil2.BarraProgreso(self, title, "", nregs).mostrar()

            for n, recno in enumerate(li_selected):
                if tmpBP.is_canceled():
                    break

                game = self.dbGames.read_game_recno(recno)
                if n:
                    tmpBP.pon(n)
                tmpBP.mensaje(mensaje % (n + 1,))

                fgm.other_game(game)

            is_canceled = tmpBP.is_canceled()
            tmpBP.cerrar()

            if not is_canceled:
                is_created = fgm.xprocesa()

                if is_created:
                    li_created = [name]
                    li_not_created = None
                else:
                    li_not_created = [name]
                    li_created = None
                WDB_Utils.mensajeEntrenamientos(self, li_created, li_not_created)

            return

    def tw_uti_tactic(self):
        def rutinaDatos(recno, skip_first):
            dic = {}
            for key in self.dbGames.li_fields:
                dic[key] = self.dbGames.field(recno, key)
            p = self.dbGames.read_game_recno(recno)
            if skip_first:
                dic["PGN_REAL"] = p.pgn()
                p.skip_first()
                dic["FEN"] = p.get_tag("FEN")
            dic["PGN"] = p.pgn()
            dic["PLIES"] = len(p)
            return dic

        liRegistrosSelected = self.grid.recnosSeleccionados()
        liRegistrosTotal = range(self.dbGames.reccount())

        WDB_Utils.create_tactics(
            self.procesador, self, liRegistrosSelected, liRegistrosTotal, rutinaDatos, self.dbGames.get_name()
        )

    def tw_pack(self):
        um = QTUtil2.unMomento(self)
        self.dbGames.pack()
        um.final()

    def tw_massive_analysis(self):
        liSeleccionadas = self.grid.recnosSeleccionados()
        nSeleccionadas = len(liSeleccionadas)

        alm = WindowAnalysisParam.massive_analysis_parameters(
            self, self.configuration, nSeleccionadas > 1, siDatabase=True
        )
        if alm:

            if alm.siVariosSeleccionados:
                nregs = nSeleccionadas
            else:
                nregs = self.dbGames.reccount()

            tmpBP = QTUtil2.BarraProgreso2(self, _("Mass analysis"), formato2="%p%")
            tmpBP.ponTotal(1, nregs)
            tmpBP.ponRotulo(1, _("Game"))
            tmpBP.ponRotulo(2, _("Moves"))
            tmpBP.mostrar()

            if alm.num_moves:
                lni = Util.ListaNumerosImpresion(alm.num_moves)
            else:
                lni = None

            ap = AnalysisGame.AnalyzeGame(self.procesador, alm, True)

            ap.cached_begin()

            for n in range(nregs):

                if tmpBP.is_canceled():
                    break

                tmpBP.pon(1, n + 1)

                if alm.siVariosSeleccionados:
                    n = liSeleccionadas[n]

                game = self.dbGames.read_game_recno(n)
                self.grid.goto(n, 0)
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
                ap.xprocesa(game, tmpBP)

                self.dbGames.save_game_recno(n, game)
                self.changes = True

            ap.cached_end()

            if not tmpBP.is_canceled():
                ap.terminar(True)

                liCreados = []
                liNoCreados = []

                if alm.tacticblunders:
                    if ap.siTacticBlunders:
                        liCreados.append(alm.tacticblunders)
                    else:
                        liNoCreados.append(alm.tacticblunders)

                for x in (alm.pgnblunders, alm.fnsbrilliancies, alm.pgnbrilliancies):
                    if x:
                        if Util.exist_file(x):
                            liCreados.append(x)
                        else:
                            liNoCreados.append(x)

                if alm.bmtblunders:
                    if ap.si_bmt_blunders:
                        liCreados.append(alm.bmtblunders)
                    else:
                        liNoCreados.append(alm.bmtblunders)
                if alm.bmtbrilliancies:
                    if ap.si_bmt_brilliancies:
                        liCreados.append(alm.bmtbrilliancies)
                    else:
                        liNoCreados.append(alm.bmtbrilliancies)
                if liCreados:
                    WDB_Utils.mensajeEntrenamientos(self, liCreados, liNoCreados)
                    self.procesador.entrenamientos.rehaz()

            else:
                ap.terminar(False)

            tmpBP.cerrar()

    def tw_themes(self):

        um = QTUtil2.unMomento(self, _("Analyzing tactical themes"))
        a = WDB_Theme_Analysis.SelectedGameThemeAnalyzer(self)

        um.final()
        if len(a.dic_themes) == 0:
            QTUtil2.message(self, _("No themes were found in selected games!"))
            return
        wma = WDB_Theme_Analysis.WDBMoveAnalysis(self, a.li_output_dic, a.title, a.missing_tags_output)
        wma.exec_()

    def tw_polyglot(self):
        titulo = self.dbGames.get_name() + ".bin"
        resp = PolyglotImportExports.export_polyglot_config(self, self.configuration, titulo)
        if resp is None:
            return
        path_bin, uniform = resp
        resp = PolyglotImportExports.import_polyglot_config(self, self.configuration, os.path.basename(path_bin), False)
        if resp is None:
            return
        plies, st_side, st_results, ru, min_games, min_score, calc_weight, save_score = resp
        db = UtilSQL.DictBig()

        def fsum(keymove, pt):
            num, pts = db.get(keymove, (0, 0))
            num += 1
            pts += pt
            db[keymove] = num, pts

        dltmp = PolyglotImportExports.ImportarPGNDB(self, titulo)
        dltmp.show()

        ok = PolyglotImportExports.add_db(
            self.dbGames, plies, st_results, st_side, ru, time.time, 1.2, dltmp.dispatch, fsum
        )
        dltmp.close()

        if ok:
            PolyglotImportExports.create_bin_from_dbbig(
                self, path_bin, db, min_games, min_score, calc_weight, save_score
            )

    def tw_exportar_db(self, lista):
        dbpath = QTVarios.select_db(self, self.configuration, False, True)
        if not dbpath:
            return
        if dbpath == ":n":
            dbpath = new_database(self, self.configuration)
            if dbpath is None:
                return

        dlTmp = QTVarios.ImportarFicheroDB(self)
        dlTmp.ponExportados()
        dlTmp.show()

        dbn = DBgames.DBgames(dbpath)
        if dbn.allows_duplicates:
            dlTmp.hide_duplicates()
        dbn.append_db(self.dbGames, lista, dlTmp)
        dbn.close()
        self.changes = False

    def tw_exportar_pgn(self, only_selected):
        w = WindowSavePGN.WSaveVarios(self, self.configuration)
        if w.exec_():
            ws = WindowSavePGN.FileSavePGN(self, w.dic_result)
            if ws.open():
                pb = QTUtil2.BarraProgreso1(self, _("Saving..."), formato1="%p%")
                pb.mostrar()
                if only_selected:
                    li_sel = self.grid.recnosSeleccionados()
                else:
                    li_sel = list(range(self.dbGames.reccount()))
                pb.ponTotal(len(li_sel))
                for n, recno in enumerate(li_sel):
                    pb.pon(n)
                    game = self.dbGames.read_game_recno(recno)
                    if pb.is_canceled():
                        break
                    if game is None:
                        continue
                    pgn = game.pgn()
                    result = game.resultado()
                    if n > 0 or not ws.is_new:
                        ws.write("\n\n")
                    if result in ("*", "1-0", "0-1", "1/2-1/2"):
                        if not pgn.endswith(result):
                            pgn += " " + result
                    ws.write(pgn + "\n")

                if not pb.is_canceled():
                    self.changes = False
                pb.close()
                ws.close()

    def tw_importar_PGN(self):
        files = SelectFiles.select_pgns(self)
        if not files:
            return None

        dlTmp = QTVarios.ImportarFicheroPGN(self)
        if self.dbGames.allows_duplicates:
            dlTmp.hide_duplicates()
        dlTmp.show()
        self.dbGames.import_pgns(files, dlTmp)
        self.changes = True

        self.rehaz_columnas()
        self.actualiza(True)
        if self.wsummary:
            self.wsummary.reset()

    def tw_importar_DB(self):
        path = QTVarios.select_db(self, self.configuration, False, False)
        if not path:
            return None

        dlTmp = QTVarios.ImportarFicheroDB(self)
        if self.dbGames.allows_duplicates:
            dlTmp.hide_duplicates()
        dlTmp.show()

        dbn = DBgames.DBgames(path)
        self.dbGames.append_db(dbn, range(dbn.all_reccount()), dlTmp)
        self.changes = True

        self.rehaz_columnas()
        self.actualiza(True)
        if self.wsummary:
            self.wsummary.reset()

    def tw_importar_lichess(self):
        mens_base = _("You must follow the next steps")
        mens_puzzles = _("Download the puzzles in csv format from LiChess website")
        link_puzzles = "https://database.lichess.org/#puzzles"

        mens_7z = _("Uncompress this file with a tool like 7-Zip")
        link_7z = "https://www.7-zip.org/"
        mens_unzip = _("Uncompress this file")

        mens_eco = _(
            "If you want to include a field with the opening, you have to download and unzip in the same folder as the puzzle file, the file indicated below"
        )
        link_eco = (
            "https://sourceforge.net/projects/lucaschessr/files/Version_R2/lichess_db_puzzle_pv_id.eval.bz2/download"
        )
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

        path = SelectFiles.leeFichero(
            self, self.configuration.carpetaBase, "csv", _("From the Lichess Puzzle Database")
        )
        if not path:
            return

        tam = Util.filesize(path)
        if tam < 10:
            return

        dic_gid_pv = {}
        path_eco = os.path.join(os.path.dirname(path), "lichess_db_puzzle_pv_id.eval")
        if Util.exist_file(path_eco):
            um = QTUtil2.unMomento(self, _("Working..."))
            with open(path_eco, "rt") as f:
                dic_pv_id = eval(f.read())
            for pv, li_gids in dic_pv_id.items():
                g = Game.pv_game(None, pv)
                for gid in li_gids:
                    dic_gid_pv[gid] = g.opening
            um.final()

        def url_id(url):
            li = url.split("/")
            key = li[-1]
            if "black" in key:
                key = li[-2]
            if "#" in key:
                key = key.split("#")[0]
            return key

        with open(path, "rt") as f:
            pb = QTUtil2.BarraProgreso1(self, _("Importing"), formato1="%p%")
            pb.setFocus()
            pb.ponTotal(tam)
            pb.show()
            line = f.readline()
            n = 1
            g = Game.Game()
            while line:
                line = line.strip()
                if line:
                    li = line.split(",")
                    nli = len(li)
                    if nli < 9:
                        continue
                    puzzleid, fen, moves, rating, ratingdeviation, popularity, nbplays, themes, gameurl = (
                        li[:9] if nli > 9 else li
                    )
                    g.li_moves = []
                    g.li_tags = []
                    g.set_fen(fen)
                    g.read_pv(moves)
                    g.set_tag("Site", "LiChess")
                    g.set_tag("Event", "Puzzle %s" % puzzleid)
                    g.set_tag("Rating", rating)
                    g.set_tag("RatingDeviation", ratingdeviation)
                    g.set_tag("Popularity", popularity)
                    g.set_tag("NBPlays", nbplays)
                    g.set_tag("Themes", themes)
                    g.set_tag("GameURL", gameurl)
                    if dic_gid_pv:
                        gid = url_id(gameurl)
                        opening = dic_gid_pv.get(gid)
                        if opening:
                            g.set_tag("ECO", opening.eco)
                            g.set_tag("Opening", opening.tr_name)
                    self.dbGames.insert(g, with_commit=(n % 1000) == 0)
                if n % 10 == 0:
                    pb.pon(f.tell())
                    if pb.is_canceled():
                        break
                line = f.readline()
                n += 1
            pb.cerrar()
        self.dbGames.commit()
        self.changes = True

        self.rehaz_columnas()
        self.actualiza(True)


class WOptionsDatabase(QtWidgets.QDialog):
    def __init__(self, owner, configuration, dic_data):
        super(WOptionsDatabase, self).__init__(owner)

        self.new = len(dic_data) == 0

        self.dic_data = dic_data
        self.dic_data_resp = None

        def d_str(key):
            return dic_data.get(key, "")

        def d_true(key):
            return dic_data.get(key, True)

        def d_false(key):
            return dic_data.get(key, False)

        title = _("New database") if self.new else "%s: %s" % (_("Database"), d_str("NAME"))
        self.setWindowTitle(title)
        self.setWindowIcon(Iconos.DatabaseMas())
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self.configuration = configuration
        self.resultado = None

        valid_rx = r'^[^<>:;,?"*|/\\]+'

        lb_name = Controles.LB2P(self, _("Name"))
        self.ed_name = Controles.ED(self, d_str("NAME")).controlrx(valid_rx)

        ly_name = Colocacion.H().control(lb_name).control(self.ed_name)

        link_file = d_str("LINK_FILE")
        folder = os.path.dirname(Util.relative_path(link_file))
        folder = folder[len(configuration.folder_databases()) :]
        if folder.strip():
            folder = folder.strip(os.sep)
            li = folder.split(os.sep)
            nli = len(li)
            group = li[0]
            subgroup1 = li[1] if nli > 1 else ""
            subgroup2 = li[2] if nli > 2 else ""
        else:
            group = ""
            subgroup1 = ""
            subgroup2 = ""

        lb_group = Controles.LB2P(self, _("Group"))
        self.ed_group = Controles.ED(self, group).controlrx(valid_rx)
        self.bt_group = (
            Controles.PB(self, "", self.mira_group).ponIcono(Iconos.BuscarC(), 16).ponToolTip(_("Group lists"))
        )
        ly_group = (
            Colocacion.H().control(lb_group).control(self.ed_group).espacio(-10).control(self.bt_group).relleno(1)
        )

        lb_subgroup_l1 = Controles.LB2P(self, _("Subgroup"))
        self.ed_subgroup_l1 = Controles.ED(self, subgroup1).controlrx(valid_rx)
        self.bt_subgroup_l1 = (
            Controles.PB(self, "", self.mira_subgroup_l1).ponIcono(Iconos.BuscarC(), 16).ponToolTip(_("Group lists"))
        )
        ly_subgroup_l1 = (
            Colocacion.H()
            .espacio(40)
            .control(lb_subgroup_l1)
            .control(self.ed_subgroup_l1)
            .espacio(-10)
            .control(self.bt_subgroup_l1)
            .relleno(1)
        )

        lb_subgroup_l2 = Controles.LB2P(self, "%s → %s" % (_("Subgroup"), _("Subgroup")))
        self.ed_subgroup_l2 = Controles.ED(self, subgroup2).controlrx(valid_rx)
        self.bt_subgroup_l2 = (
            Controles.PB(self, "", self.mira_subgroup_l2).ponIcono(Iconos.BuscarC(), 16).ponToolTip(_("Group lists"))
        )
        ly_subgroup_l2 = (
            Colocacion.H()
            .espacio(40)
            .control(lb_subgroup_l2)
            .control(self.ed_subgroup_l2)
            .espacio(-10)
            .control(self.bt_subgroup_l2)
            .relleno(1)
        )

        x1 = -8
        ly_group = Colocacion.V().otro(ly_group).espacio(x1).otro(ly_subgroup_l1).espacio(x1).otro(ly_subgroup_l2)

        gb_group = Controles.GB(self, "%s (%s)" % (_("Group"), _("optional")), ly_group)

        lb_summary = Controles.LB2P(self, _("Opening explorer depth (0=disable)"))
        self.sb_summary = Controles.SB(self, dic_data.get("SUMMARY_DEPTH", 12), 0, 999)
        ly_summary = Colocacion.H().control(lb_summary).control(self.sb_summary).relleno(1)

        self.external_folder = d_str("EXTERNAL_FOLDER")
        lb_external = Controles.LB2P(self, _("Store in an external folder"))
        self.bt_external = Controles.PB(self, self.external_folder, self.select_external, False)
        self.bt_external.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        )
        bt_remove_external = Controles.PB(self, "", self.remove_external).ponIcono(Iconos.Remove1(), 16)
        ly_external = (
            Colocacion.H().control(lb_external).control(self.bt_external).espacio(-8).control(bt_remove_external)
        )

        self.chb_complete = Controles.CHB(self, _("Allow complete games"), d_true("ALLOWS_COMPLETE_GAMES"))
        self.chb_positions = Controles.CHB(self, _("Allow positions"), d_true("ALLOWS_POSITIONS"))
        self.chb_duplicate = Controles.CHB(self, _("Allow duplicates"), d_false("ALLOWS_DUPLICATES"))
        self.chb_zeromoves = Controles.CHB(self, _("Allow without moves"), d_true("ALLOWS_ZERO_MOVES"))
        ly_res = (
            Colocacion.V()
            .controlc(self.chb_complete)
            .controlc(self.chb_positions)
            .controlc(self.chb_duplicate)
            .controlc(self.chb_zeromoves)
        )

        gb_restrictions = Controles.GB(self, _("Import restrictions"), ly_res)

        li_acciones = [
            (_("Save"), Iconos.Aceptar(), self.save),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
        ]
        self.tb = QTVarios.LCTB(self, li_acciones)

        x0 = 16

        layout = Colocacion.V().control(self.tb).espacio(x0)
        layout.otro(ly_name).espacio(x0).control(gb_group).espacio(x0)
        layout.otro(ly_summary).espacio(x0)
        layout.otro(ly_external).espacio(x0)
        layout.control(gb_restrictions)
        layout.margen(9)

        self.setLayout(layout)

        self.ed_name.setFocus()

    def select_external(self):
        folder = SelectFiles.get_existing_directory(self, self.external_folder, _("Use an external folder"))
        if folder:
            folder = os.path.realpath(folder)
            default = os.path.realpath(self.configuration.folder_databases())
            if folder.startswith(default):
                QTUtil2.message_error(
                    self, "%s:\n%s\n\n%s" % (_("The folder must be outside the default folder"), default, folder)
                )
                return
            self.external_folder = folder

        self.bt_external.set_text(self.external_folder)

    def remove_external(self):
        self.external_folder = ""
        self.bt_external.set_text("")

    def menu_groups(self, carpeta):
        if Util.exist_folder(carpeta):
            with os.scandir(carpeta) as it:
                li = [entry.name for entry in it if entry.is_dir()]
            if li:
                rondo = QTVarios.rondoPuntos()
                menu = QTVarios.LCMenu(self)
                for direc in li:
                    menu.opcion(direc, direc, rondo.otro())
                return menu.lanza()

    def mira_group(self):
        resp = self.menu_groups(self.configuration.folder_databases())
        if resp:
            self.ed_group.set_text(resp)

    def mira_subgroup_l1(self):
        group = self.ed_group.texto().strip()
        if group:
            carpeta = os.path.join(self.configuration.folder_databases(), group)
            resp = self.menu_groups(carpeta)
            if resp:
                self.ed_subgroup_l1.set_text(resp)

    def mira_subgroup_l2(self):
        group = self.ed_group.texto().strip()
        if group:
            subgroup = self.ed_subgroup_l1.texto().strip()
            if subgroup:
                carpeta = os.path.join(self.configuration.folder_databases(), group, subgroup)
                resp = self.menu_groups(carpeta)
                if resp:
                    self.ed_subgroup_l2.set_text(resp)

    def save(self):
        name = self.ed_name.texto().strip()
        if not name:
            QTUtil2.message_error(self, _("You must indicate a name"))
            return

        folder = self.configuration.folder_databases()
        group = self.ed_group.texto()
        if group:
            folder = os.path.join(folder, group)
            subgroup_l1 = self.ed_subgroup_l1.texto()
            if subgroup_l1:
                folder = os.path.join(folder, subgroup_l1)
                subgroup_l2 = self.ed_subgroup_l2.texto()
                if subgroup_l2:
                    folder = os.path.join(folder, subgroup_l2)
        if not Util.exist_folder(folder):
            try:
                os.makedirs(folder, True)
            except:
                QTUtil2.message_error(self, "%s\n%s" % (_("Unable to create the folder"), folder))
                return

        filename = "%s.lcdb" % name
        if self.external_folder:
            filepath_with_data = os.path.join(self.external_folder, filename)
        else:
            filepath_with_data = os.path.join(folder, filename)

        test_exist = self.new
        if not self.new:
            previous = self.dic_data["FILEPATH"]
            test_exist = not Util.same_path(previous, filepath_with_data)

        if test_exist and Util.exist_file(filepath_with_data):
            QTUtil2.message_error(self, "%s\n%s" % (_("This database already exists."), filepath_with_data))
            return

        if self.external_folder:
            filepath_in_databases = os.path.join(folder, "%s.lcdblink" % name)
            with open(filepath_in_databases, "wt", encoding="utf-8", errors="ignore") as q:
                q.write(filepath_with_data)
        else:
            filepath_in_databases = filepath_with_data

        self.dic_data_resp = {
            "ALLOWS_DUPLICATES": self.chb_duplicate.valor(),
            "ALLOWS_POSITIONS": self.chb_positions.valor(),
            "ALLOWS_COMPLETE_GAMES": self.chb_complete.valor(),
            "ALLOWS_ZERO_MOVES": self.chb_zeromoves.valor(),
            "SUMMARY_DEPTH": self.sb_summary.valor(),
        }

        self.dic_data_resp["FILEPATH"] = filepath_in_databases
        self.dic_data_resp["EXTERNAL_FOLDER"] = self.external_folder

        self.dic_data_resp["FILEPATH_WITH_DATA"] = filepath_with_data

        self.accept()


def new_database(owner, configuration):
    dic_data = {}
    w = WOptionsDatabase(owner, configuration, dic_data)
    if w.exec_():
        filepath = w.dic_data_resp["FILEPATH"]
        if w.external_folder:
            with open(filepath, "wt", encoding="utf-8", errors="ignore") as q:
                q.write(w.dic_data_resp["FILEPATH_WITH_DATA"])
        db = DBgames.DBgames(filepath)
        for key, value in w.dic_data_resp.items():
            db.save_config(key, value)
        db.close()
        return filepath
    else:
        return None


class WTags(LCDialog.LCDialog):
    def __init__(self, owner, dbgames: [DBgames.DBgames]):
        LCDialog.LCDialog.__init__(self, owner, _("Tags"), Iconos.Tags(), "tagsedition")
        self.dbgames = dbgames
        self.dic_cambios = None

        dcabs = dbgames.read_config("dcabs", {})
        li_basetags = dbgames.li_tags()
        if li_basetags[0] == "PLYCOUNT":
            del li_basetags[0]

        self.li_data = []
        for tag in li_basetags:
            dic = {
                "KEY": tag,
                "LABEL": dcabs.get(tag, Util.primera_mayuscula(tag)),
                "ACTION": "-",
                "VALUE": "",
                "NEW": False,
            }
            dic["PREV_LABEL"] = dic["KEY"]
            self.li_data.append(dic)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("KEY", _("Key"), 80, align_center=True)
        o_columns.nueva(
            "LABEL", _("PGN Label"), 80, align_center=True, edicion=Delegados.LineaTexto(rx="[A-Za-z_0-9]*")
        )

        self.fill_column = _("Fill column with value")
        self.remove_column = _("Remove column")
        self.nothing = "-"
        self.li_actions = [self.nothing, self.fill_column, self.remove_column]
        o_columns.nueva("ACTION", _("Action"), 80, align_center=True, edicion=Delegados.ComboBox(self.li_actions))
        o_columns.nueva("VALUE", self.fill_column, 200, edicion=Delegados.LineaTextoUTF8())
        self.gtags = Grid.Grid(self, o_columns, is_editable=True)

        li_acciones = (
            (_("Save"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
            (_("New"), Iconos.Nuevo(), self.new),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        ly = Colocacion.V().control(tb).control(self.gtags).margen(4)

        self.setLayout(ly)

        self.register_grid(self.gtags)
        self.restore_video(anchoDefecto=self.gtags.anchoColumnas() + 20, altoDefecto=400)

        self.gtags.gotop()

    def grid_num_datos(self, grid):
        return len(self.li_data)

    def grid_dato(self, grid, row, ocol):
        return self.li_data[row][ocol.key]

    def grid_setvalue(self, grid, row, o_column, value):
        key = o_column.key
        dic = self.li_data[row]
        value = value.strip()
        if key == "VALUE" and value:
            dic["ACTION"] = self.fill_column
        elif key == "ACTION" and value != self.fill_column:
            dic["VALUE"] = ""
        elif key == "LABEL":
            new = dic["NEW"]
            if new:
                newkey = value.upper()
                for xfila, xdic in enumerate(self.li_data):
                    if xfila != row:
                        if xdic["KEY"] == newkey or xdic["PREV_LABEL"] == newkey:
                            QTUtil2.message_error(self, _("This tag is repeated"))
                            return
                dic["KEY"] = newkey
                dic["PREV_LABEL"] = newkey
            else:
                if len(value) == 0:
                    return
        dic[key] = value
        self.gtags.refresh()

    def aceptar(self):
        dic_cambios = {"CREATE": [], "RENAME": [], "FILL": [], "REMOVE": []}
        for dic in self.li_data:
            if dic["NEW"]:
                key = dic["KEY"]
                if len(key) == 0 or dic["ACTION"] == self.remove_column:
                    continue
                dic_cambios["CREATE"].append(dic)
            elif dic["LABEL"] != dic["PREV_LABEL"]:
                dic_cambios["RENAME"].append(dic)
            if dic["ACTION"] == self.remove_column:
                dic_cambios["REMOVE"].append(dic)
            elif dic["ACTION"] == self.fill_column:
                dic_cambios["FILL"].append(dic)

        self.dic_cambios = dic_cambios
        self.accept()

    def new(self):
        dic = {"KEY": "", "PREV_LABEL": "", "LABEL": "", "ACTION": "-", "VALUE": "", "NEW": True}
        self.li_data.append(dic)
        self.gtags.refresh()
