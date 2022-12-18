import os.path

from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code import Util
from Code.QT import Controles


def init_app_style(app, configuration):
    app.setStyle(QtWidgets.QStyleFactory.create(configuration.x_style))

    path = Code.path_resource("Styles", configuration.x_style_mode + ".qss")
    if not os.path.isfile(path):
        configuration.x_style_mode = "Light"
        configuration.graba()
        path = Code.path_resource("Styles", configuration.x_style_mode + ".qss")

    path_colors = Code.path_resource("Styles", configuration.x_style_mode + ".colors")
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
        default = """QWidget{
background-color: %s;
color: %s;
selection-background-color: %s;
selection-color: %s;
}\n""" % (
            dic_colors["BACKGROUND"],
            dic_colors["FOREGROUND"],
            dic_colors["SELECTION_BACKGROUND"], # Code.dic_colors["SELECTION_BACKGROUND"], para que no de error check_colors
            dic_colors["SELECTION_FOREGROUND"], # Code.dic_colors["SELECTION_FOREGROUND"], para que no de error check_colors
        )

        app.setStyleSheet(default + style_sheet)
        # app.setStyleSheet(style_sheet)

    qpalette = QtWidgets.QApplication.style().standardPalette()
    # QtGui.QPalette.Window, "Window"),
    # (QtGui.QPalette.WindowText, "WindowText"),
    # (QtGui.QPalette.Base, "Base"),
    # (QtGui.QPalette.Text, "Text"),

    # qpalette.setColor(QtGui.QPalette.Window, Code.dic_qcolors["BACKGROUND"])
    # qpalette.setColor(QtGui.QPalette.WindowText, Code.dic_qcolors["FOREGROUND"])
    # qpalette.setColor(QtGui.QPalette.Text, Code.dic_qcolors["FOREGROUND"])
    # qpalette.setColor(QtGui.QPalette.Base, Code.dic_qcolors["BACKGROUND"])
    qpalette.setColor(QtGui.QPalette.Link, Code.dic_qcolors["LINKS"])
    app.setPalette(qpalette)

    app.setEffectEnabled(QtCore.Qt.UI_AnimateMenu)

    QtGui.QFontDatabase.addApplicationFont(Code.path_resource("IntFiles", "ChessAlpha2.ttf"))

    font = Controles.TipoLetra(configuration.x_font_family, puntos=configuration.x_font_points)
    app.setFont(font)
