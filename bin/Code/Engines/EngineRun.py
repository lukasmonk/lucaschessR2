import os
import random
import signal
import subprocess
import sys
import threading
import time

import psutil
from PySide2 import QtCore

import Code
from Code import Util
from Code.Base.Constantes import BOOK_BEST_MOVE, BOOK_RANDOM_UNIFORM, BOOK_RANDOM_PROPORTIONAL
from Code.Books import Books
from Code.Engines import EngineResponse
from Code.Engines import Priorities
from Code.QT import QTUtil2


class RunEngine:
    def __init__(self, name, exe, li_options_uci=None, num_multipv=0, priority=None, args=None, log=None):
        self.log = None
        if log:
            self.log_open(log)

        if Code.DEBUG_ENGINES:
            self.put_line = self.put_line_debug
            self.xstdout_thread = self.xstdout_thread_debug
        else:
            self.put_line = self.put_line_base
            self.xstdout_thread = self.xstdout_thread_base

        self.end_time_humanize = None

        self.name = name

        self.is_white = True

        self.gui_dispatch = None
        self.ultDispatch = 0
        self.minDispatch = 1.0  # seconds
        self.who_dispatch = name
        self.uci_ok = False

        self.emulate_movetime = False

        self.uci_lines = []

        if not os.path.isfile(exe):
            QTUtil2.message_error(None, "%s:\n  %s" % (_("Engine not found"), exe))
            return

        self.pid = None
        self.exe = os.path.abspath(exe)
        self.direxe = os.path.dirname(exe)
        self.priority = priority
        self.working = True
        self.liBuffer = []
        self.starting = True
        self.best_move_done = True
        self.args = ["./%s" % os.path.basename(self.exe)]
        if args:
            self.args.extend(args)

        self.direct_dispatch = None

        self.mrm = None
        self.stopped = False

        self.start()

        self.lock_ac = True

        self.orden_uci()

        txt_uci_analysismode = "UCI_AnalyseMode"
        uci_analysismode_set = False

        setoptions = False
        if li_options_uci:
            for opcion, valor in li_options_uci:
                if type(valor) == bool:
                    valor = str(valor).lower()
                self.set_option(opcion, valor)
                setoptions = True
                if opcion == txt_uci_analysismode:
                    uci_analysismode_set = True

        self.num_multipv = num_multipv
        if num_multipv:
            self.set_multipv(num_multipv)
            if not uci_analysismode_set and num_multipv > 1:
                for line in self.uci_lines:
                    if txt_uci_analysismode in line:
                        self.set_option(txt_uci_analysismode, "true")
                        setoptions = True
                        break

        if setoptions:
            self.put_line_base("isready")
            self.wait_mrm("readyok", 1000)

        self.ucinewgame()

    def cerrar(self):
        self.working = False

    def put_line_debug(self, line: str):
        if self.working:
            if line == "stop":
                self.stopped = True
            Code.xpr(self.name, "put>>> %s\n" % line)
            self.stdin_lock.acquire()
            line = line.encode()
            if self.log:
                self.log.write(">>> %s\n" % line)
            self.stdin.write(line + b"\n")
            try:
                self.stdin.flush()
            except:
                pass
            self.stdin_lock.release()

    def put_line_base(self, line: str):
        if self.working:
            if line == "stop":
                self.stopped = True
            self.stdin_lock.acquire()
            line = line.encode()
            if self.log:
                self.log.write(">>> %s\n" % line)
            self.stdin.write(line + b"\n")
            try:
                self.stdin.flush()
            except:
                pass
            self.stdin_lock.release()

    def get_lines(self):
        self.stdout_lock.acquire()
        li = self.liBuffer
        self.liBuffer = []
        self.stdout_lock.release()
        return li

    def hay_datos(self):
        return len(self.liBuffer) > 0

    def reset(self):
        self.stdout_lock.acquire()
        self.mrm = EngineResponse.MultiEngineResponse(self.name, self.is_white)
        self.stdout_lock.release()

    def xstdout_thread_base(self, stdout, lock):
        # try:
        while self.working:
            line = stdout.readline()
            if not line:
                break
            line = str(line, "latin-1", "ignore")
            if self.end_time_humanize:
                if "bestmove" in line:
                    while time.time() < self.end_time_humanize and self.working:
                        time.sleep(0.1)
                        lock.acquire()
                        self.liBuffer.append("info string humanizing")
                        lock.release()
                    self.end_time_humanize = None
            lock.acquire()
            self.liBuffer.append(line)
            if self.direct_dispatch:
                self.mrm.dispatch(line)
            lock.release()
            if self.log:
                self.log.write(line.strip() + "\n")
            if self.direct_dispatch and "bestmove" in line:
                self.direct_dispatch()
        # except Exception as e:
        #     sys.stderr.write("\n" + Code.stack_lines(True) + "\n")
        #     sys.stderr.write("\nException: %s\n" % str(e))
        #     sys.stderr.write("Type: %s\n" % type(e))
        #     sys.stderr.write("Error: %s\n%s\n" % (str(e.args), "-"*80))
        # finally:
        stdout.close()

    def xstdout_thread_debug(self, stdout, lock):
        try:
            while self.working:
                line = stdout.readline()
                if not line:
                    break
                line = str(line, "latin-1", "ignore")
                if self.end_time_humanize:
                    if "bestmove" in line:
                        while time.time() < self.end_time_humanize and self.working:
                            time.sleep(0.1)
                            lock.acquire()
                            self.liBuffer.append("info string humanizing")
                            lock.release()
                        self.end_time_humanize = None
                Code.pr(self.name, line)
                lock.acquire()
                self.liBuffer.append(line)
                if self.direct_dispatch:
                    self.mrm.dispatch(line)
                lock.release()
                if self.direct_dispatch and "bestmove" in line:
                    self.direct_dispatch()
        except:
            pass
        finally:
            stdout.close()

    def start_engine(self):
        if Code.is_windows:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            env = None
        else:
            startupinfo = None
            ld_library = os.environ.get("LD_LIBRARY_PATH", "")
            if ld_library:
                ld_library += ":"
            ld_library += os.path.abspath(self.direxe)
            env = {**os.environ, "LD_LIBRARY_PATH": ld_library}
        curdir = os.path.abspath(os.curdir)  # problem with "." as curdir
        os.chdir(self.direxe)  # to fix problems with non ascii folders

        self.process = subprocess.Popen(
            self.args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, startupinfo=startupinfo, env=env
        )
        os.chdir(curdir)

        self.pid = self.process.pid
        if self.priority is not None:
            try:
                p = psutil.Process(self.pid)
                p.nice(Priorities.priorities.value(self.priority))
            except:
                pass

        self.stdin = self.process.stdin
        self.stdout = self.process.stdout

    def start(self):
        self.start_engine()

        self.stdout_lock = threading.Lock()
        stdout_thread = threading.Thread(target=self.xstdout_thread, args=(self.process.stdout, self.stdout_lock))
        stdout_thread.daemon = True
        stdout_thread.start()

        self.stdin_lock = threading.Lock()

        self.starting = False

    def close(self):
        self.working = False
        if self.log:
            self.log_close()
            self.log = None

        if self.pid:
            try:
                if self.process.poll() is None:
                    self.put_line("stop")
                    self.put_line("quit")
                    time.sleep(0.1)
                    self.process.kill()
                    self.process.terminate()
            except:
                if Code.is_windows:
                    subprocess.call(["taskkill", "/F", "/T", "/PID", str(self.pid)])
                else:
                    os.kill(self.pid, signal.SIGTERM)
                sys.stderr.write("INFO X CLOSE: except - the engine %s won't close properly.\n" % self.exe)

            self.pid = None

    def log_open(self, file):
        self.log = open(file, "at", encoding="utf-8")
        self.log.write("%s       %s\n\n" % (str(Util.today()), "-" * 70))

    def log_close(self):
        if self.log:
            self.log.close()
            self.log = None

    def dispatch(self):
        QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
        if self.gui_dispatch:
            tm = time.time()
            if tm - self.ultDispatch < self.minDispatch:
                return True
            self.ultDispatch = tm
            self.mrm.ordena()
            rm = self.mrm.best_rm_ordered()
            rm.who_dispatch = self.who_dispatch
            if not self.gui_dispatch(rm):
                return False
        return True

    def wait_mrm(self, seektxt, msStop):
        self.stopped = False
        ini_tiempo = time.time()
        stop = False
        while True:
            if self.hay_datos():
                for line in self.get_lines():
                    if (
                            not self.stopped
                    ):  # problema con información que llega tras stop, que no muestra lineas completas de pv en stockfish
                        self.mrm.dispatch(line)
                    if seektxt in line:
                        if not self.dispatch():
                            self.put_line("stop")
                        return True

            queda = msStop - int((time.time() - ini_tiempo) * 1000)
            if queda <= 0:
                if stop:
                    return True
                self.put_line("stop")
                msStop += 2000
                stop = True
            if not self.hay_datos():
                if not self.dispatch():
                    self.put_line("stop")
                    return False
                time.sleep(0.001)

    def wait_list(self, txt, ms_stop):
        ini_tiempo = time.time()
        stop = False
        ok = False
        li = []
        while True:
            lt = self.get_lines()
            if lt:
                for line in lt:
                    if txt in line:
                        ok = True
                        break
                li.extend(lt)
                if ok:
                    return li, True

            queda = ms_stop - int((time.time() - ini_tiempo) * 1000)
            if queda <= 0:
                if stop:
                    return li, False
                self.put_line("stop")
                ms_stop += 2000
                stop = True
            if not self.hay_datos():
                time.sleep(0.001)

    def work_ok(self, orden):
        self.reset()
        self.put_line(orden)
        self.put_line("isready")
        return self.wait_list("readyok", 1000)

    def work_bestmove(self, orden, msmax_time):
        self.reset()
        self.put_line(orden)
        self.wait_mrm("bestmove", msmax_time)

    def work_infinite(self, busca, msmax_time):
        self.reset()
        self.put_line("go infinite")
        self.wait_mrm(busca, msmax_time)

    def seek_bestmove(self, max_time, max_depth, is_savelines):
        env = "go"
        ms_time = None
        if max_depth:
            env += " depth %d" % max_depth
        elif max_time:
            if self.emulate_movetime:
                env += " infinite"
                ms_time = max_time
            else:
                env += " movetime %d" % max_time

        if ms_time is None:
            ms_time = 10000
            if max_time:
                ms_time = max_time if max_depth else max_time + 5000
            elif max_depth:
                ms_time = 10000000000  # non stop

        self.reset()
        if is_savelines:
            self.mrm.save_lines()
        self.mrm.set_time_depth(max_time, max_depth)

        self.work_bestmove(env, ms_time)

        self.mrm.ordena()

        return self.mrm

    def seek_bestmove_time(self, time_white, time_black, inc_time_move):
        env = "go wtime %d btime %d" % (time_white, time_black)
        if inc_time_move:
            env += " winc %d binc %d" % (inc_time_move, inc_time_move)
        max_time = time_white if self.is_white else time_black

        self.reset()
        self.mrm.set_time_depth(max_time, None)

        self.work_bestmove(env, max_time)

        self.mrm.ordena()
        return self.mrm

    def set_game_position(self, game, njg=99999):
        pos_inicial = "startpos" if game.is_fen_initial() else "fen %s" % game.first_position.fen()
        li = [move.movimiento().lower() for n, move in enumerate(game.li_moves) if n < njg]
        moves = " moves %s" % (" ".join(li)) if li else ""
        if not li:
            self.ucinewgame()
        self.work_ok("position %s%s" % (pos_inicial, moves))
        self.is_white = game.is_white() if njg > 9000 else game.move(njg).is_white()

    def set_fen_position(self, fen):
        self.ucinewgame()
        self.work_ok("position fen %s" % fen)
        self.is_white = "w" in fen

    def ucinewgame(self):
        self.work_ok("ucinewgame")

    def ac_inicio(self, game):
        self.lock_ac = True
        self.set_game_position(game)
        self.reset()
        self.put_line("go infinite")
        self.lock_ac = False

    def ac_inicio_limit(self, game, max_time, max_depth):
        self.lock_ac = True
        self.best_move_done = False
        self.set_game_position(game)
        self.reset()
        env = "go"
        if max_depth:
            env += " depth %d" % max_depth
        elif max_time:
            env += " movetime %d" % max_time
        self.put_line(env)
        self.lock_ac = False

    def ac_lee(self):
        if self.lock_ac:
            return True
        nlines = 0
        for line in self.get_lines():
            if "bestmove" in line:
                self.best_move_done = True
            self.mrm.dispatch(line)
            nlines += 1
        return nlines

    def ac_estado(self):
        self.ac_lee()
        self.mrm.ordena()
        return self.mrm

    def ac_minimo(self, minimo_tiempo, lock_ac):
        self.ac_lee()
        self.mrm.ordena()

        while self.mrm.time_used() * 1000 < minimo_tiempo:
            time.sleep(0.1)

        self.lock_ac = lock_ac
        return self.ac_estado()

    def ac_minimo_td(self, min_time, min_depth, lock_ac):
        self.ac_lee()
        self.mrm.ordena()
        rm = self.mrm.best_rm_ordered()
        while rm.time < min_time or rm.depth < min_depth:
            time.sleep(0.1)
            self.ac_lee()
            rm = self.mrm.best_rm_ordered()
        self.lock_ac = lock_ac
        return self.ac_estado()

    def ac_final(self, minimo_ms_time):
        self.ac_minimo(minimo_ms_time, True)
        self.put_line("stop")
        time.sleep(0.1)
        return self.ac_estado()

    def ac_final_limit(self, min_time):
        if not self.best_move_done:
            self.ac_lee()
            self.mrm.ordena()
            rm = self.mrm.best_rm_ordered()
            while rm.time < min_time and not self.best_move_done:
                time.sleep(0.1)
                self.ac_lee()
                rm = self.mrm.best_rm_ordered()
        return self.ac_estado()

    def analysis_stable(self, game, njg, ktime, kdepth, is_savelines, st_centipawns, st_depths, st_timelimit):
        self.set_game_position(game, njg)
        self.reset()
        if is_savelines:
            self.mrm.save_lines()
        self.put_line("go infinite")

        def lee():
            for line in self.get_lines():
                self.mrm.dispatch(line)
            self.mrm.ordena()
            return self.mrm.best_rm_ordered()

        ok_time = False if ktime else True
        ok_depth = False if kdepth else True
        while self.gui_dispatch(None):
            rm = lee()
            if not ok_time:
                ok_time = rm.time >= ktime
            if not ok_depth:
                ok_depth = rm.depth >= kdepth
            if ok_time and ok_depth:
                break
            time.sleep(0.1)

        if st_timelimit == 0:
            st_timelimit = 999999
        while not self.mrm.is_stable(st_centipawns, st_depths) and self.gui_dispatch(None) and st_timelimit > 0.0:
            time.sleep(0.1)
            st_timelimit -= 0.1
            lee()
        self.put_line("stop")
        return self.mrm

    def set_gui_dispatch(self, gui_dispatch, who_dispatch=None):
        self.gui_dispatch = gui_dispatch
        if who_dispatch is not None:
            self.who_dispatch = who_dispatch

    def set_multipv(self, num_multipv):
        if num_multipv == 0:
            num_multipv = 1
        self.work_ok("setoption name MultiPV value %s" % num_multipv)

    def orden_uci(self):
        self.reset()
        self.put_line("uci")
        li, self.uci_ok = self.wait_list("uciok", 10000)
        self.uci_lines = [x for x in li if x.startswith("id ") or x.startswith("option name")] if self.uci_ok else []

    def set_option(self, name, value):
        if value:
            self.put_line("setoption name %s value %s" % (name, value))
        else:
            self.put_line("setoption name %s" % name)

    def bestmove_game(self, game, max_time, max_depth):
        self.set_game_position(game)
        return self.seek_bestmove(max_time, max_depth, False)

    def bestmove_game_jg(self, game, njg, max_time, max_depth, is_savelines=False):
        self.set_game_position(game, njg)
        return self.seek_bestmove(max_time, max_depth, is_savelines)

    def bestmove_fen(self, fen, max_time, max_depth, is_savelines=False):
        self.set_fen_position(fen)
        return self.seek_bestmove(max_time, max_depth, is_savelines)

    def bestmove_time(self, game, time_white, time_black, inc_time_move):
        self.set_game_position(game)
        return self.seek_bestmove_time(time_white, time_black, inc_time_move)

    def busca_mate(self, game, mate):
        self.ac_inicio(game)
        tm = 10000
        li_r = []
        while tm > 0:
            tm -= 100
            time.sleep(0.1)
            mrm = self.ac_estado()
            li = mrm.bestmoves()
            if li:
                if 0 < li[0].mate <= mate:
                    li_r = li
                    break
        self.ac_final(-1)
        return li_r

    def play_with_return(self, play_return, game, line, max_time, max_depth):
        self.set_game_position(game)

        def dispatch():
            self.direct_dispatch = None
            self.mrm.ordena()
            play_return(self.mrm)

        self.reset()
        self.mrm.set_time_depth(max_time, max_depth)

        self.direct_dispatch = dispatch
        self.working = True
        self.put_line(line)

    def set_humanize(self, movetime):
        self.end_time_humanize = time.time() + movetime

    def not_humanize(self):
        self.end_time_humanize = None

    def play_bestmove_time(self, play_return, game, time_white, time_black, inc_time_move):
        env = "go wtime %d btime %d" % (time_white, time_black)
        if inc_time_move:
            env += " winc %d binc %d" % (inc_time_move, inc_time_move)
        max_time = time_white if self.is_white else time_black
        self.play_with_return(play_return, game, env, max_time, None)

    def play_bestmove_game(self, play_return, game, max_time, max_depth):
        env = "go"
        if max_depth:
            env += " depth %d" % max_depth
        elif max_time:
            env += " movetime %d" % max_time
        self.play_with_return(play_return, game, env, max_time, max_depth)

    def play_bestmove_nodes(self, play_return, game, nodes, max_time, max_depth):
        env = f"go nodes {nodes}"
        self.play_with_return(play_return, game, env, max_time, max_depth)


def nodes_maia(level):
    dic_nodes = {1100: 1, 1200: 2, 1300: 5, 1400: 12, 1500: 30, 1600: 60, 1700: 130, 1800: 300, 1900: 450}
    if not Code.configuration.x_maia_nodes_exponential:
        for elo in dic_nodes:
            dic_nodes[elo] = 1
    return dic_nodes.get(level, 1)


class MaiaEngine(RunEngine):
    def __init__(self, name, exe, li_options_uci=None, num_multipv=0, priority=None, args=None, log=None, level=0):
        RunEngine.__init__(self, name, exe, li_options_uci, num_multipv, priority, args, log)
        self.stopping = False
        self.level = level

        book_name = "1100-1500.bin" if level <= 1500 else "1600-1900.bin"
        book_path = Util.opj(os.path.dirname(exe), book_name)
        self.book = Books.Book("P", book_name, book_path, True)
        self.book.polyglot()
        self.book_select = []
        mp = (level - 1100) // 10
        ap = 40 - 20 * (level - 1100) // 800
        au = 100 - mp - ap
        self.book_select.extend([BOOK_BEST_MOVE] * mp)
        self.book_select.extend([BOOK_RANDOM_PROPORTIONAL] * ap)
        self.book_select.extend([BOOK_RANDOM_UNIFORM] * au)

        self.nodes = nodes_maia(level)

    def play_bestmove_time(self, play_return, game, time_white, time_black, inc_time_move):
        if self.test_book(game):
            play_return(self.mrm)
            return
        env = f"go nodes {self.nodes}"
        max_time = time_white if self.is_white else time_black
        self.play_with_return(play_return, game, env, max_time, None)

    def play_bestmove_game(self, play_return, game, max_time, max_depth):
        if self.test_book(game):
            play_return(self.mrm)
            return
        env = f"go nodes {self.nodes}"
        self.play_with_return(play_return, game, env, max_time, max_depth)

    def play_bestmove_nodes(self, play_return, game, nodes, max_time, max_depth):
        if self.test_book(game):
            play_return(self.mrm)
            return
        env = f"go nodes {nodes}"
        self.play_with_return(play_return, game, env, max_time, max_depth)

    def test_book(self, game):
        if len(game) < 30:
            pv = self.book.eligeJugadaTipo(game.last_position.fen(), random.choice(self.book_select))
            if pv:
                self.mrm.dispatch(f"bestmove {pv}")
                self.mrm.ordena()
                return True
        return False

    def work_bestmove(self, orden, msmax_time):
        self.reset()
        orden = f"go nodes {self.nodes}"
        self.put_line(orden)
        self.wait_mrm("bestmove", msmax_time)

    def reset(self):
        self.mrm = EngineResponse.MultiEngineResponse(self.name, self.is_white)
