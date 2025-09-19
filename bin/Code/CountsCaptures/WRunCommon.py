from PySide2 import QtWidgets

from Code.QT import Colocacion, Controles, Iconos


class EDCelda(Controles.ED):
    def focusOutEvent(self, event):
        self.parent.focusOut(self)
        Controles.ED.focusOutEvent(self, event)


class WEdMove(QtWidgets.QWidget):
    def __init__(self, owner):
        QtWidgets.QWidget.__init__(self)

        self.PM_EMPTY, self.PM_OK, self.PM_WRONG, self.PM_REPEATED, self.PM_MOVE = (
            Iconos.pmPuntoBlanco(),
            Iconos.pmAceptarPeque(),
            Iconos.pmDelete(),
            Iconos.pmRepeat(),
            Iconos.pmMover(),
        )

        self.owner = owner

        self.origen = EDCelda(self, "").caracteres(2).controlrx("(|[a-h][1-8])").relative_width(32).align_center()

        self.arrow = arrow = Controles.LB(self).put_image(self.PM_MOVE)
        arrow.mousePressEvent = self.pulsa_flecha

        self.destino = EDCelda(self, "").caracteres(2).controlrx("(|[a-h][1-8])").relative_width(32).align_center()

        self.result = Controles.LB(self).set_wrap().put_image(self.PM_EMPTY)

        ly = (
            Colocacion.H()
            .relleno()
            .control(self.origen)
            .espacio(2)
            .control(arrow)
            .espacio(2)
            .control(self.destino)
            .espacio(2)
            .control(self.result)
            .margen(0)
            .relleno()
        )
        self.setLayout(ly)

    def focusOut(self, quien):
        self.owner.set_last_square(quien)

    def activa(self):
        self.setFocus()
        self.origen.setFocus()

    def activaDestino(self):
        self.setFocus()
        self.destino.setFocus()

    def movimiento(self):
        from_sq = self.origen.texto()
        if len(from_sq) != 2:
            from_sq = ""

        to_sq = self.destino.texto()
        if len(to_sq) != 2:
            from_sq = ""

        return from_sq + to_sq

    def deshabilita(self):
        self.origen.set_disabled(True)
        self.destino.set_disabled(True)

    def habilita(self):
        self.origen.set_disabled(False)
        self.destino.set_disabled(False)
        self.result.put_image(self.PM_EMPTY)

    def limpia(self):
        self.origen.set_text("")
        self.destino.set_text("")
        self.habilita()
        self.origen.setFocus()

    def correcta(self):
        self.result.put_image(self.PM_OK)

    def error(self):
        self.result.put_image(self.PM_WRONG)

    def repetida(self):
        self.result.put_image(self.PM_REPEATED)

    def pulsa_flecha(self, event):
        self.limpia()


class WEdMovePGN(QtWidgets.QWidget):
    def __init__(self, owner):
        QtWidgets.QWidget.__init__(self)

        self.PM_EMPTY, self.PM_OK, self.PM_WRONG, self.PM_REPEATED, self.PM_MOVE = (
            Iconos.pmPuntoBlanco(),
            Iconos.pmAceptarPeque(),
            Iconos.pmDelete(),
            Iconos.pmRepeat(),
            Iconos.pmMover(),
        )

        self.owner = owner

        self.celda = EDCelda(self, "").caracteres(8).relative_width(64).align_center()

        self.result = Controles.LB(self).set_wrap().put_image(self.PM_EMPTY)

        ly = Colocacion.H().relleno().control(self.celda).espacio(2).control(self.result).margen(0).relleno()
        self.setLayout(ly)

    def focusOut(self, quien):
        self.owner.set_last_square(quien)

    def activa(self):
        self.setFocus()
        self.celda.setFocus()

    def movimiento(self):
        return self.celda.texto()

    def deshabilita(self):
        self.celda.set_disabled(True)

    def habilita(self):
        self.celda.set_disabled(False)
        self.result.put_image(self.PM_EMPTY)

    def limpia(self):
        self.celda.set_text("")
        self.habilita()
        self.celda.setFocus()

    def correcta(self):
        self.result.put_image(self.PM_OK)

    def error(self):
        self.result.put_image(self.PM_WRONG)

    def repetida(self):
        self.result.put_image(self.PM_REPEATED)
