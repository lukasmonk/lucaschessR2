from typing import List, Tuple

import Code
from Code.Analysis import AnalysisIndexes, WindowAnalysis, WindowAnalysisVariations
from Code.Base import Game, Move
from Code.Base.Constantes import TOP_RIGHT
from Code.Engines import EngineResponse
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios


class ControlAnalysis:
    wmu: None
    rm: EngineResponse.EngineResponse
    game: Game.Game
    mrm: EngineResponse.MultiEngineResponse
    list_rm_name: List[Tuple[EngineResponse.EngineResponse, str, int]]

    def __init__(self, tb_analysis, mrm, pos_selected, number, xengine):

        self.tb_analysis = tb_analysis
        self.number = number
        self.xengine = xengine
        self.with_figurines = tb_analysis.configuration.x_pgn_withfigurines

        self.mrm = mrm
        self.pos_selected = pos_selected

        self.pos_rm_active = pos_selected
        self.pos_mov_active = 0

        self.move = tb_analysis.move

        self.is_active = False

        self.list_rm_name = self.do_lirm()  # rm, name, centpawns

    def time_engine(self):
        return self.mrm.name.strip()

    def time_label(self):
        if self.mrm.max_time:
            t = "%0.2f" % (float(self.mrm.max_time) / 1000.0,)
            t = t.rstrip("0")
            if t[-1] == ".":
                t = t[:-1]
            eti_t = "%s: %s" % (_("Second(s)"), t)
        elif self.mrm.max_depth:
            eti_t = "%s: %d" % (_("Depth"), self.mrm.max_depth)
        else:
            eti_t = ""
        return eti_t

    def do_lirm(self) -> List[Tuple[EngineResponse.EngineResponse, str, int]]:
        li = []
        pb = self.move.position_before
        for rm in self.mrm.li_rm:
            pv1 = rm.pv.split(" ")[0]
            from_sq = pv1[:2]
            to_sq = pv1[2:4]
            promotion = pv1[4].lower() if len(pv1) == 5 else None

            name = (
                pb.pgn(from_sq, to_sq, promotion)
                if self.with_figurines
                else pb.pgn_translated(from_sq, to_sq, promotion)
            )
            if name:
                txt = rm.abbrev_text_base()
                if txt:
                    name += "(%s)" % txt
                li.append((rm, name, rm.centipawns_abs()))

        return li

    def set_wmu(self, wmu):
        self.wmu = wmu
        self.is_active = True

    def desactiva(self):
        self.wmu.hide()
        self.is_active = False

    def is_selected(self, pos_rm):
        return pos_rm == self.pos_selected

    def set_pos_rm_active(self, pos_rm):
        self.pos_rm_active = pos_rm
        self.rm = self.list_rm_name[self.pos_rm_active][0]
        self.game = Game.Game(self.move.position_before)
        self.game.read_pv(self.rm.pv)
        self.game.is_finished()
        self.pos_mov_active = 0

    def pgn_active(self):
        num_mov = self.game.primeraJugada()
        style_number = "color:%s; font-weight: bold;" % Code.dic_colors["PGN_NUMBER"]
        style_select = "color:%s;font-weight: bold;" % Code.dic_colors["PGN_SELECT"]
        style_moves = "color:%s;" % Code.dic_colors["PGN_MOVES"]
        li_pgn = []
        if self.game.starts_with_black:
            li_pgn.append('<span style="%s">%d...</span>' % (style_number, num_mov))
            num_mov += 1
            salta = 1
        else:
            salta = 0
        for n, move in enumerate(self.game.li_moves):
            if n % 2 == salta:
                li_pgn.append('<span style="%s">%d.</span>' % (style_number, num_mov))
                num_mov += 1

            xp = move.pgn_html(self.with_figurines)
            if n == self.pos_mov_active:
                xp = '<span style="%s">%s</span>' % (style_select, xp)
            else:
                xp = '<span style="%s">%s</span>' % (style_moves, xp)

            li_pgn.append('<a href="%d" style="text-decoration:none;">%s</a> ' % (n, xp))

        return " ".join(li_pgn)

    def score_active(self):
        rm = self.list_rm_name[self.pos_rm_active][0]
        return rm.texto()

    def score_active_depth(self):
        rm = self.list_rm_name[self.pos_rm_active][0]
        txt = "%s   -   %s: %d" % (rm.texto(), _("Depth"), rm.depth)
        return txt

    def complexity(self):
        return AnalysisIndexes.get_complexity(self.move.position_before, self.mrm)

    def winprobability(self):
        return AnalysisIndexes.get_winprobability(self.move.position_before, self.mrm)

    def narrowness(self):
        return AnalysisIndexes.get_narrowness(self.move.position_before, self.mrm)

    def efficientmobility(self):
        return AnalysisIndexes.get_efficientmobility(self.move.position_before, self.mrm)

    def piecesactivity(self):
        return AnalysisIndexes.get_piecesactivity(self.move.position_before, self.mrm)

    def active_position(self):
        n_movs = len(self.game)
        if self.pos_mov_active >= n_movs:
            self.pos_mov_active = n_movs - 1
        if self.pos_mov_active < 0:
            self.pos_mov_active = -1
            return self.game.move(0).position_before, None, None
        else:
            move_active = self.game.move(self.pos_mov_active)
            return move_active.position, move_active.from_sq, move_active.to_sq

    def get_game(self):
        game_original: Game.Game = self.move.game
        if self.move.movimiento():
            game_send = game_original.copy_until_move(self.move)
            # if len(game_send) == 0:
            #     game_send = game_original.copia()
        else:
            game_send = game_original.copia()
        if self.pos_mov_active > -1:
            for nmove in range(self.pos_mov_active + 1):
                move = self.game.move(nmove)
                move_send = move.clone(game_send)
                game_send.add_move(move_send)
        return game_send

    def change_mov_active(self, accion):
        if accion == "Adelante":
            self.pos_mov_active += 1
        elif accion == "Atras":
            self.pos_mov_active -= 1
        elif accion == "Inicio":
            self.pos_mov_active = -1
        elif accion == "Final":
            self.pos_mov_active = len(self.game) - 1

    def set_pos_mov_active(self, pos):
        if 0 <= pos < len(self.game):
            self.pos_mov_active = pos

    def is_final_position(self):
        return self.pos_mov_active >= len(self.game) - 1

    def fen_active(self):
        move = self.game.move(self.pos_mov_active if self.pos_mov_active > 0 else 0)
        return move.position.fen()

    def external_analysis(self, wowner, is_white):
        move = self.game.move(self.pos_mov_active if self.pos_mov_active >= 0 else 0)
        pts = self.score_active()
        AnalisisVariations(wowner, self.xengine, move, is_white, pts)

    def save_base(self, game, rm, is_complete):
        name = self.time_engine()
        vtime = self.time_label()
        variation = game.copia() if is_complete else game.copia(0)

        if len(variation) > 0:
            comment = "%s %s %s" % (rm.abbrev_text(), name, vtime)
            variation.move(0).set_comment(comment.strip())
        self.move.add_variation(variation)

    def put_view_manager(self):
        if self.tb_analysis.procesador.manager:
            self.tb_analysis.procesador.manager.put_view()


class CreateAnalysis:
    def __init__(self, procesador, move, pos_move):

        self.procesador = procesador
        self.configuration = procesador.configuration
        self.move = move
        self.pos_move = pos_move  # Para mostrar el pgn con los numeros correctos
        self.li_tabs_analysis = []

    def create_initial_show(self, main_window, xengine):
        move = self.move
        if move.analysis is None:
            me = QTUtil2.waiting_message.start(main_window, _("Analyzing the move...."), physical_pos=TOP_RIGHT,
                                               with_cancel=True)

            def mira(rm):
                return not me.cancelado()

            xengine.set_gui_dispatch(mira)
            mrm, pos = xengine.analysis_move(move, xengine.mstime_engine, xengine.depth_engine)
            move.analysis = mrm, pos

            si_cancelado = me.cancelado()
            me.final()
            if si_cancelado:
                return None
        else:
            mrm, pos = move.analysis

        tab_analysis = ControlAnalysis(self, mrm, pos, 0, xengine)
        self.li_tabs_analysis.append(tab_analysis)
        return tab_analysis

    def create_show(self, main_window, alm):
        if alm.engine == "default":
            xengine = Code.procesador.analyzer_clone(alm.vtime, alm.depth, alm.multiPV)

        else:
            xengine = None
            busca = alm.engine[1:] if alm.engine.startswith("*") else alm.engine
            for tab_analysis in self.li_tabs_analysis:
                if tab_analysis.xengine.key == busca:
                    xengine = tab_analysis.xengine
                    xengine.update_multipv(alm.multiPV)
                    break
            if xengine is None:
                conf_engine = self.configuration.buscaRival(alm.engine)
                conf_engine.update_multipv(alm.multiPV)
                xengine = self.procesador.creaManagerMotor(conf_engine, alm.vtime, alm.depth, has_multipv=True)

        me = QTUtil2.waiting_message.start(main_window, _("Analyzing the move...."), physical_pos=TOP_RIGHT)
        mrm, pos = xengine.analysis_move(self.move, alm.vtime, alm.depth)
        xengine.terminar()
        me.final()

        tab_analysis = ControlAnalysis(self, mrm, pos, self.li_tabs_analysis[-1].number + 1, xengine)
        self.li_tabs_analysis.append(tab_analysis)
        return tab_analysis


def show_analysis(procesador, xtutor, move, is_white, pos_move, main_window=None, must_save=True, subanalysis=False):
    main_window = procesador.main_window if main_window is None else main_window

    ma = CreateAnalysis(procesador, move, pos_move)
    if xtutor is None:
        xtutor = procesador.XTutor()
    tab_analysis0 = ma.create_initial_show(main_window, xtutor)
    move = ma.move
    if not tab_analysis0:
        return
    wa = WindowAnalysis.WAnalisis(ma, main_window, is_white, must_save, tab_analysis0, subanalysis=subanalysis)
    if subanalysis:
        wa.show()
    else:
        wa.exec_()
        busca = True
        for uno in ma.li_tabs_analysis:
            if busca:
                if uno.is_active:
                    move.analysis = uno.mrm, uno.pos_selected

                    busca = False
            xengine = uno.xengine
            if not xtutor or xengine.key != xtutor.key:
                xengine.terminar()


class AnalisisVariations:
    def __init__(self, owner, xanalyzer, move, is_white, cbase_points):

        self.owner = owner
        self.xanalyzer = xanalyzer
        self.move = move
        self.is_white = is_white
        self.position_before = move.position_before
        self.is_moving_time = False

        self.time_function = None
        self.time_pos_max = None
        self.time_pos = None
        self.time_others_tb = None
        self.rm = None
        self.pos_analyzer = None
        self.max_analyzer = None
        self.game_analyzer = None

        if self.xanalyzer.mstime_engine:
            segundos_pensando = self.xanalyzer.mstime_engine / 1000  # esta en milesimas
            if self.xanalyzer.mstime_engine % 1000 > 0:
                segundos_pensando += 1
        else:
            segundos_pensando = 3

        self.w = WindowAnalysisVariations.WAnalisisVariations(
            self, self.owner, segundos_pensando, self.is_white, cbase_points
        )
        self.reset()
        self.w.exec_()

    def reset(self):
        self.w.board.set_position(self.position_before)
        self.w.board.put_arrow_sc(self.move.from_sq, self.move.to_sq)
        self.w.board.set_dispatcher(self.player_has_moved)
        self.w.board.activate_side(not self.move.position.is_white)

    def player_has_moved(self, from_sq, to_sq, promotion=""):

        # Peon coronando
        if not promotion and self.position_before.pawn_can_promote(from_sq, to_sq):
            promotion = self.w.board.peonCoronando(not self.move.position.is_white)
            if promotion is None:
                return False

        si_bien, mens, new_move = Move.get_game_move(None, self.position_before, from_sq, to_sq, promotion)

        if si_bien:

            self.move_the_pieces(new_move.liMovs)
            self.w.board.put_arrow_sc(new_move.from_sq, new_move.to_sq)
            self.analysis_move(new_move)
            return True
        else:
            return False

    def analysis_move(self, new_move):
        me = QTUtil2.waiting_message.start(self.w, _("Analyzing the move...."))

        secs = self.w.get_seconds()
        self.xanalyzer.remove_gui_dispatch()
        self.rm = self.xanalyzer.analyzes_variation(new_move, secs * 1000, self.is_white)
        me.final()

        self.game_analyzer = Game.Game(new_move.position)
        self.game_analyzer.read_pv(self.rm.pv)

        if len(self.game_analyzer):
            self.w.boardT.set_position(self.game_analyzer.move(0).position)

        self.w.set_score(self.rm.texto())

        self.pos_analyzer = 0
        self.max_analyzer = len(self.game_analyzer)

        self.moving_analyzer(si_inicio=True)

    def move_the_pieces(self, li_movs):
        """
        Hace los movimientos de piezas en el board
        """
        for movim in li_movs:
            if movim[0] == "b":
                self.w.board.borraPieza(movim[1])
            elif movim[0] == "m":
                self.w.board.muevePieza(movim[1], movim[2])
            elif movim[0] == "c":
                self.w.board.cambiaPieza(movim[1], movim[2])

        self.w.board.disable_all()

        self.w.board.escena.update()
        self.w.update()
        QTUtil.refresh_gui()

    def process_toolbar(self, accion):
        if self.rm:
            if accion == "MoverAdelante":
                self.moving_analyzer(n_saltar=1)
            elif accion == "MoverAtras":
                self.moving_analyzer(n_saltar=-1)
            elif accion == "MoverInicio":
                self.moving_analyzer(si_inicio=True)
            elif accion == "MoverFinal":
                self.moving_analyzer(si_final=True)
            elif accion == "MoverTiempo":
                self.move_timed()
            elif accion == "MoverLibre":
                self.external_analysis()
            elif accion == "MoverFEN":
                move = self.game_analyzer.move(self.pos_analyzer)
                QTUtil.set_clipboard(move.position.fen())
                QTVarios.fen_is_in_clipboard(self.w)

    def moving_analyzer(self, si_inicio=False, n_saltar=0, si_final=False, is_base=False):
        if n_saltar:
            pos = self.pos_analyzer + n_saltar
            if 0 <= pos < self.max_analyzer:
                self.pos_analyzer = pos
            else:
                return
        elif si_inicio or is_base:
            self.pos_analyzer = 0
        elif si_final:
            self.pos_analyzer = self.max_analyzer - 1
        if self.game_analyzer.num_moves():
            move = self.game_analyzer.move(self.pos_analyzer)
            if is_base:
                self.w.boardT.set_position(move.position_before)
            else:
                self.w.boardT.set_position(move.position)
                self.w.boardT.put_arrow_sc(move.from_sq, move.to_sq)
        self.w.boardT.escena.update()
        self.w.update()
        QTUtil.refresh_gui()

    def move_timed(self):
        if self.is_moving_time:
            self.is_moving_time = False
            self.time_others_tb(True)
            self.w.stop_clock()
            return

        def otros_tb(si_habilitar):
            for accion in self.w.tb.li_acciones:
                if not accion.key.endswith("MoverTiempo"):
                    accion.setEnabled(si_habilitar)

        self.time_function = self.moving_analyzer
        self.time_pos_max = self.max_analyzer
        self.time_pos = -1
        self.time_others_tb = otros_tb
        self.is_moving_time = True
        otros_tb(False)
        self.moving_analyzer(is_base=True)
        self.w.start_clock(self.moving_time_1)

    def moving_time_1(self):
        self.time_pos += 1
        if self.time_pos == self.time_pos_max:
            self.is_moving_time = False
            self.time_others_tb(True)
            self.w.stop_clock()
            return
        if self.time_pos == 0:
            self.time_function(si_inicio=True)
        else:
            self.time_function(n_saltar=1)

    def external_analysis(self):
        move = self.game_analyzer.move(self.pos_analyzer)
        pts = self.rm.texto()
        AnalisisVariations(self.w, self.xanalyzer, move, self.is_white, pts)
