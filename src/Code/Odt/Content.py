import os
import shutil

from Code import Util
from Code.Odt import XML


class Content(XML.XML):
    def __init__(self):
        XML.XML.__init__(self, "office:document-content")
        self.add_param("xmlns:meta", "urn:oasis:names:tc:opendocument:xmlns:meta:1.0")
        self.add_param("xmlns:office", "urn:oasis:names:tc:opendocument:xmlns:office:1.0")
        self.add_param("xmlns:fo", "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0")
        self.add_param("xmlns:ooo", "http://openoffice.org/2004/office")
        self.add_param("xmlns:xlink", "http://www.w3.org/1999/xlink")
        self.add_param("xmlns:dc", "http://purl.org/dc/elements/1.1/")
        self.add_param("xmlns:style", "urn:oasis:names:tc:opendocument:xmlns:style:1.0")
        self.add_param("xmlns:text", "urn:oasis:names:tc:opendocument:xmlns:text:1.0")
        self.add_param("xmlns:draw", "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0")
        self.add_param("xmlns:dr3d", "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0")
        self.add_param("xmlns:svg", "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0")
        self.add_param("xmlns:chart", "urn:oasis:names:tc:opendocument:xmlns:chart:1.0")
        self.add_param("xmlns:rpt", "http://openoffice.org/2005/report")
        self.add_param("xmlns:table", "urn:oasis:names:tc:opendocument:xmlns:table:1.0")
        self.add_param("xmlns:number", "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0")
        self.add_param("xmlns:ooow", "http://openoffice.org/2004/writer")
        self.add_param("xmlns:oooc", "http://openoffice.org/2004/calc")
        self.add_param("xmlns:of", "urn:oasis:names:tc:opendocument:xmlns:of:1.2")
        self.add_param("xmlns:tableooo", "http://openoffice.org/2009/table")
        self.add_param("xmlns:calcext", "urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0")
        self.add_param("xmlns:drawooo", "http://openoffice.org/2010/draw")
        self.add_param("xmlns:loext", "urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0")
        self.add_param("xmlns:field", "urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0")
        self.add_param("xmlns:math", "http://www.w3.org/1998/Math/MathML")
        self.add_param("xmlns:form", "urn:oasis:names:tc:opendocument:xmlns:form:1.0")
        self.add_param("xmlns:script", "urn:oasis:names:tc:opendocument:xmlns:script:1.0")
        self.add_param("xmlns:dom", "http://www.w3.org/2001/xml-events")
        self.add_param("xmlns:xforms", "http://www.w3.org/2002/xforms")
        self.add_param("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
        self.add_param("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.add_param("xmlns:formx", "urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0")
        self.add_param("xmlns:xhtml", "http://www.w3.org/1999/xhtml")
        self.add_param("xmlns:grddl", "http://www.w3.org/2003/g/data-view#")
        self.add_param("xmlns:css3t", "http://www.w3.org/TR/css3-text/")
        self.add_param("xmlns:officeooo", "http://openoffice.org/2009/office")
        self.add_param("office:version", "1.3")
        element1 = XML.Element("office:scripts")
        self.add_content(element1)
        element2 = XML.Element("office:font-face-decls")
        self.add_content(element2)
        element3 = XML.Element("style:font-face")
        element3.add_param("style:name", "Liberation Sans")
        element3.add_param("svg:font-family", "&apos;Liberation Sans&apos;")
        element3.add_param("style:font-family-generic", "swiss")
        element3.add_param("style:font-pitch", "variable")
        element2.add_content(element3)
        element4 = XML.Element("style:font-face")
        element4.add_param("style:name", "Liberation Serif")
        element4.add_param("svg:font-family", "&apos;Liberation Serif&apos;")
        element4.add_param("style:font-family-generic", "roman")
        element4.add_param("style:font-pitch", "variable")
        element2.add_content(element4)
        element5 = XML.Element("style:font-face")
        element5.add_param("style:name", "Mangal")
        element5.add_param("svg:font-family", "Mangal")
        element5.add_param("style:font-family-generic", "system")
        element5.add_param("style:font-pitch", "variable")
        element2.add_content(element5)
        element6 = XML.Element("style:font-face")
        element6.add_param("style:name", "Mangal1")
        element6.add_param("svg:font-family", "Mangal")
        element2.add_content(element6)
        element7 = XML.Element("style:font-face")
        element7.add_param("style:name", "Microsoft YaHei")
        element7.add_param("svg:font-family", "&apos;Microsoft YaHei&apos;")
        element7.add_param("style:font-family-generic", "system")
        element7.add_param("style:font-pitch", "variable")
        element2.add_content(element7)
        element8 = XML.Element("style:font-face")
        element8.add_param("style:name", "NSimSun")
        element8.add_param("svg:font-family", "NSimSun")
        element8.add_param("style:font-family-generic", "system")
        element8.add_param("style:font-pitch", "variable")
        element2.add_content(element8)
        element9 = XML.Element("office:automatic-styles")
        self.add_content(element9)
        element10 = XML.Element("office:body")
        self.add_content(element10)
        element11 = XML.Element("office:text")
        element10.add_content(element11)
        element12 = XML.Element("text:sequence-decls")
        element11.add_content(element12)
        element13 = XML.Element("text:sequence-decl")
        element13.add_param("text:display-outline-level", "0")
        element13.add_param("text:name", "Illustration")
        element12.add_content(element13)
        element14 = XML.Element("text:sequence-decl")
        element14.add_param("text:display-outline-level", "0")
        element14.add_param("text:name", "Table")
        element12.add_content(element14)
        element15 = XML.Element("text:sequence-decl")
        element15.add_param("text:display-outline-level", "0")
        element15.add_param("text:name", "Text")
        element12.add_content(element15)
        element16 = XML.Element("text:sequence-decl")
        element16.add_param("text:display-outline-level", "0")
        element16.add_param("text:name", "Drawing")
        element12.add_content(element16)
        element17 = XML.Element("text:sequence-decl")
        element17.add_param("text:display-outline-level", "0")
        element17.add_param("text:name", "Figure")
        element12.add_content(element17)

        self.office_text = self.seek("office:text")
        self.automatic_styles = self.seek("office:automatic-styles")

        self.basic_styles()

        self.pos_png = 0
        self.li_path_png = []
        self.fmt_png = "Pictures/Image%03d.png"

    def run(self, folder):
        if self.li_path_png:
            folder_pictures = Util.opj(folder, "Pictures")
            os.mkdir(folder_pictures)
            for pos, path_ori in enumerate(self.li_path_png):
                path_dest = Util.opj(folder, self.fmt_png % pos)
                shutil.copy(path_ori, path_dest)

        path_content = Util.opj(folder, "content.xml")
        self.save(path_content)

    def add_style_paragraph(self, name, bold, align=None, fontsize=None):
        element = XML.Element("style:style")
        element.add_param("style:name", name)
        element.add_param("style:family", "paragraph")
        element.add_param("style:parent-style-name", "Standard")

        fontweight = "bold" if bold else "normal"
        element1 = XML.Element("style:text-properties")
        element1.add_param("fo:font-weight", fontweight)
        element1.add_param("officeooo:rsid", "00036ce6")
        element1.add_param("officeooo:paragraph-rsid", "00036ce6")
        element1.add_param("style:font-weight-asian", fontweight)
        element1.add_param("style:font-weight-complex", fontweight)
        element.add_content(element1)

        if align:
            element2 = XML.Element("style:paragraph-properties")
            element2.add_param("fo:text-align", align)
            element2.add_param("style:justify-single-word", "false")
            element.add_content(element2)

        if fontsize:
            element3 = XML.Element("style:text-properties")
            element3.add_param("fo:font-size", fontsize)
            element3.add_param("style:font-size-asian", fontsize)
            element3.add_param("style:font-size-complex", fontsize)
            element.add_content(element3)

        self.automatic_styles.add_content(element)

    def basic_styles(self):
        self.add_style_paragraph("PARA_CENTERED", False, "center")
        self.add_style_paragraph("PARA_BOLD", True)
        self.add_style_paragraph("PARA_BOLD_CENTERED", True, "center")
        self.add_style_paragraph("PARA_8", False, fontsize="8pt")

        # Page break
        element1 = XML.Element("style:style")
        element1.add_param("style:name", "PAGE_BREAK")
        element1.add_param("style:family", "paragraph")
        element1.add_param("style:parent-style-name", "Standard")
        element2 = XML.Element("style:paragraph-properties")
        element2.add_param("fo:text-align", "start")
        element2.add_param("style:justify-single-word", "false")
        element2.add_param("fo:break-after", "page")
        element1.add_content(element2)
        element3 = XML.Element("style:text-properties")
        element3.add_param("fo:font-weight", "normal")
        element3.add_param("officeooo:rsid", "000518a3")
        element3.add_param("officeooo:paragraph-rsid", "000518a3")
        element3.add_param("style:font-weight-asian", "normal")
        element3.add_param("style:font-weight-complex", "normal")
        element1.add_content(element3)
        self.automatic_styles.add_content(element1)

        # Graphics
        element1 = XML.Element("style:style")
        element1.add_param("style:name", "PNG_IMAGE")
        element1.add_param("style:family", "graphic")
        element1.add_param("style:parent-style-name", "Graphics")
        element2 = XML.Element("style:graphic-properties")
        element2.add_param("style:vertical-pos", "top")
        element2.add_param("style:vertical-rel", "baseline")
        element2.add_param("style:horizontal-pos", "center")
        element2.add_param("style:horizontal-rel", "paragraph")
        element2.add_param("style:mirror", "none")
        element2.add_param("fo:clip", "rect(0cm, 0cm, 0cm, 0cm)")
        element2.add_param("draw:luminance", "0%")
        element2.add_param("draw:contrast", "0%")
        element2.add_param("draw:red", "0%")
        element2.add_param("draw:green", "0%")
        element2.add_param("draw:blue", "0%")
        element2.add_param("draw:gamma", "100%")
        element2.add_param("draw:color-inversion", "false")
        element2.add_param("draw:image-opacity", "100%")
        element2.add_param("draw:color-mode", "standard")
        element1.add_content(element2)
        self.automatic_styles.add_content(element1)

    def register_table_style(self, name: str, width: float, num_cols: int, border: int):
        element = XML.Element("style:style")
        element.add_param("style:name", name)
        element.add_param("style:family", "table")
        self.automatic_styles.add_content(element)

        element1 = XML.Element("style:table-properties")
        element1.add_param("style:width", "%dcm" % width)
        element1.add_param("table:align", "margins")
        element.add_content(element1)

        name_col = f"{name}.A"
        element1 = XML.Element("style:style")
        element1.add_param("style:name", name_col)
        element1.add_param("style:family", "table-column")
        self.automatic_styles.add_content(element1)
        element2 = XML.Element("style:table-column-properties")
        element2.add_param("style:column-width", "%0.02fcm" % (width / num_cols,))
        element2.add_param("style:rel-column-width", "32767*")
        element1.add_content(element2)

        name_cell = name_col + "1"
        element1 = XML.Element("style:style")
        element1.add_param("style:name", name_cell)
        element1.add_param("style:family", "table-cell")
        self.automatic_styles.add_content(element1)
        element2 = XML.Element("style:table-cell-properties")
        element2.add_param("fo:padding", "0.097cm")
        element2.add_param("fo:border", "none" if not border else str(border))
        element1.add_content(element2)

    def write_element(self, parent, element):
        if parent is None:
            parent = self.office_text
        parent.add_content(element)

    def create_table(self, style: str, num_cols: int, parent=None):
        element_table = XML.Element("table:table")
        element_table.add_param("table:name", style)
        element_table.add_param("table:style-name", style)
        self.write_element(parent, element_table)

        element_table.add_extra("NUM_COLS", num_cols)
        element_table.add_extra("STYLE", style)

        element_col = XML.Element("table:table-column")
        element_col.add_param("table:style-name", f"{style}.A")
        element_col.add_param("table:number-columns-repeated", str(num_cols))
        element_table.add_content(element_col)

        return element_table

    @staticmethod
    def add_table_row(element_table: XML.Element):
        element_row = XML.Element("table:table-row")
        element_table.add_content(element_row)
        element_row.add_extra("STYLE_TABLE", element_table.get_extra("STYLE"))
        return element_row

    @staticmethod
    def add_table_cell(element_row: XML.Element):
        style = element_row.get_extra("STYLE_TABLE")
        name_cell = f"{style}.A1"
        element_cell = XML.Element("table:table-cell")
        element_cell.add_param("table:style-name", name_cell)
        element_cell.add_param("office:value-type", "string")

        element_row.add_content(element_cell)
        return element_cell

    def writeln(self, txt, bold, align_center, parent=None):
        if bold:
            style = "PARA_BOLD_CENTERED" if align_center else "PARA_BOLD"
        else:
            style = "PARA_CENTERED" if align_center else "Standard"

        element = XML.Element("text:p")
        element.add_param("text:style-name", style)
        if txt:
            element.set_value(txt)

        self.write_element(parent, element)
        return element

    def writeln8(self, txt, parent=None):
        element = XML.Element("text:p")
        element.add_param("text:style-name", "PARA_8")
        element.set_value(txt)

        self.write_element(parent, element)
        return element

    def page_break(self, parent=None):
        element = XML.Element("text:p")
        element.add_param("text:style-name", "PAGE_BREAK")

        self.write_element(parent, element)

    def line_break(self, parent=None):
        element = XML.Element("text:p")
        element.add_param("text:style-name", "Standard")

        self.write_element(parent, element)

    def add_png(self, path_png, width, height=None, align_center=False, parent=None):
        """<text:p text:style-name="P6"><draw:frame draw:style-name="fr1" draw:name="Imagen1" text:anchor-type="as-char" svg:width="8.729cm" svg:height="8.729cm" draw:z-index="0"><draw:image xlink:href="Pictures/100000010000014A0000014A845C32C77CCA2B7E.png" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad" draw:mime-type="image/png"/></draw:frame></text:p>"""
        self.li_path_png.append(path_png)
        internal_path = self.fmt_png % self.pos_png
        self.pos_png += 1

        internal_name = "Image%03d" % self.pos_png
        element = XML.Element("text:p")
        element.add_param("text:style-name", "PARA_CENTERED" if align_center else "Standard")
        element2 = XML.Element("draw:frame")
        element2.add_param("draw:style-name", "PNG_IMAGE")
        element2.add_param("draw:name", internal_name)
        element2.add_param("text:anchor-type", "as-char")
        element2.add_param("svg:width", "%.02fcm" % width)
        element2.add_param("svg:height", "%.02fcm" % (height if height else width))
        element2.add_param("draw:z-index", "0")
        element.add_content(element2)
        element3 = XML.Element("draw:image")
        element3.add_param("xlink:href", internal_path)
        element3.add_param("xlink:type", "simple")
        element3.add_param("xlink:show", "embed")
        element3.add_param("xlink:actuate", "onLoad")
        element3.add_param("draw:mime-type", "image/png")
        element2.add_content(element3)

        self.write_element(parent, element)

        return internal_path

    def add_hyperlink(self, http, txt, parent=None):
        element = XML.Element("text:p")
        element.add_param("text:style-name", "Standard")
        element2 = XML.Element("text:a")
        element2.add_param("xlink:type", "simple")
        element2.add_param("xlink:href", http)
        element2.add_param("text:style-name", "Internet_20_link")
        element2.add_param("text:visited-style-name", "Visited_20_Internet_20_Link")
        element.add_content(element2)
        element2.set_value(txt)

        self.write_element(parent, element)
