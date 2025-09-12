from PySide2 import QtGui

import Code


class Icons:
    NORMAL = 0
    SEPIA = 1
    DARK = 2
    dic_files = {NORMAL: "Iconos", SEPIA: "Iconos_sepia", DARK: "Iconos_dark"}
    bin_icons = None
    dic_icons = None
    mode = NORMAL

    def reset(self, mode):
        self.mode = mode
        self.bin_icons = self.read_bin()
        self.dic_icons = self.read_dic()

    def combobox(self):
        return [(_("By default"), self.NORMAL), (_("Sepia"), self.SEPIA), (_("Dark"), self.DARK)]

    def read_bin(self):
        file = self.dic_files[self.mode] + ".bin"
        with open(Code.path_resource("IntFiles", file), "rb") as f:
            return f.read()

    def read_dic(self):
        file = self.dic_files[self.mode] + ".dic"
        with open(Code.path_resource("IntFiles", file), "rt") as f:
            d = {}
            for linea in f:
                key, rg = linea.split("=")
                xfrom, xto = rg.strip().split(",")
                d[key] = (int(xfrom), int(xto))
            return d

    def icon(self, name):
        return self.__getattr__(name)

    def pixmap(self, name):
        return self.__getattr__("pm" + name)

    def get(self, name_icon):
        is_pixmap = name_icon[0] == "p"
        if is_pixmap:
            name_icon = name_icon[2:]
        xfrom, xto = self.dic_icons[name_icon]
        pm = QtGui.QPixmap()
        pm.loadFromData(self.bin_icons[xfrom:xto])
        return pm if is_pixmap else QtGui.QIcon(pm)


icons = Icons()
iget = icons.get
