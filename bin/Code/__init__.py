import os
import ssl
import subprocess
import sys
from shutil import which

from Code import Util

Util.randomize()

current_dir = os.path.abspath(os.path.realpath(os.path.dirname(sys.argv[0])))
if current_dir:
    os.chdir(current_dir)

lucas_chess = None  # asignado en Translate

folder_OS = Util.opj(current_dir, "OS", sys.platform)

folder_engines = Util.opj(folder_OS, "Engines")
sys.path.insert(0, folder_OS)
sys.path.insert(0, os.path.realpath(os.curdir))

folder_resources = os.path.realpath("../Resources")
folder_root = os.path.realpath("..")

pending = Util.opj(folder_root, "bin", "pending.py")
if os.path.isfile(pending):
    with open(pending, "rt") as f:
        for linea in f:
            exec(linea.rstrip())
    os.remove(pending)


def path_resource(*lista):
    p = folder_resources
    for x in lista:
        p = Util.opj(p, x)
    return os.path.realpath(p)


is_linux = Util.is_linux()
is_windows = not is_linux


def startfile(path: str) -> bool:
    try:
        path = os.path.abspath(path)
        if is_windows:
            os.startfile(path)
        else:  # Linux
            opener = None

            if os.path.isdir(path):
                desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
                if "kde" in desktop and which("dolphin"):
                    opener = "dolphin"
                elif "gnome" in desktop and which("nautilus"):
                    opener = "nautilus"
                elif which("xdg-open"):
                    opener = "xdg-open"
            elif which("xdg-open"):
                opener = "xdg-open"

            if not opener:
                return False

            env = os.environ.copy()
            env.pop("LD_LIBRARY_PATH", None)
            env['DISPLAY'] = os.getenv('DISPLAY', ':0')
            env['DBUS_SESSION_BUS_ADDRESS'] = os.getenv('DBUS_SESSION_BUS_ADDRESS', 'unix:path=/run/user/{os.getuid()}/bus')
            env['HOME'] = os.getenv('HOME', os.path.expanduser('~'))

            subprocess.Popen([opener, path],
                             env=env,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        return True
    except:
        return False


if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
        ssl, "_create_unverified_context", None
):
    ssl._create_default_https_context = getattr(ssl, "_create_unverified_context")

configuration = None
procesador = None

all_pieces = None

tbook = path_resource("Openings", "GMopenings.bin")
tbookPTZ = path_resource("Openings", "fics15.bin")
tbookI = path_resource("Openings", "irina.bin")
xtutor = None

font_mono = "Courier New" if is_windows else "Mono"

list_engine_managers = None

mate_en_dos = 180805

runSound = None

translations = None

analysis_eval = None

eboard = None

dic_colors = None
dic_qcolors = None

dic_markers = {}

themes = None

main_window = None

garbage_collector = None


def get_themes():
    global themes
    if themes is None:
        from Code.Themes import Themes
        themes = Themes.Themes()
    return themes


def relative_root(path):
    # Used only for titles/labels
    try:
        path = os.path.normpath(os.path.abspath(path))
        rel = os.path.relpath(path, folder_root)
        if not rel.startswith(".."):
            path = rel
    except ValueError:
        pass

    return path


BASE_VERSION = "B"  # Para el control de updates que necesitan reinstalar entero
VERSION = "R 2.21-FP-8"
DEBUG = False
DEBUG_ENGINES = False

if DEBUG:
    import traceback
    import sys
    import time


    def pr(*x):
        lx = len(x) - 1

        for n, cl in enumerate(x):
            sys.stdout.write(str(cl))
            if n < lx:
                sys.stdout.write(" ")


    def prln(*x):
        pr(*x)
        pr("\n")
        return True


    def prlns(*x):
        prln("-" * 80)
        prln(*x)
        stack()
        prln("-" * 80)
        return True


    def stack(si_previo=False):
        if si_previo:
            pr("-" * 80 + "\n")
            pr(traceback.format_stack())
            pr("\n" + "-" * 80 + "\n")
        for line in traceback.format_stack()[:-1]:
            pr(line.strip() + "\n")


    def printf(*txt, sif=False):
        with open("stack.txt", "at", encoding="utf-8") as q:
            for t in txt:
                q.write(str(t) + " ")
            q.write("\n")
        if sif:
            prln(txt)


    def xpr(name, line):
        t = time.time()
        if name:
            li = name.split(" ")
            name = li[0]

        pr("%0.02f %s %s" % (t - tdbg[0], name, line))
        tdbg[0] = t
        return True


    tdbg = [time.time(), 0]
    if DEBUG_ENGINES:
        prln("", "Modo debug engine")


    def ini_timer(txt=None):
        tdbg[1] = time.time()
        if txt:
            prln(txt)


    def end_timer(txt=None):
        t = time.time() - tdbg[1]
        c = txt + " " if txt else ""
        c += "%0.03f" % t
        prln(c)


    # def dbg_print(move_base):
    #     from Code.Base import Game, Position, Move
    #     game: Game.Game = move_base.game
    #     position: Position.Position = game.first_position.copia()
    #     move: Move.Move
    #     for move in move_base.game.li_moves:
    #         ok, li = position.play(move.from_sq, move.to_sq, move.promotion)
    #         if not ok:
    #             stack()
    #         break

    import builtins

    for key, routine in (
            ("stack", stack),
            ("pr", pr),
            ("prln", prln),
            ("prlns", prlns),
            ("ini_timer", ini_timer),
            ("end_timer", end_timer)):
        setattr(builtins, key, routine)

    # builtins.__dict__["dbg_print"] = dbg_print
    prln("Modo debug")
