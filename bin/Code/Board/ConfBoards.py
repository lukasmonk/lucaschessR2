import Code
from Code.Base.Constantes import ZVALUE_PIECE
from Code.Board import BoardTypes


class JS:
    def save_dic(self):
        dic = {}
        for x in dir(self):
            if x.startswith("x_"):
                dic[x] = getattr(self, x)
            elif x.startswith("o_"):
                dic[x] = getattr(self, x).save_dic()
        return dic

    def restore_dic(self, dic):
        dc = dir(self)
        for x in dc:
            if x in dic:
                if x.startswith("x_"):
                    setattr(self, x, dic[x])
                elif x.startswith("o_"):
                    xvar = getattr(self, x)
                    xvar.restore_dic(dic[x])


class ConfigTabTema(JS):
    def __init__(self):
        self.defecto()

    def defecto(self):
        self.x_colorBlancas = 4294769635
        self.x_colorNegras = 4291672985
        self.x_colorExterior = 4294967295
        self.x_colorTexto = 4286212691
        self.x_colorFrontera = 4288262839
        self.o_fTransicion = self.flechaDefecto()
        self.o_fAlternativa = self.flechaAlternativaDefecto()
        self.x_siTemaDefecto = False
        self.x_png64Blancas = ""
        self.x_png64Negras = ""
        self.x_transBlancas = 0
        self.x_transNegras = 0
        self.x_colorFondo = self.x_colorBlancas
        self.x_png64Fondo = ""
        self.x_png64Exterior = ""
        self.o_fActivo = self.flechaActivoDefecto()
        self.o_fRival = self.flechaRivalDefecto()
        self.x_png64Thumb = ""
        self.x_extendedColor = False
        self.x_transSideIndicator = 0
        self.x_sideindicator_white = 0
        self.x_sideindicator_black = 0
        self.x_sideindicator_default = True

    def flechaDefecto(self):
        bf = BoardTypes.Flecha()
        bf.grosor = 1
        bf.altocabeza = 20
        bf.tipo = 1
        bf.destino = "m"
        bf.width_square = 32
        bf.color = 4293848576
        bf.colorinterior = 4292532736
        bf.opacity = 0.8
        bf.redondeos = True
        bf.forma = "3"
        bf.ancho = 4
        bf.vuelo = 5
        bf.descuelgue = 6
        bf.physical_pos.orden = ZVALUE_PIECE - 1
        return bf

    def flechaAlternativaDefecto(self):
        bf = self.flechaDefecto()
        bf.grosor = 4
        # bf.altocabeza=6
        bf.forma = "a"
        bf.tipo = 2
        return bf

    def flechaActivoDefecto(self):
        bf = BoardTypes.Flecha()
        bf.physical_pos.orden = ZVALUE_PIECE - 2
        bf.grosor = 1
        bf.altocabeza = 22
        bf.tipo = 1
        bf.destino = "m"
        bf.width_square = 36
        bf.color = 4283760767
        bf.colorinterior = 4294923520
        bf.colorinterior2 = -1
        bf.redondeos = False
        bf.forma = "3"
        bf.ancho = 5
        bf.vuelo = 4
        bf.descuelgue = 6
        return bf

    def flechaRivalDefecto(self):
        bf = BoardTypes.Flecha()
        bf.physical_pos.orden = ZVALUE_PIECE - 2
        bf.grosor = 1
        bf.altocabeza = 22
        bf.tipo = 1
        bf.destino = "m"
        bf.width_square = 36
        bf.color = 4281749760
        bf.colorinterior = 4289396480
        bf.colorinterior2 = -1
        bf.redondeos = False
        bf.forma = "3"
        bf.ancho = 5
        bf.vuelo = 4
        bf.descuelgue = 6
        return bf

    def copia(self):
        ct = ConfigTabTema()
        ct.restore_dic(self.save_dic())
        return ct


class ConfigTabBase(JS):
    def __init__(self):
        self.start()

    def start(self):
        self.x_nomPiezas = ""
        self.x_tipoLetra = ""
        self.x_cBold = ""
        self.x_tamLetra = -1
        self.x_tamRecuadro = -1
        self.x_tamFrontera = -1
        self.x_nCoordenadas = -1
        self.x_sepLetras = -9999

    def defecto(self):
        self.x_nomPiezas = "Chessicons"
        self.x_tipoLetra = "Arial"
        self.x_cBold = "S"
        self.x_tamLetra = 72
        self.x_tamRecuadro = 100
        self.x_tamFrontera = 100
        self.x_nCoordenadas = 4
        self.x_sepLetras = 100

    def copia(self):
        ct = ConfigTabBase()
        ct.restore_dic(self.save_dic())
        return ct


class ConfigBoard(JS):
    def __init__(self, xid, ancho_pieza, padre="BASE"):
        self._id = xid
        self.x_anchoPieza = ancho_pieza
        self._anchoPiezaDef = ancho_pieza
        self.o_tema = ConfigTabTema()
        self.o_tema.x_siTemaDefecto = xid != "BASE"
        self.o_base = ConfigTabBase()
        self._padre = padre
        self._confPadre = None
        self.is_base = xid == "BASE"

    def __str__(self):
        return self.o_tema.save_dic()

    def id(self):
        return self._id

    def confPadre(self):
        if self._confPadre is None:
            self._confPadre = Code.configuration.config_board(self._padre, self._anchoPiezaDef)
        return self._confPadre

    def width_piece(self, valor=None):
        if valor is None:
            return self.x_anchoPieza if self.x_anchoPieza else self.ponDefAnchoPieza()
        else:
            self.x_anchoPieza = valor
            return self.x_anchoPieza

    def ponDefAnchoPieza(self):
        return self.width_piece(self._anchoPiezaDef)

    def cambiaPiezas(self, nomPiezas):
        self.o_base.x_nomPiezas = nomPiezas

    def nomPiezas(self):
        np = self.o_base.x_nomPiezas
        if np == "" and self._id == "BASE":
            return "Chessicons"
        return np if np else self.confPadre().nomPiezas()

    def nCoordenadas(self):
        nc = self.o_base.x_nCoordenadas
        if self._id == "BASE" and nc == -1:
            return 4
        return self.confPadre().nCoordenadas() if nc < 0 else nc

    def sepLetras(self):
        nc = self.o_base.x_sepLetras
        if self._id == "BASE" and nc == -9999:
            return 190
        return self.confPadre().sepLetras() if nc == -9999 else nc

    def siDefPiezas(self):
        return self.o_base.x_nomPiezas == ""

    def siDefBold(self):
        return self.o_base.x_cBold == ""

    def siDefTipoLetra(self):
        return self.o_base.x_tipoLetra == ""

    def siDefTamLetra(self):
        return self.o_base.x_tamLetra == -1

    def siDefTamRecuadro(self):
        return self.o_base.x_tamRecuadro == -1

    def siDefTamFrontera(self):
        return self.o_base.x_tamFrontera == -1

    def siDefCoordenadas(self):
        return self.o_base.x_nCoordenadas == -1

    def siDefSepLetras(self):
        return self.o_base.x_sepLetras == -9999

    def siDefTema(self):
        return self.o_tema.x_siTemaDefecto

    def ponDefTema(self, si):
        self.o_tema.x_siTemaDefecto = si

    def guardaEnDisco(self):
        Code.configuration.cambiaConfBoard(self)

    def porDefecto(self, tipo):
        tp = tipo[0]
        siC = siS = siR = False
        if tp == "t":
            siC = siS = siR = True
        elif tp == "c":
            siC = True
        elif tp == "s":
            siS = True
        elif tp == "r":
            siR = True
        is_base = self._id == "BASE"
        if siC:
            if is_base:
                self.o_tema.defecto()
            else:
                self.o_tema.x_siTemaDefecto = True
        if siS:
            self.width_piece(self._anchoPiezaDef)
        if siR:
            if is_base:
                self.o_base.defecto()
            else:
                self.o_base.start()

    def graba(self):
        return self.save_dic()

    def grabaTema(self):
        return self.o_tema.save_dic()

    def leeTema(self, dic: dict):
        self.o_tema = ConfigTabTema()  # al poner campos nuevos que no permanezcan
        self.o_tema.restore_dic(dic)

    def grabaBase(self):
        return self.o_base.save_dic()

    def leeBase(self, txt):
        self.o_base.restore_dic(txt)

    def lee(self, dic):
        self.restore_dic(dic)

    def copia(self, xid):
        ct = ConfigBoard(xid, self._anchoPiezaDef)
        ct.lee(self.graba())
        return ct

    def colorBlancas(self, ncolor=None):
        if ncolor is not None:
            self.o_tema.x_colorBlancas = ncolor
        return self.confPadre().colorBlancas() if self.o_tema.x_siTemaDefecto else self.o_tema.x_colorBlancas

    def colorNegras(self, ncolor=None):
        if ncolor is not None:
            self.o_tema.x_colorNegras = ncolor
        return self.confPadre().colorNegras() if self.o_tema.x_siTemaDefecto else self.o_tema.x_colorNegras

    def sideindicator_white(self, ncolor=None):
        if ncolor is not None:
            self.o_tema.x_sideindicator_white = ncolor
        if self.o_tema.x_siTemaDefecto:
            return self.confPadre().sideindicator_white()
        return self.colorBlancas() if self.o_tema.x_sideindicator_default else self.o_tema.x_sideindicator_white

    def sideindicator_black(self, ncolor=None):
        if ncolor is not None:
            self.o_tema.x_sideindicator_black = ncolor
        if self.o_tema.x_siTemaDefecto:
            return self.confPadre().sideindicator_black()
        return self.colorNegras() if self.o_tema.x_sideindicator_default else self.o_tema.x_sideindicator_black

    def sideindicators_default(self, ok=None):
        if ok is not None:
            self.o_tema.x_sideindicator_default = ok
        return self.o_tema.x_sideindicator_default

    def colorFondo(self, ncolor=None):
        if ncolor is not None:
            self.o_tema.x_colorFondo = ncolor
        return self.confPadre().colorFondo() if self.o_tema.x_siTemaDefecto else self.o_tema.x_colorFondo

    def transBlancas(self, nTrans=None):
        if nTrans is not None:
            self.o_tema.x_transBlancas = nTrans
        return self.confPadre().transBlancas() if self.o_tema.x_siTemaDefecto else self.o_tema.x_transBlancas

    def transNegras(self, nTrans=None):
        if nTrans is not None:
            self.o_tema.x_transNegras = nTrans
        return self.confPadre().transNegras() if self.o_tema.x_siTemaDefecto else self.o_tema.x_transNegras

    def transSideIndicator(self, nTrans=None):
        if nTrans is not None:
            self.o_tema.x_transSideIndicator = nTrans
        return (
            self.confPadre().transSideIndicator() if self.o_tema.x_siTemaDefecto else self.o_tema.x_transSideIndicator
        )

    def png64Blancas(self, png64=None):
        if png64 is not None:
            self.o_tema.x_png64Blancas = png64
        return self.confPadre().png64Blancas() if self.o_tema.x_siTemaDefecto else self.o_tema.x_png64Blancas

    def png64Negras(self, png64=None):
        if png64 is not None:
            self.o_tema.x_png64Negras = png64
        return self.confPadre().png64Negras() if self.o_tema.x_siTemaDefecto else self.o_tema.x_png64Negras

    def png64Fondo(self, png64=None):
        if png64 is not None:
            self.o_tema.x_png64Fondo = png64
        return self.confPadre().png64Fondo() if self.o_tema.x_siTemaDefecto else self.o_tema.x_png64Fondo

    def png64Exterior(self, png64=None):
        if png64 is not None:
            self.o_tema.x_png64Exterior = png64
        return self.confPadre().png64Exterior() if self.o_tema.x_siTemaDefecto else self.o_tema.x_png64Exterior

    def png64Thumb(self, png64=None):
        if png64 is not None:
            self.o_tema.x_png64Thumb = png64
        return self.confPadre().png64Thumb() if self.o_tema.x_siTemaDefecto else self.o_tema.x_png64Thumb

    def extended_color(self, ext=None):
        if ext is not None:
            self.o_tema.x_extendedColor = ext
        return self.confPadre().extended_color() if self.o_tema.x_siTemaDefecto else self.o_tema.x_extendedColor

    def colorExterior(self, ncolor=None):
        if ncolor is not None:
            self.o_tema.x_colorExterior = ncolor
        return self.confPadre().colorExterior() if self.o_tema.x_siTemaDefecto else self.o_tema.x_colorExterior

    def colorTexto(self, ncolor=None):
        if ncolor is not None:
            self.o_tema.x_colorTexto = ncolor
        return self.confPadre().colorTexto() if self.o_tema.x_siTemaDefecto else self.o_tema.x_colorTexto

    def colorFrontera(self, ncolor=None):
        if ncolor is not None:
            self.o_tema.x_colorFrontera = ncolor
        return self.confPadre().colorFrontera() if self.o_tema.x_siTemaDefecto else self.o_tema.x_colorFrontera

    def fTransicion(self, valor=None):
        if valor:
            self.o_tema.o_fTransicion = valor
        else:
            return self.confPadre().fTransicion() if self.o_tema.x_siTemaDefecto else self.o_tema.o_fTransicion

    def fAlternativa(self, valor=None):
        if valor:
            self.o_tema.o_fAlternativa = valor
        else:
            return self.confPadre().fAlternativa() if self.o_tema.x_siTemaDefecto else self.o_tema.o_fAlternativa

    def flechaDefecto(self):
        return self.o_tema.flechaDefecto()

    def flechaAlternativaDefecto(self):
        return self.o_tema.flechaAlternativaDefecto()

    def fActivo(self, valor=None):
        if valor:
            self.o_tema.o_fActivo = valor
        else:
            return self.confPadre().fActivo() if self.o_tema.x_siTemaDefecto else self.o_tema.o_fActivo

    def flechaActivoDefecto(self):
        return self.o_tema.flechaActivoDefecto()

    def fRival(self, valor=None):
        if valor:
            self.o_tema.o_fRival = valor
        else:
            return self.confPadre().fRival() if self.o_tema.x_siTemaDefecto else self.o_tema.o_fRival

    def flechaRivalDefecto(self):
        return self.o_tema.flechaRivalDefecto()

    def font_type(self):
        t = self.o_base.x_tipoLetra
        if not t:
            return "Arial" if self.is_base else self.confPadre().font_type()
        else:
            return t

    def bold(self):
        t = self.o_base.x_cBold
        if not t:
            return True if self.is_base else self.confPadre().bold()
        else:
            return t == "S"

    def tamLetra(self):
        t = self.o_base.x_tamLetra
        if t < 0:
            return 72 if self.is_base else self.confPadre().tamLetra()
        else:
            return t

    def tamRecuadro(self):
        t = self.o_base.x_tamRecuadro
        if t < 0:
            return 100 if self.is_base else self.confPadre().tamRecuadro()
        else:
            return t

    def tamFrontera(self):
        t = self.o_base.x_tamFrontera
        if t < 0:
            return 100 if self.is_base else self.confPadre().tamFrontera()
        else:
            return t

    def ponNomPiezas(self, valor=None):
        if not valor:
            self.o_base.x_nomPiezas = "Chessicons" if self.is_base else ""
        else:
            self.o_base.x_nomPiezas = valor
        return self.o_base.x_nomPiezas

    def set_font_type(self, valor=None):
        if not valor:
            self.o_base.x_tipoLetra = "Arial" if self.is_base else ""
        else:
            self.o_base.x_tipoLetra = valor
        return self.o_base.x_tipoLetra

    def ponBold(self, valor=None):
        if valor is None:
            self.o_base.x_cBold = "S" if self.is_base else ""
        else:
            self.o_base.x_cBold = "S" if valor else "N"
        return self.o_base.x_cBold == "S"

    def ponTamLetra(self, valor=None):
        if valor is None:
            self.o_base.x_tamLetra = 100 if self.is_base else -1
        else:
            self.o_base.x_tamLetra = valor
        return self.o_base.x_tamLetra

    def ponTamRecuadro(self, valor=None):
        if valor is None:
            self.o_base.x_tamRecuadro = 100 if self.is_base else -1
        else:
            self.o_base.x_tamRecuadro = valor
        return self.o_base.x_tamRecuadro

    def ponTamFrontera(self, valor=None):
        if valor is None:
            self.o_base.x_tamFrontera = 100 if self.is_base else -1
        else:
            self.o_base.x_tamFrontera = valor
        return self.o_base.x_tamFrontera

    def ponCoordenadas(self, valor=None):
        if valor is None:
            self.o_base.x_nCoordenadas = 4 if self.is_base else -1
        else:
            self.o_base.x_nCoordenadas = valor
        return self.o_base.x_nCoordenadas

    def ponSepLetras(self, valor=None):
        if valor is None:
            self.o_base.x_sepLetras = 190 if self.is_base else -9999
        else:
            self.o_base.x_sepLetras = valor
        return self.o_base.x_nCoordenadas
