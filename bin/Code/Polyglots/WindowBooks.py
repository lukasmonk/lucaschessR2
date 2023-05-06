import Code
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTVarios


def eligeJugadaBooks(main_window, li_moves, is_white, siSelectSiempre=True):
    main_window.cursorFueraBoard()
    menu = QTVarios.LCMenu(main_window)
    f = Controles.TipoLetra(name=Code.font_mono, puntos=10)
    menu.ponFuente(f)

    titulo = _("White") if is_white else _("Black")
    icono = Iconos.Carpeta()

    menu.opcion(None, titulo, icono)
    menu.separador()

    icono = Iconos.PuntoNaranja() if is_white else Iconos.PuntoNegro()

    for from_sq, to_sq, promotion, pgn, peso in li_moves:
        menu.opcion((from_sq, to_sq, promotion), pgn, icono)
        menu.separador()

    resp = menu.lanza()
    if resp:
        return resp
    else:
        if siSelectSiempre:
            from_sq, to_sq, promotion, pgn, peso = li_moves[0]
            return from_sq, to_sq, promotion
        else:
            return None
