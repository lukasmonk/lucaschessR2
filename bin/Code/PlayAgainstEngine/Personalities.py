from Code.Base.Constantes import (
    ADJUST_BETTER,
    ADJUST_HIGH_LEVEL,
    ADJUST_INTERMEDIATE_LEVEL,
    ADJUST_LOW_LEVEL,
    ADJUST_SELECTED_BY_PLAYER,
    ADJUST_SIMILAR,
    ADJUST_SOMEWHAT_BETTER,
    ADJUST_SOMEWHAT_BETTER_MORE,
    ADJUST_SOMEWHAT_BETTER_MORE_MORE,
    ADJUST_SOMEWHAT_WORSE_LESS,
    ADJUST_SOMEWHAT_WORSE_LESS_LESS,
    ADJUST_WORSE,
    ADJUST_WORST_MOVE,
)
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios


class Personalities:
    def __init__(self, owner, configuration):
        self.owner = owner
        self.configuration = configuration

    def list_personalities(self, siTodos):
        liAjustes = [
            (_("Best move"), ADJUST_BETTER),
            (_("Somewhat better") + "++", ADJUST_SOMEWHAT_BETTER_MORE_MORE),
            (_("Somewhat better") + "+", ADJUST_SOMEWHAT_BETTER_MORE),
            (_("Somewhat better"), ADJUST_SOMEWHAT_BETTER),
            (_("Similar to the player"), ADJUST_SIMILAR),
            (_("Somewhat worse"), ADJUST_WORSE),
            (_("Somewhat worse") + "-", ADJUST_SOMEWHAT_WORSE_LESS),
            (_("Somewhat worse") + "--", ADJUST_SOMEWHAT_WORSE_LESS_LESS),
            (_("Worst move"), ADJUST_WORST_MOVE),
            ("-" * 30, None),
            (_("High level"), ADJUST_HIGH_LEVEL),
            (_("Intermediate level"), ADJUST_INTERMEDIATE_LEVEL),
            (_("Low level"), ADJUST_LOW_LEVEL),
            ("-" * 30, None),
            (_("Move selected by the player"), ADJUST_SELECTED_BY_PLAYER),
        ]
        if siTodos and self.configuration.li_personalities:
            liAjustes.append(("-" * 30, None))
            for num, una in enumerate(self.configuration.li_personalities):
                liAjustes.append((una["NOMBRE"], 1000 + num))
        return liAjustes

    def list_personalities_minimum(self):
        liAjustes = [
            (_("Best move"), ADJUST_BETTER),
            (_("Move selected by the player"), ADJUST_SELECTED_BY_PLAYER),
        ]
        return liAjustes

    def label(self, nAjuste):
        for lb, n in self.list_personalities(True):
            if n == nAjuste:
                return lb
        return ""

    def edit(self, una, icono):
        if una is None:
            una = {}

        # Datos basicos
        li_gen = [(None, None)]
        li_gen.append((FormLayout.Editbox(_("Name")), una.get("NOMBRE", "")))

        li_gen.append((None, None))

        config = FormLayout.Fichero(_("Debug file"), "txt", True)
        li_gen.append((config, una.get("DEBUG", "")))

        li_gen.append((None, None))

        li_gen.append((None, _("Serious errors, select the best move if:")))
        li_gen.append(
            (FormLayout.Editbox(_("Mate is less than or equal to"), tipo=int, ancho=50), una.get("MAXMATE", 0))
        )
        li_gen.append(
            (
                FormLayout.Editbox(_("The loss of centipawns is greater than"), tipo=int, ancho=50),
                una.get("MINDIFPUNTOS", 0),
            )
        )
        li_gen.append((None, None))
        li_gen.append(
            (
                FormLayout.Editbox(
                    _("Max. loss of centipawns per move by the <br> engine to reach a leveled evaluation"),
                    tipo=int,
                    ancho=50,
                ),
                una.get("ATERRIZAJE", 50),
            )
        )

        # Opening
        liA = [(None, None)]

        config = FormLayout.Fichero(_("Polyglot book"), "bin", False)
        liA.append((config, una.get("BOOK", "")))

        # Medio juego
        liMJ = [(None, None)]

        # # Ajustar
        liMJ.append(
            (FormLayout.Combobox(_("Strength"), self.list_personalities(False)), una.get("ADJUST", ADJUST_BETTER))
        )

        # Movimiento siguiente
        liMJ.append((None, _("In the next move")))

        trlistaSG = [_("To move a pawn"), _("Advance piece"), _("Make check"), _("Capture")]
        listaSG = ["MOVERPEON", "AVANZARPIEZA", "JAQUE", "CAPTURAR"]
        for n, opcion in enumerate(listaSG):
            liMJ.append((FormLayout.Spinbox(trlistaSG[n], -2000, +2000, 50), una.get(opcion, 0)))

        # Movimientos previstos
        liMJ.append((None, _("In the expected moves")))
        trlistaPR = [_("Keep the two bishops"), _("Advance"), _("Make check"), _("Capture")]
        listaPR = ["2B", "AVANZAR", "JAQUE", "CAPTURAR"]
        for n, opcion in enumerate(listaPR):
            liMJ.append((FormLayout.Spinbox(trlistaPR[n], -2000, +2000, 50), una.get(opcion + "PR", 0)))

        # Final
        liF = [(None, None)]

        # Ajustar
        liF.append(
            (FormLayout.Combobox(_("Strength"), self.list_personalities(False)), una.get("AJUSTARFINAL", ADJUST_BETTER))
        )

        liF.append((FormLayout.Spinbox(_("Maximum pieces at this stage"), 0, 32, 50), una.get("MAXPIEZASFINAL", 0)))
        liF.append((None, None))

        # Movimiento siguiente
        liF.append((None, _("In the next move")))
        for n, opcion in enumerate(listaSG):
            liF.append((FormLayout.Spinbox(trlistaSG[n], -2000, +2000, 50), una.get(opcion + "F", 0)))

        # Movimientos previstos
        liF.append((None, _("In the expected moves")))
        for n, opcion in enumerate(listaPR):
            liF.append((FormLayout.Spinbox(trlistaPR[n], -2000, +2000, 50), una.get(opcion + "PRF", 0)))

        while True:
            lista = []
            lista.append((li_gen, _("Basic data"), ""))
            lista.append((liA, _("Opening"), ""))
            lista.append((liMJ, _("Middlegame"), ""))
            lista.append((liF, _("Endgame"), ""))
            resultado = FormLayout.fedit(
                lista, title=_("Personalities"), parent=self.owner, anchoMinimo=460, icon=icono
            )
            if resultado:
                accion, liResp = resultado
                liGenR, liAR, liMJR, liFR = liResp

                name = liGenR[0].strip()

                if not name:
                    QTUtil2.message_error(self.owner, _("Name missing"))
                    continue

                una = {}
                # Base
                una["NOMBRE"] = name
                una["DEBUG"] = liGenR[1]
                una["MAXMATE"] = liGenR[2]
                una["MINDIFPUNTOS"] = liGenR[3]
                una["ATERRIZAJE"] = liGenR[4]

                # Opening
                una["BOOK"] = liAR[0]

                # Medio
                una["ADJUST"] = liMJR[0]

                for num, opcion in enumerate(listaSG):
                    una[opcion] = liMJR[num + 1]

                nSG = len(listaSG) + 1
                for num, opcion in enumerate(listaPR):
                    una[opcion + "PR"] = liMJR[num + nSG]

                # Final
                una["AJUSTARFINAL"] = liFR[0]
                una["MAXPIEZASFINAL"] = liFR[1]

                for num, opcion in enumerate(listaSG):
                    una[opcion + "F"] = liFR[num + 2]

                nSG = len(listaSG) + 2
                for num, opcion in enumerate(listaPR):
                    una[opcion + "PRF"] = liFR[num + nSG]

                return una

            return None

    def lanzaMenu(self):
        menu = QTVarios.LCMenu(self.owner)
        f = Controles.TipoLetra(puntos=8, peso=75)
        menu.ponFuente(f)
        icoCrear = Iconos.Mas()
        icoEditar = Iconos.ModificarP()
        icoBorrar = Iconos.Delete()
        icoVerde = Iconos.PuntoVerde()
        icoRojo = Iconos.PuntoNaranja()

        menu.opcion(("c", None), _("New personality"), icoCrear)

        li_personalities = self.configuration.li_personalities
        if li_personalities:
            menu.separador()
            menuMod = menu.submenu(_("Edit"), icoEditar)
            for num, una in enumerate(li_personalities):
                menuMod.opcion(("e", num), una["NOMBRE"], icoVerde)
            menu.separador()
            menuBor = menu.submenu(_("Delete"), icoBorrar)
            for num, una in enumerate(li_personalities):
                menuBor.opcion(("b", num), una["NOMBRE"], icoRojo)
        resp = menu.lanza()
        if resp:
            siRehacer = False
            accion, num = resp
            if accion == "c":
                una = self.edit(None, icoCrear)
                if una:
                    li_personalities.append(una)
                    siRehacer = True
            elif accion == "e":
                una = self.edit(li_personalities[num], icoEditar)
                if una:
                    li_personalities[num] = una
                    siRehacer = True
            elif accion == "b":
                if QTUtil2.pregunta(self.owner, _X(_("Delete %1?"), li_personalities[num]["NOMBRE"])):
                    del li_personalities[num]
                    siRehacer = True

            if siRehacer:
                self.configuration.graba()
                return True
        return False
