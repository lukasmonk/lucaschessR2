import time

from Code import Manager
from Code import Util
from Code.Base import Game, Position
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_CONFIG,
    TB_HELP,
    TB_NEXT,
    TB_UTILITIES,
    TB_COMMENTS,
    GT_OPENING_LINES,
    TOP_RIGHT,
)
from Code.Openings import OpeningLines, ManagerOPL
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2


class ManagerOpeningLinesPositions(ManagerOPL.ManagerOpeningLines):
    def start(self, pathFichero):
        self.pathFichero = pathFichero
        dbop = OpeningLines.Opening(pathFichero)
        self.reinicio(dbop)

    def reinicio(self, dbop):
        self.dbop = dbop
        self.game_type = GT_OPENING_LINES

        self.training = self.dbop.training()
        self.li_trainPositions = self.training["LITRAINPOSITIONS"]
        self.pos_active = self.training.get("POS_TRAINPOSITIONS", 0)
        if self.pos_active >= len(self.li_trainPositions):
            self.pos_active = 0
        self.trposition = self.li_trainPositions[self.pos_active]

        self.tm = 0
        for game_info in self.li_trainPositions:
            for tr in game_info["TRIES"]:
                self.tm += tr["TIME"]

        self.liMensBasic = ["%s: %d/%d" % (_("Movement"), self.pos_active + 1, len(self.li_trainPositions))]

        self.siAyuda = False
        self.with_automatic_jump = self.training.get("AUTOJUMP_TRAINPOSITIONS", True)

        cp = Position.Position()
        cp.read_fen(self.trposition["FENM2"] + " 0 1")

        self.game = Game.Game(first_position=cp)

        self.hints = 9999  # Para que analice sin problemas

        self.is_human_side_white = self.training["COLOR"] == "WHITE"
        self.is_engine_side_white = not self.is_human_side_white

        self.dic_comments = self.dbop.dic_fen_comments()

        self.tb_with_comments([TB_CLOSE, TB_HELP, TB_CONFIG])
        self.main_window.active_game(True, False)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(cp)
        self.show_side_indicator(True)
        self.remove_hints()
        self.put_pieces_bottom(self.is_human_side_white)
        self.pgn_refresh(True)

        self.show_info_extra()

        self.state = ST_PLAYING

        self.check_boards_setposition()

        self.errores = 0
        self.ini_time = time.time()
        self.show_labels()
        self.play_next_move()

    def get_help(self):
        self.siAyuda = True
        self.tb_with_comments([TB_CLOSE, TB_CONFIG])

        self.show_help()
        self.show_labels()

    def show_labels(self):
        li = []
        li.append("%s: %d" % (_("Errors"), self.errores))
        if self.siAyuda:
            li.append(_("Help activated"))
        self.set_label1("\n".join(li))

        tgm = 0
        for tr in self.trposition["TRIES"]:
            tgm += tr["TIME"]

        mas = time.time() - self.ini_time

        mens = "\n" + "\n".join(self.liMensBasic)
        mens += "\n%s:\n    %s %s\n    %s %s" % (
            _("Working time"),
            time.strftime("%H:%M:%S", time.gmtime(tgm + mas)),
            _("Current"),
            time.strftime("%H:%M:%S", time.gmtime(self.tm + mas)),
            _("Total"),
        )

        self.set_label2(mens)

    def posicionTerminada(self):
        tm = time.time() - self.ini_time

        sin_errores = self.errores == 0 and self.siAyuda is False

        dictry = {"DATE": Util.today(), "TIME": tm, "AYUDA": self.siAyuda, "ERRORS": self.errores}
        self.trposition["TRIES"].append(dictry)

        is_finished = False
        if sin_errores:
            self.pos_active += 1
            self.trposition["NOERROR"] += 1
            if self.pos_active >= len(self.li_trainPositions):
                QTUtil2.message(
                    self.main_window,
                    "%s\n\n%s"
                    % (_("Congratulations, goal achieved"), _("Next time you will start from the first position")),
                )
                self.pos_active = 0
                is_finished = True
            self.training["POS_TRAINPOSITIONS"] = self.pos_active

        else:
            self.trposition["NOERROR"] = max(0, self.trposition["NOERROR"] - 1)
            no_error = self.trposition["NOERROR"]
            salto = self.pos_active + 2 ** (no_error + 1) + 1
            num_posics = len(self.li_trainPositions)
            if salto > num_posics:
                salto = num_posics

            li_nuevo = self.li_trainPositions[:]
            del li_nuevo[self.pos_active]
            if salto >= len(li_nuevo):
                li_nuevo.append(self.trposition)
            else:
                li_nuevo.insert(salto, self.trposition)
            self.training["LITRAINPOSITIONS"] = li_nuevo

        self.tb_with_comments([TB_CLOSE, TB_NEXT, TB_CONFIG])

        self.dbop.setTraining(self.training)
        self.state = ST_ENDGAME
        self.show_labels()
        if is_finished:
            self.end_game()
        elif self.with_automatic_jump:
            self.reinicio(self.dbop)

    def show_help(self):
        liMoves = self.trposition["MOVES"]
        for pv in liMoves:
            self.board.show_arrow_mov(pv[:2], pv[2:4], "mt", opacity=0.80)
        QTUtil.refresh_gui()

    def run_action(self, key):
        if key == TB_CLOSE:
            self.end_game()

        elif key == TB_CONFIG:
            base = _("What to do after solving")
            if self.with_automatic_jump:
                li_extra_options = [("lmo_stop", "%s: %s" % (base, _("Stop")), Iconos.PuntoRojo())]
            else:
                li_extra_options = [("lmo_jump", "%s: %s" % (base, _("Jump to the next")), Iconos.PuntoVerde())]

            resp = self.configurar(with_sounds=True, with_change_tutor=False, li_extra_options=li_extra_options)
            if resp in ("lmo_stop", "lmo_jump"):
                self.with_automatic_jump = resp == "lmo_jump"
                self.training["AUTOJUMP_TRAINPOSITIONS"] = self.with_automatic_jump

        elif key == TB_UTILITIES:
            self.utilities()

        elif key == TB_NEXT:
            self.reinicio(self.dbop)

        elif key == TB_HELP:
            self.get_help()

        elif key == TB_COMMENTS:
            self.change_comments()

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def final_x(self):
        return self.end_game()

    def end_game(self):
        self.dbop.close()
        self.procesador.start()
        self.procesador.openings()
        return False

    def play_next_move(self):
        self.show_labels()
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.set_side_indicator(is_white)
        self.refresh()

        self.activate_side(is_white)
        self.human_is_playing = True
        if self.siAyuda:
            self.show_help()

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            self.beep_error()
            return False
        pvSel = from_sq + to_sq + promotion
        lipvObj = self.trposition["MOVES"]

        if not (pvSel in lipvObj):
            self.errores += 1
            mens = "%s: %d" % (_("Error"), self.errores)
            QTUtil2.temporary_message(self.main_window, mens, 1.0, physical_pos=TOP_RIGHT)
            self.show_labels()
            self.beep_error()
            self.sigueHumano()
            return False

        if "LIPV" in self.trposition:
            self.game = Game.Game()
            self.game.read_lipv(self.trposition["LIPV"])
            self.game.assign_opening()
            self.add_coments_all_game()
        else:
            self.move_the_pieces(move.liMovs)
            self.add_move(move, True)
        self.goto_end()
        self.posicionTerminada()
        return True
