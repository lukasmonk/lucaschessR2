import time
import copy
import random


import Code
from Code import Adjournments
from Code import Manager
from Code import Util
from Code.Base import Move
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    GT_AGAINST_GM,
    TB_CLOSE,
    TB_REINIT,
    TB_CONFIG,
    TB_ADJOURN,
    TB_UTILITIES,
)
from Code.GM import GM
from Code.GM import WindowGM
from Code.Openings import Opening
from Code.QT import QTUtil2
from Code.QT import WindowJuicio
from Code.SQL import UtilSQL


class ManagerGM(Manager.Manager):
    ini_time_s = 0.0

    def start(self, record):
        self.base_inicio(record)
        self.play_next_move()

    def base_inicio(self, record):
        self.game_type = GT_AGAINST_GM

        self.hints = 9999  # Para que analice sin problemas

        self.puntos = 0

        self.record = record

        self.gm = record.gm
        self.is_white = record.is_white
        self.modo = record.modo
        self.with_adjudicator = record.with_adjudicator
        self.show_evals = record.show_evals
        self.engine = record.engine
        self.vtime = record.vtime
        self.depth = record.depth
        self.multiPV = record.multiPV
        self.mostrar = record.mostrar
        self.select_rival_move = record.select_rival_move
        self.jugInicial = record.jugInicial
        self.gameElegida = record.gameElegida
        self.bypass_book = record.bypass_book
        self.opening = record.opening
        self.on_bypass_book = True if self.bypass_book else False
        if self.on_bypass_book:
            self.bypass_book.polyglot()
        self.on_opening = True if self.opening else False

        self.is_analyzing = False

        if self.with_adjudicator:
            self.puntos = 0
            tutor = self.configuration.buscaRival(self.engine)
            t_t = self.vtime * 100
            self.xtutor = self.procesador.creaManagerMotor(tutor, t_t, self.depth)
            self.xtutor.set_multipv(self.multiPV)
            self.analysis = None
            self.continueTt = not Code.configuration.x_engine_notbackground

        self.book = Opening.OpeningPol(999)

        self.thinking(True)

        default = GM.get_folder_gm()
        carpeta = default if self.modo == "estandar" else self.configuration.personal_training_folder
        self.engine_gm = GM.GM(carpeta, self.gm)
        self.engine_gm.filter_side(self.is_white)
        if self.gameElegida is not None:
            self.engine_gm.set_game_selected(self.gameElegida)

        self.is_human_side_white = self.is_white
        self.is_engine_side_white = not self.is_white
        self.thinking(False)

        self.set_toolbar((TB_CLOSE, TB_REINIT, TB_ADJOURN, TB_CONFIG, TB_UTILITIES))
        self.main_window.active_game(True, False)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.remove_hints()
        self.put_pieces_bottom(self.is_white)
        dic = GM.dic_gm()
        self.nombreGM = dic[self.gm.lower()] if self.modo == "estandar" else self.gm
        rot = _("Grandmaster")
        rotulo1 = rot + ": <b>%s</b>" if self.modo == "estandar" else "<b>%s</b>"
        self.set_label1(rotulo1 % self.nombreGM)

        self.rival_name = ""
        self.textoPuntuacion = ""
        self.ponRotuloSecundario()
        self.pgn_refresh(True)
        self.show_info_extra()

        self.state = ST_PLAYING

        self.check_boards_setposition()

    def ponRotuloSecundario(self):
        self.set_label2(self.rival_name + "<br><br>" + self.textoPuntuacion)

    def run_action(self, key):
        if key == TB_CLOSE:
            self.end_game()

        elif key == TB_REINIT:
            self.reiniciar()

        elif key == TB_ADJOURN:
            self.adjourn()

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True)

        elif key == TB_UTILITIES:
            self.utilities()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def final_x(self):
        if self.state == ST_ENDGAME:
            return True
        return self.end_game()

    def end_game(self):
        self.analyze_terminate()
        siJugadas = len(self.game) > 0
        if siJugadas and self.state != ST_ENDGAME:
            self.game.set_unknown()
            self.set_end_game()
        self.procesador.start()

        return False

    def reiniciar(self):
        if QTUtil2.pregunta(self.main_window, _("Restart the game?")):
            self.analyze_terminate()
            self.game.set_position()
            self.main_window.activaInformacionPGN(False)
            self.start(self.record)

    def analyze_begin(self):
        if not self.is_finished():
            if self.continueTt:
                self.xtutor.ac_inicio(self.game)
            else:
                self.xtutor.ac_inicio_limit(self.game)
            self.is_analyzing = True

    def analyze_state(self):
        self.xtutor.engine.ac_lee()
        self.mrm = copy.deepcopy(self.xtutor.ac_estado())
        return self.mrm

    def analyze_minimum(self, min_time):
        self.mrm = copy.deepcopy(self.xtutor.ac_minimo(min_time, False))
        return self.mrm

    def analyze_end(self):
        if self.is_analyzing:
            self.is_analyzing = False
            if self.continueTt:
                self.mrm_tutor = self.xtutor.ac_final(self.xtutor.mstime_engine)
            else:
                self.mrm_tutor = self.xtutor.ac_final_limit()

    def analyze_end_now(self):
        if self.is_analyzing:
            self.is_analyzing = False
            self.mrm_tutor = self.xtutor.ac_final(0)

    def play_next_move(self):
        self.analyze_end_now()
        self.disable_all()

        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        if (len(self.game) > 0) and self.engine_gm.is_finished():
            self.put_result()
            return

        self.set_side_indicator(is_white)
        self.refresh()

        si_rival = is_white == self.is_engine_side_white

        if self.jugInicial > 1:
            si_jug_inicial = len(self.game) < (self.jugInicial - 1) * 2
        else:
            si_jug_inicial = False

        li_alternativas = self.engine_gm.alternativas()
        nli_alternativas = len(li_alternativas)

        # Movimiento automatico
        if si_jug_inicial or self.on_opening or self.on_bypass_book:
            si_buscar = True
            if self.on_opening:
                li_pv = self.opening.a1h8.split(" ")
                nj = len(self.game)
                if len(li_pv) > nj:
                    move = li_pv[nj]
                    if move in li_alternativas:
                        si_buscar = False
                    else:
                        self.on_opening = False
                else:
                    self.on_opening = False

            if si_buscar:
                if self.on_bypass_book:
                    li_moves = self.bypass_book.get_list_moves(self.last_fen())
                    li_n = []
                    for from_sq, to_sq, promotion, pgn, peso in li_moves:
                        move = from_sq + to_sq + promotion
                        if move in li_alternativas:
                            li_n.append(move)
                    if li_n:
                        si_buscar = False
                        nli_alternativas = len(li_n)
                        if nli_alternativas > 1:
                            pos = random.randint(0, nli_alternativas - 1)
                            move = li_n[pos]
                        else:
                            move = li_n[0]
                    else:
                        self.on_bypass_book = None

            if si_buscar:
                if si_jug_inicial:
                    si_buscar = False
                    if nli_alternativas > 1:
                        pos = random.randint(0, nli_alternativas - 1)
                        move = li_alternativas[pos]
                    elif nli_alternativas == 1:
                        move = li_alternativas[0]

            if not si_buscar:
                self.rival_has_moved(move)
                self.play_next_move()
                return

        if si_rival:
            if nli_alternativas > 1:
                if self.select_rival_move:
                    li_moves = self.engine_gm.get_moves_txt(self.game.last_position, False)
                    from_sq, to_sq, promotion = WindowGM.select_move(self, li_moves, False)
                    move = from_sq + to_sq + promotion
                else:
                    pos = random.randint(0, nli_alternativas - 1)
                    move = li_alternativas[pos]
            else:
                move = li_alternativas[0]

            self.rival_has_moved(move)
            self.play_next_move()

        else:
            self.human_is_playing = True
            self.ini_time_s = time.time()
            if self.with_adjudicator:
                self.thinking(True)
                self.analyze_begin()
                self.thinking(False)
            self.activate_side(is_white)

    def analyze_terminate(self):
        if self.is_analyzing:
            self.is_analyzing = False
            self.xtutor.terminar()

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        time_s_end = time.time()
        jgUsu = self.check_human_move(from_sq, to_sq, promotion)
        if not jgUsu:
            return False


        movimiento = jgUsu.movimiento()
        position = self.game.last_position
        is_valid = self.engine_gm.is_valid_move(movimiento)
        analysis = None

        if not is_valid:
            self.board.set_position(position)
            self.board.activate_side(self.is_human_side_white)
            li_moves = self.engine_gm.get_moves_txt(position, True)
            desde_gm, hasta_gm, promotion_gm = WindowGM.select_move(self, li_moves, True)
            si_analiza_juez = self.with_adjudicator
            if si_analiza_juez:
                if self.book:
                    fen = self.last_fen()
                    siH = self.book.check_human(fen, from_sq, to_sq)
                    is_gm = self.book.check_human(fen, desde_gm, hasta_gm)
                    if is_gm and siH:
                        si_analiza_juez = False
                    else:
                        self.book = False
        else:
            si_analiza_juez = (
                    self.with_adjudicator and self.mostrar is None
            )  # None es ver siempre False no ver nunca True ver si diferentes
            if len(movimiento) == 5:
                promotion = movimiento[4].lower()
            desde_gm, hasta_gm, promotion_gm = from_sq, to_sq, promotion

        ok, mens, jg_gm = Move.get_game_move(self.game, position, desde_gm, hasta_gm, promotion_gm)
        mov_gm = jg_gm.pgn_translated()
        mov_usu = jgUsu.pgn_translated()

        if si_analiza_juez:
            um = QTUtil2.analizando(self.main_window)
            mrm = self.analyze_minimum(self.vtime * 100)

            continue_tt = self.continueTt

            rm_usu, nada = mrm.search_rm(jgUsu.movimiento())
            if rm_usu is None:
                self.analyze_end_now()
                continue_tt = False
                rm_usu = self.xtutor.valora(position, from_sq, to_sq, promotion)
                mrm.add_rm(rm_usu)

            rm_gm, pos_gm = mrm.search_rm(jg_gm.movimiento())
            if rm_gm is None:
                self.analyze_end_now()
                continue_tt = False
                rm_gm = self.xtutor.valora(position, desde_gm, hasta_gm, promotion_gm)
                pos_gm = mrm.add_rm(rm_gm)

            um.final()

            analysis = mrm, pos_gm
            dpts = rm_usu.centipawns_abs() - rm_gm.centipawns_abs()

            if self.mostrar is None or ((self.mostrar is True) and not is_valid):
                w = WindowJuicio.WJuicio(
                    self,
                    self.xtutor,
                    self.nombreGM,
                    position,
                    mrm,
                    rm_gm,
                    rm_usu,
                    analysis,
                    is_competitive=not self.show_evals,
                    continue_tt=continue_tt
                )
                w.exec_()

                rm, pos_gm = w.analysis[0].search_rm(jg_gm.movimiento())
                analysis = w.analysis[0], pos_gm

                rm_usu = w.rmUsu
                rm_gm = w.rmObj
                dpts = w.difPuntos()

            self.puntos += dpts

            comentario0 = "<b>%s</b> : %s = %s<br>" % (self.configuration.x_player, mov_usu, rm_usu.texto())
            comentario0 += "<b>%s</b> : %s = %s<br>" % (self.nombreGM, mov_gm, rm_gm.texto())
            comentario1 = "<br><b>%s</b> = %+d<br>" % (_("Difference"), dpts)
            comentario2 = "<b>%s</b> = %+d<br>" % (_("Centipawns accumulated"), self.puntos)
            self.textoPuntuacion = comentario2
            self.ponRotuloSecundario()

            if not is_valid:
                jg_gm.set_comment(
                    (comentario0 + comentario1 + comentario2)
                    .replace("<b>", "")
                    .replace("</b>", "")
                    .replace("<br>", "\n")
                )

        self.analyze_end_now()

        self.move_the_pieces(jg_gm.liMovs)

        jg_gm.analysis = analysis
        jg_gm.set_time_ms(int((time_s_end-self.ini_time_s) * 1000))
        self.add_move(jg_gm, True)
        self.error = ""
        self.play_next_move()
        return True

    def analize_position(self, row, key):
        if self.state != ST_ENDGAME:
            return
        Manager.Manager.analize_position(self, row, key)

    def rival_has_moved(self, move):
        from_sq = move[:2]
        to_sq = move[2:4]
        promotion = move[4:]

        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if ok:
            self.error = ""

            self.add_move(move, False)
            self.move_the_pieces(move.liMovs, True)

            return True
        else:
            self.error = mens
            return False

    def add_move(self, move, is_player_move):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beep_extended(is_player_move)

        txt = self.engine_gm.label_game_if_unique(is_gm=self.modo == "estandar")
        if txt:
            self.rival_name = txt
        self.ponRotuloSecundario()

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

        self.engine_gm.play(move.movimiento())

    def put_result(self):
        self.state = ST_ENDGAME
        self.board.disable_all()

        mensaje = _("Game ended")

        txt, porc, txtResumen = self.engine_gm.resultado(self.game)
        mensaje += "<br><br>" + txt
        if self.with_adjudicator:
            mensaje += "<br><br><b>%s</b> = %+d<br>" % (_("Centipawns accumulated"), self.puntos)

        self.message_on_pgn(mensaje)

        db_histo = UtilSQL.DictSQL(self.configuration.ficheroGMhisto)

        gmK = "P_%s" % self.gm if self.modo == "personal" else self.gm

        dic = {}
        dic["FECHA"] = Util.today()
        dic["PUNTOS"] = self.puntos
        dic["PACIERTOS"] = porc
        dic["JUEZ"] = self.engine
        dic["TIEMPO"] = self.vtime
        dic["RESUMEN"] = txtResumen

        liHisto = db_histo[gmK]
        if liHisto is None:
            liHisto = []
        liHisto.insert(0, dic)
        db_histo[gmK] = liHisto
        db_histo.pack()
        db_histo.close()

    def save_state(self):
        dic = {}
        li_vars = dir(self)
        ti = type(1)
        tb = type(True)
        ts = type("x")
        for var in li_vars:
            xvar = getattr(self, var)
            if not var.startswith("__"):
                if type(xvar) in (ti, tb, ts):
                    dic[var] = xvar
        dic["record"] = self.record
        dic["game"] = self.game.save()
        dic["labels"] = self.get_labels()
        dic["motorgm"] = self.engine_gm
        return dic

    def run_adjourn(self, dic):
        labels = None, None, None
        motorgm = None
        for k, v in dic.items():
            if k == "record":
                self.base_inicio(v)
            elif k == "game":
                self.game.restore(v)
            elif k == "labels":
                labels = v
            elif k == "motorgm":
                motorgm = v
            else:
                setattr(self, k, v)
        if motorgm:
            self.engine_gm = motorgm
        self.restore_labels(labels)
        self.pgn_refresh(True)
        self.repeat_last_movement()
        self.play_next_move()

    def adjourn(self):
        if QTUtil2.pregunta(self.main_window, _("Do you want to adjourn the game?")):
            dic = self.save_state()

            label_menu = "%s %s" % (_("Play like a Grandmaster"), self.nombreGM)
            self.state = ST_ENDGAME

            with Adjournments.Adjournments() as adj:
                adj.add(self.game_type, dic, label_menu)
                adj.si_seguimos(self)

    def current_pgn(self):
        gm = self.gm
        motor_gm = self.engine_gm

        game_gm = motor_gm.get_last_game()

        if game_gm:
            event = game_gm.event
            oponent = game_gm.oponent
            fecha = game_gm.date
            result = game_gm.result
        else:
            event = "?"
            oponent = "?"
            fecha = "????.??.??"
            result = "*"

        if self.is_white:
            blancas = gm
            negras = oponent
        else:
            blancas = oponent
            negras = gm

        resp = '[Event "%s"]\n' % event
        resp += '[Date "%s"]\n' % fecha
        resp += '[White "%s"]\n' % blancas
        resp += '[Black "%s"]\n' % negras
        resp += '[Result "%s"]\n' % result.strip()

        ap = self.game.opening
        if ap:
            resp += '[ECO "%s"]\n' % ap.eco
            resp += '[Opening "%s"]\n' % ap.tr_name

        resp += "\n" + self.game.pgn_base() + " " + result.strip()

        return resp
