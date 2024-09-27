import os
import random
import time

import FasterCode

import Code
from Code import Util
from Code.Base.Constantes import ADJUST_SELECTED_BY_PLAYER
from Code.Engines import Priorities, EngineResponse, EngineRunDirect, EngineRun
from Code.SQL import UtilSQL


class ListEngineManagers:
    def __init__(self):
        self.lista = []
        self.with_logs = False

    def append(self, engine_manager):
        self.verify()
        self.lista.append(engine_manager)
        if self.with_logs:
            engine_manager.log_open()

    def verify(self):
        self.lista = [engine_manager for engine_manager in self.lista if engine_manager.activo]

    def close_all(self):
        self.verify()
        for engine_manager in self.lista:
            engine_manager.terminar()
        self.lista = []

    def is_logs_active(self):
        return self.with_logs

    def active_logs(self, ok: bool):
        self.verify()
        if ok != self.with_logs:
            for engine_manager in self.lista:
                if ok:
                    engine_manager.log_open()
                else:
                    engine_manager.log_close()
            self.with_logs = ok

    def set_active_logs(self):
        # Tournaments/Leagues/Swiss
        Code.configuration.log_engines_set(self.with_logs)

    def check_active_logs(self):
        if Code.configuration.log_engines_check_active():
            self.with_logs = True


class EngineManager:
    def __init__(self, conf_engine, direct=False):

        self.engine = None
        self.confMotor = conf_engine
        self.name = conf_engine.nombre_ext(False)
        self.key = conf_engine.key
        self.num_multipv = 0
        self.mstime_engine = conf_engine.max_time * 1000
        self.depth_engine = conf_engine.max_depth

        self.pv = ""
        self.from_sq = ""
        self.to_sq = ""
        self.promotion = ""
        self.without_movements = False

        self.nodes = 0

        self.function = _("Opponent").lower()  # para distinguir entre tutor y analizador

        self.priority = Priorities.priorities.normal

        self.dispatching = None

        self.activo = True  # No es suficiente con engine == None para saber si esta activo y se puede logear

        self.ficheroLog = None

        self.direct = direct

        self.cache_analysis = None

        Code.list_engine_managers.append(self)

    def set_nodes(self, nodes):
        self.nodes = nodes

    def set_direct(self):
        self.direct = True

    def options(self, mstime_engine, depth_engine, has_multipv):
        self.mstime_engine = mstime_engine
        self.depth_engine = depth_engine
        self.num_multipv = self.confMotor.multiPV if has_multipv else 0
        if self.engine:
            self.update_multipv(self.num_multipv)

        if self.key in ("daydreamer", "cinnamon") and depth_engine and depth_engine == 1:
            self.depth_engine = 2

    def set_priority(self, priority):
        self.priority = priority if priority else Priorities.priorities.normal

    def set_priority_very_low(self):
        self.priority = Priorities.priorities.verylow

    def maximize_multipv(self):
        self.num_multipv = 9999

    def set_gui_dispatch(self, rutina, who_dispatch=None):
        if self.engine:
            self.engine.set_gui_dispatch(rutina, who_dispatch)
        else:
            self.dispatching = rutina, who_dispatch

    def remove_gui_dispatch(self):
        self.set_gui_dispatch(None)

    def update_multipv(self, xmultipv):
        self.confMotor.update_multipv(xmultipv)
        self.num_multipv = self.confMotor.multiPV
        self.check_engine()
        self.engine.set_multipv(self.confMotor.multiPV)

    def remove_multipv(self):
        self.num_multipv = 0

    def set_multipv(self, num_multipv):
        self.confMotor.update_multipv(num_multipv)
        self.num_multipv = self.confMotor.multiPV

    def check_engine(self):
        if self.engine is not None:
            return False
        self.set_multipv(self.num_multipv)

        exe = self.confMotor.ejecutable()
        args = self.confMotor.argumentos()
        li_uci = self.confMotor.liUCI

        maia_level = None
        if self.name.lower().startswith("maia") or "lc0" in self.name.lower():
            for comando, valor in li_uci:
                if comando == "WeightsFile":
                    if valor.startswith("maia"):
                        maia_level = int(valor[5:9])
                        break

        if maia_level:
            self.engine = EngineRun.MaiaEngine(
                self.name,
                exe,
                li_uci,
                self.num_multipv,
                priority=self.priority,
                args=args,
                log=self.ficheroLog,
                level=maia_level,
            )
        elif self.direct:
            self.engine = EngineRunDirect.DirectEngine(
                self.name, exe, li_uci, self.num_multipv, priority=self.priority, args=args, log=self.ficheroLog
            )
        else:
            self.engine = EngineRun.RunEngine(
                self.name, exe, li_uci, self.num_multipv, priority=self.priority, args=args, log=self.ficheroLog
            )

        if self.confMotor.siDebug:
            self.engine.siDebug = True
            self.engine.nomDebug = self.confMotor.nomDebug

        if self.confMotor.emulate_movetime:
            self.engine.emulate_movetime = True

        if self.dispatching:
            rutina, who_dispatch = self.dispatching
            self.engine.set_gui_dispatch(rutina, who_dispatch)

        return True

    def play_seconds(self, game, seconds):
        self.check_engine()
        mrm = self.engine.bestmove_game(game, seconds * 1000, None)
        return mrm.best_rm_ordered() if mrm else None

    def play_time(self, game, seconds_white, seconds_black, seconds_move, adjusted=0):
        self.check_engine()
        if self.mstime_engine or self.depth_engine:
            return self.play_game(game, adjusted)
        mseconds_white = int(seconds_white * 1000)
        mseconds_black = int(seconds_black * 1000)
        mseconds_move = int(seconds_move * 1000)
        mrm = self.engine.bestmove_time(game, mseconds_white, mseconds_black, mseconds_move)
        if mrm is None:
            return None

        if adjusted:
            mrm.game = game
            if adjusted >= 1000:
                mrm.fen_base = game.last_position.fen()
            return mrm.best_adjusted_move(adjusted) if adjusted != ADJUST_SELECTED_BY_PLAYER else mrm
        else:
            return mrm.best_rm_ordered()

    def play_time_tourney(self, game, seconds_white, seconds_black, seconds_move):
        self.check_engine()
        if self.mstime_engine or self.depth_engine:
            mrm = self.engine.bestmove_game(game, self.mstime_engine, self.depth_engine)
        else:
            mseconds_white = int(seconds_white * 1000)
            mseconds_black = int(seconds_black * 1000)
            mseconds_move = int(seconds_move * 1000) if seconds_move else 0
            mrm = self.engine.bestmove_time(game, mseconds_white, mseconds_black, mseconds_move)
        return mrm

    def play_game_raw(self, game):
        self.check_engine()
        return self.engine.bestmove_game(game, self.mstime_engine, self.depth_engine)

    def play_game(self, game, adjusted=0):
        self.check_engine()

        mrm = self.engine.bestmove_game(game, self.mstime_engine, self.depth_engine)

        if adjusted:
            mrm.game = game
            if adjusted >= 1000:
                mrm.fen_base = game.last_position.fen()
            return mrm.best_adjusted_move(adjusted) if adjusted != ADJUST_SELECTED_BY_PLAYER else mrm
        else:
            return mrm.best_rm_ordered()

    def play_game_maia(self, game):
        self.check_engine()

        if self.depth_engine:
            self.engine.nodes = int(self.depth_engine ** 2)

        mrm = self.engine.bestmove_game(game, self.mstime_engine, self.depth_engine)
        return mrm.best_rm_ordered()

    def play_fixed_depth_time_tourney(self, game):
        self.check_engine()

        return self.engine.bestmove_game(game, self.mstime_engine, self.depth_engine)

    def analiza(self, fen):
        self.check_engine()
        return self.engine.bestmove_fen(fen, self.mstime_engine, self.depth_engine)

    def valora(self, position, from_sq, to_sq, promotion):
        self.check_engine()

        new_position = position.copia()
        new_position.play(from_sq, to_sq, promotion)

        fen = new_position.fen()
        if FasterCode.fen_ended(fen):
            rm = EngineResponse.EngineResponse("", position.is_white)
            rm.sinInicializar = False
            self.without_movements = True
            self.pv = from_sq + to_sq + promotion
            self.from_sq = from_sq
            self.to_sq = to_sq
            self.promotion = promotion
            return rm
        if self.num_multipv > 1:
            self.engine.set_multipv(1)
        mrm = self.engine.bestmove_fen(fen, self.mstime_engine, self.depth_engine)
        if self.num_multipv > 1:
            self.engine.set_multipv(self.num_multipv)
        rm = mrm.best_rm_ordered()
        rm.change_side(position)
        mv = from_sq + to_sq + (promotion if promotion else "")
        rm.pv = mv + " " + rm.pv
        rm.from_sq = from_sq
        rm.to_sq = to_sq
        rm.promotion = promotion if promotion else ""
        rm.is_white = position.is_white
        return rm

    def control(self, fen, profundidad):
        self.check_engine()
        return self.engine.bestmove_fen(fen, 0, profundidad)

    def terminar(self):
        if self.engine:
            self.engine.close()
            self.log_close()
            self.engine = None
            self.activo = False

    def analysis_move(self, move, vtime, depth=0):
        self.check_engine()

        mrm = self.engine.bestmove_fen(move.position_before.fen(), vtime, depth, is_savelines=True)
        mv = move.movimiento()
        if not mv:
            return mrm, 0
        rm, n = mrm.search_rm(move.movimiento())
        if rm:
            return mrm, n

        # No esta considerado, obliga a hacer el analysis de nuevo from_sq position
        if move.game is not None and (move.is_mate or move.is_draw):
            rm = EngineResponse.EngineResponse(self.name, move.position_before.is_white)
            rm.from_sq = mv[:2]
            rm.to_sq = mv[2:4]
            rm.promotion = mv[4] if len(mv) == 5 else ""
            rm.pv = mv
            if move.is_mate:
                rm.mate = 1
        else:
            position = move.position

            mrm1 = self.engine.bestmove_fen(position.fen(), vtime, depth)
            if mrm1 and mrm1.li_rm:
                rm = mrm1.li_rm[0]
                rm.change_side(position)
                rm.pv = mv + " " + rm.pv
            else:
                rm = EngineResponse.EngineResponse(self.name, mrm1.is_white)
                rm.pv = mv
            rm.from_sq = mv[:2]
            rm.to_sq = mv[2:4]
            rm.promotion = mv[4] if len(mv) == 5 else ""
            rm.is_white = move.position_before.is_white
        pos = mrm.add_rm(rm)

        return mrm, pos

    def analysis_cached_begin(self):
        self.cache_analysis = UtilSQL.DictBig()

    def analysis_cached_end(self):
        self.cache_analysis.close()

    def analyzes_move_game(
            self,
            game,
            njg,
            vtime,
            depth=0,
            stability=False,
            st_centipawns=0,
            st_depths=0,
            st_timelimit=0,
            window=None,
    ):
        self.check_engine()
        key = None
        if self.cache_analysis is not None:
            move = game.move(njg)
            key = move.position_before.fenm2() + move.movimiento()
            if key in self.cache_analysis:
                return self.cache_analysis[key]
        resp = self.analyzes_move_game_raw(
            game, njg, vtime, depth, stability, st_centipawns, st_depths, st_timelimit, window
        )
        if self.cache_analysis is not None:
            self.cache_analysis[key] = resp
        return resp

    def analyzes_move_game_raw(
            self, game, njg, mstime, depth, stability, st_centipawns, st_depths, st_timelimit, window
    ):
        self.check_engine()
        ini_time = time.time()
        if stability:
            mrm = self.engine.analysis_stable(game, njg, mstime, depth, True, st_centipawns, st_depths, st_timelimit)
        else:
            mrm = self.engine.bestmove_game_jg(game, njg, mstime, depth, is_savelines=True)

        mrm.ordena()
        self.remove_gui_dispatch()
        ms_used = int((time.time() - ini_time) * 1000)

        if njg > 9000:
            return mrm, 0

        move = game.move(njg)
        mv = move.movimiento()
        if not mv:
            return mrm, 0
        rm, n = mrm.search_rm(mv)
        if rm:
            return mrm, n
        rm_best = mrm.best_rm_ordered()

        if move.is_mate:
            rm = EngineResponse.EngineResponse(None, None)
            rm.restore(rm_best.save())
            rm.pv = move.movimiento()
            rm.from_sq = move.from_sq
            rm.to_sq = move.to_sq
            rm.promotion = move.promotion
            pos = mrm.add_rm(rm)
            return mrm, pos

        # No esta considerado, obliga a hacer el analysis de nuevo from_sq position
        if rm_best.depth and (depth > rm_best.depth or depth == 0):
            depth = rm_best.depth

        if ms_used < mstime:
            mstime = ms_used

        # if window:
        #     um = QTUtil2.one_moment_please(window, _("Finishing the analysis...")) if mstime > 1000 else None
        # else:
        #     um = None

        self.engine.set_multipv(1)
        mrm_next = self.engine.bestmove_game_jg(game, njg + 1, mstime, depth, is_savelines=True)
        self.engine.set_multipv(self.engine.num_multipv)

        # if um:
        #     um.final()

        if mrm_next and mrm_next.li_rm:
            rm = mrm_next.li_rm[0]
            rm.change_side(move.position)
            rm.pv = mv + " " + rm.pv
        else:
            rm = EngineResponse.EngineResponse(self.name, mrm_next.is_white)
            rm.pv = mv
        rm.from_sq = mv[:2]
        rm.to_sq = mv[2:4]
        rm.promotion = mv[4] if len(mv) == 5 else ""
        rm.is_white = move.position_before.is_white
        pos = mrm.add_rm(rm)

        return mrm, pos

    def analyzes_variation(self, move, vtime, is_white):
        self.check_engine()

        mrm = self.engine.bestmove_fen(move.position.fen(), vtime, None)
        if mrm.li_rm:
            rm = mrm.li_rm[0]
        else:
            rm = EngineResponse.EngineResponse("", is_white)
        return rm

    def ac_inicio(self, game):
        self.check_engine()
        self.engine.ac_inicio(game)

    def ac_inicio_limit(self, game):
        # tutor cuando no se quiere que trabaje en background
        self.check_engine()
        self.engine.ac_inicio_limit(game, self.mstime_engine, self.depth_engine)

    def ac_minimo(self, min_mstime, lock_ac):
        self.check_engine()
        return self.engine.ac_minimo(min_mstime, lock_ac)

    def ac_minimo_td(self, min_mstime, min_depth, lock_ac):
        self.check_engine()
        return self.engine.ac_minimo_td(min_mstime, min_depth, lock_ac)

    def ac_estado(self):
        self.check_engine()
        return self.engine.ac_estado()

    def ac_final(self, min_mstime):
        self.check_engine()
        return self.engine.ac_final(min_mstime)

    def ac_final_limit(self):
        self.check_engine()
        return self.engine.ac_final_limit(self.mstime_engine)

    def set_option(self, name, value):
        self.check_engine()
        self.engine.set_option(name, value)

    def busca_mate(self, game, mate):
        self.check_engine()
        return self.engine.busca_mate(game, mate)

    def stop(self):
        if self.engine:
            self.engine.put_line("stop")

    def current_rm(self):
        if not self.engine:
            return None
        mrm = self.engine.mrm
        if mrm is None:
            return None
        mrm.ordena()
        return mrm.best_rm_ordered()

    def play_time_routine(
            self, game, routine_return, seconds_white, seconds_black, seconds_move, adjusted=0, factor_humanize=0,
            limit_time_seconds=None
    ):
        self.check_engine()

        self.engine.set_max_time_current(limit_time_seconds)

        def play_return(mrm):
            if self.engine:
                self.remove_gui_dispatch()
                if mrm is None:
                    resp = None
                elif adjusted:
                    mrm.ordena()
                    mrm.game = game
                    if adjusted >= 1000:
                        mrm.fen_base = game.last_position.fen()
                    resp = mrm.best_adjusted_move(adjusted) if adjusted != ADJUST_SELECTED_BY_PLAYER else mrm
                else:
                    resp = mrm.best_rm_ordered()
            else:
                resp = None
            routine_return(resp)

        if factor_humanize:
            if self.mstime_engine or self.depth_engine:
                seconds_white, seconds_black, seconds_move = 15.0 * 60, 15.0 * 60, 6
            self.humanize(factor_humanize, game, seconds_white, seconds_black, seconds_move)
        else:
            self.engine.not_humanize()

        if self.nodes:
            self.engine.play_bestmove_nodes(play_return, game, self.nodes, seconds_white * 1000, seconds_black * 1000)
        elif self.mstime_engine or self.depth_engine:
            self.engine.play_bestmove_game(play_return, game, self.mstime_engine, self.depth_engine)
        else:
            self.engine.play_bestmove_time(
                play_return, game, seconds_white * 1000, seconds_black * 1000, seconds_move * 1000
            )

    def humanize(self, factor, game, seconds_white, seconds_black, seconds_move):
        # Hay que tener en cuenta
        # Si estamos enla apertura -> mas rápido
        # Si hay muchas opciones -> mas lento
        # Si hay pocas piezas
        # Si son las primeras 20 jugadas, el procentaje aumenta de 1 a 100
        # para el resto
        movestogo = 40
        last_position = game.last_position
        if last_position.is_white:
            movetime_seconds = seconds_white + movestogo * seconds_move
        else:
            movetime_seconds = seconds_black + movestogo * seconds_move
        movetime_seconds = movetime_seconds * 9 / (movestogo * 10)

        porc = 100.0
        if last_position.num_moves < 40:
            porc = 10.0 + last_position.num_moves * 90.0 / 30.0

        nmoves = min(20, len(last_position.get_exmoves()))
        if nmoves == 1:
            self.engine.not_humanize()
            return
        x = 70.0 + nmoves * 30.0 / 20.0
        porc *= x / 100.0

        x = 80.0 + random.randint(1, 40)
        porc *= x / 100.0

        movetime_seconds *= porc / 100.0

        movetime_seconds = max(random.randint(1, 4), movetime_seconds)

        average_previous_user = game.average_mstime_user(5)
        if average_previous_user:
            movetime_seconds = max(min(0.8 * average_previous_user / 1000, 60), movetime_seconds)  # max 1 minute

        self.engine.set_humanize(movetime_seconds * factor)

    def log_open(self):
        if self.ficheroLog:
            return
        carpeta = Util.opj(Code.configuration.carpeta, "EngineLogs")
        if not os.path.isdir(carpeta):
            os.mkdir(carpeta)
        plantlog = "%s_%%05d" % Util.opj(carpeta, self.name)
        pos = 1
        nomlog = plantlog % pos

        while os.path.isfile(nomlog):
            pos += 1
            nomlog = plantlog % pos
        self.ficheroLog = nomlog

        if self.engine:
            self.engine.log_open(nomlog)

    def log_close(self):
        self.ficheroLog = None
        if self.engine:
            self.engine.log_close()
