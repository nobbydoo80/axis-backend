import os
import logging

from datatableview import datatables, helpers

from .models import Workflow, WorkflowStatus, CertifiableObject


__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class WorkflowStatusDatatable(datatables.Datatable):
    name = datatables.TextColumn(source="certifiable_object__name", processor="get_name")
    state = datatables.TextColumn(source="state", processor="get_state")

    class Meta:
        columns = ["name", "state", "eep_program"]

    def __init__(self, *args, **kwargs):
        super(WorkflowStatusDatatable, self).__init__(*args, **kwargs)

        workflow = kwargs["workflow"]
        config = workflow.get_config()
        object_type = kwargs["view"].kwargs["type"]
        self.columns["state"].label = config.get_object_type_state_label(object_type=object_type)
        self.columns["eep_program"].label = config.get_eep_program_verbose_name(
            object_type=object_type
        )

    def get_name(self, instance, **kwargs):
        data = helpers.link_to_model(instance.certifiable_object)
        if instance.data.get("escalated"):
            data = """<strong>%s</strong>""" % (data,)
        return data

    def get_state(self, instance, **kwargs):
        data = instance.get_state_display()
        if instance.data.get("escalated"):
            data += """ <span class="label label-warning">Elevated</span>"""
        return data


class CertifiableObjectDatatable(datatables.Datatable):
    name = datatables.TextColumn(source="__str__", processor=helpers.link_to_model)
    parent = datatables.TextColumn(source="parent.__str__", processor="get_parent_link")

    class Meta:
        columns = ["name", "parent"]

    def __init__(self, *args, **kwargs):
        super(CertifiableObjectDatatable, self).__init__(*args, **kwargs)

        workflow = kwargs["workflow"]
        config = workflow.get_config()
        this_type = kwargs["view"].kwargs["type"]
        parent_type = config.get_parent_type(object_type=this_type)
        if parent_type:
            parent_label = config.get_object_type_name(object_type=parent_type)
            self.columns["parent"].label = parent_label

    def get_parent_link(self, instance, **kwargs):
        if instance.parent:
            return helpers.link_to_model(instance.parent)
        return "-"


class InlineWorkflowStatusDatatable(datatables.Datatable):
    name = datatables.TextColumn("Name", processor="get_name")
    units = datatables.DisplayColumn("Number of Units", processor="get_number_of_units")
    cfa = datatables.DisplayColumn("Conditioned Floor Area", processor="get_conditioned_floor_area")

    class Meta:
        columns = ["name", "units", "cfa"]

    def get_name(self, instance, **kwargs):
        return helpers.link_to_model(instance.certifiable_object)

    def get_number_of_units(self, instance, **kwargs):
        return instance.data.get("number_of_units") or "-"

    def get_conditioned_floor_area(self, instance, **kwargs):
        try:
            return "{:,d}".format(int(float(instance.data["conditioned_floor_area"])))
        except:
            return "-"
