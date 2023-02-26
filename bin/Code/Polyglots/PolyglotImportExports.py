import math
import os
import time

import FasterCode
from PySide2 import QtCore, QtWidgets

from Code import Util
from Code.Base.Constantes import CALCWEIGHT_NUMGAMES, CALCWEIGHT_SCORE, FEN_INITIAL, CALCWEIGHT_NUMGAMES_SCORE
from Code.Databases import DBgames
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import SelectFiles
from Code.SQL import UtilSQL


class PolyglotExport:
    def __init__(self, wpolyglot):
        self.wpolyglot = wpolyglot
        self.configuration = wpolyglot.configuration
        self.db_entries = wpolyglot.db_entries

    def exportar(self):
        resp = self.export_polyglot_config()
        if resp is None:
            return None
        path_bin, uniform = resp
        self.export_create_polyglot(path_bin, uniform)

    def export_polyglot_config(self):
        return export_polyglot_config(self.wpolyglot, self.configuration, self.wpolyglot.title + ".bin")

    def export_create_polyglot(self, path_bin, uniform):
        total = len(self.db_entries)

        bp = QTUtil2.BarraProgreso(self.wpolyglot, _("Create book"), os.path.basename(path_bin), total)
        wpoly = FasterCode.PolyglotWriter(path_bin)

        bp.mostrar()
        li_current = []
        key_current = 0

        def save():
            if not li_current:
                return
            factor = None
            if not uniform:
                weight_max = max(xentry.weight for xentry in li_current)
                if weight_max >= 32767:
                    factor = 32767 / weight_max
                li_current.sort(key=lambda x: x.weight, reverse=True)
            for xentry in li_current:
                if xentry.weight > 0:
                    if uniform:
                        xentry.weight = 100
                    elif factor:
                        xentry.weight = max(int(factor * xentry.weight), 1)
                    if xentry.score > 32767:
                        xentry.score = 32767
                    if xentry.depth > 255:
                        xentry.depth = 255
                    if xentry.learn > 255:
                        xentry.learn = 255
                    wpoly.write(xentry)

        for entry in self.db_entries.get_all():
            bp.inc()
            if entry is None:
                break
            if entry.key != key_current:
                save()
                key_current = entry.key
                li_current = [entry]
            else:
                li_current.append(entry)
        save()

        wpoly.close()
        bp.close()
        QTUtil2.message_bold(self.wpolyglot, "%s\n%s" % (_("Saved"), path_bin))


class PolyglotImport:
    def __init__(self, wpolyglot):
        self.wpolyglot = wpolyglot
        self.configuration = wpolyglot.configuration
        self.db_entries = wpolyglot.db_entries

    def importar(self):
        menu = QTVarios.LCMenu(self.wpolyglot)
        menu.opcion("pgn", _("PGN"), Iconos.Board())
        menu.separador()
        menu.opcion("database", _("Database"), Iconos.Database())
        menu.separador()
        menu.opcion("polyglot", _("Polyglot book"), Iconos.Libros())
        menu.separador()
        resp = menu.lanza()
        if resp == "pgn":
            self.import_pgn()
        elif resp == "database":
            self.import_db()
        elif resp == "polyglot":
            self.import_polyglot()

    def menu_collisions(self):
        menu = QTVarios.LCMenu(self.wpolyglot)
        menu.opcion(
            "", _("What to do in case of collisions"), is_disabled=True, tipoLetra=Controles.TipoLetra(peso=700)
        )
        menu.separador()
        menu.opcion("replace", _("Replace"), Iconos.Recuperar())
        menu.separador()
        menu.opcion("add", _("Add"), Iconos.Mas())
        menu.separador()
        menu.opcion("discard", _("Discard"), Iconos.Menos())
        return menu.lanza()

    def import_polyglot(self):
        dic = self.configuration.read_variables("POLYGLOT_IMPORT")

        folder = dic.get("FOLDER_BIN", "")

        path_bin = SelectFiles.leeFichero(self.wpolyglot, folder, "bin", titulo=_("Polyglot bin file name"))
        if not path_bin:
            return

        dic["FOLDER_BIN"] = os.path.dirname(path_bin)
        self.configuration.write_variables("POLYGLOT_IMPORT", dic)

        total = Util.filesize(path_bin) // 16
        if total <= 0:
            return

        collisions = "replace"
        if len(self.db_entries) > 0:
            collisions = self.menu_collisions()
            if not collisions:
                return

        bp = QTUtil2.BarraProgreso(self.wpolyglot, _("Import"), os.path.basename(path_bin), total)

        pol_import = FasterCode.Polyglot(path_bin)
        for entry in pol_import:
            bp.inc()
            self.db_entries.replace_entry(entry, collisions)
        self.db_entries.commit()
        pol_import.close()
        bp.close()
        QTUtil2.message_bold(self.wpolyglot, "%s\n%s" % (_("Imported"), path_bin))
        self.wpolyglot.set_position(self.wpolyglot.position, False)

    def import_polyglot_config(self, titulo):
        return import_polyglot_config(self.wpolyglot, self.configuration, titulo, True)

    def import_db(self):
        path_db = QTVarios.select_db(self.wpolyglot, self.configuration, True, False)
        if not path_db:
            return

        titulo = "%s %s" % (_("Import"), os.path.basename(path_db))
        resp = self.import_polyglot_config(titulo)
        if resp is None:
            return
        plies, st_side, st_results, ru, min_games, min_score, calc_weight, save_score, collisions = resp

        db = UtilSQL.DictBig()

        def fsum(keymove, pt):
            num, pts = db.get(keymove, (0, 0))
            num += 1
            pts += pt
            db[keymove] = num, pts

        dltmp = ImportarPGNDB(self.wpolyglot, os.path.basename(path_db))
        dltmp.show()

        db_games = DBgames.DBgames(path_db)

        ok = add_db(db_games, plies, st_results, st_side, ru, time.time, 1.2, dltmp.dispatch, fsum)
        dltmp.close()
        if not ok:
            db.close()
            db_games.close()
            return

        self.merge(db, min_games, min_score, calc_weight, save_score, collisions)

    def import_pgn(self):
        li_path_pgn = SelectFiles.select_pgns(self.wpolyglot)
        if not li_path_pgn:
            return
        titulo = "%s %d %s" % (_("Import"), len(li_path_pgn), _("PGN"))
        resp = self.import_polyglot_config(titulo)
        if resp is None:
            return
        plies, st_side, st_results, ru, min_games, min_score, calc_weight, save_score, collisions = resp

        db = UtilSQL.DictBig()
        for path_pgn in li_path_pgn:

            def fsum(keymove, pt):
                num, pts = db.get(keymove, (0, 0))
                num += 1
                pts += pt
                db[keymove] = num, pts

            dltmp = ImportarPGNDB(self.wpolyglot, os.path.basename(path_pgn))
            dltmp.show()
            ok = self.add_pgn(path_pgn, plies, st_results, st_side, ru.encode(), time.time, 1.2, dltmp.dispatch, fsum)
            dltmp.close()
            if not ok:
                db.close()
                return

        self.merge(db, min_games, min_score, calc_weight, save_score, collisions)

    def add_pgn(self, path_pgn, plies, st_results, st_side, bunknown_convert, ftime, time_dispatch, dispatch, fsum):
        time_prev = ftime()
        cancelled = False
        bfen_inicial = FEN_INITIAL.encode()

        with FasterCode.PGNreader(path_pgn, plies) as fpgn:
            bsize = fpgn.size
            dispatch(True, bsize, 0)
            num_games = 0
            for (body, raw, pv, liFens, bdCab, bdCablwr, btell) in fpgn:
                if len(liFens) == 0:
                    continue

                if (ftime() - time_prev) >= time_dispatch:
                    time_prev = ftime()
                    if not dispatch(False, btell, num_games):
                        cancelled = True
                        break

                result = bdCab.get(b"RESULT", b"*")
                if result == b"*":
                    result = bunknown_convert
                if not (result in st_results):
                    continue

                if result == b"1-0":
                    pw = 2
                    pb = 0
                elif result == b"0-1":
                    pw = 0
                    pb = 2
                else:  # if result == b"1/2-1/2":
                    pw = 1
                    pb = 1

                if b"FEN" in bdCab:
                    bfen0 = bdCab[b"FEN"]
                else:
                    bfen0 = bfen_inicial
                lipv = pv.split(" ")
                is_white = b" w" in bfen0
                for pos, bfen in enumerate(liFens):
                    if is_white in st_side:
                        mv = lipv[pos]
                        move = FasterCode.string_movepolyglot(mv)
                        key = FasterCode.hash_polyglot(bfen0)
                        keymove = FasterCode.keymove_str(key, move)
                        pt = pw if is_white else pb
                        fsum(keymove, pt)

                    is_white = not is_white
                    bfen0 = bfen

                num_games += 1

        return not cancelled

    def merge(self, db, min_games, min_score, calc_weight, save_score, collisions):
        um = QTUtil2.unMomento(self.wpolyglot, _("Saving..."))
        g_nueva = iter(fuente_dbbig(db, min_games, min_score, calc_weight, save_score))

        for n_key, dic_data in g_nueva:
            if n_key is None:
                break
            for move, entry in dic_data.items():
                self.db_entries.replace_entry(entry, collisions)
        db.close()

        self.wpolyglot.set_position(self.wpolyglot.position, False)
        um.final()


class ImportarPGNDB(QtWidgets.QDialog):
    def __init__(self, parent, titulo):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self.is_canceled = False

        self.setWindowTitle(titulo)
        self.setWindowIcon(Iconos.Import8())
        self.fontB = Controles.TipoLetra(puntos=10, peso=75)

        self.lbgames_readed = Controles.LB(self).ponFuente(self.fontB)

        self.bp = QtWidgets.QProgressBar()
        self.bp.setFont(self.fontB)

        self.lb_previsto = Controles.LB(self)
        self.li_times = []
        self.time_inicial = None
        self.invalid_prevision = True
        self.total = None

        self.bt_cancelar = Controles.PB(self, _("Cancel"), self.cancelar, plano=False).ponIcono(Iconos.Delete())

        lyBT = Colocacion.H().relleno().control(self.bt_cancelar)

        layout = Colocacion.V()
        layout.control(self.lbgames_readed)
        layout.control(self.bp)
        layout.control(self.lb_previsto)
        layout.espacio(20)
        layout.otro(lyBT)

        self.setLayout(layout)

        self.setMinimumWidth(480)

    def test_invalid_prevision(self):
        if len(self.li_times) < 5:
            return
        ntm = len(self.li_times[-5:])
        media = 0.0
        for tm in self.li_times:
            media += tm
        media /= ntm
        sdev = 0
        for tm in self.li_times:
            sdev += (tm - media) ** 2
        sdev = math.sqrt(sdev / (ntm - 1))

        if sdev < media / 10:
            self.invalid_prevision = False

    def cancelar(self):
        self.is_canceled = True

    def dispatch(self, is_total, valor, num_games):
        if is_total:
            self.bp.setRange(0, valor)
            self.time_inicial = time.time()
            self.total = valor
        elif valor > 0:
            self.bp.setValue(valor)
            self.lbgames_readed.set_text("%s: %d" % (_("Games read"), num_games))
            tm = time.time() - self.time_inicial

            tm1 = tm / valor
            if self.invalid_prevision:
                self.li_times.append(tm1)
                self.test_invalid_prevision()
            else:
                previsto = int(tm1 * (self.total - valor))
                minutos = previsto // 60
                seconds = previsto % 60
                lb_min = _("minutes") if minutos > 1 else _("minute")
                self.lb_previsto.set_text(
                    "%s: %d %s %d %s" % (_("Pending time"), minutos, lb_min, seconds, _("seconds"))
                )

        QTUtil.refresh_gui()
        return not self.is_canceled


def fuente_dbbig(db, min_games, min_score, calc_weight, save_score):
    db_iter = iter(db.items())
    current_key = None
    dic = None

    def pasa_filtro(dic_act):
        li = []
        max_weight = 0
        for imove, (num, suma) in dic_act.items():
            if (num < min_games) or ((suma / num) < (min_score / 50)):
                li.append(imove)
            elif suma > max_weight:
                max_weight = suma
        if len(li) > 0:
            if len(li) == len(dic_act):
                return False
            for imove in li:
                del dic_act[imove]
        if max_weight > 32767:
            factor = max_weight / 32767
            for imove, (num, suma) in dic.items():
                dic_act[imove] = (num // factor, suma // factor)
        return True

    def dic_entry(key, dic_act):
        d = {}
        for imove, (num, sum) in dic_act.items():
            e = FasterCode.Entry()
            e.key = key
            e.move = imove
            score = (sum / num) / 2.0 if num > 0.0 else 0.0
            if calc_weight == CALCWEIGHT_NUMGAMES:
                e.weight = num
            elif calc_weight == CALCWEIGHT_NUMGAMES_SCORE:
                e.weight = int(sum * score)
            else:
                e.weight = int(score * 10_000)
            if save_score:
                e.score = int(score * 10_000)
            d[imove] = e
        return d

    while True:
        k, v = next(db_iter, (None, None))
        if k is None:
            break
        key, move = FasterCode.str_keymove(k)
        if key != current_key:
            if current_key is not None:
                if pasa_filtro(dic):
                    yield current_key, dic_entry(current_key, dic)
            current_key = key
            dic = {}
        dic[move] = v
    if current_key is not None:
        if pasa_filtro(dic):
            yield current_key, dic_entry(current_key, dic)

    yield None, None


def create_bin_from_dbbig(owner, path_bin, db, min_games, min_score, calc_weight, save_score):
    g_nueva = iter(fuente_dbbig(db, min_games, min_score, calc_weight, save_score))

    um = QTUtil2.unMomento(owner, _("Saving..."))
    wpoly = FasterCode.PolyglotWriter(path_bin)

    for n_key, dic_data in g_nueva:
        if n_key is not None:
            li = list(dic_data.keys())
            li.sort(key=lambda x: dic_data[x].weight, reverse=True)
            for imv in li:
                ent = dic_data[imv]
                if ent.weight > 0:
                    wpoly.write(ent)

    wpoly.close()

    um.final()
    QTUtil2.message_bold(owner, "%s\n%s" % (_("Saved"), path_bin))


def import_polyglot_config(owner, configuration, titulo, with_collisions):
    dic = configuration.read_variables("POLYGLOT_IMPORT")

    form = FormLayout.FormLayout(owner, titulo, Iconos.Import8(), anchoMinimo=440)
    form.separador()

    form.spinbox(_("Maximum movements"), 1, 999, 60, dic.get("PLIES", 50))
    form.separador()

    li_options = (("%s + %s" % (_("White"), _("Black")), {True, False}), (_("White"), {True}), (_("Black"), {False}))
    form.combobox(_("Side to include"), li_options, dic.get("SIDE", {True, False}))
    form.separador()

    form.apart_simple(_("Include games when result is"))
    form.checkbox("1-0", dic.get("1-0", True))
    form.checkbox("0-1", dic.get("0-1", True))
    form.checkbox("1/2-1/2", dic.get("1/2-1/2", True))
    form.separador()
    li_options = ((_("Discard"), ""), ("1-0", "1-0"), ("0-1", "0-1"), ("1/2-1/2", "1/2-1/2"))
    form.combobox("%s %s" % (_("Unknown result"), _("convert to")), li_options, dic.get("*", ""))
    form.separador()

    form.spinbox(_("Minimum number of games"), 1, 999999, 50, dic.get("MINGAMES", 3))
    form.spinbox(_("Minimum score") + " (0-100)", 0, 100, 50, dic.get("MINSCORE", 0))

    form.separador()
    li_options = (
        (_("Number of games"), CALCWEIGHT_NUMGAMES),
        (_("Number of games") + " * " + _("Score"), CALCWEIGHT_NUMGAMES_SCORE),
        (_("Score") + "% * 100", CALCWEIGHT_SCORE),
    )
    form.combobox(_("Calculation of the weight"), li_options, dic.get("CALCWEIGHT", CALCWEIGHT_NUMGAMES))
    form.separador()
    form.checkbox(_("Save score"), dic.get("SAVESCORE", False))
    form.separador()

    if with_collisions:
        li_options = ((_("Replace"), "replace"), (_("Add"), "add"), (_("Discard"), "discard"))
        form.combobox(_("What to do in case of collisions"), li_options, dic.get("COLLISIONS", "replace"))

    resultado = form.run()

    if not resultado:
        return None
    accion, resp = resultado
    if with_collisions:
        plies, st_side, r1_0, r0_1, r1_1, ru, min_games, min_score, calc_weight, save_score, collisions = resp
    else:
        plies, st_side, r1_0, r0_1, r1_1, ru, min_games, min_score, calc_weight, save_score = resp
    if not (r1_0 or r0_1 or r1_1 or ru != ""):
        return None

    st_results = set()
    if r1_0:
        st_results.add(b"1-0")
    if r1_1:
        st_results.add(b"1/2-1/2")
    if r0_1:
        st_results.add(b"0-1")
    if ru != "":
        st_results.add(b"*")

    dic["PLIES"] = plies
    dic["SIDE"] = st_side
    dic["1-0"] = r1_0
    dic["0-1"] = r0_1
    dic["1/2-1/2"] = r1_1
    dic["*"] = ru
    dic["MINGAMES"] = min_games
    dic["MINSCORE"] = min_score
    dic["CALCWEIGHT"] = calc_weight
    dic["SAVESCORE"] = save_score
    configuration.write_variables("POLYGLOT_IMPORT", dic)

    if with_collisions:
        return plies, st_side, st_results, ru, min_games, min_score, calc_weight, save_score, collisions
    else:
        return plies, st_side, st_results, ru, min_games, min_score, calc_weight, save_score


def export_polyglot_config(owner, configuration, file_nom_def):
    dic = configuration.read_variables("POLYGLOT_EXPORT")
    form = FormLayout.FormLayout(owner, _("Export to"), Iconos.Export8(), anchoMinimo=440)
    form.separador()

    folder = dic.get("FOLDER", "")
    file_def = os.path.realpath(os.path.join(folder, file_nom_def))
    form.file(_("Polyglot book"), "bin", True, file_def)
    form.separador()
    form.checkbox(_("Uniform distribution"), dic.get("UNIFORM", False))
    form.separador()

    resultado = form.run()

    if not resultado:
        return None
    accion, resp = resultado
    path_bin, uniform = resp
    if not path_bin:
        return None

    dic["FOLDER"] = os.path.dirname(path_bin)
    dic["UNIFORM"] = uniform
    configuration.write_variables("POLYGLOT_EXPORT", dic)

    path_bin = os.path.realpath(path_bin)
    if Util.exist_file(path_bin):
        yn = QTUtil2.preguntaCancelar(
            owner,
            _X(_("The file %1 already exists, what do you want to do?"), os.path.basename(path_bin)),
            si=_("Overwrite"),
            no=_("Choose another"),
        )
        if yn is None:
            return
        if not yn:
            return export_polyglot_config(owner, configuration, os.path.basename(path_bin))

    return path_bin, uniform


def add_db(db, plies, st_results, st_side, unknown_convert, ftime, time_dispatch, dispatch, fsum):
    time_prev = ftime()
    cancelled = False
    st_results = {x.decode() for x in st_results}

    dispatch(True, len(db), 0)
    for num_games, (xpv, result) in enumerate(db.yield_polyglot()):
        if (ftime() - time_prev) >= time_dispatch:
            time_prev = ftime()
            if not dispatch(False, num_games, num_games):
                cancelled = True
                break
        if not (result in st_results):
            continue
        if result == "*":
            result = unknown_convert

        if result == "1-0":
            pw = 2
            pb = 0
        elif result == "0-1":
            pw = 0
            pb = 2
        else:  # if result == b"1/2-1/2":
            pw = 1
            pb = 1

        if xpv.startswith("|"):
            nada, fen, xpv = xpv.split("|")
        else:
            fen = FEN_INITIAL
        lipv = FasterCode.xpv_lipv(xpv)[:plies]
        is_white = " w" in fen
        FasterCode.set_fen(fen)
        for mv in lipv:
            if is_white in st_side:
                move = FasterCode.string_movepolyglot(mv)
                fen = FasterCode.get_fen()
                key = FasterCode.hash_polyglot8(fen)
                keymove = FasterCode.keymove_str(key, move)
                pt = pw if is_white else pb
                fsum(keymove, pt)
            FasterCode.make_move(mv)
            is_white = not is_white

    return not cancelled
