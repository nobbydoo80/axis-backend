"""test_reports.py: """


from tempfile import NamedTemporaryFile

from axis.core.tests.testcases import AxisTestCase
from .mixins import CustomerAPS2019ModelTestMixin
from ..reports import ECBSVGBuilder, CheckRequest

__author__ = "Artem Hruzd"
__date__ = "07/23/2019 17:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class APSReportTests(CustomerAPS2019ModelTestMixin, AxisTestCase):
    def test_ecbsvg_builder_report(self):
        col_names = ["Col1", "Col2", "Col3", "Col4", "Col5", "Col6"]
        data = [
            col_names,
            ["1146", "1210", "1278", "1361", "1469", "1608"],
            ["205", "185", "203", "219", "186", "237"],
            ["53", "53", "53", "67", "66", "66"],
            ["410", "417", "426", "454", "467", "484"],
            ["177", "177", "177", "177", "177", "177"],
            ["846", "833", "859", "917", "897", "964"],
            ["70", "69", "72", "76", "75", "80"],
        ]

        a = ECBSVGBuilder(data)
        svg_str = a.build()

        for col_name in col_names:
            self.assertIn(col_name, svg_str)

    def test_check_request_report(self):
        from axis.incentive_payment.tests.factories import (
            basic_pending_builder_incentive_distribution_factory,
        )

        incentive_distribution = basic_pending_builder_incentive_distribution_factory()
        with NamedTemporaryFile() as f:
            from PyPDF2 import PdfReader

            check_request = CheckRequest(filename=f)
            check_request.build(invoice=incentive_distribution)
            pdf_obj = PdfReader(f)
            doc_info = pdf_obj.metadata
            self.assertIn("ReportLab PDF Library", doc_info["/Creator"])
