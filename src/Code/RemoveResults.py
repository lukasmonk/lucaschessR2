import os

import Code
from Code.QT import QTVarios, Iconos, QTUtil2


class RemoveResults:
    def __init__(self, wowner):
        self.wowner = wowner
        self.configuration = Code.configuration
        self.list_results = [
            (_("Challenge 101"), Iconos.Wheel(), self.rem_101),
            (_("Check your memory on a chessboard"), Iconos.Memoria(), self.rem_check_your_memory),
        ]

    def menu(self):
        menu = QTVarios.LCMenu(self.wowner)

        menu.opcion(None, _("Remove results"), Iconos.Delete(), is_disabled=True)
        menu.separador()

        for label, icon, action in self.list_results:
            menu.opcion((action, label), label, icon)
            menu.separador()

        resp = menu.lanza()
        if resp:
            action, label = resp
            mens = f'{label}\n\n{_("Remove results")}\n\n\n{_("Are you sure?")}'
            if not QTUtil2.pregunta(self.wowner, mens):
                return
            action()
            Code.procesador.entrenamientos.rehaz()
            QTUtil2.temporary_message(self.wowner, _("Done"), 0.8)

    def rem_101(self):
        self.configuration.write_variables("challenge101", {})


    def rem_check_your_memory(self):
        os.remove(self.configuration.file_memory)
