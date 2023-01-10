import os.path

from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code import Util
from Code.QT import Controles


def init_app_style(app, configuration):
    app.setStyle(QtWidgets.QStyleFactory.create(configuration.x_style))

    file = configuration.x_style_mode
    path = Code.path_resource("Styles", file + ".qss")
    if not os.path.isfile(path):
        configuration.x_style_mode = "By default"
        configuration.graba()
        path = Code.path_resource("Styles", configuration.x_style_mode + ".qss")

    path_colors = Code.path_resource("Styles", file + ".colors")
    Code.dic_colors = dic_colors = Util.ini_base2dic(path_colors)
    dic_personal = Util.ini_base2dic(configuration.file_colors())
    dic_colors.update(dic_personal)
    Code.dic_qcolors = qdic = {}
    for key, color in dic_colors.items():
        qdic[key] = QtGui.QColor(color)

    with open(path) as f:
        current = None
        li_lines = []
        for line in f:
            line = line.strip()
            if line and not line.startswith("/"):
                if current is None:
                    current = line
                elif line == "}":
                    current = None
                elif "#" in line:
                    try:
                        key, value = line.split(":")
                    except:
                        continue
                    key = key.strip()
                    color = "#" + value.split("#")[1][:6]
                    key_gen = "%s|%s" % (current, key)
                    if key_gen in dic_colors:
                        line = line.replace(color, dic_colors[key_gen])
            li_lines.append(line)

        style_sheet = "\n".join(li_lines)
        default = """*{
background-color: %s;
color: %s;
}\n""" % (
            dic_colors["BACKGROUND"],
            dic_colors["FOREGROUND"],
        )
        if configuration.x_style_mode != "By default":
            app.setStyleSheet(default + style_sheet)
        else:
            configuration.style_sheet_default = style_sheet

    qpalette = QtWidgets.QApplication.style().standardPalette()
    qpalette.setColor(QtGui.QPalette.Link, Code.dic_qcolors["LINKS"])
    app.setPalette(qpalette)

    app.setEffectEnabled(QtCore.Qt.UI_AnimateMenu)

    QtGui.QFontDatabase.addApplicationFont(Code.path_resource("IntFiles", "ChessAlpha2.ttf"))

    font = Controles.TipoLetra(configuration.x_font_family, puntos=configuration.x_font_points)
    app.setFont(font)
