import Code
from Code.QT import QTVarios, Iconos


class CoordinatesConfig:
    def __init__(self):
        self.with_pieces = True
        self.with_coordinates = True
        self.read()

    def read(self):
        dic = Code.configuration.read_variables("COORDINATES")
        self.with_pieces = dic.get("WITH_PIECES", self.with_pieces)
        self.with_coordinates = dic.get("WITH_COORDINATES", self.with_coordinates)

    def write(self):
        dic = {"WITH_PIECES": self.with_pieces, "WITH_COORDINATES": self.with_coordinates}
        Code.configuration.write_variables("COORDINATES", dic)

    def change(self, owner):
        menu = QTVarios.LCMenu(owner)
        menu.opcion("with_pieces", _("Show pieces"), Iconos.Checked() if self.with_pieces else Iconos.Unchecked())
        menu.separador()
        menu.opcion(
            "with_coordinates", _("Show coordinates"), Iconos.Checked() if self.with_coordinates else Iconos.Unchecked()
        )
        resp = menu.lanza()
        if resp:
            if resp == "with_pieces":
                self.with_pieces = not self.with_pieces
            else:
                self.with_coordinates = not self.with_coordinates
            self.write()
