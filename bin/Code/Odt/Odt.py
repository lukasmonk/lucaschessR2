import os
import shutil

import Code
from Code import Util
from Code.Odt import Content, Styles, Others, Settings


class ODT:
    def __init__(self):
        self.content = Content.Content()
        self.styles = Styles.Styles()
        self.manifest = Others.Manifest()
        self.meta = Others.Meta()
        self.meta_inf = Others.MetaINF()
        self.settings = Settings.Settings()
        self.width_cm = 17.0
        self.dic_tables_ncols = {}

    def create(self, path):
        folder_temp = Code.configuration.temporary_folder()
        pos = 0
        plant_folder = Util.opj(folder_temp, "temp%03d")
        while os.path.isdir(plant_folder % pos):
            pos += 1

        folder = plant_folder % pos
        os.mkdir(folder)

        self.meta_inf.run(folder)
        self.content.run(folder)
        self.styles.run(folder)
        self.manifest.run(folder)
        self.meta.run(folder)
        self.settings.run(folder)

        path_mimetype = Util.opj(folder, "mimetype")
        with open(path_mimetype, "wt") as q:
            q.write("application/vnd.oasis.opendocument.text")

        if os.path.isfile(path):
            os.unlink(path)
        pzip = path + ".zip"
        if os.path.isfile(pzip):
            os.remove(pzip)
        shutil.make_archive(path, "zip", folder)
        os.rename(pzip, path)
        os.startfile(path)

    def landscape(self):
        self.styles.landscape()
        self.width_cm = 24.5

    def margins(self, top, bottom, left, right):
        self.styles.margins(top, bottom, left, right)
        self.width_cm += 2.0

    def set_header(self, txt):
        self.styles.header(txt)

    def add_paragraph(self, txt, bold=False, align_center=False, parent=None):
        return self.content.writeln(txt, bold, align_center, parent)

    def add_paragraph8(self, txt, parent=None):
        return self.content.writeln8(txt, parent)

    def add_pagebreak(self, parent=None):
        self.content.page_break(parent)

    def add_linebreak(self, parent=None):
        self.content.line_break(parent)

    def add_png(self, path_png, width, align_center=False, parent=None):
        internal_path = self.content.add_png(path_png, width, align_center=align_center, parent=parent)
        self.meta_inf.add_png(internal_path)

    def add_hyperlink(self, http, txt, parent=None):
        self.content.add_hyperlink(http, txt, parent)

    def register_table(self, name, num_cols, border=0):
        self.dic_tables_ncols[name] = num_cols
        self.content.register_table_style(name, self.width_cm, num_cols, border)

    def create_table(self, name, parent=None):
        return self.content.create_table(name, self.dic_tables_ncols[name], parent=parent)

    def add_row(self, element_table):
        return self.content.add_table_row(element_table)

    def add_cell(self, element_row):
        return self.content.add_table_cell(element_row)
