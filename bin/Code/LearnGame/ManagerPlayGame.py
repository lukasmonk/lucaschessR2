import copy
import time

from Code import Manager
from Code import Util
from Code.Base import Game, Move
from Code.Base.Constantes import (
    GT_LEARN_PLAY,
    ST_ENDGAME,
    ST_PLAYING,
    RS_WIN_PLAYER,
    RS_WIN_OPPONENT,
    TB_CLOSE,
    TB_REINIT,
    TB_CONFIG,
    TB_CANCEL,
    TB_UTILITIES,
    TB_QUIT
)
from Code.LearnGame import WindowPlayGame
from Code.Openings import Opening
from Code.QT import QTUtil2
from Code.QT import WindowJuicio


class ManagerPlayGame(Manager.Manager):
    is_human_side_white: bool
    is_human_side_black: bool
    game_obj: Game.Game
    close_on_exit = False
    name_obj_white: str
    name_obj_black: str
    is_analyzing: bool
    recno: int
    analysis: object
    comment = None
    numJugadasObj: int
    posJugadaObj: int
    siSave: bool
    puntosMax: int
    min_mstime: int
    puntos: int
    vtime: float
    show_all: bool
    book = None
    show_rating_always = None
    show_rating_different = None
    show_rating_never = None
    show_rating = None
    mrm = None
    mrm_tutor = None
    ini_time = None

    def start(self, recno, is_white, is_black, close_on_exit=False):
        self.game_type = GT_LEARN_PLAY

        self.close_on_exit = close_on_exit

        db = WindowPlayGame.DBPlayGame(self.configuration.file_play_game())
        reg = db.leeRegistro(recno)
        db.close()

        game_obj = Game.Game()
        game_obj.restore(reg["GAME"])
        self.game.set_position(game_obj.first_position)
        self.name_obj_white = game_obj.get_tag("WHITE")
        self.name_obj_black = game_obj.get_tag("BLACK")
        label = db.label(recno)

        self.recno = recno
        self.resultado = None
        self.human_is_playing = False
        self.analysis = None
        self.comment = None
        self.is_analyzing = False
        self.is_human_side_white = is_white
        self.is_human_side_black = is_black
        self.numJugadasObj = game_obj.num_moves()
        self.game_obj = game_obj
        self.posJugadaObj = 0

        if is_white and is_black:
            self.auto_rotate = self.get_auto_rotate()

        self.siSave = False
        self.min_mstime = 5000

        self.xtutor.options(self.min_mstime, 0, True)
        self.xtutor.maximize_multipv()

        self.puntosMax = 0
        self.puntos = 0
        self.vtime = 0.0

        self.book = Opening.OpeningPol(999)

        self.set_toolbar((TB_CANCEL, TB_REINIT, TB_CONFIG, TB_UTILITIES))

        self.main_window.active_game(True, False)
        self.remove_hints(True, True)

        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(self.is_human_side_white)
        self.show_side_indicator(True)
        self.set_label1(label)
        self.set_label2("")

        self.pgn_refresh(True)
        self.show_info_extra()
        self.check_boards_setposition()

        self.state = ST_PLAYING

        var_config = "LEARN_GAME_PLAY_AGAINST"

        dic = self.configuration.read_variables(var_config)

        self.show_all = dic.get("SHOW_ALL", False)
        self.show_rating_always, self.show_rating_different, self.show_rating_never = None, True, False
        self.show_rating = dic.get("SHOW_RATING", self.show_rating_always)

        self.play_next_move()

    def name_obj(self):
        return self.name_obj_white if self.game.last_position.is_white else self.name_obj_black

    def name_obj_common(self):
        if self.is_human_side_black and self.is_human_side_white:
            return self.name_obj_white + "/" + self.name_obj_black
        elif self.is_human_side_white:
            return self.name_obj_white
        else:
            return self.name_obj_black

    def set_score(self):
        lb_score = _("Score in relation to")
        self.set_label2(f'{lb_score}:<table border="1" cellpadding="5" cellspacing="0" style="margin-left:60px">'
                        f'<tr><td align="right">{self.name_obj_common()}</td><td align="right"><b>{self.puntos:+d}'
                        f'</b></td></tr>'
                        f'<tr><td align="right">{self.xtutor.name}</td>'
                        f'<td align="right"><b>{-self.puntosMax:+d}</b></td>'
                        '</tr></table>')

    def run_action(self, key):
        if key == TB_CLOSE:
            if self.close_on_exit:
                self.procesador.run_action(TB_QUIT)
            else:
                self.procesador.start()
                self.procesador.play_game_show(self.recno)

        elif key == TB_CANCEL:
            if self.close_on_exit:
                self.run_action(TB_QUIT)
            else:
                self.cancelar()

        elif key == TB_REINIT:
            self.reiniciar(True)

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True)

        elif key == TB_UTILITIES:
            self.utilidadesElo()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def final_x(self):
        return self.cancelar()

    def cancelar(self):
        self.puntos = -999
        self.analyzer_close()
        self.procesador.start()
        return False

    def reiniciar(self, with_question):
        if with_question:
            if not QTUtil2.pregunta(self.main_window, _("Restart the game?")):
                return
        self.main_window.activaInformacionPGN(False)
        self.game.set_position(self.game_obj.first_position)
        self.posJugadaObj = 0
        self.puntos = 0
        self.puntosMax = 0
        self.set_score()
        self.vtime = 0.0
        self.book = Opening.OpeningPol(999)
        self.state = ST_PLAYING
        self.board.set_position(self.game.first_position)
        self.pgn_refresh(True)
        self.check_boards_setposition()
        self.analyze_end()

        self.play_next_move()

    def valid_mrm(self, pv_usu, pv_obj, mrm_actual):
        move = self.game_obj.move(self.posJugadaObj)
        if move.analysis:
            mrm, pos = move.analysis
            ms_analisis = mrm.get_time()
            if ms_analisis > self.min_mstime:
                if mrm_actual.get_time() > ms_analisis and mrm_actual.contain(pv_usu) and mrm_actual.contain(pv_obj):
                    return None
                if mrm.contain(pv_obj) and mrm.contain(pv_usu):
                    return mrm
        return None

    def analyze_begin(self):
        if not self.is_finished():
            if self.continueTt:
                self.xtutor.ac_inicio(self.game)
            else:
                self.xtutor.ac_inicio_limit(self.game)
            self.is_analyzing = True

    def analyze_minimum(self):
        self.mrm = copy.deepcopy(self.xtutor.ac_minimo(self.min_mstime, False))
        return self.mrm

    def analyze_state(self):
        self.xtutor.engine.ac_lee()
        self.mrm = copy.deepcopy(self.xtutor.ac_estado())
        return self.mrm

    def analyze_end(self):
        if self.is_analyzing:
            self.siSave = True
            self.is_analyzing = False
            self.xtutor.ac_final(-1)

    def analyzer_close(self):
        if self.is_analyzing:
            self.is_analyzing = False
        self.xtutor.terminar()

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()
        is_white = self.game.last_position.is_white

        num_moves = len(self.game)
        if num_moves >= self.numJugadasObj:
            self.put_result()
            return

        if is_white:
            is_turn_human = self.is_human_side_white
        else:
            is_turn_human = self.is_human_side_black

        self.set_side_indicator(is_white)

        self.refresh()

        if is_turn_human:
            self.human_is_playing = True
            if self.auto_rotate:
                if is_white != self.board.is_white_bottom:
                    self.board.rotate_board()

            self.human_is_playing = True
            self.thinking(True)
            self.analyze_begin()
            self.activate_side(is_white)
            self.thinking(False)
            self.ini_time = time.time()
        else:
            self.add_move(False)
            self.play_next_move()

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        jg_usu = self.check_human_move(from_sq, to_sq, promotion)
        if not jg_usu:
            return False

        time_used = time.time() - self.ini_time
        self.vtime += time_used

        jg_obj = self.game_obj.move(self.posJugadaObj)

        si_analiza_juez = True
        if self.book:
            fen = self.last_fen()
            si_book_usu = self.book.check_human(fen, from_sq, to_sq)
            si_book_obj = self.book.check_human(fen, jg_obj.from_sq, jg_obj.to_sq)
            if si_book_usu and si_book_obj:
                if jg_obj.movimiento() != jg_usu.movimiento():
                    bmove = _("book move")
                    comment = "%s: %s %s\n%s: %s %s" % (
                        self.name_obj(),
                        jg_obj.pgn_translated(),
                        bmove,
                        self.configuration.x_player,
                        jg_usu.pgn_translated(),
                        bmove,
                    )
                    if self.show_rating in (self.show_rating_always, self.show_rating_different):
                        QTUtil2.message_information(self.main_window, comment)
                si_analiza_juez = False
            else:
                si_analiza_juez = True
                if not si_book_obj:
                    self.book = None

        analysis = None
        comment = None

        if si_analiza_juez:
            um = QTUtil2.analizando(self.main_window)
            pv_usu = jg_usu.movimiento()
            pv_obj = jg_obj.movimiento()
            mrm = self.analyze_minimum()
            position = self.game.last_position

            continue_tt = self.continueTt

            rm_usu, nada = mrm.search_rm(pv_usu)
            if rm_usu is None:
                self.analyze_end()
                continue_tt = False
                rm_usu = self.xtutor.valora(position, jg_usu.from_sq, jg_usu.to_sq, jg_usu.promotion)
                mrm.add_rm(rm_usu)

            rm_obj, pos_obj = mrm.search_rm(pv_obj)
            if rm_obj is None:
                self.analyze_end()
                continue_tt = False
                rm_obj = self.xtutor.valora(position, jg_obj.from_sq, jg_obj.to_sq, jg_obj.promotion)
                pos_obj = mrm.add_rm(rm_obj)

            analysis = mrm, pos_obj
            um.final()

            if self.show_rating == self.show_rating_different:
                si_analiza_juez = pv_usu != pv_obj
            elif self.show_rating == self.show_rating_never:
                si_analiza_juez = False

            if si_analiza_juez:
                w = WindowJuicio.WJuicio(self, self.xtutor, self.name_obj(), position, mrm, rm_obj, rm_usu, analysis,
                                         is_competitive=not self.show_all, continue_tt=continue_tt)
                w.exec_()

                analysis = w.analysis
                if w.siAnalisisCambiado:
                    self.siSave = True
                dpts = w.difPuntos()
                dpts_max = w.difPuntosMax()
                rm_usu = w.rmUsu
                rm_obj = w.rmObj
            else:
                dpts = rm_usu.score_abs5() - rm_obj.score_abs5()
                dpts_max = mrm.best_rm_ordered().score_abs5() - rm_usu.score_abs5()

            self.puntos += dpts
            self.puntosMax += dpts_max

            comentario_usu = " %s" % (rm_usu.abbrev_text())
            comentario_obj = " %s" % (rm_obj.abbrev_text())
            comentario_puntos = "%s = %d %+d %+d = %d" % (
                _("Score"),
                self.puntos - dpts,
                rm_usu.centipawns_abs(),
                -rm_obj.centipawns_abs(),
                self.puntos,
            )
            comment = "%s: %s %s\n%s: %s %s\n%s" % (
                self.name_obj(),
                jg_obj.pgn_translated(),
                comentario_obj,
                self.configuration.x_player,
                jg_usu.pgn_translated(),
                comentario_usu,
                comentario_puntos,
            )
            self.set_score()

        self.analyze_end()

        self.add_move(True, analysis, comment, time_used_s=time_used)
        self.play_next_move()
        return True

    def add_move(self, is_player_move, analysis=None, comment=None, time_used_s= None):
        move: Move.Move = self.game_obj.move(self.posJugadaObj)
        self.posJugadaObj += 1
        if analysis:
            move.analysis = analysis
        if comment:
            move.set_comment(comment)

        if time_used_s:
            move.set_time_ms(int(time_used_s*1000))

        self.game.add_move(move)
        self.check_boards_setposition()

        self.move_the_pieces(move.liMovs, True)
        self.board.set_position(move.position)
        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beep_extended(is_player_move)

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

    def put_result(self):
        self.analyzer_close()
        self.disable_all()
        self.human_is_playing = False

        self.state = ST_ENDGAME

        if self.puntos < 0:
            mensaje = _("Unfortunately you have lost.")
            quien = RS_WIN_OPPONENT
        else:
            mensaje = _("Congratulations you have won.")
            quien = RS_WIN_PLAYER

        self.beep_result_change(quien)

        self.message_on_pgn(mensaje)
        self.set_end_game()
        self.guardar()

    def guardar(self):
        db = WindowPlayGame.DBPlayGame(self.configuration.file_play_game())
        reg = db.leeRegistro(self.recno)

        dic_intento = {
            "DATE": Util.today(),
            "COLOR": ("w" if self.is_human_side_white else "") + ("b" if self.is_human_side_black else ""),
            "POINTS": self.puntos,
            "POINTSMAX": self.puntosMax,
            "TIME": self.vtime,
        }

        if not ("LIINTENTOS" in reg):
            reg["LIINTENTOS"] = []
        reg["LIINTENTOS"].insert(0, dic_intento)

        if self.siSave:
            reg["GAME"] = self.game_obj.save()
            self.siSave = False

        db.cambiaRegistro(self.recno, reg)

        db.close()
