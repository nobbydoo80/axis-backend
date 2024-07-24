"""pdfgen.py: A generic pdfgeneration framework"""


import tempfile
from io import StringIO
from zipfile import ZipFile

from django.http.response import HttpResponse
from reportlab.lib.colors import Color
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas, pathobject
from reportlab.platypus.doctemplate import SimpleDocTemplate

__author__ = "Michael Jeffrey"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]


class CoordinateMixin(object):
    """use polar coordinates instead of cartesian"""

    inch = 72
    letter = (8.5 * inch, 11 * inch)

    def _myX(self, x):
        return x * self.inch

    def _myY(self, y):
        return self.letter[1] - y * self.inch

    def to_pt(self, value):
        return value * self.inch


class AxisPanel(CoordinateMixin):
    padding = 0.1

    def __init__(self, x=0, y=0, width=7.5, height=0, **kwargs):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.clear = kwargs.get("clear", False)

    def pt_width(self):
        return self.width * self.inch

    def pt_height(self):
        return self.height * self.inch

    def _width_on_page(self):
        """return coordinate where end of panel is expected to be"""
        return self.x + self.width

    def _height_on_page(self):
        """return coordinate where end of panel is expected to be"""
        return self.y + self.height + self.padding * 2

    def final_width(self):
        return self.width

    def final_height(self):
        return self.height + self.padding * 2

    def expected_space(self, spacing):
        """return (x, y) coordinates of expected bottom right of the panel"""
        return self._width_on_page() + spacing, self._height_on_page() + spacing


class AxisCanvas(canvas.Canvas, CoordinateMixin):
    def roundRect(self, x, y, width, height, radius, stroke=1, fill=0):
        """
        override of the roundRect method for consistency.
        :param x: top left x coordinate in inches
        :param y: top left y coordinate in inches
        :param width: width in inches
        :param height: height in inches
        :param radius: radius in points
        """
        x = self._myX(x)
        y = self._myY(y + height)
        width *= self.inch
        height *= self.inch
        canvas.Canvas.roundRect(
            self, x=x, y=y, width=width, height=height, radius=radius, stroke=stroke, fill=fill
        )

    def rect(self, x, y, width, height, stroke=1, fill=0):
        """
        Override of the rect method for consistency
        :param x: top left x coordinate in inches
        :param y: top left y coordinate in inches
        :param width: width in inches
        :param height: height in inches
        """
        x = self._myX(x)
        y = self._myY(y + height)
        width *= self.inch
        height *= self.inch
        canvas.Canvas.rect(self, x=x, y=y, width=width, height=height, stroke=stroke, fill=fill)


class AxisClipAndGradient(CoordinateMixin):
    def __init__(self, clip, x1, y1, x2, y2, colors, positions=None, extend=True):
        self.clip = clip
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.colors = colors
        self.positions = positions
        self.extend = extend

    def axisDraw(self, canvas):
        canvas.saveState()
        canvas.clipPath(self.clip)
        canvas.linearGradient(
            self._myX(self.x1),
            self._myY(self.y1),
            self._myX(self.x2),
            self._myY(self.y2),
            self.colors,
            positions=self.positions,
            extend=self.extend,
        )
        canvas.restoreState()


class AxisParagraphTable(CoordinateMixin):
    def __init__(self, paragraph, x, y, width, height, panel=None):
        self.paragraph = paragraph
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.panel = panel

    def abs_y(self):
        if not self.panel:
            return self.y + self.height
        return self.panel.y + self.y + self.height

    def abs_x(self):
        if not self.panel:
            return self.x
        return self.panel.x + self.x

    def axisDraw(self, canvas):
        canvas.saveState()
        self.paragraph.drawOn(canvas, self._myX(self.abs_x()), self._myY(self.abs_y()))
        canvas.restoreState()


class AxisRoundedRect(CoordinateMixin):
    def __init__(self, x, y, width, height, radius, **kwargs):
        default_color = Color(0, 0, 0)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius = radius
        self.strokeColor = kwargs.get("strokeColor", default_color)
        self.fillColor = kwargs.get("fillColor", default_color)
        self.stroke = kwargs.get("stroke", 1)
        self.fill = kwargs.get("fill", 0)

    def axisDraw(self, canvas):
        """This method assumes that you are passing it an AxisCanvas"""
        canvas.saveState()
        if type(self.fillColor) is dict:
            canvas.setFillColorRGB(**self.fillColor)
        else:
            canvas.setFillColor(self.fillColor)
        if type(self.strokeColor) is dict:
            canvas.setStrokeColorRGB(**self.strokeColor)
        else:
            canvas.setStrokeColor(self.strokeColor)
        canvas.roundRect(
            self.x,
            self.y,
            self.width,
            self.height,
            radius=self.radius,
            stroke=self.stroke,
            fill=self.fill,
        )
        canvas.restoreState()


class AxisImage(CoordinateMixin):
    def __init__(self, image, x, y, width, height, radius=False):
        self.image = image
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius = radius
        self.image._restrictSize(self.to_pt(self.width), self.to_pt(self.height))

    def axisDraw(self, canvas):
        canvas.saveState()
        if self.radius:
            canvas.setStrokeColor(Color(0, 0, 0, alpha=0.2))
            p = AxisPath()
            p.roundRect(self.x, self.y, self.width, self.height, self.radius)
            canvas.clipPath(p)

        self.image.drawOn(canvas, self._myX(self.x), self._myY(self.y + self.height))
        canvas.restoreState()


class AxisPath(pathobject.PDFPathObject, CoordinateMixin):
    """Extending the reportlab Path object to throw in some extra methods"""

    def __init__(self, *args, **kwargs):
        default_color = {"r": 0, "g": 0, "b": 0}
        self.strokeColor = kwargs.get("strokeColor", default_color)
        self.fillColor = kwargs.get("fillColor", default_color)
        self.stroke = kwargs.get("stroke", 1)
        self.fill = kwargs.get("fill", 0)
        self.panel = kwargs.get("panel", None)
        pathobject.PDFPathObject.__init__(self)

    def axisDraw(self, canvas):
        """given the canvas, draw the path onto it"""
        canvas.saveState()
        if type(self.strokeColor) is dict:
            canvas.setStrokeColorRGB(**self.strokeColor)
        else:
            canvas.setStrokeColor(self.strokeColor)
        if type(self.fillColor) is dict:
            canvas.setFillColorRGB(**self.fillColor)
        else:
            canvas.setFillColor(self.fillColor)
        canvas.drawPath(self, stroke=self.stroke, fill=self.fill)
        canvas.restoreState()

    def move(self, x, y):
        """
        :param x: x coordinate in inches
        :param y: y coordinate in inches
        """
        self.moveTo(self._myX(x), self._myY(y))

    def line(self, x, y):
        """
        :param x: x coordinate in inches
        :param y: y coordinate in inches
        """
        self.lineTo(self._myX(x), self._myY(y))

    def curve(self, x1, y1, x2, y2, x3, y3, debug_canvas=False):
        """
        Create a curved based off of dimension in inches ending at (x3, y3)
        :param x1: first bezier handle x in inches
        :param y1: first bezier handle y in inches
        :param x2: second bezier handle x in inches
        :param y2: second bezier handle y in inches
        :param x3: endpoint x in inches
        :param y3: endpoint y in inches
        :param debug_canvas: passing this method the canvas object will draw the bezier points
        """
        self.curveTo(
            self._myX(x1), self._myY(y1), self._myX(x2), self._myY(y2), self._myX(x3), self._myY(y3)
        )
        if debug_canvas:
            debug_canvas.circle(self._myX(x1), self._myY(y1), 3, fill=0)
            debug_canvas.circle(self._myX(x2), self._myY(y2), 3, fill=0)
            debug_canvas.circle(self._myX(x3), self._myY(y3), 3, fill=0)

    def topLeftArc(self, x, y, radius=5):
        """
        Create a radius for a top left corner given the coordinates with no radius
        Arc will be drawn in clockwise fashion
        :param x: x coordinate in inches
        :param y: y coordinate in inches
        :param radius: radius in points
        """
        r = radius / self.inch
        self.line(x, y + r)
        self.curve(x, y + (0.5 * r), x + (0.5 * r), y, x + r, y)

    def topRightArc(self, x, y, radius=5):
        """
        Create a radius for a top right corner given the coordinates with no radius
        Arc will be drawn in clockwise fashion
        :param x: x coordinate in inches
        :param y: y coordinate in inches
        :param radius: radius in points
        """
        r = radius / self.inch
        self.line(x - r, y)
        self.curve(x - (0.5 * r), y, x, y + (0.5 * r), x, y + r)

    def bottomRightArc(self, x, y, radius=5):
        """
        Create a radius for a top right corner given the coordinates with no radius
        Arc will be drawn in clockwise fashion
        :param x: x coordinate in inches
        :param y: y coordinate in inches
        :param radius: radius in points
        """
        r = radius / self.inch
        self.line(x, y - r)
        self.curve(x, y - (0.5 * r), x - (0.5 * r), y, x - r, y)

    def bottomLeftArc(self, x, y, radius=5):
        """
        Create a radius for a top right corner given the coordinates with no radius
        Arc will be drawn in clockwise fashion
        :param x: x coordinate in inches
        :param y: y coordinate in inches
        :param radius: radius in points
        """
        r = radius / self.inch
        self.line(x + r, y)
        self.curve(x + (0.5 * r), y, x, y - (0.5 * r), x, y - r)

    def roundRect(self, x, y, width, height, radius):
        x = self._myX(x)
        y = self._myY(y + height)
        width *= self.inch
        height *= self.inch
        pathobject.PDFPathObject.roundRect(self, x, y, width, height, radius)


class AxisParagraph(CoordinateMixin):
    """An alternative to Paragraph but has ability to kern and adjust type"""

    ALIGNMENT_MAP = {"left": 0, "center": 1, "right": 2}
    VALIGNMENT_MAP = {"top": 0, "bottom": 1, "middle": 2}
    inch = 72.0
    page_width = 8.5
    page_height = 11

    def __init__(
        self,
        x,
        y,
        text,
        font="Arial",
        size=12,
        charSpace=0,
        wordSpace=0,
        leading=None,
        alignment=0,
        valignment=0,
        color=Color(0, 0, 0),
        price=False,
        canvas=None,
        debug=False,
        **kwargs,
    ):
        self.x = x
        self.y = y
        self.text = text
        if not isinstance(self.text, (tuple, list)):
            self.text = [text]
        self.font = font
        self.size = size
        self.charSpace = charSpace
        self.wordSpace = wordSpace
        self.price = price
        self._setup_calculated_variables(alignment, valignment, leading)

        self.canvas = canvas
        self.color = color

        self.debug = debug
        self.asterisk_offset = kwargs.get("asterisk_offset", 0) / self.inch

    def _setup_calculated_variables(self, alignment, valignment, leading):
        # setting alignment
        if isinstance(alignment, str) and alignment.lower() in self.ALIGNMENT_MAP.keys():
            self.alignment = self.ALIGNMENT_MAP[alignment]
        elif isinstance(alignment, int) and alignment in self.ALIGNMENT_MAP.values():
            self.alignment = alignment
        else:
            raise Exception("{} is not an accepted alignment value".format(alignment))

        # setting vertical alignment
        if isinstance(valignment, str) and valignment.lower() in self.VALIGNMENT_MAP.keys():
            self.valignment = self.VALIGNMENT_MAP[valignment]
        elif isinstance(valignment, int) and valignment in self.VALIGNMENT_MAP.values():
            self.valignment = valignment
        else:
            raise Exception("{} is not an accepted valignment value".format(alignment))

        # set leading
        self.leading = leading if isinstance(leading, (float, int)) else self.size

    def string_width(self, in_points=False):
        """returns the strings width in inches using a canvas method"""
        widths = []
        for line in self.text:
            widths.append(stringWidth(line, self.font, self.size))
        width = max(widths)
        width += (len(max(self.text)) - 1) * self.charSpace
        if in_points:
            return width
        return width / self.inch

    def string_height(self, in_points=False):
        """returns the strings height in inches using leading method"""
        height = self.size * 0.8 if len(self.text) == 1 else len(self.text) * self.leading
        if in_points:
            return height
        return height / self.inch

    def wrap(self, in_points=False):
        """return width and height of string in inches, unless specified for points"""
        return self.string_width(in_points=in_points), self.string_height(in_points=in_points)

    def _get_aligned_coords(self, in_points=False):
        """get coordinates taking into account horizontal and vertical alignment"""
        x, y = self.x, self.y
        if self.alignment == 1:  # align center
            x = self.x - (self.string_width() / 2)
        elif self.alignment == 2:  # align right
            x = self.x - self.string_width()

        if self.valignment == 0:  # valign top
            y = self.y + self.size / self.inch * 0.8
        elif self.valignment == 2:  # valign middle
            y = self.y - self.string_height() / 2

        if in_points:
            return x * self.inch, y * self.inch
        return x, y

    def format_text(self, variables):
        new_lines = []
        for line in self.text:
            new_lines.append(line.format(**variables))
        self.text = new_lines

    def _draw_text(self, x, y, text, size, font, leading, charSpace, color):
        self.canvas.saveState()
        to = self.canvas.beginText()
        to.setTextOrigin(self._myX(x), self._myY(y))
        to.setFont(font, size, leading=leading)
        to.setCharSpace(charSpace)
        to.setFillColor(color)
        for line in text:
            to.textLine(line)
        self.canvas.drawText(to)
        self.canvas.restoreState()

    def draw(self):
        if self.debug:
            self.canvas.setFillColor(Color(0.9, 0.9, 0.9))
            dx, dy = self._get_aligned_coords()
            dw, dh = self.wrap()
            self.canvas.rect(dx, dy, dw, dh, fill=1)
            self.canvas.circle(dx, dy, r=5, fill=0)
        x, y = self._get_aligned_coords()
        extra = (self.font, self.leading, self.charSpace, self.color)
        self._draw_text(x, y, self.text, self.size, *extra)

        if self.price:
            width = self.string_width()
            d_width = stringWidth("$", self.font, self.size / 2) / self.inch
            self._draw_text(x - d_width, y - self.size / self.inch / 3, "$", self.size / 2, *extra)
            self._draw_text(x + width, y - self.asterisk_offset, "*", 20, *extra)


class AxisSimpleDocTemplate(SimpleDocTemplate, object):
    file_name = "report.pdf"
    file_name_plural = "reports.zip"
    inner_file_name = "report_{obj.pk}.pdf"  # Appears inside of a zip

    @classmethod
    def new(cls, object_list, file_name=None, variables={}, **kwargs):
        if len(object_list) > 1:
            return cls.generate_report_zip(object_list, file_name=file_name, variables=variables)
        if len(object_list) == 0:
            obj = None
        else:
            obj = object_list[0]
        return cls.generate_report_pdf(obj, file_name=file_name, variables=variables)

    @classmethod
    def build_httpreponse_payload(cls, file_type, file_name, file):
        response = HttpResponse(content_type="application/{}".format(file_type))

        content_disposition = "attachment; filename={file_name}"
        response["Content-Disposition"] = content_disposition.format(file_name=file_name)
        file.seek(0)
        response.write(file.read())

        return response

    @classmethod
    def generate_report_pdf(cls, obj, file_name=None, variables={}):
        tmp_file = tempfile.NamedTemporaryFile()

        report = cls(filename=tmp_file)
        report.build(obj=obj, variables=variables)
        if not file_name:
            file_name = report.get_file_name()

        return cls.build_httpreponse_payload("pdf", file_name, tmp_file)

    @classmethod
    def generate_report_zip(cls, object_list, file_name=None, variables={}):
        in_memory = StringIO()
        zip = ZipFile(in_memory, "a")

        for obj in object_list:
            tmp_file = tempfile.NamedTemporaryFile()

            report = cls(filename=tmp_file)
            report.build(obj=obj, variables=variables)
            inner_file_name = report.get_inner_file_name()
            tmp_file.seek(0)
            zip.writestr(inner_file_name, tmp_file.read())

        zip.close()

        if not file_name:
            file_name = report.get_file_name(many=True)

        return cls.build_httpreponse_payload("zip", file_name, in_memory)

    def build(self, obj, variables={}, flowables=[], *args, **kwargs):
        self._obj = obj
        self._variables = variables
        return super(AxisSimpleDocTemplate, self).build(flowables, *args, **kwargs)

    def get_file_name(self, many=False):
        if many:
            return self.file_name_plural
        return self.file_name

    def get_inner_file_name(self):
        return self.inner_file_name.format(obj=self._obj)
