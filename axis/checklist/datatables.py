"""views.py: Django community"""


import logging

import datatableview
from datatableview import datatables, helpers
from django.urls import reverse

from axis.company.models import Company
from django.core.exceptions import ObjectDoesNotExist

from .models import CheckList, Section, Question

__author__ = "Jacob Buchholdt"
__date__ = "6/28/17 12:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class ChecklistListDatatable(datatables.Datatable):
    module = CheckList

    checklist = datatables.DisplayColumn(
        "Checklist", sources=["name"], processor="get_column_Checklist_data"
    )
    public = datatables.DisplayColumn(
        "Public", sources=["public"], processor=helpers.make_boolean_checkmark
    )
    owner = datatables.DisplayColumn("Owner", sources=["owner"], processor="get_column_Owner_data")

    class Meta:
        columns = ["checklist", "public", "owner"]
        ordering = ["checklist"]

    def get_column_Checklist_data(self, instance, *args, **kwargs):
        url = reverse("checklist:checklist_detail", kwargs={"slug": instance.slug})
        return """<a href="{}">{}</a>""".format(url, instance.name)

    def get_column_Owner_data(self, instance, *args, **kwargs):
        try:
            company = Company.objects.get(group=instance.group)
            return datatableview.helpers.link_to_model(company)
        except ObjectDoesNotExist:
            return ""


class SectionListDatatable(datatables.Datatable):
    module = Section
    name = datatables.TextColumn("Name", sources=["name"], processor=helpers.link_to_model)
    created_date = datatables.TextColumn("Created date", sources=[""])
    delete = datatables.TextColumn("Delete", sources=[""], processor="get_column_Delete_data")

    class Meta:
        columns = ["name", "created_date", "delete"]
        ordering = ["name"]

    def get_column_Delete_data(self, obj, *args, **kwargs):
        delete = '<a href="{}"><i class="fa fa-trash-o"></i> Delete</a>'
        return delete.format(reverse("checklist:section_delete", kwargs={"slug": obj.slug}))


class QuestionListDatatable(datatables.Datatable):
    module = Question

    question = datatables.TextColumn(
        "Question", sources=["question"], processor="get_column_Question_data"
    )
    answer_type = datatables.TextColumn(
        "Answer type", sources=["type"], processor=helpers.attrgetter("get_type_display")
    )
    required = datatables.TextColumn(
        "Required", sources=["is_required"], processor=helpers.make_boolean_checkmark
    )
    section = datatables.TextColumn(
        "Section", sources=["section__name"], processor="get_column_Section_data"
    )

    class Meta:
        columns = ["question", "answer_type", "required", "section"]
        ordering = ["question"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.checklist = kwargs.pop("checklist")
        self.section = kwargs.pop("section")
        self.program = kwargs.pop("program")
        super(QuestionListDatatable, self).__init__(*args, **kwargs)

    def get_column_Question_data(self, instance, *args, **kwargs):
        url = reverse("checklist:question_detail", kwargs={"pk": instance.id})
        data = """<a href="{}">{}</a>""".format(url, instance)
        if self.user.is_superuser:
            data += " ({})".format(instance.slug)
        return data

    def get_column_Section_data(self, instance, **kwargs):
        sections = []
        if self.checklist:
            for section in instance.section_set.filter(checklist=self.checklist):
                url = reverse("checklist:section_detail", kwargs={"slug": section.slug})
                sections.append("""<a href="{}">{}</a>""".format(url, section.name))
            return "<br />".join(sections)
