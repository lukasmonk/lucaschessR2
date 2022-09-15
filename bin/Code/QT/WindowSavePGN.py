import encodings
import os

import chardet.universaldetector
from PySide2 import QtWidgets

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


class WBaseSave(QtWidgets.QWidget):
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
        liCodecs = [k for k in set(v for k, v in encodings.aliases.aliases.items())]
        liCodecs.sort()
        liCodecs = [(k, k) for k in liCodecs]
        liCodecs.insert(0, (_("Same as file"), "file"))
        liCodecs.insert(0, ("%s: %s" % (_("By default"), _("UTF-8")), "default"))
        self.cb_codecs = Controles.CB(self, liCodecs, self.codec)

        # Rest
        self.chb_overwrite = Controles.CHB(self, _("Overwrite"), False)
        if with_remcomments:
            self.chb_remove_c_v = Controles.CHB(self, _("Remove comments and variations"), self.remove_c_v)

        lyF = Colocacion.H().control(lb_file).control(self.bt_file).control(bt_history).control(bt_boxrooms).relleno(1)
        lyC = Colocacion.H().control(lb_codec).control(self.cb_codecs).relleno(1)
        ly = Colocacion.V().espacio(15).otro(lyF).otro(lyC).control(self.chb_overwrite)
        if with_remcomments:
            ly.control(self.chb_remove_c_v)
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
        dicVariables = self.configuration.read_variables("SAVEPGN")
        self.history_list = dicVariables.get("LIHISTORICO", [])
        self.codec = dicVariables.get("CODEC", "default")

    def vars_save(self):
        if self.file:
            dicVariables = self.configuration.read_variables("SAVEPGN")
            if self.file in self.history_list:
                del self.history_list[self.history_list.index(self.file)]
            self.history_list.insert(0, self.file)
            dicVariables["LIHISTORICO"] = self.history_list
            dicVariables["CODEC"] = self.cb_codecs.valor()
            self.configuration.write_variables("SAVEPGN", dicVariables)

    def history(self):
        menu = QTVarios.LCMenu(self, puntos=9)
        menu.setToolTip(_("To choose: <b>left button</b> <br>To erase: <b>right button</b>"))
        rp = QTVarios.rondoPuntos()
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

        icoTras = Iconos.BoxRoom()
        boxrooms = self.configuration.boxrooms()
        li_tras = boxrooms.lista()
        for ntras, uno in enumerate(li_tras):
            folder, boxroom = uno
            menu.opcion((0, ntras), "%s  (%s)" % (boxroom, folder), icoTras)
        menu.separador()
        menu.opcion((1, 0), _("New boxroom"), Iconos.NewBoxRoom())

        resp = menu.lanza()
        if resp is not None:

            op, ntras = resp
            if op == 0:
                if menu.siIzq:
                    folder, boxroom = li_tras[ntras]
                    self.file = os.path.join(folder, boxroom)
                    self.show_file()
                elif menu.siDer:
                    boxrooms.delete(ntras)

            elif op == 1:
                resp = SelectFiles.salvaFichero(
                    self, _("Boxrooms PGN"), self.configuration.x_save_folder + "/", "pgn", False
                )
                if resp:
                    resp = os.path.realpath(resp)
                    folder, boxroom = os.path.split(resp)
                    if folder != self.configuration.x_save_folder:
                        self.configuration.x_save_folder = folder
                        self.configuration.graba()

                    boxrooms.append(folder, boxroom)

        self.wowner.check_toolbar()

    def terminar(self):
        self.dic_result = {
            "FILE": self.file,
            "CODEC": self.cb_codecs.valor(),
            "OVERWRITE": self.chb_overwrite.valor(),
            "REMCOMMENTSVAR": self.chb_remove_c_v.valor() if self.with_remcomments else False,
        }
        self.vars_save()


class WSave(LCDialog.LCDialog):
    def __init__(self, owner, game, configuration):
        titulo = _("Save to PGN")
        icono = Iconos.PGN()
        extparam = "savepgn"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.game = game
        self.game.order_tags()
        self.body = self.game.pgnBase()
        if self.game.opening:
            if not self.game.get_tag("ECO"):
                self.game.set_tag("ECO", self.game.opening.eco)
            if not self.game.get_tag("Opening"):
                self.game.set_tag("Opening", self.game.opening.tr_name)

        self.li_labels = [[k, v] for k, v in self.game.li_tags]
        self.configuration = configuration
        self.file = ""
        self.vars_read()

        f = Controles.TipoLetra(puntos=configuration.x_pgn_fontpoints)

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
        tabs.ponFuente(f)

        # Tab-file -----------------------------------------------------------------------------------------------
        lb_file = Controles.LB(self, _("File to save") + ": ").ponFuente(f)
        bt_history = (
            Controles.PB(self, "", self.history).ponIcono(Iconos.Favoritos(), 24).ponToolTip(_("Previous")).ponFuente(f)
        )
        bt_boxrooms = (
            Controles.PB(self, "", self.boxrooms).ponIcono(Iconos.BoxRooms(), 24).ponToolTip(_("Boxrooms PGN"))
        )
        self.bt_file = Controles.PB(self, "", self.file_select, plano=False).anchoMinimo(300).ponFuente(f)

        # Codec
        lb_codec = Controles.LB(self, _("Encoding") + ": ").ponFuente(f)
        liCodecs = [k for k in set(v for k, v in encodings.aliases.aliases.items())]
        liCodecs.sort()
        liCodecs = [(k, k) for k in liCodecs]
        liCodecs.insert(0, (_("Same as file"), "file"))
        liCodecs.insert(0, ("%s: %s" % (_("By default"), _("UTF-8")), "default"))
        self.cb_codecs = Controles.CB(self, liCodecs, self.codec).ponFuente(f)

        # Rest
        self.chb_overwrite = Controles.CHB(self, _("Overwrite"), False).ponFuente(f)
        self.chb_remove_comments = Controles.CHB(self, _("Remove comments"), self.remove_comments).ponFuente(f)
        self.chb_remove_variations = Controles.CHB(self, _("Remove variations"), self.remove_variations).ponFuente(f)
        self.chb_remove_nags = Controles.CHB(self, _("Remove NAGs"), self.remove_nags).ponFuente(f)

        lyF = Colocacion.H().control(lb_file).control(self.bt_file).control(bt_history).control(bt_boxrooms).relleno(1)
        lyC = Colocacion.H().control(lb_codec).control(self.cb_codecs).relleno(1)
        ly = (
            Colocacion.V()
            .espacio(15)
            .otro(lyF)
            .otro(lyC)
            .espacio(10)
            .control(self.chb_overwrite)
            .espacio(10)
            .control(self.chb_remove_comments)
            .control(self.chb_remove_variations)
            .control(self.chb_remove_nags)
            .relleno(1)
        )
        w = QtWidgets.QWidget()
        w.setLayout(ly)
        tabs.new_tab(w, _("File"))
        self.chb_overwrite.hide()

        # Tab-labels -----------------------------------------------------------------------------------------------
        liAccionesWork = (
            ("", Iconos.Mas22(), self.labels_more),
            None,
            ("", Iconos.Menos22(), self.labels_less),
            None,
            ("", Iconos.Arriba(), self.labels_up),
            None,
            ("", Iconos.Abajo(), self.labels_down),
            None,
        )
        tb_labels = Controles.TBrutina(self, liAccionesWork, icon_size=16, with_text=False)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("ETIQUETA", _("Label"), 150, edicion=Delegados.LineaTextoUTF8())
        o_columns.nueva("VALOR", _("Value"), 420, edicion=Delegados.LineaTextoUTF8())

        self.grid_labels = Grid.Grid(self, o_columns, is_editable=True)
        self.grid_labels.ponFuente(f)
        n = self.grid_labels.anchoColumnas()
        self.grid_labels.setFixedWidth(n + 20)

        # Layout
        ly = Colocacion.V().control(tb_labels).control(self.grid_labels).margen(3)
        w = QtWidgets.QWidget()
        w.setLayout(ly)
        tabs.new_tab(w, _("Labels"))

        # Tab-Body -----------------------------------------------------------------------------------------------
        self.em_body = Controles.EM(self, self.body, siHTML=False).ponFuente(f)
        tabs.new_tab(self.em_body, _("Body"))

        layout = Colocacion.V().control(tb).control(tabs)

        self.setLayout(layout)

        if self.history_list:
            fich = self.history_list[0]
            if os.path.isfile(fich):
                self.file = fich
                self.show_file()

        self.register_grid(self.grid_labels)
        self.restore_video()

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
        self.bt_file.set_text(self.file)
        if os.path.isfile(self.file):
            self.chb_overwrite.show()
        else:
            self.chb_overwrite.hide()

    def vars_read(self):
        dicVariables = self.configuration.read_variables("SAVEPGN")
        self.history_list = dicVariables.get("LIHISTORICO", [])
        self.codec = dicVariables.get("CODEC", "default")
        self.remove_comments = dicVariables.get("REMCOMMENTS", False)
        self.remove_variations = dicVariables.get("REMVARIATIONS", False)
        self.remove_nags = dicVariables.get("REMNAGS", False)

    def vars_save(self):
        dicVariables = {}
        dicVariables["LIHISTORICO"] = self.history_list
        dicVariables["CODEC"] = self.cb_codecs.valor()
        dicVariables["REMCOMMENTS"] = self.chb_remove_comments.isChecked()
        dicVariables["REMVARIATIONS"] = self.chb_remove_variations.isChecked()
        dicVariables["REMNAGS"] = self.chb_remove_nags.isChecked()
        self.configuration.write_variables("SAVEPGN", dicVariables)

    def history(self):
        menu = QTVarios.LCMenu(self, puntos=9)
        menu.setToolTip(_("To choose: <b>left button</b> <br>To erase: <b>right button</b>"))
        rp = QTVarios.rondoPuntos()
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

        icoTras = Iconos.BoxRoom()
        boxrooms = self.configuration.boxrooms()
        li_tras = boxrooms.lista()
        for ntras, uno in enumerate(li_tras):
            folder, boxroom = uno
            menu.opcion((0, ntras), "%s  (%s)" % (boxroom, folder), icoTras)
        menu.separador()
        menu.opcion((1, 0), _("New boxroom"), Iconos.NewBoxRoom())

        resp = menu.lanza()
        if resp is not None:

            op, ntras = resp
            if op == 0:
                if menu.siIzq:
                    folder, boxroom = li_tras[ntras]
                    self.file = os.path.join(folder, boxroom)
                    self.show_file()
                elif menu.siDer:
                    boxrooms.delete(ntras)

            elif op == 1:
                resp = SelectFiles.salvaFichero(
                    self, _("Boxrooms PGN"), self.configuration.x_save_folder + "/", "pgn", False
                )
                if resp:
                    resp = os.path.realpath(resp)
                    folder, boxroom = os.path.split(resp)
                    if folder != self.configuration.x_save_folder:
                        self.configuration.x_save_folder = folder
                        self.configuration.graba()

                    boxrooms.append(folder, boxroom)

    def current_pgn(self):
        pgn = ""
        for key, value in self.li_labels:
            key = key.strip()
            value = value.strip()
            if key and value:
                pgn += '[%s "%s"]\n' % (key, value)
        body = self.em_body.texto().strip()
        if not body:
            body = "*"
        else:

            def remove(xbody, ini, end):
                lic = []
                nkey = 0
                for c in xbody:
                    if nkey:
                        if c == end:
                            nkey -= 1
                        elif c == ini:
                            nkey += 1
                        continue
                    if c == ini:
                        nkey += 1
                        continue
                    lic.append(c)
                return "".join(lic)

            if self.chb_remove_comments.isChecked():
                body = remove(body, "{", "}")

            if self.chb_remove_variations.isChecked():
                body = remove(body, "(", ")")

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
                pgn = ("\n\n") + pgn

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
            QTUtil2.mensajeTemporal(self.parent(), _("Saved"), 0.8)
            self.terminar()
        except:
            QTUtil2.message_error(self, _("Unable to save"))

    def portapapeles(self):
        pgn = self.current_pgn()
        QTUtil.ponPortapapeles(pgn)
        QTUtil2.mensajeTemporal(self, _("It is saved in the clipboard to paste it wherever you want."), 2)

    def terminar(self):
        self.vars_save()
        self.save_video()
        self.accept()

    def reinit(self):
        self.vars_read()
        self.body = self.game.pgnBase()
        if self.game.opening:
            if not self.game.get_tag("ECO"):
                self.game.set_tag("ECO", self.game.opening.eco)
            if not self.game.get_tag("Opening"):
                self.game.set_tag("Opening", self.game.opening.tr_name)

        self.li_labels = [[k, v] for k, v in self.game.li_tags]
        self.grid_labels.refresh()
        self.em_body.set_text(self.body)

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
            trad = TrListas.pgnLabel(lb)
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
    def __init__(self, owner, configuration):
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

        self.wbase = WBaseSave(self, configuration)

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
    def __init__(self, owner, dic_vars):
        self.owner = owner
        self.file = dic_vars["FILE"]
        self.overwrite = dic_vars["OVERWRITE"]
        self.codec = dic_vars["CODEC"]
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
        # try:
        modo = "wt" if self.overwrite else "at"
        self.is_new = self.overwrite or not os.path.isfile(self.file)

        self.f = open(self.file, modo, encoding=self.codec, errors="ignore")
        return True

    def write(self, pgn):
        self.f.write(pgn)

    def close(self):
        self.f.close()

    def um(self):
        self.xum = QTUtil2.unMomento(self.owner, _("Saving..."))

    def um_final(self, with_message=True):
        if self.xum:
            self.xum.final()
        if with_message:
            QTUtil2.message_bold(self.owner, _X(_("Saved to %1"), self.file))

    def pb(self, total):
        self._pb = QTUtil2.BarraProgreso(self.owner, self.file, "", total)
        self._pb_total = total
        self.pb_pos(0)

    def pb_pos(self, pos):
        self._pb.pon(pos)
        self._pb.mensaje("%d/%d" % (pos, self._pb_total))

    def pb_cancel(self):
        return self._pb.is_canceled()

    def pb_close(self):
        self._pb.cerrar()
