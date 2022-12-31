import gettext
_ = gettext.gettext
import os
import time

from PySide2 import QtCore, QtWidgets

import Code
from Code import Util
from Code.Base.Constantes import FEN_INITIAL
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.SQL import UtilSQL


class WFiltrar(QtWidgets.QDialog):
    def __init__(self, w_parent, o_columns, liFiltro, dbSaveNom=None):
        super(WFiltrar, self).__init__()

        if dbSaveNom is None:
            dbSaveNom = Code.configuration.ficheroFiltrosPGN

        self.setWindowTitle(_("Filter"))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)
        self.setWindowIcon(Iconos.Filtrar())

        self.liFiltro = liFiltro
        nFiltro = len(liFiltro)
        self.dbSaveNom = dbSaveNom

        li_fields = [(x.head, '"%s"' % x.key) for x in o_columns.li_columns if x.key not in ("__num__", "opening")]
        li_fields.insert(0, ("", None))
        li_condicion = [
            ("", None),
            (_("Equal"), "="),
            (_("Not equal"), "<>"),
            (_("Greater than"), ">"),
            (_("Less than"), "<"),
            (_("Greater than or equal"), ">="),
            (_("Less than or equal"), "<="),
            (_("Like (wildcard = *)"), "LIKE"),
            (_("Not like (wildcard = *)"), "NOT LIKE"),
        ]

        li_union = [("", None), (_("AND"), "AND"), (_("OR"), "OR")]

        f = Controles.TipoLetra(puntos=12)  # 0, peso=75 )

        lb_col = Controles.LB(self, _("Column")).ponFuente(f)
        lb_par0 = Controles.LB(self, "(").ponFuente(f)
        lb_par1 = Controles.LB(self, ")").ponFuente(f)
        lb_con = Controles.LB(self, _("Condition")).ponFuente(f)
        lb_val = Controles.LB(self, _("Value")).ponFuente(f)
        lb_uni = Controles.LB(self, "+").ponFuente(f)

        ly = Colocacion.G()
        ly.controlc(lb_uni, 0, 0).controlc(lb_par0, 0, 1).controlc(lb_col, 0, 2)
        ly.controlc(lb_con, 0, 3).controlc(lb_val, 0, 4).controlc(lb_par1, 0, 5)

        self.numC = 8
        liC = []

        union, par0, campo, condicion, valor, par1 = None, False, None, None, "", False
        for i in range(self.numC):
            if i > 0:
                c_union = Controles.CB(self, li_union, union)
                ly.controlc(c_union, i + 1, 0)
            else:
                c_union = None

            c_par0 = Controles.CHB(self, "", par0).anchoFijo(20)
            ly.controlc(c_par0, i + 1, 1)
            c_campo = Controles.CB(self, li_fields, campo)
            ly.controlc(c_campo, i + 1, 2)
            c_condicion = Controles.CB(self, li_condicion, condicion)
            ly.controlc(c_condicion, i + 1, 3)
            c_valor = Controles.ED(self, valor)
            ly.controlc(c_valor, i + 1, 4)
            c_par1 = Controles.CHB(self, "", par1).anchoFijo(20)
            ly.controlc(c_par1, i + 1, 5)

            liC.append((c_union, c_par0, c_campo, c_condicion, c_valor, c_par1))

        self.liC = liC

        # Toolbar
        li_acciones = [
            (_("Accept"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
            (_("Reinit"), Iconos.Reiniciar(), self.reiniciar),
            None,
            (_("Save/Restore"), Iconos.Grabar(), self.grabar),
            None,
        ]

        tb = QTVarios.LCTB(self, li_acciones)

        # Layout
        layout = Colocacion.V().control(tb).otro(ly).margen(3)
        self.setLayout(layout)

        liC[0][2].setFocus()

        if nFiltro > 0:
            self.lee_filtro(self.liFiltro)

    def grabar(self):
        if not self.lee_filtro_actual():
            return
        with UtilSQL.DictSQL(self.dbSaveNom, tabla="Filters") as dbc:
            liConf = dbc.keys(si_ordenados=True)
            if len(liConf) == 0 and len(self.liFiltro) == 0:
                return
            menu = Controles.Menu(self)
            SELECCIONA, BORRA, GRABA = range(3)
            for x in liConf:
                menu.opcion((SELECCIONA, x), x, Iconos.PuntoAzul())
            menu.separador()

            if len(self.liFiltro) > 0:
                submenu = menu.submenu(_("Save current"), Iconos.Mas())
                if liConf:
                    for x in liConf:
                        submenu.opcion((GRABA, x), x, Iconos.PuntoAmarillo())
                submenu.separador()
                submenu.opcion((GRABA, None), _("New"), Iconos.NuevoMas())

            if liConf:
                menu.separador()
                submenu = menu.submenu(_("Remove"), Iconos.Delete())
                for x in liConf:
                    submenu.opcion((BORRA, x), x, Iconos.PuntoRojo())
            resp = menu.lanza()

            if resp:
                op, name = resp

                if op == SELECCIONA:
                    liFiltro = dbc[name]
                    self.lee_filtro(liFiltro)
                elif op == BORRA:
                    if QTUtil2.pregunta(self, _X(_("Delete %1?"), name)):
                        del dbc[name]
                elif op == GRABA:
                    if self.lee_filtro_actual():
                        if name is None:
                            li_gen = [FormLayout.separador]
                            li_gen.append((_("Name") + ":", ""))

                            resultado = FormLayout.fedit(li_gen, title=_("Filter"), parent=self, icon=Iconos.Libre())
                            if resultado:
                                accion, li_gen = resultado

                                name = li_gen[0].strip()
                                if name:
                                    dbc[name] = self.liFiltro
                        else:
                            dbc[name] = self.liFiltro

    def lee_filtro(self, liFiltro):
        self.liFiltro = liFiltro
        nFiltro = len(liFiltro)

        for i in range(self.numC):
            if nFiltro > i:
                union, par0, campo, condicion, valor, par1 = liFiltro[i]
            else:
                union, par0, campo, condicion, valor, par1 = None, False, None, None, "", False
            c_union, c_par0, c_campo, c_condicion, c_valor, c_par1 = self.liC[i]
            if c_union:
                c_union.set_value(union)
            c_par0.set_value(par0)
            c_campo.set_value(campo)
            c_condicion.set_value(condicion)
            c_valor.set_text(valor)
            c_par1.set_value(par1)

    def reiniciar(self):
        for i in range(self.numC):
            self.liC[i][1].set_value(False)
            self.liC[i][2].setCurrentIndex(0)
            self.liC[i][3].setCurrentIndex(0)
            self.liC[i][4].set_text("")
            self.liC[i][5].set_value(False)
            if i > 0:
                self.liC[i][0].setCurrentIndex(0)
        self.aceptar()

    def lee_filtro_actual(self):
        self.liFiltro = []

        npar = 0

        for i in range(self.numC):
            par0 = self.liC[i][1].valor()
            campo = self.liC[i][2].valor()
            condicion = self.liC[i][3].valor()
            valor = self.liC[i][4].texto().rstrip()
            par1 = self.liC[i][5].valor()

            if campo and condicion:
                if campo == "PLIES":
                    valor = valor.strip()
                    if valor.isdigit():
                        valor = "%d" % int(valor)  # fonkap patch %3d -> %d
                if par0:
                    npar += 1
                if par1:
                    npar -= 1
                if npar < 0:
                    break
                if i > 0:
                    union = self.liC[i][0].valor()
                    if union:
                        self.liFiltro.append([union, par0, campo, condicion, valor, par1])
                else:
                    self.liFiltro.append([None, par0, campo, condicion, valor, par1])
            else:
                break
        if npar:
            QTUtil2.message_error(self, _("The parentheses are unbalanced."))
            return False
        return True

    def aceptar(self):
        if self.lee_filtro_actual():
            self.accept()

    def where(self):
        where = ""
        for union, par0, campo, condicion, valor, par1 in self.liFiltro:
            valor = valor.upper()
            if condicion in ("LIKE", "NOT LIKE"):
                valor = valor.replace("*", "%")
                if not ("%" in valor):
                    valor = "%" + valor + "%"

            if union:
                where += " %s " % union
            if par0:
                where += "("
            if condicion in ("=", "<>") and not valor:
                where += "(( %s %s ) OR (%s %s ''))" % (
                    campo,
                    "IS NULL" if condicion == "=" else "IS NOT NULL",
                    campo,
                    condicion,
                )
            else:
                valor = valor.upper()
                if valor.isupper():
                    # where += "UPPER(%s) %s '%s'" % (campo, condicion, valor)  # fonkap patch
                    where += "%s %s '%s' COLLATE NOCASE" % (campo, condicion, valor)  # fonkap patch
                elif valor.isdigit():  # fonkap patch
                    where += "CAST(%s as decimal) %s %s" % (campo, condicion, valor)  # fonkap patch
                else:
                    where += "%s %s '%s'" % (campo, condicion, valor)  # fonkap patch
            if par1:
                where += ")"
        return where


class EM_SQL(Controles.EM):
    def __init__(self, owner, where, li_fields):
        self.li_fields = li_fields
        Controles.EM.__init__(self, owner, where, siHTML=False)

    def mousePressEvent(self, event):
        Controles.EM.mousePressEvent(self, event)
        if event.button() == QtCore.Qt.RightButton:
            menu = QTVarios.LCMenu(self)
            rondo = QTVarios.rondoPuntos()
            for txt, key in self.li_fields:
                menu.opcion(key, txt, rondo.otro())
            resp = menu.lanza()
            if resp:
                self.insertarTexto(resp)


class WFiltrarRaw(LCDialog.LCDialog):
    def __init__(self, w_parent, o_columns, where):
        LCDialog.LCDialog.__init__(self, w_parent, _("Filter"), Iconos.Filtrar(), "rawfilter")

        self.where = ""
        li_fields = [(x.head, x.key) for x in o_columns.li_columns if x.key != "__num__"]
        f = Controles.TipoLetra(puntos=12)  # 0, peso=75 )

        lbRaw = Controles.LB(self, "%s:" % _("Raw SQL")).ponFuente(f)
        self.edRaw = EM_SQL(self, where, li_fields).altoFijo(72).anchoMinimo(512).ponFuente(f)

        lbHelp = Controles.LB(self, _("Right button to select a column of database")).ponFuente(f)
        lyHelp = Colocacion.H().relleno().control(lbHelp).relleno()

        ly = Colocacion.H().control(lbRaw).control(self.edRaw)

        # Toolbar
        li_acciones = [
            (_("Accept"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
        ]
        tb = QTVarios.LCTB(self, li_acciones)

        # Layout
        layout = Colocacion.V().control(tb).otro(ly).otro(lyHelp).margen(3)
        self.setLayout(layout)

        self.edRaw.setFocus()

        self.restore_video(siTam=False)

    def aceptar(self):
        self.where = self.edRaw.texto()
        self.save_video()
        self.accept()


def mensajeEntrenamientos(owner, liCreados, liNoCreados):
    txt = ""
    if liCreados:
        txt += _("Created the following trainings") + ":"
        txt += "<ul>"
        for x in liCreados:
            txt += "<li>%s</li>" % os.path.basename(x)
        txt += "</ul>"
    if liNoCreados:
        txt += _("No trainings created due to lack of data") + ":"
        txt += "<ul>"
        for x in liNoCreados:
            txt += "<li>%s</li>" % os.path.basename(x)
        txt += "</ul>"
    QTUtil2.message_bold(owner, txt)


def create_tactics(procesador, wowner, li_registros_selected, li_registros_total, rutina_datos, name):
    nregs = len(li_registros_selected)

    form = FormLayout.FormLayout(wowner, _("Create tactics training"), Iconos.Tacticas())

    form.separador()
    form.edit(_("Name"), name)

    form.separador()
    li_j = [(_("By default"), 0), (_("White"), 1), (_("Black"), 2)]
    form.combobox(_("Point of view"), li_j, 0)

    form.separador()
    form.checkbox(_("Skip the first move"), False)

    form.separador()
    selected = nregs > 1
    form.checkbox("%s (%d)" % (_("Only selected games"), nregs), selected)
    form.separador()

    resultado = form.run()

    if not resultado:
        return

    accion, li_gen = resultado

    menuname = li_gen[0].strip()
    if not menuname:
        return
    pointview = str(li_gen[1])
    skip_first = li_gen[2]
    only_selected = li_gen[3]

    li_registros = li_registros_selected if only_selected else li_registros_total
    nregs = len(li_registros)

    rest_dir = Util.valid_filename(menuname)
    nom_dir = os.path.join(Code.configuration.folder_tactics(), rest_dir)
    nom_ini = os.path.join(nom_dir, "Config.ini")
    if os.path.isfile(nom_ini):
        dic_ini = Util.ini2dic(nom_ini)
        n = 1
        while True:
            if "TACTIC%d" % n in dic_ini:
                if "MENU" in dic_ini["TACTIC%d" % n]:
                    if dic_ini["TACTIC%d" % n]["MENU"].upper() == menuname.upper():
                        break
                else:
                    break
                n += 1
            else:
                break
        nom_tactic = "TACTIC%d" % n
    else:
        Util.create_folder(nom_dir)
        nom_tactic = "TACTIC1"
        dic_ini = {}
    nom_fns = os.path.join(nom_dir, "Puzzles.fns")
    if os.path.isfile(nom_fns):
        n = 1
        nom_fns = os.path.join(nom_dir, "Puzzles-%d.fns")
        while os.path.isfile(nom_fns % n):
            n += 1
        nom_fns = nom_fns % n

    # Se crea el file con los puzzles
    f = open(nom_fns, "wt", encoding="utf-8", errors="ignore")

    tmp_bp = QTUtil2.BarraProgreso(wowner, menuname, "%s: %d" % (_("Games"), nregs), nregs)
    tmp_bp.mostrar()

    fen0 = FEN_INITIAL

    t = time.time()

    for n in range(nregs):

        if tmp_bp.is_canceled():
            break

        tmp_bp.pon(n + 1)
        if time.time() - t > 1.0 or (nregs - n) < 10:
            tmp_bp.mensaje("%d/%d" % (n + 1, nregs))
            t = time.time()

        recno = li_registros[n]

        dic_valores = rutina_datos(recno, skip_first)
        plies = dic_valores["PLIES"]
        if plies == 0:
            continue

        pgn = dic_valores["PGN"]
        li = pgn.split("\n")
        if len(li) == 1:
            li = pgn.split("\r")
        li = [linea for linea in li if not linea.strip().startswith("[")]
        num_moves = " ".join(li).replace("\r", "").replace("\n", "")
        if not num_moves.strip("*"):
            continue

        def xdic(k):
            x = dic_valores.get(k, "")
            if x is None:
                x = ""
            elif "?" in x:
                x = x.replace(".?", "").replace("?", "")
            return x.strip()

        fen = dic_valores.get("FEN")
        if not fen:
            fen = fen0

        event = xdic("EVENT")
        site = xdic("SITE")
        date = xdic("DATE")
        gameurl = xdic("GAMEURL")
        themes = xdic("THEMES")
        if site == event:
            es = event
        else:
            es = event + " " + site
        es = es.strip()
        if date:
            if es:
                es += " (%s)" % date
            else:
                es = date
        white = xdic("WHITE")
        black = xdic("BLACK")
        wb = ("%s-%s" % (white, black)).strip("-")

        li_titulo = []

        def add_titulo(txt):
            if txt:
                li_titulo.append(txt)

        add_titulo(es)
        add_titulo(wb)
        add_titulo(themes)
        if gameurl:
            add_titulo('<a href="%s">%s</a>' % (gameurl, gameurl))
        for other in ("TASK", "SOURCE"):
            v = xdic(other)
            add_titulo(v)
        titulo = "<br>".join(li_titulo)

        if skip_first:
            pgn_real = dic_valores["PGN_REAL"].replace("\n", " ").replace("\r", " ")
            txt = fen + "|%s|%s|%s\n" % (titulo, num_moves, pgn_real)
        else:
            txt = fen + "|%s|%s\n" % (titulo, num_moves)

        f.write(txt)

    f.close()
    tmp_bp.cerrar()

    # Se crea el file de control
    dic_ini[nom_tactic] = d = {}
    d["MENU"] = menuname
    d["FILESW"] = "%s:100" % os.path.basename(nom_fns)
    d["POINTVIEW"] = pointview

    Util.dic2ini(nom_ini, dic_ini)

    def sp(num):
        return " " * num

    QTUtil2.message_bold(
        wowner,
        (
            "%s<br>%s<br><br>%s<br>%s<br>%s"
            % (
                _("Tactic training %s created.") % menuname,
                _("You can access this training from"),
                "%s/%s" % (_("Trainings"), _("Tactics")),
                "%s1) %s / %s <br>%s➔ %s"
                % (sp(5), _("Training positions"), _("Tactics"), sp(12), _("for a standard training")),
                "%s2) %s / %s <br>%s➔ %s"
                % (
                    sp(5),
                    _("Learn tactics by repetition"),
                    _("Personal tactics"),
                    sp(12),
                    _("for a training by repetition"),
                ),
            )
        ),
    )

    procesador.entrenamientos.rehaz()
