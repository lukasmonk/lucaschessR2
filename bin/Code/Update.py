import os
import shutil
import urllib.request
import zipfile

import Code
from Code import Util
from Code.Board import Eboard
from Code.QT import QTUtil2, SelectFiles

WEBUPDATES = "https://lucaschess.pythonanywhere.com/static/updater/updates_%s.txt" % (
    "win32" if Code.is_windows else "linux"
)

WEBUPDATES_EBOARD_VERSION = "https://lucaschess.pythonanywhere.com/static/updater/version_eboards_%s.txt" % (
    "win32" if Code.is_windows else "linux"
)

WEBUPDATES_EBOARD_ZIP = "https://lucaschess.pythonanywhere.com/static/updater/eboards_%s.zip" % (
    "win32" if Code.is_windows else "linux"
)


def update_file(titulo, urlfichero, tam):
    shutil.rmtree("actual", ignore_errors=True)
    Util.create_folder("actual")

    # Se trae el file
    global progreso, is_beginning
    progreso = QTUtil2.BarraProgreso(None, titulo, _("Updating..."), 100).mostrar()
    is_beginning = True

    def hook(bloques, tambloque, tamfichero):
        global progreso, is_beginning
        if is_beginning:
            total = tamfichero / tambloque
            if tambloque * total < tamfichero:
                total += 1
            progreso.set_total(total)
            is_beginning = False
        progreso.inc()

    local_file = urlfichero.split("/")[-1]
    local_file = "actual/%s" % local_file
    urllib.request.urlretrieve(urlfichero, local_file, hook)

    is_canceled = progreso.is_canceled()
    progreso.cerrar()

    if is_canceled:
        return False

    # Comprobamos que se haya traido bien el file
    if tam != Util.filesize(local_file):
        return False

    # Se descomprime
    zp = zipfile.ZipFile(local_file, "r")
    zp.extractall("actual")

    # Se ejecuta act.py
    exec(open("actual/act.py").read())

    return True


def update_eboard(main_window):
    version_local = Eboard.version()

    ftxt = Code.configuration.ficheroTemporal("txt")
    ok = Util.urlretrieve(WEBUPDATES_EBOARD_VERSION, ftxt)

    if not ok:
        return

    with open(ftxt, "rt") as f:
        version_remote = f.read().strip()

    if version_local == version_remote:
        return

    um = QTUtil2.one_moment_please(main_window, _("Downloading eboards drivers"))

    fzip = Code.configuration.ficheroTemporal("zip")
    ok = Util.urlretrieve(WEBUPDATES_EBOARD_ZIP, fzip)

    um.final()

    if ok:
        zfobj = zipfile.ZipFile(fzip)
        for name in zfobj.namelist():
            path_dll = Util.opj(Code.folder_OS, "DigitalBoards", name)
            with open(path_dll, "wb") as outfile:
                outfile.write(zfobj.read(name))
        zfobj.close()

        with open(Util.opj(Code.folder_OS, "DigitalBoards", "news"), "rt", encoding="utf-8") as f:
            news = f.read().strip()

        QTUtil2.message(
            main_window, _("Updated the eboards drivers") + "\n %s: %s\n%s" % (_("Version"), version_remote, news)
        )

    else:

        QTUtil2.message_error(main_window, _("It has not been possible to update the eboards drivers"))


def update(main_window):
    if Code.configuration.x_digital_board:
        if Code.eboard:
            Code.eboard.deactivate()
        update_eboard(main_window)

    # version = "R 1.01 -> R01.01 -> 01.01 -> 0101 -> bytes
    current_version = Code.VERSION.replace(" ", "0").replace(".", "")[1:].encode()
    base_version = Code.BASE_VERSION.encode()
    mens_error = None
    done_update = False

    try:
        f = urllib.request.urlopen(WEBUPDATES)
        for blinea in f:
            act = blinea.strip()
            if act and not act.startswith(b"#"):  # Comentarios
                li = act.split(b" ")
                if len(li) == 4 and li[3].isdigit():
                    base, version, urlfichero, tam = li
                    if base == base_version:
                        if current_version < version:
                            if not update_file(_X(_("version %1"), version.decode()), urlfichero.decode(), int(tam)):
                                mens_error = _X(
                                    _("An error has occurred during the upgrade to version %1"), version.decode()
                                )
                            else:
                                done_update = True

        f.close()
    except urllib.error.URLError:
        mens_error = _("Encountered a network problem, cannot access the Internet")

    if mens_error:
        QTUtil2.message_error(main_window, mens_error)
        return False

    if not done_update:
        QTUtil2.message_bold(main_window, _("There are no pending updates"))
        return False

    return True


def test_update(procesador):
    current_version = Code.VERSION.replace(" ", "0").replace(".", "")[1:].encode()
    base_version = Code.BASE_VERSION.encode()
    nresp = 0
    try:
        f = urllib.request.urlopen(WEBUPDATES)
        for blinea in f:
            act = blinea.strip()
            if act and not act.startswith(b"#"):  # Comentarios
                li = act.split(b" ")
                if len(li) == 4 and li[3].isdigit():
                    base, version, urlfichero, tam = li
                    if base == base_version:
                        if current_version < version:
                            nresp = QTUtil2.question_withcancel_123(
                                procesador.main_window,
                                _("Update"),
                                _("Version %s is ready to update") % version.decode(),
                                _("Update now"),
                                _("Do not do anything"),
                                _("Don't ask again"),
                            )
                            break
        f.close()
    except:
        pass

    if nresp == 1:
        procesador.actualiza()
    elif nresp == 3:
        procesador.configuration.x_check_for_update = False
        procesador.configuration.graba()


def update_manual(main_window):
    config = Code.configuration

    dic = config.read_variables("MANUAL_UPDATE")

    folder = dic.get("FOLDER", config.folder_userdata())

    path_zip = SelectFiles.leeFichero(main_window, folder, "zip")
    if not path_zip or not Util.exist_file(path_zip):
        return

    dic["FOLDER"] = os.path.dirname(path_zip)
    config.write_variables("MANUAL_UPDATE", dic)

    folder_actual = Util.opj(Code.folder_root, "bin", "actual")
    shutil.rmtree(folder_actual, ignore_errors=True)
    Util.create_folder(folder_actual)

    shutil.copy(path_zip, folder_actual)

    local_file = Util.opj(folder_actual, os.path.basename(path_zip))

    zp = zipfile.ZipFile(local_file, "r")
    zp.extractall(folder_actual)

    path_act_py = Util.opj(folder_actual, "act.py")

    exec(open(path_act_py).read())

    return True
