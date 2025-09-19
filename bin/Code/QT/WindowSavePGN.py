import encodings
import os

import chardet.universaldetector
from PySide2 import QtWidgets

import Code
from Code import Util
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2, SelectFiles
from Code.QT import QTVarios
from Code.Translations import TrListas


def read_config_savepgn() -> dict:
    return Code.configuration.read_variables("SAVEPGN")


def write_config_savepgn(dic: dict) -> None:
    Code.configuration.write_variables("SAVEPGN", dic)


class WBaseSave(QtWidgets.QWidget):
    history_list: list
    codec: str
    seventags: bool
    dic_result: dict

    def __init__(self, wowner, configuration, with_remcomments=False):
        QtWidgets.QWidget.__init__(self, wowner)

        self.wowner = wowner
        self.file = ""
        self.configuration = configuration
        self.with_remcomments = with_remcomments
        self.vars_read()

        lb_file = Controles.LB(self, _("File to save") + ": ")
        bt_history = Controles.PB(self, "", self.history).ponIcono(Iconos.Favoritos(), 24).ponToolTip(_("Previous"))
        bt_boxrooms = (
            Controles.PB(self, "", self.boxrooms).ponIcono(Iconos.BoxRooms(), 24).ponToolTip(_("Boxrooms PGN"))
        )
        self.bt_file = Controles.PB(self, "", self.file_select, plano=False).anchoMinimo(300)

        # Codec
        lb_codec = Controles.LB(self, _("Encoding") + ": ")
        li_codecs = [k for k in set(v for k, v in encodings.aliases.aliases.items())]
        li_codecs.sort()
        li_codecs = [(k, k) for k in li_codecs]
        li_codecs.insert(0, (_("Same as file"), "file"))
        li_codecs.insert(0, ("%s: %s" % (_("By default"), _("UTF-8")), "default"))
        self.cb_codecs = Controles.CB(self, li_codecs, self.codec)

        # Rest
        self.chb_overwrite = Controles.CHB(self, _("Overwrite"), False)
        if with_remcomments:
            self.chb_remove_c_v = Controles.CHB(self, _("Remove comments and variations"), False)

        self.chb_seventags = Controles.CHB(self, _("With the seven standard labels (STR)"), True)

        ly_f = Colocacion.H().control(lb_file).control(self.bt_file).control(bt_history).control(bt_boxrooms).relleno(1)
        ly_c = Colocacion.H().control(lb_codec).control(self.cb_codecs).relleno(1)
        ly = Colocacion.V().espacio(15).otro(ly_f).otro(ly_c).control(self.chb_overwrite)
        if with_remcomments:
            ly.control(self.chb_remove_c_v)
        ly.control(self.chb_seventags)
        ly.relleno(1)

        self.chb_overwrite.hide()

        self.setLayout(ly)

    def file_select(self):
        last_dir = ""
        if self.file:
            last_dir = os.path.dirname(self.file)
        elif self.history_list:
            last_dir = os.path.dirname(self.history_list[0])
            if not os.path.isdir(last_dir):
                last_dir = ""
        if not last_dir:
            last_dir = self.configuration.carpeta
        fich = SelectFiles.leeCreaFichero(self, last_dir, "pgn")
        if fich:
            if not fich.lower().endswith(".pgn"):
                fich += ".pgn"
            self.file = fich
            self.show_file()

    def show_file(self):
        self.file = os.path.realpath(self.file)
        self.bt_file.set_text(self.file)
        if os.path.isfile(self.file):
            self.chb_overwrite.show()
        else:
            self.chb_overwrite.hide()
        self.wowner.check_toolbar()

    def vars_read(self):
        dic_vars = read_config_savepgn()
        self.history_list = dic_vars.get("LIHISTORICO", [])
        self.codec = dic_vars.get("CODEC", "default")
        self.seventags = dic_vars.get("SEVENTAGS", True)

    def vars_save(self):
        if self.file:
            dic_vars = read_config_savepgn()
            if self.file in self.history_list:
                del self.history_list[self.history_list.index(self.file)]
            self.history_list.insert(0, self.file)
            dic_vars["LIHISTORICO"] = self.history_list
            dic_vars["CODEC"] = self.cb_codecs.valor()
            dic_vars["SEVENTAGS"] = self.chb_seventags.isChecked()
            write_config_savepgn(dic_vars)

    def history(self):
        menu = QTVarios.LCMenu(self, puntos=9)
        menu.setToolTip(_("To choose: <b>left button</b> <br>To erase: <b>right button</b>"))
        rp = QTVarios.rondo_puntos()
        for pos, txt in enumerate(self.history_list):
            menu.opcion(pos, txt, rp.otro())
        pos = menu.lanza()
        if pos is not None:
            if menu.siIzq:
                self.file = self.history_list[pos]
                self.show_file()
            elif menu.siDer:
                del self.history_list[pos]
        self.wowner.check_toolbar()

    def boxrooms(self):
        menu = QTVarios.LCMenu(self, puntos=9)
        menu.setToolTip(_("To choose: <b>left button</b> <br>To erase: <b>right button</b>"))

        ico_tras = Iconos.BoxRoom()
        boxrooms = self.configuration.boxrooms()
        li_tras = boxrooms.lista()
        for ntras, uno in enumerate(li_tras):
            folder, boxroom = uno
            menu.opcion((0, ntras), "%s  (%s)" % (boxroom, folder), ico_tras)
        menu.separador()
        menu.opcion((1, 0), _("New boxroom"), Iconos.NewBoxRoom())

        resp = menu.lanza()
        if resp is not None:

            op, ntras = resp
            if op == 0:
                if menu.siIzq:
                    folder, boxroom = li_tras[ntras]
                    self.file = Util.opj(folder, boxroom)
                    self.show_file()
                elif menu.siDer:
                    boxrooms.delete(ntras)

            elif op == 1:
                resp = SelectFiles.salvaFichero(
                    self, _("Boxrooms PGN"), self.configuration.save_folder() + "/", "pgn", False
                )
                if resp:
                    resp = os.path.realpath(resp)
                    folder, boxroom = os.path.split(resp)
                    if folder != self.configuration.save_folder():
                        self.configuration.set_save_folder(folder)

                    boxrooms.append(folder, boxroom)

        self.wowner.check_toolbar()

    def terminar(self):
        self.dic_result = {
            "FILE": self.file,
            "CODEC": self.cb_codecs.valor(),
            "OVERWRITE": self.chb_overwrite.valor(),
            "REMCOMMENTSVAR": self.chb_remove_c_v.valor() if self.with_remcomments else False,
            "SEVENTAGS": self.chb_seventags.isChecked()
        }
        self.vars_save()


class WSave(LCDialog.LCDialog):
    history_list: list
    codec: str
    remove_comments: bool
    remove_variations: bool
    remove_nags: bool
    seventags: bool

    def __init__(self, owner, game):
        titulo = _("Save to PGN")
        icono = Iconos.PGN()
        extparam = "savepgn"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.vars_read()

        self.game_base = game

        self.game = self.game_reset(self.seventags)

        self.li_labels = [[k, v] for k, v in self.game.li_tags]
        self.configuration = Code.configuration
        self.file = ""

        # Opciones
        li_options = [
            (_("Save"), Iconos.GrabarFichero(), self.save),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.terminar),
            None,
            (_("Clipboard"), Iconos.Clipboard(), self.portapapeles),
            None,
            (_("Reinit"), Iconos.Reiniciar(), self.reinit),
            None,
        ]
        tb = QTVarios.LCTB(self, li_options)

        tabs = Controles.Tab(self)

        # Tab-file -----------------------------------------------------------------------------------------------
        lb_file = Controles.LB(self, _("File to save") + ": ")
        bt_history = Controles.PB(self, "", self.history).ponIcono(Iconos.Favoritos(), 24).ponToolTip(_("Previous"))
        bt_boxrooms = (
            Controles.PB(self, "", self.boxrooms).ponIcono(Iconos.BoxRooms(), 24).ponToolTip(_("Boxrooms PGN"))
        )
        self.bt_file = Controles.PB(self, "", self.file_select, plano=False).anchoMinimo(300)

        # Codec
        lb_codec = Controles.LB(self, _("Encoding") + ": ")
        li_codecs = [k for k in set(v for k, v in encodings.aliases.aliases.items())]
        li_codecs.sort()
        li_codecs = [(k, k) for k in li_codecs]
        li_codecs.insert(0, (_("Same as file"), "file"))
        li_codecs.insert(0, ("%s: %s" % (_("By default"), _("UTF-8")), "default"))
        self.cb_codecs = Controles.CB(self, li_codecs, self.codec)

        # Rest
        self.chb_overwrite = Controles.CHB(self, _("Overwrite"), False)
        self.chb_remove_comments = Controles.CHB(self, _("Remove comments"), self.remove_comments).capture_changes(self,
                                                                                                                   self.check_all)
        self.chb_remove_variations = Controles.CHB(self, _("Remove variations"),
                                                   self.remove_variations).capture_changes(self, self.check_all)
        self.chb_remove_nags = Controles.CHB(self, _("Remove NAGs"), self.remove_nags).capture_changes(self,
                                                                                                       self.check_all)
        self.chb_seventags = Controles.CHB(self, _("With the seven standard labels (STR)"), self.seventags).capture_changes(self, self.check_seventags)

        ly_f = Colocacion.H().control(lb_file).control(self.bt_file).control(bt_history).control(bt_boxrooms).relleno(1)
        ly_c = Colocacion.H().control(lb_codec).control(self.cb_codecs).relleno(1)
        ly = (
            Colocacion.V()
            .espacio(15)
            .otro(ly_f)
            .otro(ly_c)
            .espacio(10)
            .control(self.chb_overwrite)
            .espacio(10)
            .control(self.chb_remove_comments)
            .control(self.chb_remove_variations)
            .control(self.chb_remove_nags)
            .control(self.chb_seventags)
            .relleno(1)
        )
        w = QtWidgets.QWidget()
        w.setLayout(ly)
        tabs.new_tab(w, _("File"))
        self.chb_overwrite.hide()

        # Tab-labels -----------------------------------------------------------------------------------------------
        li_acciones_work = (
            ("", Iconos.Mas22(), self.labels_more),
            None,
            ("", Iconos.Menos22(), self.labels_less),
            None,
            ("", Iconos.Arriba(), self.labels_up),
            None,
            ("", Iconos.Abajo(), self.labels_down),
            None,
        )
        tb_labels = Controles.TBrutina(self, li_acciones_work, icon_size=16, with_text=False)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("ETIQUETA", _("Label"), 150, edicion=Delegados.LineaTextoUTF8())
        o_columns.nueva("VALOR", _("Value"), 420, edicion=Delegados.LineaTextoUTF8())

        self.grid_labels = Grid.Grid(self, o_columns, is_editable=True)
        n = self.grid_labels.anchoColumnas()
        self.grid_labels.setFixedWidth(n + 20)

        # Layout
        ly = Colocacion.V().control(tb_labels).control(self.grid_labels).margen(3)
        w = QtWidgets.QWidget()
        w.setLayout(ly)
        tabs.new_tab(w, _("PGN labels"))

        # Tab-Body -----------------------------------------------------------------------------------------------
        self.em_body = Controles.EM(self, "", siHTML=False)
        tabs.new_tab(self.em_body, _("Body"))

        # Tab-Body language ---------------------------------------------------------------------------------------
        self.with_body_sp = self.configuration.translator() != "en" and not self.configuration.x_pgn_english
        if self.with_body_sp:
            self.em_body_sp = Controles.EM(self, "", siHTML=False)
            tabs.new_tab(self.em_body_sp, self.configuration.language())

        layout = Colocacion.V().control(tb).control(tabs)

        self.setLayout(layout)

        if self.history_list:
            fich = self.history_list[0]
            if os.path.isfile(fich):
                self.file = fich
                self.show_file()

        self.register_grid(self.grid_labels)
        self.restore_video()

        self.check_all()

        self.tabs = tabs

    def game_reset(self, with_seventags):
        game = self.game_base.copia()
        if game.opening:
            if not game.get_tag("ECO"):
                game.set_tag("ECO", self.game.opening.eco)
            if not game.get_tag("Opening"):
                game.set_tag("Opening", self.game.opening.tr_name)
        if with_seventags:
            game.add_seventags()
        return game


    def check_info_base(self):
        body = self.check_info(self.game.pgn_base())
        self.em_body.set_text(body)

    def check_info_sp(self):
        body_sp = self.check_info(self.game.pgn_translated())
        self.em_body_sp.set_text(body_sp)

    def check_seventags(self):
        self.game = self.game_reset(self.chb_seventags.isChecked())
        self.li_labels = [[k, v] for k, v in self.game.li_tags]
        self.grid_labels.refresh()

    def check_all(self):
        self.check_info_base()
        if self.with_body_sp:
            self.check_info_sp()

    def check_info(self, body):

        def remove(ini, end):
            xlic = []
            nkey = 0
            for xc in body:
                if nkey:
                    if xc == end:
                        nkey -= 1
                    elif xc == ini:
                        nkey += 1
                    continue
                if xc == ini:
                    nkey += 1
                    continue
                xlic.append(xc)
            return "".join(xlic)

        changed = False
        if self.chb_remove_comments.isChecked():
            body = remove("{", "}")
            changed = True

        if self.chb_remove_variations.isChecked():
            body = remove("(", ")")
            changed = True

        if self.chb_remove_nags.isChecked():
            lic = []
            nag = False
            for c in body:
                if nag:
                    if c.isdigit():
                        continue
                    nag = False
                if c in "?!":
                    continue
                if c == "$":
                    nag = True
                    continue
                if c == " ":
                    if lic and lic[-1] == " ":
                        continue
                lic.append(c)
            body = "".join(lic)
            changed = True

        if changed:
            body = body.replace("\n", " ").replace("\r", " ")
            while "  " in body:
                body = body.replace("  ", " ")
            linea = ""
            body_new = ""
            for bl in body.split(" "):
                nbl = len(bl) + 1
                if linea and (len(linea) + nbl) > 80:
                    body_new += linea.strip() + "\n"
                    linea = ""
                linea += bl + " "
            if linea:
                body_new += linea.strip() + "\n"
            body = body_new

        return body

    def file_select(self):
        last_dir = ""
        if self.file:
            last_dir = os.path.dirname(self.file)
        elif self.history_list:
            last_dir = os.path.dirname(self.history_list[0])
            if not os.path.isdir(last_dir):
                last_dir = ""

        if not last_dir:
            last_dir = self.configuration.carpeta
        fich = SelectFiles.salvaFichero(self, _("File to save"), last_dir, "pgn", confirm_overwrite=False)
        if fich:
            if not fich.lower().endswith(".pgn"):
                fich += ".pgn"
            self.file = fich
            self.show_file()

    def show_file(self):
        self.bt_file.set_text(self.file)
        if os.path.isfile(self.file):
            self.chb_overwrite.show()
        else:
            self.chb_overwrite.hide()

    def vars_read(self):
        dic_variables = read_config_savepgn()
        self.history_list = dic_variables.get("LIHISTORICO", [])
        self.codec = dic_variables.get("CODEC", "default")
        self.remove_comments = dic_variables.get("REMCOMMENTS", False)
        self.remove_variations = dic_variables.get("REMVARIATIONS", False)
        self.remove_nags = dic_variables.get("REMNAGS", False)
        self.seventags = dic_variables.get("SEVENTAGS", True)

    def vars_save(self):
        dic_vars = {
            "LIHISTORICO": self.history_list,
            "CODEC": self.cb_codecs.valor(),
            "REMCOMMENTS": self.chb_remove_comments.isChecked(),
            "REMVARIATIONS": self.chb_remove_variations.isChecked(),
            "REMNAGS": self.chb_remove_nags.isChecked(),
            "SEVENTAGS": self.chb_seventags.isChecked()
        }
        write_config_savepgn(dic_vars)

    def history(self):
        menu = QTVarios.LCMenu(self, puntos=9)
        menu.setToolTip(_("To choose: <b>left button</b> <br>To erase: <b>right button</b>"))
        rp = QTVarios.rondo_puntos()
        for pos, txt in enumerate(self.history_list):
            menu.opcion(pos, txt, rp.otro())
        pos = menu.lanza()
        if pos is not None:
            if menu.siIzq:
                self.file = self.history_list[pos]
                self.show_file()
            elif menu.siDer:
                del self.history_list[pos]

    def boxrooms(self):
        menu = QTVarios.LCMenu(self, puntos=9)
        menu.setToolTip(_("To choose: <b>left button</b> <br>To erase: <b>right button</b>"))

        ico_tras = Iconos.BoxRoom()
        boxrooms = self.configuration.boxrooms()
        li_tras = boxrooms.lista()
        for ntras, uno in enumerate(li_tras):
            folder, boxroom = uno
            menu.opcion((0, ntras), "%s  (%s)" % (boxroom, folder), ico_tras)
        menu.separador()
        menu.opcion((1, 0), _("New boxroom"), Iconos.NewBoxRoom())

        resp = menu.lanza()
        if resp is not None:

            op, ntras = resp
            if op == 0:
                if menu.siIzq:
                    folder, boxroom = li_tras[ntras]
                    self.file = Util.opj(folder, boxroom)
                    self.show_file()
                elif menu.siDer:
                    boxrooms.delete(ntras)

            elif op == 1:
                resp = SelectFiles.salvaFichero(
                    self, _("Boxrooms PGN"), self.configuration.save_folder() + "/", "pgn", False
                )
                if resp:
                    resp = os.path.realpath(resp)
                    folder, boxroom = os.path.split(resp)
                    if folder != self.configuration.save_folder():
                        self.configuration.set_save_folder(folder)

                    boxrooms.append(folder, boxroom)

    def current_pgn(self):
        pgn = ""
        result = "*"
        for key, value in self.li_labels:
            key = key.strip()
            value = str(value).strip()
            if key and value:
                pgn += '[%s "%s"]\n' % (key, value)
                if key == "Result":
                    result = value
        body = self.em_body.texto().strip()
        if not body:
            body = result
        else:
            body += f" {result}"

        pgn += "\n%s\n" % body
        if "\r\n" in pgn:
            pgn = pgn.replace("\r\n", "\n")

        return pgn

    def save(self):
        pgn = self.current_pgn()
        modo = "w"
        if os.path.isfile(self.file):
            if not self.chb_overwrite.isChecked():
                modo = "a"
                pgn = f"\n\n{pgn}"

        codec = self.cb_codecs.valor()

        if codec == "default":
            codec = "utf-8"
        elif codec == "file":
            codec = "utf-8"
            if Util.exist_file(self.file):
                with open(self.file, "rb") as f:
                    u = chardet.universaldetector.UniversalDetector()
                    for n, x in enumerate(f):
                        if x.strip():
                            u.feed(x)
                        if n == 1000:
                            break
                    u.close()
                    codec = u.result.get("encoding", "utf-8")

        try:
            with open(self.file, modo, encoding=codec, errors="ignore") as q:
                if modo == "a":
                    q.write("\n\n")
                q.write(pgn)
            if self.file in self.history_list:
                self.history_list.remove(self.file)
            self.history_list.insert(0, self.file)
            QTUtil2.temporary_message(self.parent(), _("Saved"), 0.8)
            self.terminar()
        except:
            QTUtil2.message_error(self, _("Unable to save"))

    def portapapeles(self):
        pos_tab = self.tabs.current_position()
        tab_text = self.tabs.tabText(pos_tab)
        mens = ""

        if pos_tab == 0:
            mens = self.current_pgn()
        elif pos_tab == 1:
            mens = self.current_pgn()
            tab_text = self.tabs.tabText(0)
        elif pos_tab == 2:
            mens = self.em_body.texto()
        elif pos_tab == 3:
            mens = self.em_body_sp.texto()

        QTUtil.set_clipboard(mens)
        QTUtil2.temporary_message(self, f"<big>{tab_text}</big><br><br>" + _(
            "It is saved in the clipboard to paste it wherever you want."), 2)

    def terminar(self):
        self.vars_save()
        self.save_video()
        self.accept()

    def reinit(self):
        self.vars_read()
        if self.game.opening:
            if not self.game.get_tag("ECO"):
                self.game.set_tag("ECO", self.game.opening.eco)
            if not self.game.get_tag("Opening"):
                self.game.set_tag("Opening", self.game.opening.tr_name)

        self.li_labels = [[k, v] for k, v in self.game.li_tags]
        self.grid_labels.refresh()

        self.check_all()

    def labels_more(self):
        self.li_labels.append(["", ""])
        self.grid_labels.goto(len(self.li_labels) - 1, 0)
        self.grid_labels.refresh()

    def labels_less(self):
        recno = self.grid_labels.recno()
        if recno > -1:
            del self.li_labels[recno]
            self.grid_labels.refresh()

    def labels_up(self):
        recno = self.grid_labels.recno()
        if recno:
            self.li_labels[recno], self.li_labels[recno - 1] = (self.li_labels[recno - 1], self.li_labels[recno])
            self.grid_labels.goto(recno - 1, 0)
            self.grid_labels.refresh()

    def labels_down(self):
        n0 = self.grid_labels.recno()
        if n0 < len(self.li_labels) - 1:
            n1 = n0 + 1
            self.li_labels[n0], self.li_labels[n1] = self.li_labels[n1], self.li_labels[n0]
            self.grid_labels.goto(n1, 0)
            self.grid_labels.refresh()

    def grid_num_datos(self, grid):
        return len(self.li_labels)

    def grid_setvalue(self, grid, row, o_column, valor):
        col = 0 if o_column.key == "ETIQUETA" else 1
        self.li_labels[row][col] = valor

    def grid_dato(self, grid, row, o_column):
        if o_column.key == "ETIQUETA":
            lb, value = self.li_labels[row]
            ctra = lb.upper()
            trad = TrListas.pgn_label(lb)
            if trad != ctra:
                key = trad
            else:
                if lb:
                    key = lb
                else:
                    key = ""
            return key
        return self.li_labels[row][1]


class WSaveVarios(LCDialog.LCDialog):
    dic_result: dict

    def __init__(self, owner, with_remcomments=False):
        configuration = Code.configuration
        titulo = _("Save to PGN")
        icono = Iconos.PGN()
        extparam = "savepgnvarios"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.configuration = configuration

        # Opciones
        li_options = [
            (_("Save"), Iconos.GrabarFichero(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
        ]
        self.tb = QTVarios.LCTB(self, li_options)

        self.wbase = WBaseSave(self, configuration, with_remcomments=with_remcomments)

        layout = Colocacion.V().control(self.tb).control(self.wbase)

        self.setLayout(layout)

        self.restore_video()

        self.check_toolbar()

    def check_toolbar(self):
        self.tb.set_pos_visible(0, len(self.wbase.file) > 0)

    def aceptar(self):
        if self.wbase.file:
            self.wbase.terminar()
            self.dic_result = self.wbase.dic_result
            self.save_video()
            self.accept()
        else:
            self.reject()


class FileSavePGN:
    is_new: bool
    _progress_bar = None
    _pb_total: int
    _file_handle = None

    def __init__(self, owner, dic_vars):
        self.owner = owner
        self.file = dic_vars["FILE"]
        self.overwrite = dic_vars["OVERWRITE"]
        self.codec = dic_vars["CODEC"]
        self.seventags = dic_vars.get("SEVENTAGS", True)
        if self.codec == "default" or self.codec is None:
            self.codec = "utf-8"
        elif self.codec == "file":
            self.codec = "utf-8"
            if Util.exist_file(self.file):
                with open(self.file, "rb") as f:
                    u = chardet.universaldetector.UniversalDetector()
                    for n, x in enumerate(f):
                        u.feed(x)
                        if n == 1000:
                            break
                    u.close()
                    self.codec = u.result.get("encoding", "utf-8")
        self.xum = None

    def open(self):
        modo = "wt"
        if Util.exist_file(self.file):
            if not self.overwrite:
                modo = "at"
        self.is_new = self.overwrite or not os.path.isfile(self.file)
        try:
            self._file_handle = open(self.file, modo, encoding=self.codec, errors="ignore")
            return True
        except FileNotFoundError:
            return False

    def write(self, pgn):
        self._file_handle.write(pgn)

    def close(self):
        self._file_handle.close()

    def um(self):
        self.xum = QTUtil2.one_moment_please(self.owner, _("Saving..."))

    def um_final(self, with_message=True):
        if self.xum:
            self.xum.final()
        if with_message:
            QTUtil2.message_bold(self.owner, _X(_("Saved to %1"), self.file))

    def pb(self, total):
        self._progress_bar = QTUtil2.BarraProgreso(self.owner, self.file, "", total)
        self._pb_total = total
        self.pb_pos(0)

    def pb_pos(self, pos):
        self._progress_bar.pon(pos)
        self._progress_bar.mensaje("%d/%d" % (pos, self._pb_total))

    def pb_cancel(self):
        return self._progress_bar.is_canceled()

    def pb_close(self):
        self._progress_bar.cerrar()
