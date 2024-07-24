"""pypdf.py: """


import io

from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import BooleanObject, NameObject, IndirectObject, TextStringObject

__author__ = "Artem Hruzd"
__date__ = "04/29/2020 11:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class AxisPdfFileReader(PdfReader):
    """
    Patches PdfReader class to run common initialization settings
    """

    def __init__(self, stream, strict=True):
        super(AxisPdfFileReader, self).__init__(stream=stream, strict=strict)

        if "/AcroForm" in self.trailer["/Root"]:
            self.trailer["/Root"]["/AcroForm"].update(
                {NameObject("/NeedAppearances"): BooleanObject(True)}
            )


class AxisPdfFileWriter(PdfWriter):
    """
    Patches PdfWriter class for filling forms
    """

    checkbox_true_identificator = "/Yes"

    def __init__(self):
        super(AxisPdfFileWriter, self).__init__()

        self.set_need_appearances_writer()

        if "/AcroForm" in self._root_object:
            # Acro form is form field, set needs appearances to fix printing issues
            self._root_object["/AcroForm"].update(
                {NameObject("/NeedAppearances"): BooleanObject(True)}
            )

    def set_need_appearances_writer(self):
        # See 12.7.2 and 7.7.2 for more information:
        # http://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/PDF32000_2008.pdf
        try:
            catalog = self._root_object
            # get the AcroForm tree and add "/NeedAppearances attribute
            if "/AcroForm" not in catalog:
                self._root_object.update(
                    {NameObject("/AcroForm"): IndirectObject(len(self._objects), 0, self)}
                )

            need_appearances = NameObject("/NeedAppearances")
            self._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
        except Exception as e:
            print("set_need_appearances_writer() catch : ", repr(e))

    def updatePageFormFieldValues(self, page, fields):
        """
        Patched version allow to update Checkbox and Radio fields
        Update the form field values for a given page from a fields dictionary.
        Copy field texts and values from fields to page.

        :param page: Page reference from PDF writer where the annotations
            and field data will be updated.
        :param fields: a Python dictionary of field names (/T) and text
            values (/V) or objects if you need more complex logic, like changing font color, size
        """

        try:
            # pages without form do not have Annots
            annots = page["/Annots"]
        except KeyError:
            return

        # Iterate through pages, update field values
        for j in range(0, len(annots)):
            writer_annot = page["/Annots"][j].get_object()
            for field in fields:
                if writer_annot.get("/T") == field:
                    if isinstance(fields[field], dict):
                        writer_annot.update(fields[field])
                    elif isinstance(fields[field], str):
                        writer_annot.update(
                            {
                                NameObject("/V"): TextStringObject(fields[field]),
                            }
                        )
                    elif isinstance(fields[field], bool):
                        value = self.checkbox_true_identificator if fields[field] else ""
                        writer_annot.update(
                            {
                                NameObject("/V"): NameObject(value),
                                NameObject("/AS"): NameObject(value),
                            }
                        )

    def get_pdf_stream(self):
        output_stream = io.BytesIO()
        self.write(output_stream)
        return output_stream
