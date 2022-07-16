from PySide2 import QtCore

import Code
from Code import Util
from Code.Engines import SelectEngines
from Code.Leagues import Leagues
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WLeagueConfig(LCDialog.LCDialog):
    def __init__(self, w_parent, league: Leagues.League):

        titulo = "%s: %s" % (_("League"), league.name())
        icono = Iconos.League()
        extparam = "leagueConfiguration"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        self.league: Leagues.League = league
        self.remove_seasons_delayed = False

        self.sortby = "elo"

        self.li_colors = [QTUtil.qtColor("#fefefe"), QTUtil.qtColor("#dee4e7"), QTUtil.qtColor("#b0d8cc")]

        self.select_engines = SelectEngines.SelectEngines()

        li_acciones = [
            (_("Save"), Iconos.GrabarFichero(), self.save),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancel),
        ]
        if not self.league.is_editable():
            li_acciones.append(None)
            li_acciones.append((_("Remove all seasons"), Iconos.Borrar(), self.remove_seasons))

        self.tb = QTVarios.LCTB(self, li_acciones)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("ROW", "", 15, align_center=True)
        o_columns.nueva("DIVISION", _("Division"), 60, align_center=True, edicion=Delegados.LineaTexto(siEntero=True))
        o_columns.nueva("NAME", _("Name"), 280, edicion=Delegados.LineaTextoUTF8())
        o_columns.nueva("ELO", _("Elo"), 50, align_right=True, edicion=Delegados.LineaTexto(siEntero=True))
        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, is_editable=True)
        self.register_grid(self.grid)
        self.grid.setMinimumWidth(self.grid.anchoColumnas() + 20)
        font = Controles.TipoLetra(puntos=Code.configuration.x_pgn_fontpoints)
        self.grid.ponFuente(font)

        self.bt_engines_more = Controles.PB(self, "++ " + _("Engines"), rutina=self.add_engines, plano=False).ponIcono(
            Iconos.Engines()
        )
        self.bt_human_more = Controles.PB(self, "+ " + _("Human"), rutina=self.add_human, plano=False).ponIcono(
            Iconos.Player()
        )
        self.bt_engine_more = Controles.PB(self, "+ " + _("Engine"), rutina=self.add_engine, plano=False).ponIcono(
            Iconos.Engine()
        )

        ly_bt = Colocacion.H().control(self.bt_engines_more).control(self.bt_human_more)
        ly_bt.control(self.bt_engine_more).relleno()
        self.li_lb = []
        for division in range(3):
            lb = Controles.LB(self, "").ponTipoLetra(puntos=14, peso=750).anchoFijo(40).align_center()
            self.li_lb.append(lb)
            ly_bt.control(lb)

        # Config
        lb_resign = Controles.LB(self, "%s (%s): " % (_("Minimum centipawns to assign winner"), "0=%s" % _("Disable")))
        self.ed_resign = Controles.ED(self).tipoInt(league.resign).anchoFijo(30)
        bt_resign = Controles.PB(self, "", rutina=self.borra_resign).ponIcono(Iconos.Reciclar())

        # Draw-plys
        lb_draw_min_ply = Controles.LB(self, "%s (%s): " % (_("Minimum moves to assign draw"), "0=%s" % _("Disable")))
        self.ed_draw_min_ply = Controles.ED(self).ponInt(league.draw_min_ply).anchoFijo(30).align_right()
        # Draw-puntos
        lb_draw_range = Controles.LB(self, _("Maximum centipawns to assign draw") + ": ")
        self.ed_draw_range = Controles.ED(self).tipoInt(league.draw_range).anchoFijo(30)
        bt_draw_range = Controles.PB(self, "", rutina=self.borra_draw_range).ponIcono(Iconos.Reciclar())

        # adjudicator
        self.liMotores = Code.configuration.comboMotoresMultiPV10()
        self.cbJmotor, self.lbJmotor = QTUtil2.comboBoxLB(self, self.liMotores, league.adjudicator, _("Engine"))
        self.edJtiempo = Controles.ED(self).tipoFloat(league.adjudicator_time).anchoFijo(50)
        self.lbJtiempo = Controles.LB2P(self, _("Time in seconds"))
        ly = Colocacion.G()
        ly.controld(self.lbJmotor, 3, 0).control(self.cbJmotor, 3, 1)
        ly.controld(self.lbJtiempo, 4, 0).control(self.edJtiempo, 4, 1)
        self.gbJ = Controles.GB(self, _("Adjudicator"), ly)
        # self.gbJ.setCheckable(True)
        # self.gbJ.setChecked(league.adjudicator_active)

        lb_slow = Controles.LB(self, _("Slow down the movement of pieces") + ": ")
        self.chb_slow = Controles.CHB(self, " ", league.slow_pieces)

        # Times
        minutes, seconds = self.league.time_engine_engine
        lb_minutes = Controles.LB2P(self, _("Total minutes"))
        self.ed_minutes_eng_eng = Controles.ED(self).tipoFloat(minutes).anchoFijo(35)
        self.sb_seconds_eng_eng, lb_seconds = QTUtil2.spinBoxLB(
            self, seconds, -999, 999, maxTam=35, etiqueta=_("Seconds added per move")
        )

        ly = Colocacion.H().control(lb_minutes).control(self.ed_minutes_eng_eng)
        ly.control(lb_seconds).control(self.sb_seconds_eng_eng)
        gb_time_eng_eng = Controles.GB(self, _("Engine vs engine"), ly)

        minutes, seconds = self.league.time_engine_human
        lb_minutes = Controles.LB2P(self, _("Total minutes"))
        self.ed_minutes_eng_human = Controles.ED(self).tipoFloat(minutes).anchoFijo(35)
        self.sb_seconds_eng_human, lb_seconds = QTUtil2.spinBoxLB(
            self, seconds, -999, 999, maxTam=35, etiqueta=_("Seconds added per move")
        )
        ly = Colocacion.H().control(lb_minutes).control(self.ed_minutes_eng_human)
        ly.control(lb_seconds).control(self.sb_seconds_eng_human)

        gb_time_eng_human = Controles.GB(self, _("Engine vs human"), ly)

        self.sb_migration, lb_migration = QTUtil2.spinBoxLB(
            self, self.league.migration, 1, 5, maxTam=35, etiqueta=_("Opponents who change divisions every season")
        )

        ly_options = Colocacion.G().margen(20)
        ly_res = Colocacion.H().control(self.ed_resign).control(bt_resign).relleno()
        ly_dra = Colocacion.H().control(self.ed_draw_range).control(bt_draw_range).relleno()
        ly_options.controld(lb_resign, 0, 0).otro(ly_res, 0, 1)
        ly_options.controld(lb_draw_range, 1, 0).otro(ly_dra, 1, 1)
        ly_options.controld(lb_draw_min_ply, 2, 0).control(self.ed_draw_min_ply, 2, 1)
        ly_options.control(self.gbJ, 3, 0, 2, 2)
        ly_options.controld(lb_slow, 5, 0).control(self.chb_slow, 5, 1)
        ly_options.control(gb_time_eng_eng, 6, 0, 1, 2)
        ly_options.control(gb_time_eng_human, 7, 0, 1, 2)
        ly_options.controld(lb_migration, 8, 0).control(self.sb_migration, 8, 1)

        layout_v = Colocacion.V().otro(ly_bt).control(self.grid)

        font = Controles.TipoLetra(puntos=Code.configuration.x_menu_points)

        gb_conf = Controles.GB(self, _("Options"), ly_options)
        self.gb_eng = Controles.GB(self, _("Players"), layout_v)

        if not self.league.is_editable():
            self.gb_eng.setVisible(False)

        gb_conf.setFont(font)
        self.gb_eng.setFont(font)
        layout_h = Colocacion.H().control(gb_conf).control(self.gb_eng).margen(8)

        # Layout
        layout = Colocacion.V().control(self.tb).otro(layout_h).relleno().margen(3)
        self.setLayout(layout)

        self.restore_video(siTam=True, anchoDefecto=1032)

        self.set_num_elements()
        self.sort_list()

    def remove_seasons(self):
        if QTUtil2.pregunta(self, _("Do you want to remove all results of all seasons?")):
            self.remove_seasons_delayed = True
            self.gb_eng.setVisible(True)
            self.tb.setAccionVisible(self.remove_seasons, False)

    def set_num_elements(self):
        li = self.league.list_numdivision()
        for division in range(3):
            num = li[division]
            lb = self.li_lb[division]
            lb.set_text(str(num))
            if num < 10:
                foreground = "gray"
            elif num == 10:
                foreground = "green"
            else:
                foreground = "red"
            lb.setStyleSheet("border: 1px solid LightSlateGray; background: %s;" % foreground)

    def sort_list(self):
        self.league.sort_list(self.sortby)
        self.grid.refresh()
        self.set_num_elements()

    def add_engine(self):
        cm = self.select_engines.menu(self)
        if cm:
            if not self.league.exist_engine(cm):
                self.league.add_engine(cm)
                self.sort_list()

    def add_engines(self):
        li_selected = self.select_engines.select_group(self, self.league.list_engines())
        if li_selected is not None:
            self.league.set_engines(li_selected)
            self.sort_list()

    def name_elo(self, title, icon, name, elo):
        form = FormLayout.FormLayout(self, title, icon, anchoMinimo=240)

        form.separador()

        form.edit(_("Name"), name)
        form.separador()
        form.spinbox(_("Elo"), 1, 4000, 60, elo)
        form.separador()
        resp = form.run()
        if resp:
            accion, li_resp = resp
            name, elo = li_resp
            return name, elo

    def add_human(self):
        player = Code.configuration.x_player
        if self.league.exist_name(player):
            player = ""

        resp = self.name_elo(_("Human"), Iconos.Player(), player, 1200)
        if resp:
            name, elo = resp
            self.league.add_human(name, elo)
            self.sort_list()

    def save(self):
        self.league.resign = self.ed_resign.textoInt()
        self.league.draw_min_ply = self.ed_draw_min_ply.textoInt()
        self.league.draw_range = self.ed_draw_range.textoInt()
        self.league.adjudicator = self.cbJmotor.valor()
        self.league.adjudicator_time = self.edJtiempo.textoFloat()
        self.league.adjudicator_active = True  # ☺self.gbJ.isChecked()
        self.league.slow_pieces = self.chb_slow.valor()
        self.league.time_engine_engine = (self.ed_minutes_eng_eng.textoFloat(), self.sb_seconds_eng_eng.valor())
        self.league.time_engine_human = (self.ed_minutes_eng_human.textoFloat(), self.sb_seconds_eng_human.valor())
        self.league.migration = self.sb_migration.valor()
        self.league.save()
        if self.remove_seasons_delayed:
            self.league.remove_seasons()
            Util.remove_file(self.league.path() + ".work")
        self.accept()

    def cancel(self):
        self.reject()

    def borra_resign(self):
        previo = self.ed_resign.textoInt()
        self.ed_resign.tipoInt(0 if previo else 350)

    def borra_draw_range(self):
        previo = self.ed_draw_range.textoInt()
        self.ed_draw_range.tipoInt(0 if previo else 10)
        self.ed_draw_min_ply.tipoInt(0 if previo else 50)

    @staticmethod
    def read():
        li = []
        carpeta = Code.configuration.folder_leagues()
        for entry in Util.listdir(carpeta):
            filename = entry.name
            if filename.lower().endswith(".league"):
                st = entry.stat()
                li.append((filename, st.st_ctime, st.st_mtime))

        li = sorted(li, key=lambda x: x[2], reverse=True)  # por ultima modificación y al reves
        return li

    def nom_league_pos(self, row):
        return self.list_leagues[row][0][:-4]

    def grid_num_datos(self, grid):
        return self.league.num_opponents()

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        if key == "ROW":
            return str(row + 1)
        opponent = self.league.opponent(row)
        if key == "DIVISION":
            return str(opponent.initialdivision + 1)
        if key == "ELO":
            return str(opponent.elo())
        return opponent.name()

    def grid_setvalue(self, grid, row, o_column, value):
        opponent: Leagues.Opponent = self.league.opponent(row)
        key = o_column.key
        if key == "ELO":
            if value.isdigit():
                elo = int(value)
                if 0 < elo < 4001:
                    opponent.set_elo(elo)
                    self.sort_list()
                    return
        if key == "NAME":
            name = value.strip()
            if name:
                opponent.set_name(name)
            else:
                if QTUtil2.pregunta(self, _("Do you want to remove?")):
                    self.league.remove_opponent(row)
                    self.sort_list()
                    return
        if key == "DIVISION":
            dv = int(value)
            if dv in (1, 2, 3):
                opponent.set_initialdivision(dv - 1)
                self.sort_list()
                return

        self.grid.refresh()

    def grid_color_fondo(self, grid, row, col):
        opponent: Leagues.Opponent = self.league.opponent(row)
        return self.li_colors[opponent.initialdivision]

    def grid_bold(self, grid, row, column):
        opponent: Leagues.Opponent = self.league.opponent(row)
        return opponent.is_human()

    def grid_tecla_control(self, grid, k, is_shift, is_control, is_alt):
        if k in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
            row = self.grid.recno()
            if row >= 0:
                self.league.remove_opponent(row)
                self.sort_list()
                return False
        return True

    def grid_doubleclick_header(self, grid, col):
        key = col.key
        if key == "DIVISION":
            self.sortby = "division"
        elif key == "ELO":
            self.sortby = "elo"
        self.sort_list()

    def terminar(self):
        self.save_video()
        self.accept()
