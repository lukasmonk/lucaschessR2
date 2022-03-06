import os
import shutil
import Code
from Code.Odt import Content, Styles, Others, Settings


class ODT:
    def __init__(self):
        self.content = Content.Content()
        self.styles = Styles.Styles()
        self.manifest = Others.Manifest()
        self.meta = Others.Meta()
        self.meta_inf = Others.MetaINF()
        self.settings = Settings.Settings()

    def create(self, path):
        folder_temp = Code.configuration.carpetaTemporal()
        pos = 0
        plant_folder = os.path.join(folder_temp, "temp%03d")
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

        path_mimetype = os.path.join(folder, "mimetype")
        with open(path_mimetype, "wt") as q:
            q.write("application/vnd.oasis.opendocument.text")

        if os.path.isfile(path):
            os.remove(path)
        pzip = path + ".zip"
        if os.path.isfile(pzip):
            os.remove(pzip)
        shutil.make_archive(path, "zip", folder)
        os.rename(pzip, path)
        os.startfile(path)

    def landscape(self):
        self.styles.landscape()

    def set_header(self, txt):
        self.styles.header(txt)

    def add_paragraph(self, txt, bold=False, centered=False):
        self.content.writeln(txt, bold, centered)

    def add_paragraph8(self, txt):
        self.content.writeln8(txt)

    def add_pagebreak(self):
        self.content.page_break()

    def add_linebreak(self):
        self.content.line_break()

    def add_png(self, path_png, width):
        internal_path = self.content.add_png(path_png, width)
        self.meta_inf.add_png(internal_path)

    def add_hyperlink(self, http, txt):
        self.content.add_hyperlink(http, txt)

# odt = ODT()
#
# # odt.landscape()
# # odt.header("Lucas Chess, bmt")
# odt.writeln("1.c3", bold=True, centered=True)
# odt.line_break()
# odt.line_break()
# odt.writeln("1.c3", bold=True, centered=True)
# odt.page_break()
# odt.writeln("1.c3", bold=True, centered=True)
# odt.line_break()
# odt.add_png(r"c:\lucaschess\pyLCR2\.utilities\odt\data\img1.png", 12.0)
# odt.line_break()
# odt.create("x1.odt")

