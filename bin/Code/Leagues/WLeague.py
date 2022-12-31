import gettext
_ = gettext.gettext
import collections

from PySide2 import QtWidgets, QtCore

import Code
from Code import XRun
from Code.Base import Game
from Code.Base.Constantes import RESULT_WIN_WHITE, RESULT_DRAW, RESULT_WIN_BLACK
from Code.Databases import DBgames, WDB_Games
from Code.Leagues import LeaguesWork, Leagues
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.SQL import UtilSQL

NONE, PLAY_HUMAN, REINIT = range(3)


class WLeague(LCDialog.LCDialog):
    def __init__(self, w_parent, league):

        titulo = "%s - %s %d" % (league.name(), _("Season"), league.get_current_season() + 1)
        icono = Iconos.League()
        extparam = "league"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        self.league = league
        self.season = league.read_season()
        self.li_panels, self.dic_xid_order = self.season.gen_panels_classification()
        self.li_panels_crosstabs = (
            self.season.gen_panels_crosstabs()
        )  # division - dic[xid] = [wdl, wdl] RESULT_WIN_WHITE/....
        self.li_sorted_opponents = (
            self.season.list_sorted_opponents()
        )  # division - list - opponents objects   (alphabetically)
        self.mix_panels()

        self.li_matches = self.season.get_all_matches()
        self.current_journey = self.season.get_current_journey()
        self.max_journeys = self.season.get_max_journeys()
        self.dic_xid_name = self.league.dic_names()
        self.terminated = False
        self.play_human = None
        self.result = NONE
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_matches)

        self.li_grids_divisions = []
        self.li_grids_divisions_crosstabs = []

        self.num_workers_launched = 0

        self.color_win = Code.dic_qcolors["WLEAGUE_WIN"]
        self.color_lost = Code.dic_qcolors["WLEAGUE_LOST"]
        self.color_noresult = Code.dic_qcolors["WLEAGUE_NORESULT"]
        self.color_draw = Code.dic_qcolors["WLEAGUE_DRAW"]
        self.color_migration = Code.dic_qcolors["WLEAGUE_MIGRATION"]

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Launch a worker"), Iconos.Lanzamiento(), self.launch_worker),
            None,
            (_("Update"), Iconos.Update(), self.update_matches),
            None,
            (_("Export"), Iconos.Export8(), self.export),
            None,
            (_("Seasons"), Iconos.Season(), self.seasons),
            None,
            (_("Config"), Iconos.Configurar(), self.config),
        )
        self.tb = QTVarios.LCTB(self, li_acciones)

        self.tab = Controles.Tab(self).ponTipoLetra(puntos=10).set_position("S")
        font = Controles.TipoLetra(puntos=10)

        ly = Colocacion.H()
        li_nom_divisions = [
            _("First Division"),
            _("Second Division"),
            _("Third Division"),
            _("Fourth Division"),
            _("Fifth Division"),
        ]
        num_divisions = self.league.num_divisions()
        if num_divisions > 5:
            for dv in range(6, num_divisions + 1):
                li_nom_divisions.append("%d %s" % (dv, _("Division")))
        tr = Controles.Tab(self).ponTipoLetra(puntos=10)  # .set_position("S")
        sw = "◻  "
        sb = "◼  "
        for division in range(num_divisions):
            o_col = Columnas.ListaColumnas()
            o_col.nueva("NAME", _("Opponent"), 150)
            o_col.nueva("PTS", _("Pts ||Points/score"), 50, align_center=True)
            o_col.nueva("PL", _("GP ||Games played"), 40, align_center=True)
            o_col.nueva("WIN", _("W ||Games won"), 50, align_center=True)
            o_col.nueva("DRAW", _("D ||Games drawn"), 50, align_center=True)
            o_col.nueva("LOST", _("L ||Games lost"), 50, align_center=True)
            o_col.nueva("ACT_ELO", _("Current ELO"), 90, align_center=True)
            o_col.nueva("DIF_ELO", "∆", 60, align_center=True)
            o_col.nueva("INI_ELO", _("Initial ELO"), 90, align_center=True)
            for num_op in range(len(self.li_panels[division])):
                o_col.nueva("w%d" % num_op, sw + str(num_op + 1), 40, align_center=True)
                o_col.nueva("b%d" % num_op, sb + str(num_op + 1), 40, align_center=True)

            grid = Grid.Grid(self, o_col, xid="CLASSIF%d" % division, with_header_vertical=True)
            grid.setFont(font)
            self.li_grids_divisions.append(grid)
            tr.addTab(grid, li_nom_divisions[division])
        ly.control(tr)

        w = QtWidgets.QWidget(self)
        w.setLayout(ly)

        self.tab.addTab(w, _("Classification"))
        self.tab.setIconSize(QtCore.QSize(32, 32))
        self.tab.ponIcono(0, Iconos.Classification())

        # CROSSTABS ----------------------------------------------------------------------------------------------------
        ly = Colocacion.H()
        tr = Controles.Tab(self).ponTipoLetra(puntos=10)  # .set_position("S")
        for num_division in range(num_divisions):
            o_col = Columnas.ListaColumnas()
            o_col.nueva("ORDER", _("Order"), 30, align_center=True)
            for opponent in self.li_sorted_opponents[num_division]:
                o_col.nueva(opponent.xid, opponent.name(), 30, align_center=True)
            grid = Grid.Grid(
                self,
                o_col,
                xid="CROSSTABS%d" % num_division,
                siSelecFilas=False,
                cab_vertical_font=180,
                with_header_vertical=True,
            )
            grid.setFont(font)
            grid.set_headervertical_alinright()
            # self.register_grid(grid)
            self.li_grids_divisions_crosstabs.append(grid)
            tr.addTab(grid, li_nom_divisions[num_division])
        ly.control(tr)

        w = QtWidgets.QWidget(self)
        w.setLayout(ly)

        self.tab.addTab(w, _("Crosstabs"))
        self.tab.setIconSize(QtCore.QSize(32, 32))
        self.tab.ponIcono(1, Iconos.Crosstable())

        # Matches
        o_col = Columnas.ListaColumnas()
        o_col.nueva("DIVISION", _("Division"), 60, align_center=True)
        o_col.nueva("WHITE", _("White"), 240)
        o_col.nueva("BLACK", _("Black"), 240)
        o_col.nueva("RESULT", _("Result"), 180, align_center=True)
        self.grid_matches = Grid.Grid(self, o_col, siSelecFilas=True)
        self.register_grid(self.grid_matches)
        self.grid_matches.setFont(font)

        self.dic_order = {}

        tbj = QTVarios.LCTB(self, with_text=False, icon_size=24, style=QtCore.Qt.ToolButtonIconOnly)
        tbj.new("", Iconos.MoverInicio(), self.journey_first, False)
        tbj.new("", Iconos.MoverAtras(), self.journey_previous, False)
        tbj.new("", Iconos.Journey(), self.journey_active, False)
        tbj.new("", Iconos.MoverAdelante(), self.journey_next, False)
        tbj.new("", Iconos.MoverFinal(), self.journey_last, False)

        fontd = Controles.TipoLetra(puntos=12)

        lb_journey = Controles.LB(self, _("Matchday") + ": ").ponFuente(fontd)
        self.sb_journey = Controles.SB(self, self.current_journey + 1, 1, self.max_journeys).ponFuente(fontd)
        self.sb_journey.setFixedWidth(50)
        self.sb_journey.capture_changes(self.change_sb)
        lb_info_journey = Controles.LB(self, "/ %d" % self.max_journeys).ponFuente(fontd)

        self.lb_active = (
            Controles.LB(self, _("CURRENT MATCHDAY"))
            .ponFuente(Controles.TipoLetra(puntos=16, peso=400))
            .align_center()
            .anchoMinimo(400)
        )
        self.lb_active.setStyleSheet(
            "color: %s;background: %s;padding-left:5px;padding-right:5px;" % ("white", "#437FBC")
        )

        ly0 = (
            Colocacion.H()
            .espacio(8)
            .control(lb_journey)
            .control(self.sb_journey)
            .control(lb_info_journey)
            .control(tbj)
            .relleno()
            .control(self.lb_active)
            .relleno()
        )
        ly = Colocacion.V().otro(ly0).control(self.grid_matches)

        w = QtWidgets.QWidget(self)
        w.setLayout(ly)
        self.tab.addTab(w, _("Matches"))

        layout = Colocacion.V().control(self.tb).control(self.tab).margen(8)
        self.setLayout(layout)

        self.restore_video(siTam=True, anchoDefecto=784, altoDefecto=460)

        self.update_matches()

        self.set_journey_if_active()

        for grid in self.li_grids_divisions:
            grid.resizeColumnToContents(0)

    def config(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion(
            "continue",
            _("Launch new workers when a matchday ends"),
            Iconos.Unchecked() if self.season.stop_work_journey else Iconos.Checked(),
        )
        resp = menu.lanza()
        if resp:
            self.season.stop_work_journey = not self.season.stop_work_journey
            self.season.save()

    def set_journey_if_active(self):
        antes = self.current_journey
        self.current_journey = self.season.get_current_journey()
        if antes != self.current_journey:
            self.update_matches()
            lw = LeaguesWork.LeaguesWork(self.league)
            lw.put_league()
            if self.pending_matches() and not self.season.stop_work_journey:
                for x in range(self.num_workers_launched):
                    XRun.run_lucas("-league", self.league.name())
        active = self.current_journey == self.sb_journey.valor() - 1
        self.lb_active.setVisible(active)

        self.tb_option_seasons()

    def tb_option_seasons(self):
        # Si es una sesion terminada, si es la última -> activa tb Seasons
        li_seasons = self.season.list_seasons()
        ok = len(li_seasons) > 1 or self.season.is_finished()
        self.tb.set_action_visible(self.seasons, ok)

    def set_journey(self, pos):
        if 0 < pos <= self.max_journeys:
            self.sb_journey.setValue(pos)
            self.li_matches = self.season.get_all_matches_journey(pos - 1)
            self.grid_matches.refresh()
            self.set_journey_if_active()

    def change_sb(self):
        pos = self.sb_journey.valor()
        self.li_matches = self.season.get_all_matches_journey(pos - 1)
        self.set_journey_if_active()
        self.grid_matches.refresh()

    def journey_first(self):
        self.set_journey(1)

    def journey_last(self):
        self.set_journey(self.max_journeys)

    def journey_previous(self):
        self.set_journey(self.sb_journey.valor() - 1)

    def journey_next(self):
        self.set_journey(self.sb_journey.valor() + 1)

    def journey_active(self):
        self.set_journey(self.current_journey + 1)

    def grid_num_datos(self, grid):
        if grid in self.li_grids_divisions:
            return len(self.li_panels[self.li_grids_divisions.index(grid)])
        elif grid in self.li_grids_divisions_crosstabs:
            return len(self.li_panels_crosstabs[self.li_grids_divisions_crosstabs.index(grid)]) + 1
        return len(self.li_matches)

    def grid_dato(self, grid, row, o_column):
        column = o_column.key
        if grid in self.li_grids_divisions:
            num_division = self.li_grids_divisions.index(grid)
            return self.grid_dato_division(num_division, row, column)
        elif grid in self.li_grids_divisions_crosstabs:
            num_division = self.li_grids_divisions_crosstabs.index(grid)
            return self.grid_dato_crosstab(num_division, row, column)

        else:
            xmatch = self.li_matches[row]
            if column == "RESULT":
                result = xmatch.result
                if result is None:
                    active = self.current_journey == self.sb_journey.valor() - 1
                    if xmatch.is_human_vs_engine(self.league):
                        return _("Double click to play") if active else "-"
                    if xmatch.is_human_vs_human(self.league):
                        return _("Double click to edit") if active else "-"
                    return "-"
                else:
                    return result
            if column == "WHITE":
                return self.dic_xid_name[xmatch.xid_white]
            elif column == "BLACK":
                return self.dic_xid_name[xmatch.xid_black]
            elif column == "DIVISION":
                return xmatch.label_division

    def grid_color_texto(self, grid, row, o_column):
        if grid in self.li_grids_divisions:
            if self.season.is_finished():
                migration = self.league.migration
                ndatos = self.grid_num_datos(grid)
                num_division = self.li_grids_divisions.index(grid)
                d_panel = self.li_panels[num_division][row]
                order = d_panel["ORDER"]
                if order <= migration:
                    return self.color_win
                elif order > (ndatos - migration):
                    return self.color_lost

    def grid_color_fondo(self, grid, row, o_column):
        if grid in self.li_grids_divisions_crosstabs:
            column = o_column.key
            num_division = self.li_grids_divisions_crosstabs.index(grid)
            return self.grid_color_fondo_crosstabs(num_division, row, column)

        if grid in self.li_grids_divisions:
            if self.season.is_finished():
                migration = self.league.migration
                ndatos = self.grid_num_datos(grid)
                num_division = self.li_grids_divisions.index(grid)
                d_panel = self.li_panels[num_division][row]
                order = d_panel["ORDER"]
                if order <= migration or order > (ndatos - migration):
                    return self.color_migration

    def grid_bold(self, grid, row, o_column):
        if grid in self.li_grids_divisions_crosstabs:
            return True
        migration = self.league.migration
        ndatos = self.grid_num_datos(grid)
        return (
            grid in self.li_grids_divisions
            and self.season.is_finished()
            and (row < migration or row > (ndatos - migration - 1))
        )

    def grid_doubleclick_header(self, grid, col):
        if grid == self.grid_matches:

            key = col.key
            order_prev = self.dic_order.get(key, False)
            self.dic_order[key] = order = not order_prev

            li = [(self.grid_dato(grid, row, col), xmatch) for row, xmatch in enumerate(self.li_matches)]
            li.sort(key=lambda x: x[0], reverse=not order)
            self.li_matches = [xmatch for dato, xmatch in li]

        elif grid in self.li_grids_divisions:
            num_division = self.li_grids_divisions.index(grid)
            key_order = "D", num_division, col.key
            order_next = self.dic_order.get(key_order, 0) + 1
            if order_next > 2:
                order_next = 0
            self.dic_order[key_order] = order_next

            li_panel = self.li_panels[num_division]
            if order_next == 0:
                li_panel.sort(key=lambda x: x["ORDER"])
            else:
                if col.key == "DIF_ELO":
                    li_panel.sort(key=lambda x: x["ACT_ELO"] - x["INI_ELO"], reverse=order_next == 2)

                elif col.key[0] in "wb":

                    def xsort(dic):
                        x = dic[col.key]
                        if x in ("", "-"):
                            return -1.0
                        else:
                            return float(x)

                    li_panel.sort(key=xsort, reverse=order_next == 2)

                else:
                    li_panel.sort(key=lambda x: x[col.key], reverse=order_next == 2)

        elif grid in self.li_grids_divisions_crosstabs:
            num_division = self.li_grids_divisions_crosstabs.index(grid)
            if col.key != "ORDER":
                return

            key_order = "C", num_division, "H"
            pos_order = self.dic_order.get(key_order, 0)
            pos_order += 1
            if pos_order > 2:
                pos_order = 0
            self.dic_order[key_order] = pos_order

            def order_classification(x):
                return self.dic_xid_order[x.xid]

            def order_classification_v(x):
                return -self.dic_xid_order[x.xid]

            def order_alphabetically(x):
                return self.dic_xid_name[x.xid]

            if pos_order == 0:
                func_order = order_alphabetically
            elif pos_order == 1:
                func_order = order_classification
            else:
                func_order = order_classification_v

            self.li_sorted_opponents[num_division].sort(key=func_order)

        grid.refresh()
        grid.gotop()

    def grid_doubleclick_header_vertical(self, grid, row):
        if grid in self.li_grids_divisions:
            self.grid_doble_click(grid, row, None)
        elif grid in self.li_grids_divisions_crosstabs:
            if row == 0:
                num_division = self.li_grids_divisions_crosstabs.index(grid)

                key_order = "C", num_division, "V"
                pos_order = self.dic_order.get(key_order, 0)
                pos_order += 1
                if pos_order > 2:
                    pos_order = 0
                self.dic_order[key_order] = pos_order

                def order_classification(x):
                    return self.dic_xid_order[x.key] if x.key != "ORDER" else 0

                def order_classification_v(x):
                    return -self.dic_xid_order[x.key] if x.key != "ORDER" else -999999

                def order_alphabetically(x):
                    return self.dic_xid_name[x.key] if x.key != "ORDER" else "      "

                if pos_order == 0:
                    func_order = order_alphabetically
                elif pos_order == 1:
                    func_order = order_classification
                else:
                    func_order = order_classification_v

                li_columnas = grid.oColumnasR.li_columns
                li_columnas.sort(key=func_order)
                grid.refresh()

    def grid_dato_division(self, num_division, row, nom_column):
        d_panel = self.li_panels[num_division][row]
        if nom_column == "DIF_ELO":
            dif = d_panel["ACT_ELO"] - d_panel["INI_ELO"]
            if dif == 0:
                return "-"
            if dif > 0:
                return "+%d" % dif
            else:
                return "%d" % dif
        if nom_column == "PTS":
            cpts = "%0.02f" % d_panel[nom_column]
            while cpts.endswith("0"):
                cpts = cpts[:-1]
            if cpts.endswith("."):
                cpts = cpts[:-1]
            return cpts
        if nom_column == "NAME":
            return self.dic_xid_name[d_panel["XID"]]
        return str(d_panel[nom_column])

    def grid_dato_crosstab(self, num_division, row, nom_column):
        other_xid = nom_column
        if row == 0:
            if nom_column == "ORDER":
                return ""
            else:
                return str(self.dic_xid_order[other_xid])
        op_xid = self.li_sorted_opponents[num_division][row - 1].xid
        if op_xid == other_xid:
            return ""
        if nom_column == "ORDER":
            return str(self.dic_xid_order[op_xid])

        result = self.li_panels_crosstabs[num_division][op_xid][other_xid]
        if result is None:
            return ""
        if result == RESULT_DRAW:
            return _("D ||Games drawn")
        if result == RESULT_WIN_WHITE:
            return _("W ||White")
        else:
            return _("B ||Black")

    def grid_get_header_vertical(self, grid, col):
        if grid in self.li_grids_divisions_crosstabs:
            if col == 0:
                return _("Order")
            num_division = self.li_grids_divisions_crosstabs.index(grid)
            return self.li_sorted_opponents[num_division][col - 1].name()

        elif grid in self.li_grids_divisions:
            num_division = self.li_grids_divisions.index(grid)
            d_panel = self.li_panels[num_division][col]
            return " %2d " % self.dic_xid_order[d_panel["XID"]]

    def grid_color_fondo_crosstabs(self, num_division, row, nom_column):
        if nom_column == "ORDER" or row == 0:
            return
        other_xid = nom_column
        op_xid = self.li_sorted_opponents[num_division][row - 1].xid
        if op_xid == other_xid:
            return
        result = self.li_panels_crosstabs[num_division][op_xid][other_xid]
        if result is None:
            return self.color_noresult
        if result == RESULT_DRAW:
            return self.color_draw
        if result == RESULT_WIN_WHITE:
            return self.color_win
        else:
            return self.color_lost

    def consult_matches(self, grid, row):
        num_division = self.li_grids_divisions.index(grid)
        d_panel = self.li_panels[num_division][row]
        xid_engine = d_panel["XID"]
        li_matches_played = self.season.get_all_matches_opponent(num_division, xid_engine)
        if len(li_matches_played) == 0:
            return
        self.select_match(li_matches_played, xid_engine)

    def select_match(self, li_matches, xid_engine):
        win = _("Win")
        draw = _("Draw")
        lost = _("Loss")
        dic = collections.defaultdict(list)
        dicon = {0: Iconos.Rojo(), 5: Iconos.Naranja(), 10: Iconos.Azul(), 15: Iconos.Verde(), 20: Iconos.Magenta()}
        for xmatch in li_matches:
            white = self.dic_xid_name[xmatch.xid_white]
            black = self.dic_xid_name[xmatch.xid_black]
            result = xmatch.result
            if xmatch.xid_white == xid_engine:
                icon = Iconos.Blancas()
                opponent = black
                cresult = win if result == RESULT_WIN_WHITE else (lost if result == RESULT_WIN_BLACK else draw)
            else:
                icon = Iconos.Negras()
                opponent = white
                cresult = win if result == RESULT_WIN_BLACK else (lost if result == RESULT_WIN_WHITE else draw)
            dic[opponent].append((xmatch, icon, cresult))

        menu = QTVarios.LCMenu(self)
        menu.ponTipoLetra(name=Code.font_mono, puntos=10)

        li_names = list(dic.keys())
        li_names.sort()

        for opponent in li_names:
            li = dic[opponent]
            pt = 0
            for xmatch, icon, cresult in li:
                if cresult == win:
                    pt += 10
                elif cresult == draw:
                    pt += 5
            submenu = menu.submenu(opponent, dicon.get(pt, Iconos.PuntoNegro()))
            for xmatch, icon, cresult in li:
                submenu.opcion(xmatch, cresult, icon)
            menu.separador()
        xmatch = menu.lanza()
        if xmatch:
            self.show_match_done(xmatch)

    def consult_matches_classification(self, grid, row):
        xmatch = self.li_matches[row]
        division = int(xmatch.label_division)
        if xmatch.result:
            self.show_match_done(xmatch)
            grid.refresh()

        elif xmatch.is_human_vs_engine(self.league):
            self.play_human = self.league, xmatch, division
            self.result = PLAY_HUMAN
            self.accept()

        elif xmatch.is_human_vs_human(self.league):
            game = Game.Game()
            game.set_tag("Site", Code.lucas_chess)
            game.set_tag("Event", self.league.name())
            game.set_tag("Season", str(self.league.current_num_season + 1))
            game.set_tag("Division", str(division + 1))
            game.set_tag("White", self.league.opponent_by_xid(xmatch.xid_white).name())
            game.set_tag("Black", self.league.opponent_by_xid(xmatch.xid_black).name())
            panel = self.li_panels[division]
            elo_white = elo_black = 0
            for elem in panel:
                if elem["XID"] == xmatch.xid_white:
                    elo_white = elem["ACT_ELO"]
                elif elem["XID"] == xmatch.xid_black:
                    elo_black = elem["ACT_ELO"]
            game.set_tag("WhiteElo", str(elo_white))
            game.set_tag("BlackElo", str(elo_black))

            menu = QTVarios.LCMenu(self)
            menu.opcion(RESULT_DRAW, RESULT_DRAW, Iconos.Tablas())
            menu.separador()
            menu.opcion(RESULT_WIN_WHITE, RESULT_WIN_WHITE, Iconos.Blancas())
            menu.separador()
            menu.opcion(RESULT_WIN_BLACK, RESULT_WIN_BLACK, Iconos.Negras())
            resp = menu.lanza()
            if resp is None:
                return
            game.set_tag("Result", resp)

            while True:
                game_resp = Code.procesador.manager_game(self, game, True, False, None)
                if game_resp:
                    game_resp.verify()
                    if game.resultado() in (RESULT_WIN_BLACK, RESULT_DRAW, RESULT_WIN_WHITE):
                        xmatch.result = game.resultado()
                        self.season.put_match_done(xmatch, game)
                        self.update_matches()
                        grid.refresh()
                        return
                    else:
                        QTUtil2.message_error(self, _("The game must have a valid result tag"))
                        game = game_resp
                else:
                    return

    def consult_matches_crosstabs(self, grid, row, other_xid):
        if other_xid == "ORDER" or row == 0:
            return
        num_division = self.li_grids_divisions_crosstabs.index(grid)
        op_xid = self.li_sorted_opponents[num_division][row - 1].xid
        li_matches_played = self.season.get_all_matches_opponent(num_division, op_xid)
        if other_xid == op_xid:
            self.select_match(li_matches_played, op_xid)
            return
        xmatch: Leagues.Match
        for xmatch in li_matches_played:
            if other_xid == xmatch.xid_black:
                self.show_match_done(xmatch)

    def grid_doble_click(self, grid, row, o_column):
        if grid in self.li_grids_divisions:
            nom_column = o_column.key if o_column else None
            if nom_column and nom_column[0] in "wb":
                is_white = nom_column.startswith("w")
                pos_other = int(nom_column[1:]) + 1
                num_division = self.li_grids_divisions.index(grid)
                d_panel = self.li_panels[num_division][row]
                if pos_other == d_panel["ORDER"]:
                    return
                xid = d_panel["XID"]
                for un_panel in self.li_panels[num_division]:
                    if un_panel["ORDER"] == pos_other:
                        d_panel_other = un_panel
                        break
                other_xid = d_panel_other["XID"]
                if not is_white:
                    xid, other_xid = other_xid, xid
                xmatch = self.season.get_match(num_division, xid, other_xid)
                if xmatch:
                    self.show_match_done(xmatch)
                return

            else:
                self.consult_matches(grid, row)

        elif grid in self.li_grids_divisions_crosstabs:
            self.consult_matches_crosstabs(grid, row, o_column.key)

        else:
            self.consult_matches_classification(grid, row)

    def show_match_done(self, xmatch):
        game = self.season.get_game_match(xmatch)
        if game:
            game = Code.procesador.manager_game(self, game, True, False, None)
            if game:
                self.season.put_match_done(xmatch, game)

    def update_matches(self):
        if self.terminated:
            return
        journey = self.current_journey
        if self.season.is_finished():
            self.timer.stop()
            self.season.test_next()
            self.tb.set_action_visible(self.update_matches, False)
            self.tb.set_action_visible(self.launch_worker, False)
            return
        changed = False
        division: Leagues.Division
        for division in self.season.li_divisions:
            for xmatch in division.get_all_matches(journey):
                if xmatch.result is None:
                    with UtilSQL.DictRawSQL(self.league.path(), "SEASON_%d" % self.league.current_num_season) as db:
                        game_saved = db[xmatch.xid]
                        if game_saved is not None:
                            game = Game.Game()
                            game.restore(game_saved)
                            xmatch.result = game.result
                            changed = True

        if changed:
            self.season.save()
            self.show_current_season()

        self.set_journey_if_active()

        if self.timer:
            lw = LeaguesWork.LeaguesWork(self.league)
            if lw.num_working_matches():
                self.timer.stop()
                self.timer.start(10000)
            else:
                self.timer.stop()
                self.timer.start(10000)

    def show_current_season(self):
        self.li_panels, self.dic_xid_order = self.season.gen_panels_classification()
        for grid in self.li_grids_divisions:
            grid.refresh()

        self.li_panels_crosstabs = self.season.gen_panels_crosstabs()
        self.mix_panels()
        for grid in self.li_grids_divisions_crosstabs:
            grid.refresh()
        self.grid_matches.refresh()

    def terminar(self):
        self.terminated = True
        if self.timer:
            self.timer.stop()
            self.timer = None
        self.save_video()
        self.accept()

    def closeEvent(self, event):
        self.terminated = True
        if self.timer:
            self.timer.stop()
            self.timer = None

    def pending_matches(self):
        lw = LeaguesWork.LeaguesWork(self.league)
        if lw.num_pending_matches() > 0:
            return True

        resp = False
        for xmatch in self.li_matches:
            if not xmatch.result:
                resp = True
                lw.add_match_zombie(xmatch)
        return resp

    def launch_worker(self):
        rondo = QTVarios.rondoPuntos()

        menu = QTVarios.LCMenu(self)
        menu.opcion(1, _("Launch one worker"), Iconos.Lanzamiento())
        menu.separador()

        submenu = menu.submenu(_("Launch some workers"), Iconos.Lanzamientos())

        for x in range(2, 33):
            submenu.opcion(x, str(x), rondo.otro())

        resp = menu.lanza()
        if resp:
            self.update_matches()
            lw = LeaguesWork.LeaguesWork(self.league)
            journey_work, season_work = lw.get_journey_season()
            current_journey = self.season.get_current_journey()
            if journey_work != current_journey or self.league.current_num_season != season_work:
                lw.put_league()
            if self.pending_matches():
                for x in range(resp):
                    XRun.run_lucas("-league", self.league.name())
                self.num_workers_launched = resp
            else:
                QTUtil2.message(self, _("There are no pending matches in the current matchday"))

    def export(self):
        menu = QTVarios.LCMenu(self)
        submenu = menu.submenu(_("Save all games to a database"), Iconos.DatabaseMas())
        QTVarios.menuDB(submenu, Code.configuration, True, indicador_previo="dbf_", remove_autosave=True, siNew=True)
        menu.separador()

        resp = menu.lanza()
        if resp is None:
            return

        if resp.startswith("dbf_"):
            if resp.endswith(":n"):
                database = WDB_Games.new_database(self, Code.configuration)
                if database is None:
                    return
            else:
                database = resp[4:]

            dic_raw_games = self.season.dic_raw_games()
            pb = QTUtil2.BarraProgreso(self, _("Generating the list of games to save"), "", len(dic_raw_games), 500)
            pb.mostrar()
            li_games = []
            for pos, saved in enumerate(dic_raw_games.values(), 1):
                pb.pon(pos)
                if pb.is_canceled():
                    return
                try:
                    g = Game.Game()
                    g.restore(saved)
                    li_games.append(g)
                except TypeError:
                    pass
            pb.close()

            pb = QTUtil2.BarraProgreso(self, _("Save all games to a database"), "", len(li_games), 500)
            pb.mostrar()
            db = DBgames.DBgames(database)
            nsaved = 0
            nerror = 0
            total = len(li_games)
            for pos, game in enumerate(li_games, 1):
                pb.pon(pos)
                if pb.is_canceled():
                    break
                resp = db.insert(game)
                if resp.ok:
                    nsaved += 1
                else:
                    nerror += 1
            db.close()
            pb.close()
            if total > 0:
                if nerror:
                    explanation = _("The database did not allow %d duplicate games to be recorded").replace(
                        "%d", str(nerror)
                    )
                else:
                    explanation = None
                QTUtil2.message(
                    self,
                    _("Saved") + " %d" % nsaved,
                    explanation=explanation,
                )

        else:
            num_season = int(resp)
            self.league.set_current_season(num_season)
            self.result = REINIT
            self.accept()

    def seasons(self):
        li_seasons = self.season.list_seasons()
        if len(li_seasons) > 1:
            rondo = QTVarios.rondoPuntos()
            menu = QTVarios.LCMenu(self)
            submenu = menu.submenu(_("Change the active season"), Iconos.Season())
            for num_season in li_seasons:
                if self.season.num_season != num_season:
                    submenu.opcion(str(num_season), str(num_season + 1), rondo.otro())
                    submenu.separador()

            resp = menu.lanza()
            if resp is None:
                return

            num_season = int(resp)
            self.league.set_current_season(num_season)
            self.result = REINIT
            self.accept()

    def mix_panels(self):
        for num_division, li_panel in enumerate(self.li_panels):
            for pos, un_elem in enumerate(li_panel):
                for pos_otro, otro_elem in enumerate(li_panel):
                    for side in ("w", "b"):
                        key = "%s%d" % (side, pos_otro)
                        if pos == pos_otro:
                            valor = ""
                        else:
                            xid = un_elem["XID"]
                            other_xid = self.li_panels[num_division][pos_otro]["XID"]
                            if side == "b":
                                xid, other_xid = other_xid, xid
                            result = self.li_panels_crosstabs[num_division][xid][other_xid]
                            if result is None:
                                valor = "-"
                            else:
                                if result == RESULT_DRAW:
                                    valor = self.league.score_draw
                                elif result == RESULT_WIN_WHITE:
                                    valor = self.league.score_win if side == "w" else self.league.score_lost
                                else:
                                    valor = self.league.score_lost if side == "w" else self.league.score_win
                                cs = "%0.02f" % valor
                                while cs.endswith("0"):
                                    cs = cs[:-1]
                                if cs.endswith("."):
                                    cs = cs[:-1]
                                valor = cs
                        un_elem[key] = valor


def play_league(parent, league):
    w = WLeague(parent, league)
    if w.exec_():
        if w.result == PLAY_HUMAN:
            return w.play_human
        elif w.result == REINIT:
            return play_league(parent, league)
