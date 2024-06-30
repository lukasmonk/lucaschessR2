import copy
import os

import Code
from Code import Util
from Code.Analysis import AnalysisIndexes, WindowAnalysisParam
from Code.Base import Game
from Code.Base.Constantes import INACCURACY, MISTAKE, BLUNDER, INACCURACY_MISTAKE_BLUNDER, INACCURACY_MISTAKE, \
    MISTAKE_BLUNDER
from Code.BestMoveTraining import BMT
from Code.Databases import WDB_Utils
from Code.Nags.Nags import NAG_3


class AnalyzeGame:
    def __init__(self, alm, is_massiv, li_moves=None):
        self.procesador = Code.procesador
        self.alm = alm

        self.si_bmt_blunders = False
        self.si_bmt_brilliancies = False

        self.configuration = Code.configuration
        if alm.engine == "default":
            self.xmanager = self.procesador.analyzer_clone(alm.vtime, alm.depth, alm.multiPV)
            self.xmanager.set_priority(alm.priority)
        else:
            conf_engine = copy.deepcopy(self.configuration.buscaRival(alm.engine))
            if alm.multiPV:
                conf_engine.update_multipv(alm.multiPV)
            self.xmanager = self.procesador.creaManagerMotor(conf_engine, alm.vtime, alm.depth, True,
                                                             priority=alm.priority)
        self.vtime = alm.vtime
        self.depth = alm.depth

        self.with_variations = alm.include_variations

        self.stability = alm.stability
        self.st_centipawns = alm.st_centipawns
        self.st_depths = alm.st_depths
        self.st_timelimit = alm.st_timelimit

        self.accuracy_tags = alm.accuracy_tags

        # Asignacion de variables para blunders:
        # kblunders_condition: minima condición para considerar como erróneo
        # tacticblunders: folder donde guardar tactic
        # pgnblunders: file pgn donde guardar la games
        # oriblunders: si se guarda la game original
        # bmtblunders: name del entrenamiento BMT a crear
        dic = {INACCURACY: {INACCURACY, }, MISTAKE: {MISTAKE, }, BLUNDER: {BLUNDER, },
               INACCURACY_MISTAKE_BLUNDER: {INACCURACY, BLUNDER, MISTAKE}, INACCURACY_MISTAKE: {INACCURACY, MISTAKE},
               MISTAKE_BLUNDER: {BLUNDER, MISTAKE}}
        self.kblunders_condition_list = dic.get(alm.kblunders_condition, {BLUNDER, MISTAKE})

        self.tacticblunders = (
            Util.opj(self.configuration.personal_training_folder, "../Tactics", alm.tacticblunders)
            if alm.tacticblunders
            else None
        )
        self.pgnblunders = alm.pgnblunders
        self.oriblunders = alm.oriblunders
        self.bmtblunders = alm.bmtblunders
        self.bmt_listaBlunders = None

        self.siTacticBlunders = False

        self.rut_dispatch_bp = None

        self.delete_previous = True

        # fnsbrilliancies: file fns donde guardar posiciones fen
        # pgnbrilliancies: file pgn donde guardar la games
        # oribrilliancies: si se guarda la game original
        # bmtbrilliancies: name del entrenamiento BMT a crear
        self.fnsbrilliancies = alm.fnsbrilliancies
        self.pgnbrilliancies = alm.pgnbrilliancies
        self.oribrilliancies = alm.oribrilliancies
        self.bmtbrilliancies = alm.bmtbrilliancies
        self.bmt_listaBrilliancies = None

        # Asignacion de variables comunes
        # white: si se analizan las white
        # black: si se analizan las black
        # li_players: si solo se miran los movimiento de determinados jugadores
        # book: si se usa un book de aperturas para no analizar los iniciales
        # li_selected: si se indica un alista de movimientos concreta que analizar
        # from_last_move: se determina si se empieza de atras adelante o al reves
        # delete_previous: si la game tiene un analysis previo, se determina si se hace o no
        self.white = alm.white
        self.black = alm.black
        if is_massiv:
            self.li_players = [player.upper() for player in alm.li_players] if alm.li_players else []
        else:
            self.li_players = None
        self.book = alm.book
        if self.book is not None:
            self.book.polyglot()
        self.li_selected = li_moves
        self.from_last_move = alm.from_last_move
        self.delete_previous = alm.delete_previous

    def cached_begin(self):
        self.xmanager.analysis_cached_begin()

    def cached_end(self):
        self.xmanager.analysis_cached_end()

    def terminar_bmt(self, bmt_lista, name):
        """
        Si se estan creando registros para el entrenamiento BMT (Best move Training), al final hay que grabarlos
        @param bmt_lista: lista a grabar
        @param name: name del entrenamiento
        """
        if bmt_lista and len(bmt_lista) > 0:
            bmt = BMT.BMT(self.configuration.ficheroBMT)
            dbf = bmt.read_dbf(False)

            reg = dbf.baseRegistro()
            reg.ESTADO = "0"
            reg.NOMBRE = name
            reg.EXTRA = ""
            reg.TOTAL = len(bmt_lista)
            reg.HECHOS = 0
            reg.PUNTOS = 0
            reg.MAXPUNTOS = bmt_lista.max_puntos()
            reg.FINICIAL = Util.dtos(Util.today())
            reg.FFINAL = ""
            reg.SEGUNDOS = 0
            reg.BMT_LISTA = Util.var2zip(bmt_lista)
            reg.HISTORIAL = Util.var2zip([])
            reg.REPE = 0
            reg.ORDEN = 0

            dbf.insertarReg(reg, siReleer=False)

            bmt.cerrar()

    def terminar(self, si_bmt):
        """
        Proceso final, para cerrar el engine que hemos usado
        @param si_bmt: si hay que grabar el registro de BMT
        """
        self.xmanager.terminar()
        if si_bmt:
            self.terminar_bmt(self.bmt_listaBlunders, self.bmtblunders)
            self.terminar_bmt(self.bmt_listaBrilliancies, self.bmtbrilliancies)

    def dispatch_bp(self, rut_dispatch_bp):
        """
        Se determina la rutina que se llama cada analysis
        """
        self.rut_dispatch_bp = rut_dispatch_bp

    def save_brilliancies_fns(self, file, fen, mrm, game: Game.Game, njg):
        """
        Graba cada fen encontrado en el file "file"
        """
        if not file:
            return

        cab = ""
        for k, v in game.dic_tags().items():
            ku = k.upper()
            if not (ku in ("RESULT", "FEN")):
                cab += '[%s "%s"]' % (k, v)

        game_raw = Game.game_without_variations(game)
        p = Game.Game(fen=fen)
        rm = mrm.li_rm[0]
        p.read_pv(rm.pv)
        with open(file, "at", encoding="utf-8", errors="ignore") as f:
            f.write(f"{fen}||{p.pgn_base_raw()}|{cab} {game_raw.pgn_base_raw_copy(None, njg - 1)}")
        self.procesador.entrenamientos.menu = None

    def graba_tactic(self, game, njg, mrm, pos_act):
        if not self.tacticblunders:
            return

        # Esta creado el folder
        before = "%s.fns" % _("Avoid the blunder")
        after = "%s.fns" % _("Take advantage of blunder")
        if not os.path.isdir(self.tacticblunders):
            dtactics = Util.opj(self.configuration.personal_training_folder, "../Tactics")
            if not os.path.isdir(dtactics):
                os.mkdir(dtactics)
            os.mkdir(self.tacticblunders)
            with open(Util.opj(self.tacticblunders, "Config.ini"), "wt", encoding="utf-8", errors="ignore") as f:
                f.write(
                    """[COMMON]
ed_reference=20
REPEAT=0
SHOWTEXT=1
[TACTIC1]
MENU=%s
FILESW=%s:100
[TACTIC2]
MENU=%s
FILESW=%s:100
"""
                    % (_("Avoid the blunder"), before, _("Take advantage of blunder"), after)
                )

        cab = ""
        for k, v in game.dic_tags().items():
            ku = k.upper()
            if not (ku in ("RESULT", "FEN")):
                cab += '[%s "%s"]' % (k, v)
        move = game.move(njg)

        fen = move.position_before.fen()
        p = Game.Game(fen=fen)
        rm = mrm.li_rm[0]
        p.read_pv(rm.pv)
        game_raw = Game.game_without_variations(game)
        with open(Util.opj(self.tacticblunders, before), "at", encoding="utf-8", errors="ignore") as f:
            f.write("%s||%s|%s%s\n" % (fen, p.pgn_base_raw(), cab, game_raw.pgn_base_raw_copy(None, njg - 1)))

        fen = move.position.fen()
        p = Game.Game(fen=fen)
        rm = mrm.li_rm[pos_act]
        li = rm.pv.split(" ")
        p.read_pv(" ".join(li[1:]))
        with open(Util.opj(self.tacticblunders, after), "at", encoding="utf-8", errors="ignore") as f:
            f.write("%s||%s|%s%s\n" % (fen, p.pgn_base_raw(), cab, game_raw.pgn_base_raw_copy(None, njg)))

        self.siTacticBlunders = True

        if hasattr(self.procesador, "entrenamientos") and self.procesador.entrenamientos:
            self.procesador.entrenamientos.menu = None

    def save_pgn(self, file, name, dic_cab, fen, move, rm, mj):
        """
        Graba un game en un pgn

        @param file: pgn donde grabar
        @param name: name del engine que hace el analysis
        @param dic_cab: etiquetas de head del PGN
        @param fen: fen de la position
        @param move: move analizada
        @param rm: respuesta engine
        @param mj: respuesta engine con la mejor move, usado en caso de blunders, para incluirla
        """
        if not file:
            return False

        if mj:  # blunder
            game_blunder = Game.Game()
            game_blunder.set_position(move.position_before)
            game_blunder.read_pv(rm.pv)
            jg0 = game_blunder.move(0)
            jg0.set_comment(rm.texto())

        p = Game.Game()
        p.set_position(move.position_before)
        if mj:  # blunder
            rm = mj
        p.read_pv(rm.pv)
        if p.is_finished():
            result = p.resultado()
            mas = ""  # ya lo anade en la ultima move
        else:
            mas = " *"
            result = "*"

        jg0 = p.move(0)
        t = "%0.2f" % (float(self.vtime) / 1000.0,)
        t = t.rstrip("0")
        if t[-1] == ".":
            t = t[:-1]
        eti_t = "%s %s" % (t, _("Second(s)"))

        jg0.set_comment("%s %s: %s\n" % (name, eti_t, rm.texto()))
        if mj:
            jg0.add_variation(game_blunder)

        cab = ""
        for k, v in dic_cab.items():
            ku = k.upper()
            if not (ku in ("RESULT", "FEN")):
                cab += '[%s "%s"]\n' % (k, v)
        # Nos protegemos de que se hayan escrito en el pgn original de otra forma
        cab += '[FEN "%s"]\n' % fen
        cab += '[Result "%s"]\n' % result

        with open(file, "at", encoding="utf-8", errors="ignore") as q:
            texto = cab + "\n" + p.pgn_base() + mas + "\n\n"
            q.write(texto)

        return True

    def save_bmt(self, si_blunder, fen, mrm, pos_act, cl_game, txt_game):
        """
        Se graba una position en un entrenamiento BMT
        @param si_blunder: si es blunder o brilliancie
        @param fen: position
        @param mrm: multirespuesta del engine
        @param pos_act: position de la position elegida en mrm
        @param cl_game: key de la game
        @param txt_game: la game completa en texto
        """

        previa = 999999999
        nprevia = -1
        tniv = 0
        game_bmt = Game.Game()
        cp = game_bmt.first_position
        cp.read_fen(fen)

        if len(mrm.li_rm) > 16:
            mrm_bmt = copy.deepcopy(mrm)
            if pos_act > 15:
                mrm_bmt.li_rm[15] = mrm_bmt.li_rm[pos_act]
                pos_act = 15
            mrm_bmt.li_rm = mrm_bmt.li_rm[:16]
        else:
            mrm_bmt = mrm

        for n, rm in enumerate(mrm_bmt.li_rm):
            pts = rm.centipawns_abs()
            if pts != previa:
                previa = pts
                nprevia += 1
            tniv += nprevia
            rm.nivelBMT = nprevia
            rm.siElegida = False
            rm.siPrimero = n == pos_act
            game_bmt.set_position(cp)
            game_bmt.read_pv(rm.pv)
            rm.txtPartida = game_bmt.save()

        bmt_uno = BMT.BMTUno(fen, mrm_bmt, tniv, cl_game)

        bmt_lista = self.bmt_listaBlunders if si_blunder else self.bmt_listaBrilliancies
        bmt_lista.nuevo(bmt_uno)
        bmt_lista.check_game(cl_game, txt_game)

    def xprocesa(self, game, tmp_bp, window=None):
        self.si_bmt_blunders = False
        self.si_bmt_brilliancies = False

        si_bp2 = hasattr(tmp_bp, "bp2")  # Para diferenciar el analysis de un game que usa una progressbar unica del

        def gui_dispatch(xrm):
            return not tmp_bp.is_canceled()

        self.xmanager.set_gui_dispatch(gui_dispatch)  # Dispatch del engine, si esta puesto a 4 minutos por ejemplo que
        # compruebe si se ha indicado que se cancele.

        si_blunders = self.pgnblunders or self.oriblunders or self.bmtblunders or self.tacticblunders
        si_brilliancies = self.fnsbrilliancies or self.pgnbrilliancies or self.bmtbrilliancies

        if self.bmtblunders and self.bmt_listaBlunders is None:
            self.bmt_listaBlunders = BMT.BMTLista()

        if self.bmtbrilliancies and self.bmt_listaBrilliancies is None:
            self.bmt_listaBrilliancies = BMT.BMTLista()

        xlibro_aperturas = self.book

        is_white = self.white
        is_black = self.black

        if self.li_players:
            for x in ["BLACK", "WHITE"]:
                player = game.get_tag(x)
                if player:
                    player = player.upper()
                    si = False
                    for uno in self.li_players:
                        si_z = uno.endswith("*")
                        si_a = uno.startswith("*")
                        uno = uno.replace("*", "").strip().upper()
                        if si_a:
                            if player.endswith(uno):
                                si = True
                            if si_z:  # form para poner si_a y si_z
                                si = uno in player
                        elif si_z:
                            if player.startswith(uno):
                                si = True
                        elif uno == player:
                            si = True
                        if si:
                            break
                    if not si:
                        if x == "BLACK":
                            is_black = False
                        else:
                            is_white = False

        if not (is_white or is_black):
            return

        cl_game = Util.huella()
        si_poner_pgn_original_blunders = False
        si_poner_pgn_original_brilliancies = False

        n_mov = len(game)
        if self.li_selected:
            li_pos_moves = self.li_selected[:]
        else:
            li_pos_moves = list(range(n_mov))

        st_borrar = set()
        if xlibro_aperturas is not None:
            for mov in li_pos_moves:
                if tmp_bp.is_canceled():
                    self.xmanager.remove_gui_dispatch()
                    return

                move = game.move(mov)
                if xlibro_aperturas.get_list_moves(move.position.fen()):
                    st_borrar.add(mov)
                    continue
                else:
                    break

        if self.from_last_move:
            li_pos_moves.reverse()

        n_moves = len(li_pos_moves)
        if si_bp2:
            tmp_bp.set_total(2, n_moves)

        for npos, pos_move in enumerate(li_pos_moves):
            if pos_move in st_borrar:
                continue

            if tmp_bp.is_canceled():
                self.xmanager.remove_gui_dispatch()
                return

            move = game.move(pos_move)
            if si_bp2:
                tmp_bp.pon(2, npos + 1)

            if self.rut_dispatch_bp:
                self.rut_dispatch_bp(npos, n_moves, pos_move)

            if tmp_bp.is_canceled():
                self.xmanager.remove_gui_dispatch()
                return

            li_moves_games = move.list_all_moves() if self.alm.analyze_variations else [(move, game, pos_move)]

            for move, game_move, pos_current_move in li_moves_games:

                # # white y black
                white_move = move.position_before.is_white
                if white_move:
                    if not is_white:
                        continue
                else:
                    if not is_black:
                        continue

                allow_add_variations = True
                if self.delete_previous:
                    move.analysis = None

                # si no se borran los análisis previos y existe un análisis no se tocan las variantes
                elif move.analysis:
                    if self.with_variations and move.variations:
                        allow_add_variations = False

                # -# Procesamos
                if move.analysis is None:
                    resp = self.xmanager.analyzes_move_game(
                        game_move,
                        pos_current_move,
                        self.vtime,
                        depth=self.depth,
                        stability=self.stability,
                        st_centipawns=self.st_centipawns,
                        st_depths=self.st_depths,
                        st_timelimit=self.st_timelimit,
                        window=window if window else self.procesador.main_window
                    )
                    if not resp:
                        self.xmanager.remove_gui_dispatch()
                        return

                    if tmp_bp.is_canceled():
                        self.xmanager.remove_gui_dispatch()
                        return

                    move.analysis = resp

                cp = move.position_before
                mrm, pos_act = move.analysis
                move.complexity = AnalysisIndexes.calc_complexity(cp, mrm)
                move.winprobability = AnalysisIndexes.calc_winprobability(cp, mrm)
                move.narrowness = AnalysisIndexes.calc_narrowness(cp, mrm)
                move.efficientmobility = AnalysisIndexes.calc_efficientmobility(cp, mrm)
                move.piecesactivity = AnalysisIndexes.calc_piecesactivity(cp, mrm)
                move.exchangetendency = AnalysisIndexes.calc_exchangetendency(cp, mrm)

                rm = mrm.li_rm[pos_act]
                nag, color = mrm.set_nag_color(rm)
                move.add_nag(nag)

                if si_blunders or si_brilliancies or self.with_variations:

                    mj = mrm.li_rm[0]

                    fen = move.position_before.fen()

                    if self.with_variations and allow_add_variations:
                        if not move.analisis2variantes(self.alm, self.delete_previous):
                            move.remove_all_variations()

                    ok_blunder = nag in self.kblunders_condition_list
                    if ok_blunder:
                        self.graba_tactic(game, pos_move, mrm, pos_act)

                        if self.save_pgn(self.pgnblunders, mrm.name, game.dic_tags(), fen, move, rm, mj):
                            si_poner_pgn_original_blunders = True

                        if self.bmtblunders:
                            txt_game = Game.game_without_variations(game).save()
                            self.save_bmt(True, fen, mrm, pos_act, cl_game, txt_game)
                            self.si_bmt_blunders = True

                    if move.is_brilliant():
                        move.add_nag(NAG_3)
                        self.save_brilliancies_fns(self.fnsbrilliancies, fen, mrm, game, pos_current_move)

                        if self.save_pgn(self.pgnbrilliancies, mrm.name, game.dic_tags(), fen, move, rm, None):
                            si_poner_pgn_original_brilliancies = True

                        if self.bmtbrilliancies:
                            txt_game = Game.game_without_variations(game).save()
                            self.save_bmt(False, fen, mrm, pos_act, cl_game, txt_game)
                            self.si_bmt_brilliancies = True

        # Ponemos el texto original en la ultima
        if si_poner_pgn_original_blunders and self.oriblunders:
            with open(self.pgnblunders, "at", encoding="utf-8", errors="ignore") as q:
                q.write("\n%s\n\n" % game.pgn())

        if si_poner_pgn_original_brilliancies and self.oribrilliancies:
            with open(self.pgnbrilliancies, "at", encoding="utf-8", errors="ignore") as q:
                q.write("\n%s\n\n" % game.pgn())

        if self.accuracy_tags:
            game.add_accuracy_tags()

        self.xmanager.remove_gui_dispatch()


def analysis_game(manager):
    game = manager.game
    procesador = manager.procesador
    main_window = manager.main_window

    alm = WindowAnalysisParam.analysis_parameters(main_window, True)

    if alm is None:
        return

    li_moves = []
    lni = Util.ListaNumerosImpresion(alm.num_moves)
    num_move = int(game.primeraJugada())
    is_white = not game.starts_with_black
    for nRaw in range(game.num_moves()):
        must_save = lni.siEsta(num_move)
        if must_save:
            if is_white:
                if not alm.white:
                    must_save = False
            elif not alm.black:
                must_save = False
        if must_save:
            li_moves.append(nRaw)
        is_white = not is_white
        if is_white:
            num_move += 1

    num_moves = len(li_moves)
    if len(alm.num_moves) > 0 and num_moves == 0:
        return

    # mensaje = _("Analyzing the move....")
    # tmp_bp = QTUtil2.BarraProgreso(main_window, _("Analysis"), mensaje, num_moves).show_top_right()

    mens = _("Analyzing the move....")

    manager_main_window_base = manager.main_window.base
    manager_main_window_base.show_message(mens, True, tit_cancel=_("Cancel"))
    manager_main_window_base.tb.setDisabled(True)

    ap = AnalyzeGame(alm, False, li_moves)

    def dispatch_bp(pos, ntotal, njg):
        manager_main_window_base.change_message("%s: %d/%d" % (_("Analyzing the move...."), pos + 1, ntotal))
        move = game.move(njg)
        manager.set_position(move.position)
        manager.main_window.pgnColocate(njg / 2, (njg + 1) % 2)
        manager.board.put_arrow_sc(move.from_sq, move.to_sq)
        manager.put_view()
        return not manager_main_window_base.is_canceled()

    ap.dispatch_bp(dispatch_bp)

    ap.xprocesa(game, manager_main_window_base, window=main_window)

    manager_main_window_base.tb.setDisabled(False)
    manager_main_window_base.hide_message()

    not_canceled = not manager_main_window_base.is_canceled()
    ap.terminar(not_canceled)

    if not_canceled:
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

        if li_creados or li_no_creados:
            WDB_Utils.message_creating_trainings(main_window, li_creados, li_no_creados)
            procesador.entrenamientos.rehaz()

    manager.goto_end()

    if not_canceled:
        if alm.show_graphs:
            manager.show_analysis()
