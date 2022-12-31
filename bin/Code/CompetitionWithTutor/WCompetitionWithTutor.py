import gettext
_ = gettext.gettext
from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code.About import About
from Code.CompetitionWithTutor import CompetitionWithTutor
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios


def datos(w_parent, configuration, procesador):
    # Primero determinamos la categoria
    resp = dameCategoria(w_parent, configuration, procesador)
    if resp:
        rival, categorias, categoria = resp
    else:
        return None

    w = wDatos(w_parent, rival, categorias, categoria, configuration)
    if w.exec_():
        return categorias, categoria, w.nivel, w.is_white, w.puntos
    else:
        return None


def dameCategoria(w_parent, configuration, procesador):
    dbm = CompetitionWithTutor.DBManagerCWT()
    rival_key = dbm.get_current_rival_key()
    li_grupos = dbm.grupos.liGrupos

    categorias = dbm.get_categorias_rival(rival_key)

    rival = configuration.buscaRival(rival_key)

    menu = QTVarios.LCMenu(w_parent)

    menu.opcion(None, "%s: %d %s" % (_("Total score"), dbm.puntuacion(), _("pts")), Iconos.NuevaPartida())
    menu.separador()
    menu.opcion(
        None,
        "%s: %s [%d %s]" % (_("Opponent"), rival.name, categorias.puntuacion(), _("pts")),
        Iconos.Engine(),
        is_disabled=False,
    )
    menu.separador()

    # ---------- CATEGORIAS
    ant = 1
    for x in range(6):
        cat = categorias.number(x)
        txt = cat.name()
        nm = cat.level_done

        nh = cat.hecho

        if nm > 0:
            txt += " %s %d" % (_("Level"), nm)
        if nh:
            if "B" in nh:
                txt += " +%s:%d" % (_("White"), nm + 1)
            if "N" in nh:
                txt += " +%s:%d" % (_("Black"), nm + 1)

                # if not ("B" in nh):
                # txt += "  ...  %s:%d"%( _( "White" )[0],nm+1)
                # elif not("N" in nh):
                # txt += "  ...  %s:%d"%( _( "Black" )[0],nm+1)
                # else:
                # txt += "  ...  %s:%d"%( _( "White" )[0],nm+1)

        siset_disabled = ant == 0
        ant = nm
        menu.opcion(str(x), txt, cat.icono(), is_disabled=siset_disabled)

    # ----------- RIVAL
    menu.separador()
    menuRival = menu.submenu(_("Change opponent"))

    puntuacion = categorias.puntuacion()

    icoNo = Iconos.Motor_No()
    icoSi = Iconos.Motor_Si()
    icoActual = Iconos.Motor_Actual()
    grpNo = Iconos.Grupo_No()
    grpSi = Iconos.Grupo_Si()

    for grupo in li_grupos:
        name = _X(_("%1 group"), grupo.name)
        if grupo.minPuntos > 0:
            name += " (+%d %s)" % (grupo.minPuntos, _("pts"))

        siDes = grupo.minPuntos > puntuacion
        if siDes:
            icoG = grpNo
            icoM = icoNo
        else:
            icoG = grpSi
            icoM = icoSi
        submenu = menuRival.submenu(name, icoG)

        for rv in grupo.li_rivales:
            siActual = rv.key == rival.key
            ico = icoActual if siActual else icoM
            submenu.opcion(
                "MT_" + rv.key,
                "%s: [%d %s]" % (rv.name, dbm.get_puntos_rival(rv.key), _("pts")),
                ico,
                siDes or siActual,
            )
        menuRival.separador()

    # ----------- RIVAL
    menu.separador()
    menu.opcion("get_help", _("Help"), Iconos.Ayuda())

    cursor = QtGui.QCursor.pos()
    resp = menu.lanza()
    if resp is None:
        return None
    elif resp == "get_help":
        titulo = _("Competition")
        ancho, alto = QTUtil.tamEscritorio()
        ancho = min(ancho, 700)
        txt = _(
            "<br><b>The aim is to obtain the highest possible score</b> :<ul><li>The current point score is displayed in the title bar.</li><li>To obtain points it is necessary to win on different levels in different categories.</li><li>To overcome a level it is necessary to win against the engine with white and with black.</li><li>The categories are ranked in the order of the following table:</li><ul><li><b>Beginner</b> : 5</li><li><b>Amateur</b> : 10</li><li><b>Candidate Master</b> : 20</li><li><b>Master</b> : 40</li><li><b>International Master</b> : 80</li><li><b>Grandmaster</b> : 160</li></ul><li>The score for each game is calculated by multiplying the playing level with the score of the category.</li><li>The engines are divided into groups.</li><li>To be able to play with an opponent of a particular group a minimum point score is required. The required score is shown next to the group label.</li></ul>"
        )
        About.info(w_parent, Code.lucas_chess, titulo, txt, ancho, Iconos.pmAyudaGR())
        return None

    elif resp.startswith("MT_"):
        dbm.set_current_rival_key(resp[3:])
        QtGui.QCursor.setPos(cursor)
        procesador.competicion()
        return None
    else:
        categoria = categorias.number(int(resp))
        return rival, categorias, categoria


class wDatos(QtWidgets.QDialog):
    def __init__(self, w_parent, rival, categorias, categoria, configuration):
        super(wDatos, self).__init__(w_parent)

        self.setWindowTitle(_("New game"))
        self.setWindowIcon(Iconos.Datos())
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        tb = QTVarios.tbAcceptCancel(self)

        f = Controles.TipoLetra(puntos=12, peso=75)
        flb = Controles.TipoLetra(puntos=10)

        self.max_level, self.maxNivelHecho, self.max_puntos = categorias.max_level_by_category(categoria)
        # self.max_level = max_level = categoria.level_done+1
        # self.maxNivelHecho = categoria.hecho
        # self.max_puntos = categoria.max_puntos()

        self.ed = Controles.SB(self, self.max_level, 1, self.max_level).tamMaximo(40)
        lb = Controles.LB(self, categoria.name() + " " + _("Level"))

        lb.ponFuente(f)
        self.lbPuntos = Controles.LB(self).align_right()
        self.ed.valueChanged.connect(self.nivelCambiado)

        is_white = not categoria.done_with_white()
        self.rb_white = QtWidgets.QRadioButton(_("White"))
        self.rb_white.setChecked(is_white)
        self.rb_black = QtWidgets.QRadioButton(_("Black"))
        self.rb_black.setChecked(not is_white)

        self.rb_white.clicked.connect(self.ponMaxPuntos)
        self.rb_black.clicked.connect(self.ponMaxPuntos)

        # Rival
        lbRMotor = (
            Controles.LB(self, "<b>%s</b> : %s" % (_("Engine"), rival.name)).ponFuente(flb).set_wrap().anchoFijo(400)
        )
        lbRAutor = (
            Controles.LB(self, "<b>%s</b> : %s" % (_("Author"), rival.autor)).ponFuente(flb).set_wrap().anchoFijo(400)
        )
        lbRWeb = (
            Controles.LB(self, '<b>%s</b> : <a href="%s">%s</a>' % (_("Web"), rival.url, rival.url))
            .set_wrap()
            .anchoFijo(400)
            .ponFuente(flb)
        )

        ly = Colocacion.V().control(lbRMotor).control(lbRAutor).control(lbRWeb).margen(10)
        gbR = Controles.GB(self, _("Opponent"), ly).ponFuente(f)

        # Tutor
        tutor = configuration.engine_tutor()
        lbTMotor = (
            Controles.LB(self, "<b>%s</b> : %s" % (_("Engine"), tutor.name)).ponFuente(flb).set_wrap().anchoFijo(400)
        )
        lbTAutor = (
            Controles.LB(self, "<b>%s</b> : %s" % (_("Author"), tutor.autor)).ponFuente(flb).set_wrap().anchoFijo(400)
        )
        siURL = hasattr(tutor, "url")
        if siURL:
            lbTWeb = (
                Controles.LB(self, '<b>%s</b> : <a href="%s">%s</a>' % ("Web", tutor.url, tutor.url))
                .set_wrap()
                .anchoFijo(400)
                .ponFuente(flb)
            )

        ly = Colocacion.V().control(lbTMotor).control(lbTAutor)
        if siURL:
            ly.control(lbTWeb)
        ly.margen(10)
        gbT = Controles.GB(self, _("Tutor"), ly).ponFuente(f)

        hbox = Colocacion.H().relleno().control(self.rb_white).espacio(10).control(self.rb_black).relleno()
        gbColor = Controles.GB(self, _("Side you play with"), hbox).ponFuente(f)

        lyNivel = Colocacion.H().control(lb).control(self.ed).espacio(10).control(self.lbPuntos).relleno()

        vlayout = (
            Colocacion.V()
            .otro(lyNivel)
            .espacio(10)
            .control(gbColor)
            .espacio(10)
            .control(gbR)
            .espacio(10)
            .control(gbT)
            .margen(30)
        )

        layout = Colocacion.V().control(tb).otro(vlayout).margen(3)

        self.setLayout(layout)

        self.ponMaxPuntos()

    def aceptar(self):
        self.nivel = self.ed.value()
        self.is_white = self.rb_white.isChecked()
        self.accept()

    def nivelCambiado(self, nuevo):
        self.ponMaxPuntos()

    def ponMaxPuntos(self):
        p = 0
        if self.ed.value() >= self.max_level:
            color = "B" if self.rb_white.isChecked() else "N"
            if not (color in self.maxNivelHecho):
                p = self.max_puntos
        self.lbPuntos.setText("%d %s" % (p, _("points")))
        self.puntos = p


def edit_training_position(w_parent, titulo, to_sq, etiqueta=None, pos=None, mensAdicional=None):
    w = WNumEntrenamiento(w_parent, titulo, to_sq, etiqueta, pos, mensAdicional)
    if w.exec_():
        return w.number
    else:
        return None


class WNumEntrenamiento(QtWidgets.QDialog):
    def __init__(self, w_parent, titulo, to_sq, etiqueta=None, pos=None, mensAdicional=None):
        super(WNumEntrenamiento, self).__init__(w_parent)

        self.setFont(Controles.TipoLetra(puntos=Code.configuration.x_sizefont_infolabels))

        self.setWindowTitle(titulo)
        self.setWindowIcon(Iconos.Datos())

        tb = QTVarios.tbAcceptCancel(self)

        if pos is None:
            pos = 1  # random.randint( 1, to_sq )

        if etiqueta is None:
            etiqueta = _("Training unit")

        self.ed, lb = QTUtil2.spinBoxLB(self, pos, 1, to_sq, etiqueta=etiqueta, maxTam=60)
        lb1 = Controles.LB(self, "/ %d" % to_sq)

        lyH = Colocacion.H().relleno().control(lb).control(self.ed).control(lb1).relleno().margen(15)

        lyV = Colocacion.V().control(tb).otro(lyH)
        if mensAdicional:
            lb2 = Controles.LB(self, mensAdicional)
            lb2.set_wrap().anchoMinimo(250)
            lyb2 = Colocacion.H().control(lb2).margen(15)
            lyV.otro(lyb2)
        lyV.margen(3)

        self.setLayout(lyV)

        self.resultado = None

    def aceptar(self):
        self.number = self.ed.value()
        self.accept()
