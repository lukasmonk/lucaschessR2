import os
import shutil

from PySide2 import QtSvg, QtCore

import Code
from Code import Util
from Code.Base import Game
from Code.Databases import DBgames
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import WindowSavePGN
from Code.Washing import Washing


class WWashing(LCDialog.LCDialog):
    def __init__(self, procesador):

        self.procesador = procesador
        self.configuration = procesador.configuration

        self.siPlay = False
        self.wreload = False

        self.dbwashing = Washing.DBWashing(procesador.configuration)
        self.washing = self.dbwashing.washing
        eng = self.washing.last_engine(procesador.configuration)
        finished = eng is None

        owner = procesador.main_window
        titulo = _("The Washing Machine")
        extparam = "washing"
        icono = Iconos.WashingMachine()
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        # Toolbar
        tb = QTVarios.LCTB(self)
        tb.new(_("Close"), Iconos.MainMenu(), self.terminar)
        tb.new(_("File"), Iconos.Recuperar(), self.file)
        if not finished:
            tb.new(_("Play"), Iconos.Play(), self.play)

        # Tab current
        ia = self.washing.index_average()

        c_create = "#f9e7e7"
        c_tactics = "#df8f87"
        c_reinit = "#8aa678"
        c_des = "#e4e4e4"
        c_hab = "#9dde67"
        c_act = "#dd2a2b"
        c_ia = "#cccdea"

        li_ia = ("#ffed00", "#ff8e00", "#29b41b", "#1174ff", "#bc01d9", "#eb0000")
        d_ia = li_ia[int(eng.index() / (100.0 / 6.0)) % 6]
        state = eng.state
        wsvg = QtSvg.QSvgWidget()
        with open(Code.path_resource("IntFiles/Svg", "washing-machine.svg")) as f:
            svg = f.read()
            d_create = c_des
            d_tactics = c_des
            d_reinit = c_des
            ctac = ""
            if state == Washing.CREATING:
                d_create = c_act
            elif state == Washing.REPLAY:
                d_create = c_hab
                d_tactics = c_hab
                d_reinit = c_act
            elif state == Washing.TACTICS:
                d_create = c_hab
                d_tactics = c_act
                ctac = str(eng.numTactics())
            svg = svg.replace(c_create, d_create)
            svg = svg.replace(c_tactics, d_tactics)
            svg = svg.replace(c_reinit, d_reinit)
            svg = svg.replace("TAC", ctac)
            svg = svg.replace(c_ia, d_ia)
            wsvg.load(QtCore.QByteArray(svg.encode("utf-8")))
        p = 1.0
        wsvg.setFixedSize(287.79 * p, 398.83 * p)

        if finished:
            plant = '<tr><td align="right">%s:</td><td><b>%s</b></td></tr>'
            hints, times, games = self.washing.totals()
            nEngines = self.washing.num_engines()
            html = '<h2><center>%s: %d %s</center></h2><br><table cellpadding="4">' % (
                _("Finished"),
                nEngines,
                _("Engines"),
            )
            for x in range(3):
                html += plant
            html += "</table>"

            html = html % (
                _("Hints"),
                "%d (%0.02f)" % (hints, hints * 1.0 / nEngines),
                _("Repetitions"),
                "%d (%0.02f)" % (games, games * 1.0 / nEngines),
                _("Time"),
                "%s (%s)" % (Util.secs2str(times), Util.secs2str(int(times / nEngines))),
            )

        else:
            plant = '<tr><td align="right">%s:</td><td><b>%s</b></td></tr>'
            plantverde = '<tr><td align="right">%s:</td><td style="color:green;"><b>%s</b></td></tr>'
            html = '<h2><center>%s %d/%d</center></h2><br><table cellpadding="4">'
            for x in range(8):
                html += plantverde if x == 2 else plant
            html += "</table>"
            html = html % (
                _("Washing"),
                self.washing.num_engines(),
                self.washing.total_engines(procesador.configuration),
                _("Engine"),
                eng.name,
                _("Elo"),
                eng.elo,
                "<b>%s</b>" % _("Task"),
                eng.lbState(),
                _("Color"),
                _("White") if eng.color else _("Black"),
                _("Hints"),
                "%d/%d" % (eng.hints_current, eng.hints),
                _("Repetitions"),
                eng.games,
                _("Time"),
                eng.lbTime(),
                _("Index"),
                eng.cindex(),
            )

        lbTxt = Controles.LB(self, html).set_font_type(puntos=12)
        lbIdx = Controles.LB(self, "%0.2f%%" % ia).align_center().set_font_type(puntos=36, peso=700)

        ly0 = Colocacion.V().control(wsvg).relleno(1)
        ly1 = Colocacion.V().espacio(20).control(lbTxt).espacio(20).control(lbIdx).relleno(1)
        ly2 = Colocacion.H().otro(ly0).otro(ly1)
        gbCurrent = Controles.GB(self, "", ly2)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("STEP", _("Washing"), 50, align_center=True)
        o_columns.nueva("ENGINE", _("Engine"), 170, align_center=True)
        o_columns.nueva("ELO", _("Elo"), 50, align_center=True)
        o_columns.nueva("COLOR", _("Color"), 70, align_center=True)
        o_columns.nueva("STATE", _("State"), 90, align_center=True)
        o_columns.nueva("HINTS", _("Hints"), 60, align_center=True)
        o_columns.nueva("GAMES", _("Repetitions"), 80, align_center=True)
        o_columns.nueva("TIME", _("Time"), 60, align_center=True)
        o_columns.nueva("DATE", _("Date"), 120, align_center=True)
        o_columns.nueva("INDEX", _("Index"), 60, align_center=True)

        self.grid = grid = Grid.Grid(self, o_columns, siSelecFilas=True)
        n_ancho_pgn = self.grid.anchoColumnas() + 20
        self.grid.setMinimumWidth(n_ancho_pgn)
        self.register_grid(grid)

        ly0 = Colocacion.V().control(self.grid)
        gb_datos = Controles.GB(self, "", ly0)

        self.tab = Controles.Tab()
        self.tab.new_tab(gbCurrent, _("Current"))
        self.tab.new_tab(gb_datos, _("Data"))

        # Colocamos ---------------------------------------------------------------
        ly = Colocacion.V().control(tb).control(self.tab)
        self.setLayout(ly)

        self.restore_video(siTam=True, anchoDefecto=n_ancho_pgn)

    def terminar(self):
        self.save_video()
        self.reject()

    def file(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion("saveas", _("Save a copy"), Iconos.GrabarComo())
        menu.separador()
        menu.opcion("restorefrom", _("Restore from"), Iconos.Recuperar())
        menu.separador()
        submenu = menu.submenu(_("Restart with tactics taken from"), Iconos.Nuevo())
        submenu.opcion("new_UNED", _("UNED chess school"), Iconos.Uned())
        submenu.separador()
        submenu.opcion("new_UWE", _("Uwe Auerswald"), Iconos.Uwe())
        submenu.separador()
        submenu.opcion("new_SM", _("Singular moves"), Iconos.Singular())
        menu.separador()
        submenu = menu.submenu(_("Export to"), Iconos.DatabaseMas())
        submenu.opcion("save_pgn", _("A PGN file"), Iconos.FichPGN())
        submenu.separador()
        menuDB = submenu.submenu(_("Database"), Iconos.DatabaseMas())
        QTVarios.menuDB(menuDB, self.configuration, True, indicador_previo="dbf_")  # , remove_autosave=True)
        submenu.separador()

        resp = menu.lanza()
        if resp is None:
            return
        if resp == "saveas":
            li_gen = [(None, None)]
            config = FormLayout.Editbox(_("Name"), ancho=160)
            li_gen.append((config, ""))

            resultado = FormLayout.fedit(li_gen, title=_("Name"), parent=self, icon=Iconos.GrabarComo())
            if resultado:
                accion, li_resp = resultado
                fich = name = li_resp[0]
                if name.lower()[-4:] != ".wsm":
                    fich += ".wsm"
                path = Util.opj(self.configuration.carpeta_results, fich)
                ok = True
                if Util.exist_file(path):
                    ok = QTUtil2.pregunta(
                        self,
                        _X(_("The file %1 already exists, what do you want to do?"), fich),
                        label_yes=_("Overwrite"),
                        label_no=_("Cancel"),
                    )
                if ok:
                    shutil.copy(self.dbwashing.file, path)
        elif resp == "restorefrom":
            li = []
            for fich in os.listdir(self.configuration.carpeta_results):
                if fich.endswith(".wsm") and fich != self.dbwashing.filename:
                    li.append(fich[:-4])
            if not li:
                QTUtil2.message_bold(self, _("There is no file"))
                return
            menu = QTVarios.LCMenu(self)
            for fich in li:
                menu.opcion(fich, fich, Iconos.PuntoRojo())
            resp = menu.lanza()
            if resp:
                if QTUtil2.pregunta(
                        self, "%s\n%s" % (_("Current data will be removed and overwritten."), _("Are you sure?"))
                ):
                    shutil.copy(Util.opj(self.configuration.carpeta_results, resp + ".wsm"), self.dbwashing.file)
                    self.wreload = True
                    self.save_video()
                    self.accept()
        elif resp.startswith("new_"):
            tactic = resp[4:]
            if QTUtil2.pregunta(
                    self, "%s\n%s" % (_("Current data will be removed and overwritten."), _("Are you sure?"))
            ):
                self.dbwashing.new(tactic)
                self.wreload = True
                self.save_video()
                self.accept()

        elif resp.startswith("save_") or resp.startswith("dbf_"):

            def other_pc():
                for engine in self.washing.liEngines:
                    if engine.state == Washing.ENDED:
                        game = self.dbwashing.restoreGame(engine)
                        pc = Game.Game()
                        pc.assign_other_game(game)
                        dt = engine.date if engine.date else Util.today()
                        if engine.color:
                            white = self.configuration.x_player
                            black = engine.name
                            result = "1-0"
                            whiteelo = str(self.configuration.x_elo)
                            blackelo = engine.elo
                        else:
                            black = self.configuration.x_player
                            white = engine.name
                            result = "0-1"
                            blackelo = str(self.configuration.x_elo)
                            whiteelo = engine.elo
                        tags = [
                            ["Site", "Lucas Chess"],
                            ["Event", _("The Washing Machine")],
                            ["Date", "%d.%d.%d" % (dt.year, dt.month, dt.day)],
                            ["White", white],
                            ["Black", black],
                            ["WhiteElo", whiteelo],
                            ["BlackElo", blackelo],
                            ["Result", result],
                        ]
                        ap = game.opening
                        if ap:
                            tags.append(["ECO", ap.eco])
                            tags.append(["Opening", ap.tr_name])
                        pc.set_tags(tags)
                        yield pc

            if resp.startswith("dbf_"):
                database = resp[4:]
                db = DBgames.DBgames(database)
                me = QTUtil2.waiting_message.start(self, _("Saving..."))
                n = 0
                for pc in other_pc():
                    db.insert(pc)
                    n += 1
                me.final()
                db.close()
                if n == 0:
                    QTUtil2.message_bold(self, _("There are no games to be saved"))
                else:
                    QTUtil2.message_bold(self, _X(_("Saved to %1"), database))

            else:
                w = WindowSavePGN.WSaveVarios(self, self.configuration)
                if w.exec_():
                    ws = WindowSavePGN.FileSavePGN(self, w.dic_result)
                    t = 0
                    if ws.open():
                        for n, pc in enumerate(other_pc()):
                            if n or not ws.is_new:
                                ws.write("\n\n")
                            ws.write(pc.pgn())
                            t += 1
                        ws.close()
                        if t == 0:
                            QTUtil2.message_bold(self, _("There are no games to be saved"))
                    ws.um_final(t > 0)

    def grid_num_datos(self, grid):
        return self.washing.num_engines()

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        if col == "STEP":
            return str(row + 1)
        engine = self.washing.liEngines[row]
        if col == "ENGINE":
            return engine.name
        if col == "ELO":
            return str(engine.elo)
        if col == "STATE":
            return engine.lbState()
        if col == "COLOR":
            return _("White") if engine.color else _("Black")
        if col == "HINTS":
            return str(engine.hints)
        if col == "GAMES":
            return str(engine.games)
        if col == "TIME":
            return engine.lbTime()
        if col == "DATE":
            return engine.cdate()
        if col == "INDEX":
            return engine.cindex()

    def play(self):
        self.siPlay = True
        self.save_video()
        self.accept()


def windowWashing(procesador):
    while True:
        w = WWashing(procesador)
        if w.exec_():
            if w.wreload:
                continue
            return w.siPlay
        return False
