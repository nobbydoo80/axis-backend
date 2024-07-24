"""views.py: Django checklist"""


import logging
import tempfile

from django.conf import settings
from django.http import HttpResponse
from django.utils.text import slugify
from django.views.generic import View

from axis.core.mixins import AuthenticationMixin
from axis.eep_program.models import EEPProgram
from axis.filehandling.views import AsynchronousProcessedDocumentCreateView
from .forms import AsynchronousChecklistCreateForm, BulkChecklistUploadForm
from .utils import ExcelChecklist

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__file__)


class AsynchronousChecklistCreateView(AsynchronousProcessedDocumentCreateView):
    permission_required = "checklist.add_checklist"
    form_class = AsynchronousChecklistCreateForm

    def get_context_data(self, **kwargs):
        kwargs.update(
            {
                "template": settings.STATIC_URL + "templates/Checklist_Master_Template.xlsx",
                "title": "New Checklist Creation Upload",
            }
        )
        return super(AsynchronousChecklistCreateView, self).get_context_data(**kwargs)


# Bulk
class BulkChecklistDownload(AuthenticationMixin, View):
    permission_required = "checklist.add_answer"

    breakout_choices = False

    def get(self, request, *args, **kwargs):
        eep_program = EEPProgram.objects.get(id=self.kwargs.get("pk"))
        company = self.request.user.company

        filename = slugify(eep_program.name)
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename={}.xlsx".format(filename)

        with tempfile.NamedTemporaryFile(suffix=".xlsx") as f:
            template = ExcelChecklist(
                eep_program_id=eep_program.id, company_id=company.id, user_id=self.request.user.id
            )
            template.create_bulk_checklist(
                company, eep_program=eep_program, filename=f, breakout_choices=self.breakout_choices
            )
            response.write(f.read())

        return response


class BulkChecklistUpload(AsynchronousProcessedDocumentCreateView):
    permission_required = "checklist.add_answer"
    form_class = BulkChecklistUploadForm
    template_name = "checklist/checklist_bulk_upload.html"

    def form_valid(self, form):
        # Set this kwarg; it will be sent to the task function
        self.kwargs["overwrite_old_answers"] = form.cleaned_data["update_existing_answers"]
        return super(BulkChecklistUpload, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs["title"] = "Bulk Homes with Checklist Upload"
        return super(AsynchronousProcessedDocumentCreateView, self).get_context_data(**kwargs)
