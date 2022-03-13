import sys
import os
import ssl

current_dir = os.path.abspath(os.path.realpath(os.path.dirname(sys.argv[0])))
if current_dir:
    os.chdir(current_dir)

lucas_chess = None  # asignado en Translate

folder_OS = os.path.join(current_dir, "OS", sys.platform)

folder_engines = os.path.join(folder_OS, "Engines")
sys.path.insert(0, folder_OS)
sys.path.insert(0, os.path.realpath(os.curdir))

folder_resources = os.path.realpath("../Resources")
folder_root = os.path.realpath("..")

pending = os.path.join(folder_root, "bin", "pending.py")
if os.path.isfile(pending):
    with open(pending, "rt") as f:
        for linea in f:
            exec(linea.rstrip())
    os.remove(pending)


def path_resource(*lista):
    p = folder_resources
    for x in lista:
        p = os.path.join(p, x)
    return os.path.realpath(p)


is_linux = sys.platform.startswith("linux")
is_windows = not is_linux

if is_linux:
    if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(ssl, "_create_unverified_context", None):
        ssl._create_default_https_context = ssl._create_unverified_context
    startfile = os.system
else:
    if not sys.argv[0].endswith(".py"):
        os.environ["QT_PLUGIN_PATH"] = os.path.join(current_dir, "extlibs", "PySide2", "plugins")
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(
            current_dir, "extlibs", "PySide2", "plugins", "platform"
        )
    startfile = os.startfile


configuration = None
procesador = None

todasPiezas = None

tbook = path_resource("Openings", "GMopenings.bin")
tbookPTZ = path_resource("Openings", "fics15.bin")
tbookI = path_resource("Openings", "irina.bin")
xtutor = None

font_mono = "Courier New" if is_windows else "Mono"

list_engine_managers = None

mate_en_dos = 175522

runSound = None

translations = None

analysis_eval = None

eboard = None


def relative_root(path):
    try:
        path = os.path.abspath(path)
        rel = os.path.relpath(path, folder_root)
        if not rel.startswith(".."):
            path = rel
    except ValueError:
        pass

    return path


BASE_VERSION = "B"  # Para el control de updates que necesitan reinstalar entero
VERSION = "R2.0"
DEBUG = False
DEBUG_ENGINE = False

if DEBUG:
    import traceback
    import sys
    import time

    def prlk(*x):

        lx = len(x) - 1

        for n, l in enumerate(x):
            sys.stdout.write(str(l))
            if n < lx:
                sys.stdout.write(" ")

    def prln(*x):
        prlk(*x)
        sys.stdout.write("\n")
        return True

    def stack(si_previo=False):
        if si_previo:
            prlk("-" * 80 + "\n")
            prlk(traceback.format_stack())
            prlk("\n" + "-" * 80 + "\n")
        for line in traceback.format_stack()[:-1]:
            prlk(line.strip() + "\n")

    def xpr(name, line):
        t = time.time()
        if name:
            li = name.split(" ")
            name = li[0]

        prlk("%0.02f %s %s" % (t - tdbg[0], name, line))
        tdbg[0] = t
        return True

    if DEBUG_ENGINE:
        tdbg = [time.time()]
        xpr("", "Modo debug engine")

    prln("Modo debug PYLCR2")
