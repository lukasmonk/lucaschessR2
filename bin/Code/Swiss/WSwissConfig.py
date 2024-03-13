from PySide2 import QtCore

import Code
from Code import Util
from Code.Engines import SelectEngines, WConfEngines
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.Swiss import Swiss


class WSwissConfig(LCDialog.LCDialog):

    def __init__(self, w_parent, swiss: Swiss.Swiss):

        titulo = swiss.name()
        icono = Iconos.Swiss()
        extparam = "swissconfiguration"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        self.swiss: Swiss.Swiss = swiss
        self.remove_seasons_delayed = False

        self.sortby = "elo"

        color_1 = Code.dic_qcolors["WLEAGUECONFIG_3"]
        color_2 = Code.dic_qcolors["WLEAGUECONFIG_1"]
        self.li_colors = [color_1, color_2]

        self.select_engines = SelectEngines.SelectEngines(w_parent)

        li_acciones = [
            (_("Save"), Iconos.GrabarFichero(), self.save),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancel),
            None,
            (_("External engines"), Iconos.ConfEngines(), self.engines),
        ]
        if not self.swiss.is_editable():
            li_acciones.append(None)
            li_acciones.append((_("Remove all seasons"), Iconos.Borrar(), self.remove_seasons))

        self.tb = QTVarios.LCTB(self, li_acciones)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("ROW", "", 15, align_center=True)
        o_columns.nueva("NAME", _("Name"), 280, edicion=Delegados.LineaTextoUTF8())
        o_columns.nueva("ELO", _("Elo"), 50, align_right=True, edicion=Delegados.LineaTexto(siEntero=True))
        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, is_editable=True)
        self.register_grid(self.grid)
        self.grid.setMinimumWidth(self.grid.anchoColumnas() + 20)

        self.bt_engines_more = Controles.PB(self, "++ " + _("Engines"), rutina=self.add_engines, plano=False).ponIcono(
            Iconos.Engines()
        )
        self.bt_engines_more.set_pordefecto(False)

        self.bt_human_more = Controles.PB(self, "+ " + _("Human"), rutina=self.add_human, plano=False).ponIcono(
            Iconos.Player()
        )
        self.bt_human_more.set_pordefecto(False)

        self.bt_engine_more = Controles.PB(self, "+ " + _("Engine"), rutina=self.add_engine, plano=False).ponIcono(
            Iconos.Engine()
        )
        self.bt_engine_more.set_pordefecto(False)

        self.lb_num_opponents = Controles.LB(self, "").set_font_type(puntos=12, peso=750).align_center()
        ly_bt0 = Colocacion.H().control(self.bt_engines_more).control(self.bt_human_more)
        ly_bt0.control(self.bt_engine_more).relleno().control(self.lb_num_opponents)

        # Config
        lb_resign = Controles.LB(self, "%s (%s): " % (_("Minimum centipawns to assign winner"), "0=%s" % _("Disable")))
        self.ed_resign = Controles.ED(self).tipoInt(swiss.resign).anchoFijo(30)
        bt_resign = Controles.PB(self, "", rutina=self.borra_resign).ponIcono(Iconos.Reciclar())

        # Draw-plys
        lb_draw_min_ply = Controles.LB(self,
                                       "%s (%s): " % (_("Minimum movements to assign draw"), "0=%s" % _("Disable")))
        self.ed_draw_min_ply = Controles.ED(self).ponInt(swiss.draw_min_ply).anchoFijo(30).align_right()
        # Draw-puntos
        lb_draw_range = Controles.LB(self, _("Maximum centipawns to assign draw") + ": ")
        self.ed_draw_range = Controles.ED(self).tipoInt(swiss.draw_range).anchoFijo(30)
        bt_draw_range = Controles.PB(self, "", rutina=self.borra_draw_range).ponIcono(Iconos.Reciclar())

        # adjudicator
        self.list_engines = Code.configuration.combo_engines_multipv10()
        self.cb_jmotor, self.lb_jmotor = QTUtil2.combobox_lb(self, self.list_engines, swiss.adjudicator, _("Engine"))
        self.ed_jtiempo = Controles.ED(self).tipoFloat(swiss.adjudicator_time).anchoFijo(50)
        self.lb_jtiempo = Controles.LB2P(self, _("Time in seconds"))
        ly = Colocacion.G()
        ly.controld(self.lb_jmotor, 3, 0).control(self.cb_jmotor, 3, 1)
        ly.controld(self.lb_jtiempo, 4, 0).control(self.ed_jtiempo, 4, 1)
        self.gb_j = Controles.GB(self, _("Adjudicator"), ly)

        lb_slow = Controles.LB(self, _("Slow down the movement of pieces") + ": ")
        self.chb_slow = Controles.CHB(self, " ", swiss.slow_pieces)

        # Times
        minutes, seconds = self.swiss.time_engine_engine
        lb_minutes = Controles.LB2P(self, _("Total minutes"))
        self.ed_minutes_eng_eng = Controles.ED(self).tipoFloat(minutes).anchoFijo(35)
        self.sb_seconds_eng_eng, lb_seconds = QTUtil2.spinbox_lb(
            self, seconds, -999, 999, max_width=40, etiqueta=_("Seconds added per move")
        )

        ly = Colocacion.H().control(lb_minutes).control(self.ed_minutes_eng_eng)
        ly.control(lb_seconds).control(self.sb_seconds_eng_eng)
        gb_time_eng_eng = Controles.GB(self, _("Engine vs engine"), ly)

        minutes, seconds = self.swiss.time_engine_human
        lb_minutes = Controles.LB2P(self, _("Total minutes"))
        self.ed_minutes_eng_human = Controles.ED(self).tipoFloat(minutes).anchoFijo(65)
        self.sb_seconds_eng_human, lb_seconds = QTUtil2.spinbox_lb(
            self, seconds, -999, 999, max_width=35, etiqueta=_("Seconds added per move")
        )
        ly = Colocacion.H().control(lb_minutes).control(self.ed_minutes_eng_human)
        ly.control(lb_seconds).control(self.sb_seconds_eng_human)

        gb_time_eng_human = Controles.GB(self, _("Engine vs human"), ly)

        lb_score_win = Controles.LB2P(self, _("Win"))
        lb_score_draw = Controles.LB2P(self, _("Draw"))
        lb_score_lost = Controles.LB2P(self, _("Loss"))
        lb_score_byes = Controles.LB2P(self, _("Byes"))
        self.ed_score_win = Controles.ED(self).ponFloat(self.swiss.score_win).anchoFijo(40).align_right()
        self.ed_score_draw = Controles.ED(self).ponFloat(self.swiss.score_draw).anchoFijo(40).align_right()
        self.ed_score_lost = Controles.ED(self).ponFloat(self.swiss.score_lost).anchoFijo(40).align_right()
        self.ed_score_byes = Controles.ED(self).ponFloat(self.swiss.score_byes).anchoFijo(40).align_right()
        ly_score = Colocacion.H().relleno()
        sep = 6
        ly_score.control(lb_score_win).espacio(-sep).control(self.ed_score_win).espacio(sep)
        ly_score.control(lb_score_draw).espacio(-sep).control(self.ed_score_draw).espacio(sep)
        ly_score.control(lb_score_lost).espacio(-sep).control(self.ed_score_lost).espacio(sep)
        ly_score.control(lb_score_byes).espacio(-sep).control(self.ed_score_byes)
        ly_score.relleno()
        self.gb_score = Controles.GB(self, _("System score"), ly_score)

        lb_matchdays = Controles.LB2P(self, _("Rounds"))
        self.ed_matchdays = Controles.ED(self).ponInt(self.swiss.num_matchdays).anchoFijo(40).align_right()

        ly_options = Colocacion.G().margen(20)
        ly_res = Colocacion.H().control(self.ed_resign).control(bt_resign).relleno()
        ly_dra = Colocacion.H().control(self.ed_draw_range).control(bt_draw_range).relleno()
        ly_options.controld(lb_resign, 0, 0).otro(ly_res, 0, 1)
        ly_options.controld(lb_draw_range, 1, 0).otro(ly_dra, 1, 1)
        ly_options.controld(lb_draw_min_ply, 2, 0).control(self.ed_draw_min_ply, 2, 1)
        ly_options.control(self.gb_j, 3, 0, 2, 2)
        ly_options.controld(lb_slow, 5, 0).control(self.chb_slow, 5, 1)
        ly_options.control(gb_time_eng_eng, 6, 0, 1, 2)
        ly_options.control(gb_time_eng_human, 7, 0, 1, 2)
        ly_options.control(self.gb_score, 9, 0, 1, 2)
        ly_options.controld(lb_matchdays, 11, 0).control(self.ed_matchdays, 11, 1)

        layout_v = Colocacion.V().otro(ly_bt0).control(self.grid)

        font = Controles.FontType(puntos=Code.configuration.x_font_points)

        gb_conf = Controles.GB(self, _("Options"), ly_options)
        self.gb_eng = Controles.GB(self, _("Players"), layout_v)

        if not self.swiss.is_editable():
            self.gb_eng.setVisible(False)
            # self.gb_score.setEnabled(False)

        gb_conf.setFont(font)
        self.gb_eng.setFont(font)
        layout_h = Colocacion.H().control(gb_conf).control(self.gb_eng).margen(8)

        # Layout
        layout = Colocacion.V().control(self.tb).otro(layout_h).relleno().margen(3)
        self.setLayout(layout)

        self.restore_video(siTam=True, anchoDefecto=1032)

        self.sort_list()

        previous = self.ed_resign
        previous.setFocus()
        for widget in (bt_resign, self.ed_draw_range, bt_draw_range, self.ed_draw_min_ply,
                       self.cb_jmotor, self.ed_jtiempo,
                       self.ed_minutes_eng_eng, self.sb_seconds_eng_eng,
                       self.ed_minutes_eng_human, self.sb_seconds_eng_human,
                       self.ed_score_win, self.ed_score_draw, self.ed_score_lost, self.ed_score_byes,
                       self.ed_matchdays):
            self.setTabOrder(previous, widget)
            previous = widget

        self.show_num_opponents()

    def remove_seasons(self):
        if QTUtil2.pregunta(self, _("Do you want to remove all results of all seasons?")):
            self.remove_seasons_delayed = True
            self.gb_eng.setVisible(True)
            self.tb.set_action_visible(self.remove_seasons, False)
            self.gb_score.setEnabled(True)

    def sort_list(self):
        self.swiss.sort_list_opponents()
        self.grid.refresh()

    def add_engine(self):
        cm = self.select_engines.menu(self)
        if cm:
            if not self.swiss.exist_engine(cm):
                self.swiss.add_engine(cm)
                self.sort_list()
                self.change_num_opponents()

    def add_engines(self):
        li_selected = self.select_engines.select_group(self, self.swiss.list_engines())
        if li_selected is not None:
            self.swiss.set_engines(li_selected)
            self.sort_list()
            self.change_num_opponents()

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
        if self.swiss.exist_name(player):
            player = ""

        resp = self.name_elo(_("Human"), Iconos.Player(), player, 1200)
        if resp:
            name, elo = resp
            self.swiss.add_human(name, elo)
            self.sort_list()

            self.change_num_opponents()

    def save(self):
        self.swiss.resign = self.ed_resign.textoInt()
        self.swiss.draw_min_ply = self.ed_draw_min_ply.textoInt()
        self.swiss.draw_range = self.ed_draw_range.textoInt()
        self.swiss.adjudicator = self.cb_jmotor.valor()
        self.swiss.adjudicator_time = self.ed_jtiempo.textoFloat()
        self.swiss.adjudicator_active = True
        self.swiss.slow_pieces = self.chb_slow.valor()
        mnt = self.ed_minutes_eng_eng.textoFloat()
        if mnt <= 0:
            mnt = 3.0
        self.swiss.time_engine_engine = (mnt, self.sb_seconds_eng_eng.valor())
        self.swiss.time_engine_human = (self.ed_minutes_eng_human.textoFloat(), self.sb_seconds_eng_human.valor())
        self.swiss.score_win = self.ed_score_win.textoFloat()
        self.swiss.score_draw = self.ed_score_draw.textoFloat()
        self.swiss.score_lost = self.ed_score_lost.textoFloat()
        self.swiss.score_byes = self.ed_score_byes.textoFloat()
        self.swiss.num_matchdays = self.ed_matchdays.textoInt()
        self.swiss.save()
        if self.remove_seasons_delayed:
            self.swiss.remove_seasons()
            Util.remove_file(self.swiss.path() + ".work")

        self.save_video()
        self.accept()

    def cancel(self):
        self.save_video()
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
        carpeta = Code.configuration.folder_Swisses()
        for entry in Util.listdir(carpeta):
            filename = entry.name
            if filename.lower().endswith(".swiss"):
                st = entry.stat()
                li.append((filename, st.st_ctime, st.st_mtime))

        li = sorted(li, key=lambda x: x[2], reverse=True)  # por ultima modificación y al reves
        return li

    def nom_league_pos(self, row):
        return self.list_Swisses[row][0][:-4]

    def grid_num_datos(self, grid):
        return self.swiss.num_opponents()

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        if key == "ROW":
            return str(row + 1)
        opponent = self.swiss.opponent(row)
        if key == "ELO":
            return str(opponent.get_start_elo())
        return opponent.name()

    def grid_setvalue(self, grid, row, o_column, value):
        opponent: Swiss.Opponent = self.swiss.opponent(row)
        key = o_column.key
        if key == "ELO":
            if value.isdigit():
                elo = int(value)
                if 0 < elo < 4001:
                    opponent.set_elo_start(elo)
                    self.sort_list()
                    return
        if key == "NAME":
            name = value.strip()
            if name:
                opponent.set_name(name)
            else:
                if QTUtil2.pregunta(self, _("Do you want to remove?")):
                    self.swiss.remove_opponent(row)
                    self.sort_list()
                    return

        self.grid.refresh()

    def grid_color_fondo(self, grid, row, col):
        return self.li_colors[row % 2]

    def grid_bold(self, grid, row, column):
        opponent: Swiss.Opponent = self.swiss.opponent(row)
        return opponent.is_human()

    def grid_tecla_control(self, grid, k, is_shift, is_control, is_alt):
        if k in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
            row = self.grid.recno()
            if row >= 0:
                self.swiss.remove_opponent(row)
                self.change_num_opponents()
                self.sort_list()
                return False
        return True

    # def grid_doubleclick_header(self, grid, col):
    #     return
    #     key = col.key
    #     elif key == "ELO":
    #         self.sortby = "elo"
    #     self.sort_list()

    def terminar(self):
        self.save_video()
        self.accept()

    def engines(self):
        w = WConfEngines.WConfEngines(self)
        w.exec_()
        self.select_engines.redo_external_engines()

    def change_num_opponents(self):
        n_opponents = self.swiss.num_opponents()
        num_journeys = Swiss.num_matchesdays(n_opponents)
        self.lb_num_opponents.set_text(f"{n_opponents}")
        self.ed_matchdays.set_text(str(num_journeys))

    def show_num_opponents(self):
        if self.swiss.num_matchdays == 0:
            self.change_num_opponents()
        else:
            n_opponents = self.swiss.num_opponents()
            self.lb_num_opponents.set_text(f"{n_opponents}")


