"""write_program.py: Django """
import decimal
import io
import logging

from django.core.management import BaseCommand
from django.forms import model_to_dict

from axis.eep_program.models import EEPProgram
from axis.eep_program.program_builder.base import ProgramBuilder
from axis.eep_program.program_builder.writer import ProgramWriter

__author__ = "Johnny Fang"
__date__ = "11/21/2019 10:23"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Creates a program from a legacy program."

    def add_arguments(self, parser):
        """Add arguments"""
        parser.add_argument(
            "-p",
            "--eep_program",
            action="store",
            dest="program",
            type=str,
            required=True,
            help="Whats the program slug",
        )
        parser.add_argument(
            "-f",
            "--filename",
            action="store",
            dest="filename",
            type=str,
            required=False,
            help="Whats the desired output filename?",
        )

    def handle(self, *app_labels, **options):
        """Does the lifting"""
        eep_program = EEPProgram.objects.get(slug=options["program"])
        filename = options.get("filename")

        class XXXProgram(ProgramBuilder):
            class_name = "".join([x.capitalize() for x in eep_program.slug.split("-")])
            name = eep_program.name
            slug = eep_program.slug
            owner = eep_program.owner.slug
            viewable_by_company_type = eep_program.viewable_by_company_type

            require_input_data = eep_program.require_input_data
            require_rem_data = eep_program.require_rem_data
            require_model_file = eep_program.require_model_file
            require_ekotrope_data = eep_program.require_ekotrope_data

            manual_transition_on_certify = eep_program.manual_transition_on_certify

            visibility_date = eep_program.program_visibility_date
            start_date = eep_program.program_start_date
            close_warning_date = eep_program.program_close_warning_date
            close_warning = eep_program.program_close_warning
            close_date = eep_program.program_close_date
            submit_date = eep_program.program_submit_date
            submit_warning_date = eep_program.program_submit_warning_date
            submit_warning = eep_program.program_submit_warning
            end_date = eep_program.program_end_date

            comment = eep_program.comment

            require_home_relationships = {
                "builder": eep_program.require_builder_assigned_to_home,
                "hvac": eep_program.require_hvac_assigned_to_home,
                "utility": eep_program.require_utility_assigned_to_home,
                "rater": eep_program.require_rater_assigned_to_home,
                "provider": eep_program.require_provider_assigned_to_home,
                "qa": eep_program.require_qa_assigned_to_home,
            }
            require_provider_relationships = {
                "builder": eep_program.require_builder_relationship,
                "hvac": eep_program.require_hvac_relationship,
                "utility": eep_program.require_utility_relationship,
                "rater": eep_program.require_rater_relationship,
                "provider": eep_program.require_provider_relationship,
                "qa": eep_program.require_qa_relationship,
            }

            measures = {}
            texts = {}
            descriptions = {}
            instrument_order = []
            instrument_response_policies = {}
            instrument_types = {}
            instrument_conditions = {}
            suggested_responses = {}
            suggested_response_flags = {}
            optional_measures = []

            annotations = {}

        spec = XXXProgram()
        for k, v in model_to_dict(eep_program).items():
            if k in [
                "owner",
                "collection_request",
                "required_checklists",
                "required_annotation_types",
                "slug",
                "require_builder_assigned_to_home",
                "require_builder_relationship",
                "require_hvac_assigned_to_home",
                "require_hvac_relationship",
                "require_utility_assigned_to_home",
                "require_utility_relationship",
                "require_rater_assigned_to_home",
                "require_rater_relationship",
                "require_provider_assigned_to_home",
                "require_provider_relationship",
                "require_qa_assigned_to_home",
                "require_qa_relationship",
                "program_visibility_date",
                "program_start_date",
                "program_close_warning_date",
                "program_close_warning",
                "program_close_date",
                "program_submit_date",
                "program_submit_warning_date",
                "program_submit_warning",
                "program_end_date",
                "certifiable_by",
                "opt_in_out_list",
            ]:  # TODO FIX ME
                continue

            if hasattr(spec, k) and getattr(spec, k) != v:
                if k not in ["owner"]:
                    log.error("Mis-defined attribute %r - %s != %s", k, getattr(spec, k), v)
            if v is not None:
                if isinstance(v, decimal.Decimal):
                    v = float(v)
                setattr(spec, k, v)

        if eep_program.is_qa_program:
            setattr(spec, "qa_require_home_relationships", spec.require_home_relationships.copy())
            setattr(spec, "require_home_relationships", {})
            setattr(
                spec,
                "qa_require_provider_relationships",
                spec.require_provider_relationships.copy(),
            )
            setattr(spec, "require_provider_relationships", {})

        self.write_program_file(spec, filename)

    def write_program_file(self, spec, filename=None, print_output=True):
        writer = ProgramWriter(spec, filename)
        # program_dir = os.path.dirname(writer.path)
        program_string = writer.as_string()
        with io.open(writer.path, "w", encoding="utf-8") as fh:
            fh.write(program_string)
        if print_output:
            self.stdout.write("Program builder specs '%s':" % writer.filename + "\n")
        return writer.path
