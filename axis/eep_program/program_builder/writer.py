"""writer.py: Django """
import datetime
import logging
import os

from axis.company.models import Company
from . import utils

__author__ = "Johnny Fang"
__date__ = "11/20/2019 06:00"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]

log = logging.getLogger(__name__)


class ProgramWriter:
    """produce the contents of a program file"""

    def __init__(self, spec, file_name=None):
        """ """
        self.specification = spec
        if file_name is None:
            file_name = self.specification.slug
        self.file_name = file_name

    def as_string(self):  # noqa: C901
        """Return a string of the file contents."""
        settings = self.unpack_settings()
        attrs_list = []
        import_list = []

        handled = [
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
            "visibility_date",
            "program_visibility_date",
            "start_date",
            "program_start_date",
            "close_warning_date",
            "program_close_warning_date",
            "close_warning",
            "program_close_warning",
            "close_date",
            "program_close_date",
            "submit_date",
            "program_submit_date",
            "submit_warning_date",
            "program_submit_warning_date",
            "submit_warning",
            "program_submit_warning",
            "end_date",
            "program_end_date",
            "comment",
        ]

        for setting, info in settings.items():
            if setting in handled:
                continue

            if info is not None and len(str(info)):
                if callable(info):
                    info = info()
                if type(info) == Company:
                    attrs_list.append("    %s = '%s'" % (setting, info.slug))
                else:
                    attrs_list.append("    %s = %r" % (setting, info))
            else:
                log.info("skipping %s %r", setting, info)

        p_keys = [
            ("visibility_date", "program_visibility_date"),
            ("start_date", "program_start_date"),
            ("close_warning_date", "program_close_warning_date"),
            ("close_warning", "program_close_warning"),
            ("close_date", "program_close_date"),
            ("submit_date", "program_submit_date"),
            ("submit_warning_date", "program_submit_warning_date"),
            ("submit_warning", "program_submit_warning"),
            ("end_date", "program_end_date"),
        ]
        found = False
        for label, setting in p_keys:
            if settings.get(setting) is not None:
                start = "\n" if not found else ""
                attrs_list.append("%s    %s = %r" % (start, label, settings.get(setting)))
                found = True

        if settings.get("comment"):
            attrs_list.append('\n    comment = """%s"""' % settings.get("comment"))

        is_qa = settings.get("is_qa_program", False)
        rel_key = "qa_require_home_relationships" if is_qa else "require_home_relationships"
        pro_key = "qa_require_provider_relationships" if is_qa else "require_provider_relationships"

        attrs_list.append("\n    %s = {" % rel_key)
        attrs_list.append(
            "        'builder': %r," % settings.get("require_builder_assigned_to_home", False)
        )
        attrs_list.append(
            "        'hvac': %r," % settings.get("require_hvac_assigned_to_home", False)
        )
        attrs_list.append(
            "        'utility': %r," % settings.get("require_utility_assigned_to_home", False)
        )
        attrs_list.append(
            "        'rater': %r," % settings.get("require_rater_assigned_to_home", False)
        )
        attrs_list.append(
            "        'provider': %r," % settings.get("require_provider_assigned_to_home", False)
        )
        attrs_list.append("        'qa': %r," % settings.get("require_qa_assigned_to_home", False))
        attrs_list.append("    }")
        attrs_list.append("    %s = {" % pro_key)
        attrs_list.append(
            "        'builder': %r," % settings.get("require_builder_relationship", False)
        )
        attrs_list.append("        'hvac': %r," % settings.get("require_hvac_relationship", False))
        attrs_list.append(
            "        'utility': %r," % settings.get("require_utility_relationship", False)
        )
        attrs_list.append(
            "        'rater': %r," % settings.get("require_rater_relationship", False)
        )
        attrs_list.append(
            "        'provider': %r," % settings.get("require_provider_relationship", False)
        )
        attrs_list.append("        'qa': %r," % settings.get("require_qa_relationship", False))
        attrs_list.append("    }")

        # reads goods stuff from the db (checklists stuff) so we can add more specs to our template
        self.specification.read_from_db_legacy(self.specification.slug)
        measure_list = self.build_measures_specs_string()
        if measure_list:
            attrs_list += measure_list
        #
        texts_list = self.build_texts_specs_string()
        if texts_list:
            attrs_list += texts_list

        desc_list = self.build_descriptions_specs_string()
        if desc_list:
            attrs_list += desc_list

        suggested_resp_list = self.build_suggested_responses_string()
        if suggested_resp_list:
            attrs_list += suggested_resp_list

        instrument_types = self.build_instrument_types_string()
        if instrument_types:
            attrs_list += instrument_types

        optional_measures = self.build_optional_measures_string()
        if optional_measures:
            attrs_list += optional_measures

        suggested_response_flags = self.build_suggested_response_flags_string()
        if suggested_response_flags:
            attrs_list += suggested_response_flags

        annotations_list = self.build_annotations_string()
        if annotations_list:
            attrs_list += annotations_list
            import_list.append("from collections import OrderedDict")

        attrs = "\n".join(attrs_list) + "\n" if attrs_list else ""
        today = datetime.datetime.now().strftime("%m/%d/%Y %H:%M")
        imports = IMPORT_TEMPLATE % {"today": today, "year": datetime.datetime.now().year}
        if import_list:
            imports += "\n".join(import_list)
            imports += "\n"

        class_name = self.specification.class_name
        if class_name[0] in list(map(str, range(10))):
            class_name = "Program" + class_name
        result = imports + PROGRAM_TEMPLATE % {"class_name": class_name}
        result = result + "\n" + attrs
        return result

    def unpack_settings(self):
        settings = utils.unpack_settings(self.specification, self.specification.program_settings)
        return settings

    @property
    def basedir(self):
        return os.path.abspath(os.path.dirname(__file__))

    @property
    def filename(self):
        file_name = str(self.file_name).replace("-", "_")
        if file_name.endswith(".py"):
            file_name = file_name.replace(".py", "")
        return "generated_%s.py" % file_name

    @property
    def path(self):
        return os.path.join(self.basedir, self.filename)

    def build_measures_specs_string(self):
        """Builds the 'measures' specs."""
        attrs_string = []
        if self.specification.measures:
            roles = self.specification.measures.keys()
            measures = self.specification.measures
            attrs_string.append("    measures = {")
            for role in roles:
                attrs_string.append("        '%s': {" % role)
                # what should I name this variable??
                ks = measures[role].keys()
                for k in ks:
                    attrs_string.append("            '%s': [" % k)
                    _found = []
                    for measure in measures[role][k]:
                        if measure not in _found:
                            attrs_string.append("                '%s'," % measure)
                            _found.append(measure)
                    attrs_string.append("            ],")
                attrs_string.append("        },")
            attrs_string.append("    }")
        return attrs_string

    def build_texts_specs_string(self):
        """Builds the 'texts' specs."""
        attrs_string = []
        if self.specification.texts:
            roles = self.specification.texts.keys()
            texts = self.specification.texts
            attrs_string.append("    texts = {")
            for role in roles:
                attrs_string.append("        '%s': {" % role)
                for text, value in texts[role].items():
                    attrs_string.append("""            '%s': %r,""" % (text, value))
                attrs_string.append("        },")
            attrs_string.append("    }")
        return attrs_string

    def build_descriptions_specs_string(self):
        """Builds the 'descriptions' specs"""
        attrs_string = []
        if self.specification.descriptions:
            ks = self.specification.descriptions.keys()
            items = self.specification.descriptions
            attrs_string.append("    descriptions = {")
            for key in ks:
                attrs_string.append("        '%s': {" % key)
                for description, value in items[key].items():
                    if value and len(value):
                        attrs_string.append('            \'%s\': """%s""",' % (description, value))
                attrs_string.append("        },")
            attrs_string.append("    }")
        return attrs_string

    def build_suggested_responses_string(self):
        """Builds the 'suggested_responses' specs"""
        attrs_string = []
        if self.specification.suggested_responses:
            roles = self.specification.suggested_responses.keys()
            suggested_responses = self.specification.suggested_responses
            attrs_string.append("    suggested_responses = {")
            for role in roles:
                attrs_string.append("        '%s': {" % role)
                ks = suggested_responses[role].keys()

                for k in ks:
                    key_list = []
                    if type(k) == list or type(k) == tuple:
                        for el in k:
                            key_list.append("'%s', " % el)
                    else:
                        key_list.append("'%s', " % k)
                    attrs_string.append("            (%s): [" % "".join(key_list))
                    _found = []
                    for suggested in suggested_responses[role][k]:
                        if suggested not in _found:
                            attrs_string.append("                '%s'," % suggested)
                            _found.append(suggested)
                    attrs_string.append("            ],")
                attrs_string.append("        },")
            attrs_string.append("    }")
        return attrs_string

    def build_annotations_string(self):
        attrs_string = []
        if self.specification.annotations:
            annotations_slugs = self.specification.annotations.keys()
            annotations = self.specification.annotations
            attrs_string.append("    annotations = OrderedDict((")
            for slug in annotations_slugs:
                attrs_string.append("        ('%s', {" % slug)
                name = annotations[slug]["name"]
                attrs_string.append("            'name': '%s'," % name)
                data_type = annotations[slug]["data_type"]
                attrs_string.append("            'data_type': '%s'," % data_type)
                if "valid_multiplechoice_values" in annotations[slug]:
                    vm_values = annotations[slug]["valid_multiplechoice_values"]
                    attrs_string.append(
                        "            'valid_multiplechoice_values': '%s'," % vm_values
                    )
                is_required = annotations[slug]["is_required"]
                attrs_string.append("            'is_required': '%s'," % is_required)
                attrs_string.append("        }),")
            attrs_string.append("    ))")
        return attrs_string

    def build_instrument_types_string(self):
        attrs_string = []
        if self.specification.instrument_types:
            types_keys = self.specification.instrument_types.keys()
            types = self.specification.instrument_types
            attrs_string.append("    instrument_types = {")
            for k in types_keys:
                attrs_string.append("        '%s': [" % k)
                _found = []
                for measure in types[k]:
                    if measure not in _found:
                        attrs_string.append("            '%s'," % measure)
                        _found.append(measure)
                attrs_string.append("        ],")
            attrs_string.append("    }")
        return attrs_string

    def build_optional_measures_string(self):
        """Builds the 'suggested_responses' specs string"""
        attrs_string = []
        if self.specification.optional_measures:
            optional_measures = self.specification.optional_measures
            attrs_string.append("    optional_measures = [")
            for optional_measure in optional_measures:
                attrs_string.append("        '%s'," % optional_measure)
            attrs_string.append("    ]")
        return attrs_string

    def build_suggested_response_flags_string(self):
        """Builds suggested_response_flags specs string"""
        attrs_string = []
        if self.specification.suggested_response_flags:
            attrs_string.append("    suggested_response_flags = {")
            response_flags = self.specification.suggested_response_flags
            roles = self.specification.suggested_response_flags.keys()
            for role in roles:
                attrs_string.append("        '%s': {" % role)
                measures = response_flags[role]
                for measure, question_choices in measures.items():
                    attrs_string.append("            '%s': {" % measure)
                    for choice, flags in question_choices.items():
                        attrs_string.append("                '%s': {" % choice)
                        for flag in flags.keys():
                            attrs_string.append("                '%s': True," % flag)
                        attrs_string.append("                },")
                    attrs_string.append("            },")
                attrs_string.append("        },")
            attrs_string.append("    }")
        return attrs_string


IMPORT_TEMPLATE = '''\
"""This was generated via write_program"""

__author__ = 'Steven K'
__date__ = '%(today)s'
__copyright__ = 'Copyright 2011-%(year)s Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven K', ]

from .base import ProgramBuilder
import datetime
'''
PROGRAM_TEMPLATE = """\


class %(class_name)s(ProgramBuilder):
"""

PROGRAM_TEMPLATE_EXAMPLE = """\

__author__ = 'Steven K'
__date__ = '%(today)s'
__copyright__ = 'Copyright 2011-%(year)s Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven K', ]

from .base import ProgramBuilder

class %(class_name)s(ProgramBuilder):
    name='%(name)s'
    slug='%(slug)s'
    comment=\"\"\"%(comment)s\"\"\",
    manual_transition_on_certify='%(manual_transition_on_certify)s',

    owner='%(owner)s'
    viewable_by_company_type='%(viewable_by_company_type)s'
    builder_incentive_dollar_value='%(builder_incentive_dollar_value)s'
    rater_incentive_dollar_value='%(rater_incentive_dollar_value)s'

    enable_standard_disclosure='%(enable_standard_disclosure)s'
    require_floorplan_approval='%(require_floorplan_approval)s'

    program_visibility_date='%(visibility_date)s'
    program_start_date='%(start_date)s'
    program_end_date='%(end_date)s'

    program_submit_date='%(submit_date)s'
    program_close_date='%(close_date)s'

    program_close_warning_date='%(close_warning_date)s'
    program_close_warning='%(close_warning)s'
    submit_warning_date='%(close_warning)s'
    program_submit_warning='%(submit_warning)s'

    min_hers_score='%(min_hers_score)s'
    max_hers_score='%(max_hers_score)s'

    is_public='%(is_public)s'

    annotations='%(annotations)s'

"""
