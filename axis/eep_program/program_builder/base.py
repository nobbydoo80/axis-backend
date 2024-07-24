"""Program builders"""
import enum
import logging
import sys
from collections import OrderedDict, defaultdict
from datetime import datetime

from django.db.models import F
from django_input_collection.models import get_input_model
from infrastructure.utils import deprecated

from axis.annotation.models import Type
from axis.checklist.models import Question
from axis.company.models import Company
from axis.home.models import EEPProgramHomeStatus
from . import utils

__author__ = "Autumn Valenta"
__date__ = "10/08/18 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)

CollectedInput = get_input_model()
CollectedInput = get_input_model()


class unset(object):
    pass


class ProgramBuilder(object):
    __version__ = (0, 0, 1, "alpha-qasegments")

    slug = None
    name = None
    comment = ""
    owner = None  # company slug
    visibility_date = datetime.utcnow()
    start_date = datetime.utcnow()
    end_date = None
    date_range = []
    submit_date = None
    close_date = None
    open_range = []
    close_warning_date = None
    close_warning = None
    submit_warning_date = None
    submit_warning = None

    viewable_by_company_type = None

    require_input_data = False
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False

    hers_range = [0, 100]
    require_home_relationships = []  # company types for relationship requirement flags
    require_provider_relationships = []  # company types for relationship requirement flags

    annotations = {}

    response_limit = None
    response_limit_per_user = 1
    default_instrument_type = "open"
    ordering_step_size = 100  # Group measure order advances in multiples, >=10% gap ensured between
    measures = {}
    texts = {}
    descriptions = {}
    help_text = {}  # These are longer and support html
    instrument_order = []
    instrument_response_policies = {}
    instrument_types = {}
    instrument_condition_types = {}
    instrument_conditions = {}
    suggested_responses = {}
    suggested_response_flags = {}
    optional_measures = []
    enable_multiple_inputs = {
        "default": {},
        "rater": {},
        "qa": {},
    }

    role_settings = {
        "qa": {
            "slug": lambda slug: "{slug}-qa".format(slug=slug),
            "name": lambda name: "{name} QA".format(name=name),
            "is_qa_program": True,
        },
    }
    program_settings = {
        # Map settings to model attribute names they correspond to
        "name": "name",
        "slug": "slug",
        "comment": "comment",
        "owner": lambda slug: Company.objects.get(slug=slug),
        "certifiable_by": "certifiable_by",
        "qa_certifiable_by": "qa_certifiable_by",
        "is_qa_program": "is_qa_program",
        "opt_in": "opt_in",
        # 'workflow': 'workflow',
        "workflow_default_settings": "workflow_default_settings",
        "viewable_by_company_type": "viewable_by_company_type",
        "qa_viewable_by_company_type": "viewable_by_company_type",
        "min_hers_score": "min_hers_score",
        "max_hers_score": "max_hers_score",
        "per_point_adder": "per_point_adder",
        "builder_incentive_dollar_value": "builder_incentive_dollar_value",
        "rater_incentive_dollar_value": "rater_incentive_dollar_value",
        "enable_standard_disclosure": "enable_standard_disclosure",
        "require_floorplan_approval": "require_floorplan_approval",
        "require_input_data": "require_input_data",
        "require_rem_data": "require_rem_data",
        "require_model_file": "require_model_file",
        "require_ekotrope_data": "require_ekotrope_data",
        "require_rater_of_record": "require_rater_of_record",
        # LEGACY DO NOT USE
        # 'allow_rem_input': 'allow_rem_input',
        # 'allow_ekotrope_input': 'allow_ekotrope_input',
        "manual_transition_on_certify": "manual_transition_on_certify",
        "qa_require_home_relationships": {
            "builder": "require_builder_assigned_to_home",
            "hvac": "require_hvac_assigned_to_home",
            "utility": "require_utility_assigned_to_home",
            "rater": "require_rater_assigned_to_home",
            "provider": "require_provider_assigned_to_home",
            "qa": "require_qa_assigned_to_home",
        },
        "qa_require_provider_relationships": {
            "builder": "require_builder_relationship",
            "hvac": "require_hvac_relationship",
            "utility": "require_utility_relationship",
            "rater": "require_rater_relationship",
            "provider": "require_provider_relationship",
            "qa": "require_qa_relationship",
        },
        "require_home_relationships": {
            "builder": "require_builder_assigned_to_home",
            "hvac": "require_hvac_assigned_to_home",
            "utility": "require_utility_assigned_to_home",
            "rater": "require_rater_assigned_to_home",
            "provider": "require_provider_assigned_to_home",
            "qa": "require_qa_assigned_to_home",
            "architect": "require_architect_assigned_to_home",
            "developer": "require_developer_assigned_to_home",
            "communityowner": "require_communityowner_assigned_to_home",
        },
        "require_provider_relationships": {
            "builder": "require_builder_relationship",
            "hvac": "require_hvac_relationship",
            "utility": "require_utility_relationship",
            "rater": "require_rater_relationship",
            "provider": "require_provider_relationship",
            "qa": "require_qa_relationship",
            "architect": "require_architect_relationship",
            "developer": "require_developer_relationship",
            "communityowner": "require_communityowner_relationship",
        },
        "allow_sampling": "allow_sampling",
        "allow_metro_sampling": "allow_metro_sampling",
        "require_resnet_sampling_provider": "require_resnet_sampling_provider",
        "is_legacy": "is_legacy",
        "is_public": "is_public",
        "program_visibility_date": "program_visibility_date",
        "visibility_date": "program_visibility_date",
        "program_start_date": "program_start_date",
        "start_date": "program_start_date",
        "program_close_date": "program_close_date",
        "close_date": "program_close_date",
        "program_submit_date": "program_submit_date",
        "submit_date": "program_submit_date",
        "program_end_date": "program_end_date",
        "end_date": "program_end_date",
        "program_close_warning_date": "program_close_warning_date",
        "close_warning_date": "program_close_warning_date",
        "program_close_warning": "program_close_warning",
        "close_warning": "program_close_warning",
        "program_submit_warning_date": "program_submit_warning_date",
        "submit_warning_date": "program_submit_warning_date",
        "program_submit_warning": "program_submit_warning",
        "submit_warning": "program_submit_warning",
        "is_active": "is_active",
        "is_multi_family": "is_multi_family",
    }

    collection_request_settings = {
        "response_limit": lambda n: {"max_instrument_inputs": n},
        "response_limit_per_user": lambda n: {"max_instrument_inputs_per_user": n},
    }

    # Internals
    _inputs = None
    _keys = set()

    def __init__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.from_management_command = False

    def log_error(self, msg):
        if self.from_management_command:
            self.stderr.write(msg + "\n")
        else:
            log.error(msg)

    def log_warning(self, msg):
        if self.from_management_command:
            self.stderr.write(msg + "\n")
        else:
            log.warning(msg)

    def log_info(self, msg):
        if self.from_management_command:
            self.stdout.write(msg + "\n")
        else:
            log.info(msg)

    def log_debug(self, msg):
        log.debug(msg)

    def read_from_db_legacy(self, slug):
        from axis.eep_program.models import EEPProgram

        program = EEPProgram.objects.get(slug=slug)
        # let's get the checklists if any
        for checklist in program.required_checklists.all():
            self.log_info(f"Looking at checklist {checklist!r}")
            questions = []
            for section in checklist.section_set.all():
                self.log_info(f"Looking at section {section!r}")
                for question in section.questions.all().order_by("priority"):
                    self.log_info(f"Looking at section {section!r} question {question!r}")
                    self.read_question(question, is_qa=program.is_qa_program)
                    questions.append(question)
            else:
                for question in program.get_checklist_question_set().order_by("priority"):
                    if question not in questions:
                        self.log_info(r"Looking at question {question!r}")
                        self.read_question(question, is_qa=program.is_qa_program)

        # let's get any annotations required by the program if any
        for annotation_type in program.required_annotation_types.all():
            self.log_info(f"Looking at annotations {annotation_type!r}")
            self.read_annotation_type(annotation_type)

    def read_question(self, question, is_qa):  # noqa: C901
        role = "rater"
        if is_qa:
            role = "qa"
        measure = question.slug

        # more can be found in convert_checklist_to_collection in safe_ops.py
        text = question.question
        description = question.description or ""
        self.instrument_order.append(measure)

        # gets the measures spec
        if role not in self.measures:
            self.measures[role] = {"default": [measure]}
        else:
            self.measures[role]["default"].append(measure)

        # gets the texts spec
        if role not in self.texts:
            self.texts[role] = {measure: text}
        else:
            self.texts[role][measure] = text

        # gets the descriptions spec
        if role not in self.descriptions:
            self.descriptions[role] = {measure: description}
        else:
            self.descriptions[role][measure] = description

        # gets the suggested_responses specs
        choices = question.question_choice.values_list("choice", flat=True)

        if choices:
            choices = tuple(choices)
            if role not in self.suggested_responses:
                self.suggested_responses = {role: {choices: [measure]}}
            else:
                if choices in self.suggested_responses[role]:
                    self.suggested_responses[role][choices].append(measure)
                else:
                    self.suggested_responses[role][choices] = [measure]

        # gets the  suggested_response_flags specs
        choices_flags = list(
            question.question_choice.values_list(
                "choice", "document_required", "photo_required", "comment_required"
            )
        )
        if choices_flags:
            for choice_flag in choices_flags:
                choice = choice_flag[0]
                is_document_required = choice_flag[1]
                is_photo_required = choice_flag[2]
                is_comment_required = choice_flag[3]
                if is_comment_required or is_photo_required or is_document_required:
                    if role not in self.suggested_response_flags:
                        self.suggested_response_flags[role] = {measure: {}}
                    else:
                        if measure not in self.suggested_response_flags[role]:
                            self.suggested_response_flags[role][measure] = {}
                    question_choice = self.suggested_response_flags[role][measure]
                    if choice not in question_choice:
                        question_choice[choice] = {}
                    if is_document_required:
                        question_choice[choice]["document_required"] = True
                    if is_comment_required:
                        question_choice[choice]["comment_required"] = True
                    if is_photo_required:
                        question_choice[choice]["photo_required"] = True

        # get the question type specs iff 'integer','float' or 'date'
        q_type = question.type
        if q_type:
            if q_type == "integer" or q_type == "float" or q_type == "date":
                if q_type not in self.instrument_types:
                    self.instrument_types[q_type] = [measure]
                else:
                    self.instrument_types[q_type].append(measure)

        # gets the optional questions (optional_measures) specs
        optional_measures = question.is_optional
        if optional_measures:
            if self.optional_measures:
                self.optional_measures.append(measure)
            else:
                self.optional_measures = [measure]

    def read_annotation_type(self, annotation_type):
        annotations = self.annotations
        if not annotations:
            annotations = OrderedDict()

        # I'm not sure if we are grabbing info just from the db or we will be looking into another
        # program_builder file and get data from there. if the second is True then we need to
        # determine precedence. I'm assuming program_builder file data has higher precedence
        if annotation_type.slug not in annotations:
            annotations[annotation_type.slug] = {
                "name": annotation_type.name,
                "data_type": annotation_type.data_type,
                "valid_multiplechoice_values": annotation_type.valid_multiplechoice_values,
                "is_required": annotation_type.is_required,
            }
        self.annotations = annotations

    # Utilities
    def unpack_settings(self, **attrs):
        opposite_role = "qa" if self.role == "rater" else "rater"
        attrs = {
            k: v
            for k, v in dict(self.role_settings.get(self.role, {}), **attrs).items()
            if not k.startswith("{opposite_role}_".format(opposite_role=opposite_role))
        }
        return utils.unpack_settings(self, self.program_settings, **attrs)

    def get_deep(self, queryset, program, no_input=False):
        self.log_warning(
            f"Doing deep update of collection_requests on {queryset.count()} "
            f"existing {program.slug!r} homestatuses"
        )
        if not no_input:
            return input("Are you sure? [y/N] ") != "y"

    def get_measures(self, role):
        default = OrderedDict(self.measures.get("default", {}))
        groups = OrderedDict(self.measures.get(role, default))
        if groups is not default:
            groups_ = OrderedDict(default)
            groups_.update(groups)
            groups = groups_
        return groups

    def get_text(self, role, measure_id):
        default = self.texts.get("default", {})
        measures = self.texts.get(role, default)
        return measures.get(measure_id, default.get(measure_id, ""))

    def get_description(self, role, measure_id):
        default = self.descriptions.get("default", {})
        measures = self.descriptions.get(role, default)
        return measures.get(measure_id, default.get(measure_id, ""))

    def get_help(self, role, measure_id):
        default = self.help_text.get("default", {})
        measures = self.help_text.get(role, default)
        return measures.get(measure_id, default.get(measure_id, ""))

    def get_test_requirement_type(self, role, measure_id):
        default = self.instrument_condition_types.get("default", {})
        measures = self.instrument_condition_types.get(role, default)
        return measures.get(measure_id, default.get(measure_id, "all-pass"))

    def get_suggested_responses(self, role, measure_id):
        choices = []
        default = self.suggested_responses.get("default", {})
        for _choices, measures in default.items():
            if measure_id in measures:
                choices = self.transform_enum(_choices)

        role_info = self.suggested_responses.get(role, default)
        for _choices, measures in role_info.items():
            if measure_id in measures:
                choices = self.transform_enum(_choices)
        return choices

    def get_suggested_response_flags(self, role, measure_id):
        default = self.suggested_response_flags.get("default", {})
        role_info = self.suggested_response_flags.get(role, default)
        flags = role_info.get(measure_id, {}).copy()
        flags.update(default.get(measure_id, {}))
        return flags

    def get_type(self, role, measure_id):
        for type_id, measures in self.instrument_types.items():
            if measure_id in measures:
                return type_id
        if self.get_suggested_responses(role, measure_id):
            return "multiple-choice"
        return "open"

    def get_is_multiple(self, role, measure_id):
        default = self.enable_multiple_inputs.get("default", {})
        multiple = self.enable_multiple_inputs.get(role, default)
        return multiple.get(measure_id, default.get(measure_id, False))

    def get_conditions(self, role, resolver_type, lookup_spec):
        default_conditions = self.instrument_conditions.get("default", {}).get(resolver_type, {})
        type_conditions = self.instrument_conditions.get(role, default_conditions).get(
            resolver_type, {}
        )

        conditions = defaultdict(set)
        for conditions_set in [type_conditions, default_conditions]:
            for trigger_source, condition_info in conditions_set.items():
                for _answer_spec, enabled_measures in condition_info.items():
                    if isinstance(_answer_spec, (list, tuple)):
                        try:
                            _ans_type, _answers = _answer_spec
                            answer_spec = _ans_type, self.transform_enum(_answers)
                        except ValueError:
                            answer_spec = _answer_spec
                    else:
                        answer_spec = self.transform_enum(_answer_spec)

                    if lookup_spec not in enabled_measures:
                        continue

                    # Track condition spec and target value that contributes to this measure
                    conditions[trigger_source].add(answer_spec)

        return {
            trigger_source: list(answers_info)
            for trigger_source, answers_info in conditions.items()
        }

    # Actions
    def build(self, *roles, **kwargs):
        if not roles:
            roles = list(self.measures.keys())
            if roles is None:  # No questions
                roles = ["rater"]
                if hasattr(self, "is_qa_program") and self.is_qa_program:
                    roles.append("qa")

        deep = kwargs.pop("deep", False)
        wipe = kwargs.pop("wipe", False)
        no_input = kwargs.pop("no_input", False)
        warn_only = kwargs.pop("warn_only", False)

        stderr = kwargs.pop("stderr", None)
        if stderr:
            self.stderr = stderr
        stdout = kwargs.pop("stdout", None)
        if stdout:
            self.stdout = stdout
        self.from_management_command = kwargs.pop("from_management_command", False)

        if deep and kwargs:
            raise ValueError(
                f"Option 'deep' cannot be given when collection_request "
                f"query target kwargs are used: {kwargs!r}"
            )

        if wipe:
            self.wipe(deep, **kwargs)

        to_process = []
        if kwargs:
            kwargs.setdefault("eep_program__collection_request__isnull", False)
            to_process = EEPProgramHomeStatus.objects.filter(**kwargs)
            id_list = list(to_process.values_list("id", flat=True))
            self.log_warning(
                f"Will rewrite {len(id_list)} homestatus collection requests: {kwargs!r}"
            )

        program = None
        for role in roles:
            self.setup(role=role)
            self.setup(attrs=self.unpack_settings())

            program = self.build_program()
            self.build_annotations(program)

            collection_request = self.build_collection_request(to=program, warn_only=warn_only)
            if deep:
                to_process = program.homestatuses.all()
                if not self.get_deep(no_input=no_input):
                    continue

            for home_status in to_process:
                self.log_info(
                    f"({home_status.eep_program.slug}) {home_status.id}: {home_status} "
                    f"------------"
                )
                self.build_collection_request(to=home_status)
            self.cleanup(program, collection_request)
        return program

    def setup(self, **kwargs):
        self._keys |= set(kwargs.keys())
        for k, v in kwargs.items():
            if hasattr(self, k):
                raise ValueError()
            setattr(self, k, v)

    def cleanup(self, program, collection_request, deep=True):
        for k in self._keys:
            del self.__dict__[k]
        self._keys = set()

        # NOTE: We don't want to have lots of cleanup ops, we just want the builder to do the right
        # thing in the first place.  Please don't bloat this section with shoddy bandaids.
        if self._inputs:
            self._restore_inputs()

    def wipe(self, deep, remember_inputs=True):
        if remember_inputs:
            self._cache_existing_inputs()

    def _cache_existing_inputs(self):
        cache = {}

        queryset = CollectedInput.objects.filter(home_status__eep_program__slug=self.slug)
        queryset = queryset.annotate(measure=F("instrument__measure_id"))
        strip_hard_context = [
            "instrument_id",
            "collection_request_id",
        ]
        for info in queryset.values():
            for k in strip_hard_context:
                del info[k]
            items = cache.setdefault(info["home_status_id"], [])
            items.append(info)

        self._inputs = cache

    def _restore_inputs(self):
        self._inputs

    def transform_enum(self, values):
        """Simply transform value to strings"""
        if isinstance(values, enum.EnumMeta):
            return tuple([x.value for x in values.__members__.values()])
        if not isinstance(values, (list, tuple)):
            return values
        final = []
        for value in values:
            final.append(value.value if isinstance(value, enum.Enum) else value)
        if isinstance(values, tuple):
            return tuple(final)
        return final

    def transform_enum_dict(self, data):
        if not isinstance(data, (dict)):
            return data
        final = {}
        for k, v in data.items():
            final[self.transform_enum(k)] = self.transform_enum(v)
        return final

    # Encapsulated builds
    def build_program(self):
        if "allow_rem_input" in self.attrs and self.attrs["allow_rem_input"]:
            self.log_error("Do not use `allow_rem_input`. It's not verified!")
        if "allow_ekotrope_input" in self.attrs and self.attrs["allow_ekotrope_input"]:
            self.log_error("Do not use `allow_ekotrope_input`. It's not verified!")

        certifiable_by = self.attrs.pop("certifiable_by", [])
        qa_certifiable_by = self.attrs.pop("qa_certifiable_by", [])

        program = utils.safe_ops.derive_program(**self.attrs)

        if self.role == "rater" and certifiable_by:
            for certifiable_company_slug in certifiable_by:
                program.certifiable_by.add(Company.objects.get(slug=certifiable_company_slug))

        if self.role == "qa" and qa_certifiable_by:
            for certifiable_company_slug in qa_certifiable_by:
                program.certifiable_by.add(Company.objects.get(slug=certifiable_company_slug))

        return program

    def build_annotations(self, program):
        try:
            program.required_annotation_types.clear()
        except AttributeError:
            pass

        for slug, kwargs in self.annotations.items():
            if isinstance(kwargs.get("valid_multiplechoice_values"), list):
                new_value = Type().set_valid_multiplechoice_values(
                    kwargs["valid_multiplechoice_values"]
                )
                kwargs["valid_multiplechoice_values"] = new_value
            annotation, _ = Type.objects.update_or_create(slug=slug, defaults=kwargs)
            program.required_annotation_types.add(annotation)

    def build_collection_request(self, **kwargs):
        warn_only = kwargs.pop("warn_only", False)
        collection_request = utils.safe_ops.derive_collection_request(**kwargs)
        self.validate_checklist(warn_only=warn_only)
        self.build_checklist(collection_request)
        return collection_request

    def validate_checklist(self, warn_only=False):  # noqa: C901
        """Validate the checklist for consistancy"""

        self.log_info(f"Validating {self.role} Checklist ({self.setup()})")

        top_measures = self.get_measures(self.role)
        role_measures, all_measures = [], []
        for section, _measures in top_measures.items():
            for measure in _measures:
                text = self.get_text(self.role, measure)
                if text == "":
                    raise Exception(f"Text string is not available for measure {measure!r}")
                role_measures.append(measure)
        for role in self.measures.keys():
            for section, _measures in self.get_measures(role).items():
                for measure in _measures:
                    all_measures.append(measure)

        texts = self.texts.get(self.role, {})
        for measure, text in texts.items():
            if measure not in all_measures:
                self.log_warning(f"Unused measure {measure!r} will be skipped")

        suggested_responses = {}
        if "default" in self.suggested_responses:
            suggested_responses.update(
                self.transform_enum_dict(self.suggested_responses.get("default", {}))
            )
        if self.role in self.suggested_responses:
            suggested_responses.update(
                self.transform_enum_dict(self.suggested_responses.get(self.role, {}))
            )

        rev_suggested_responses = {}

        def get_rev_suggested_responses(suggested_responses, role):
            for responses, suggested_measures in suggested_responses.items():
                for measure in suggested_measures:
                    if measure not in all_measures:
                        msg = (
                            f"Unused {self.role} suggested response measure {measure!r} "
                            f"found for {responses!r}"
                        )
                        if warn_only:
                            self.log_error(msg)
                        else:
                            raise Exception(msg)
                    if measure in rev_suggested_responses:
                        msg = (
                            f"Suggested response for measure {measure!r} is already defined "
                            f"will override"
                        )
                        if warn_only:
                            self.log_warning(msg)
                    rev_suggested_responses[measure] = responses

        get_rev_suggested_responses(
            self.transform_enum_dict(self.suggested_responses.get("default", {}).copy()), "default"
        )

        get_rev_suggested_responses(
            self.transform_enum_dict(self.suggested_responses.get(self.role, {}).copy()), self.role
        )

        already_classified = []
        for classification, inst_type_measures in self.instrument_types.items():
            for measure in inst_type_measures:
                if all_measures and measure not in all_measures:
                    msg = (
                        f"Measure {measure!r} found in instrument_types:{classification} but is "
                        f"not defined under role_measures"
                    )
                    if warn_only:
                        self.log_error(msg)
                    else:
                        raise Exception(msg)
                if role_measures and measure in already_classified:
                    msg = (
                        f"Measure {measure!r} duplicate classification in instrument "
                        f"type {classification}"
                    )
                    if warn_only:
                        self.log_error(msg)
                    else:
                        raise Exception(msg)
                elif role_measures:
                    already_classified.append(measure)

        # Check the instrument instrument_conditions for axis suggested response stuff
        # Using the wrong flags do not present as an error upstream.
        for role, condition in self.instrument_conditions.items():
            for measure, data in condition.get("instrument", {}).items():
                for answer, policy in data.items():
                    if isinstance(policy, dict):
                        invalid = {
                            "comment_required",
                            "photo_required",
                            "comment" "document_required",
                            "is_considered_failure",
                        }
                        errors = set(policy.keys()).intersection(invalid)
                        if errors:
                            msg = (
                                f"{self.role} Suggested responses {', '.join(errors)} for measure "
                                f"{measure!r} belongs in `suggested_response_flags` not "
                                f"in `instrument_conditions`"
                            )
                            if warn_only:
                                self.log_error(msg)
                            else:
                                raise Exception(msg)

        if rev_suggested_responses:
            response_flags = self.suggested_response_flags.get("default", {}).copy()
            response_flags.update(self.suggested_response_flags.get(self.role, {}).copy())
            for _measure, response_flags in response_flags.items():
                for answer, policy in response_flags.items():
                    if _measure not in rev_suggested_responses:
                        raise KeyError(
                            f"We are not finding measure {_measure!r} in "
                            f"{', '.join(rev_suggested_responses.keys())} - Response Flags "
                            f"{response_flags} Reverse {rev_suggested_responses} Role: {role}"
                        )
                    if answer not in rev_suggested_responses[_measure]:
                        msg = f"{self.role} answer {answer} for measure {_measure!r} is not defined"
                        raise Exception(msg)
                    valid = {
                        "comment_required",
                        "photo_required",
                        "document_required",
                        "is_considered_failure",
                    }
                    errors = set(policy.keys()) - valid
                    if errors:
                        msg = (
                            f"Unknown {self.role} suggested response for {_measure!r} "
                            f"{', '.join(errors)} - only allowed {valid}"
                        )
                        if warn_only:
                            self.log_error(msg)
                        else:
                            raise Exception(msg)

        # If we are basing this on responses make sure these are valid.
        for to_ask_measure in role_measures:
            conditions = self.get_conditions(self.role, "instrument", to_ask_measure)
            if not conditions:
                continue
            for measure, opts in conditions.items():
                suggested_responses = rev_suggested_responses.get(measure)
                if not suggested_responses:
                    continue
                for item in opts:
                    if isinstance(item, enum.EnumMeta):
                        item = [e.value for e in item]
                    if isinstance(item, enum.Enum):
                        item = item.value
                    if isinstance(item, (list, tuple)):
                        # _classification = item[0]
                        answers = item[1]
                        if isinstance(answers, enum.EnumMeta):
                            answers = [e.value for e in answers]
                        for answer in answers:
                            if isinstance(answer, enum.Enum):
                                answer = answer.value
                            if answer not in suggested_responses:
                                msg = (
                                    f"Unknown suggested response for instrument condition "
                                    f"{self.role} instrument {measure}: {answer} - not found in "
                                    f"{suggested_responses}"
                                )
                                if warn_only:
                                    self.log_error(msg)
                                else:
                                    raise Exception(msg)
                    elif item not in suggested_responses:
                        msg = (
                            f"Unknown suggested response for instrument condition {self.role} "
                            f"instrument {measure}: {item} - not found in {suggested_responses}"
                        )
                        if warn_only:
                            self.log_error(msg)
                        else:
                            raise Exception(msg)

    def build_checklist(self, collection_request):
        """Build out the checklist"""
        originating_instruments = list(collection_request.collectioninstrument_set.all())
        originating_instruments = {inst.measure_id: inst for inst in originating_instruments}
        groups = self.get_measures(self.role)
        i = self.ordering_step_size
        min_step_padding = min(1, int(0.10 * self.ordering_step_size))
        for group_id, measures in groups.items():
            # Map measures to instruments for later steps to use
            to_update = {
                "segment": "checklist",
                "group": group_id,
                "collection_request": collection_request,
            }
            self.log_info(
                f"build_checklist for group {group_id!r} with "
                f"{len(measures)} measures: {measures}"
            )
            groups[group_id] = self.build_instruments(measures, start_order=i, **to_update)

            # Advance 'i' to nearest next step. Padding will roll over an extra step chunk
            # size if needed in order to guarantee the padding.
            i += len(groups[group_id]) + min_step_padding
            i = (i + self.ordering_step_size) - (i % self.ordering_step_size)

            for measure in measures:
                originating_instruments.pop(measure, None)

        for measure, instrument in originating_instruments.items():
            self.log_error(f"Removing unused instrument {instrument!r}")
            collection_request.collectioninstrument_set.get(measure=measure).delete()

        self.build_conditions(groups)
        return groups

    def build_instruments(self, measures, start_order, **attrs):
        instruments = []
        for i, measure_id in enumerate(measures):
            measure_attrs = dict(
                attrs,
                **{
                    "text": self.get_text(self.role, measure_id),
                    "description": self.get_description(self.role, measure_id),
                    "help": self.get_help(self.role, measure_id),
                    "order": start_order + i,
                    "test_requirement_type": self.get_test_requirement_type(self.role, measure_id),
                },
            )
            instrument = self.build_instrument(measure_id, **measure_attrs)
            if instrument.conditions.count():
                self.log_warning(
                    f"{instrument.conditions.count()} existing conditions found on "
                    f"{instrument.measure_id} ({instrument.id}) - Removing"
                )
                instrument.conditions.all().delete()
            instruments.append(instrument)

        return instruments

    def build_instrument(self, measure_id, group, segment, **attrs):
        attrs.update(
            {
                "measure": utils.safe_ops.derive_measure(measure_id),
                "type": self.build_type(measure_id),
                "group": utils.safe_ops.derive_group(group),
                "segment": utils.safe_ops.derive_group(segment),
                "response_policy": self.build_response_policy(measure_id),
            }
        )

        # Grab explicit 'order' from instrument_order, if available
        if measure_id in self.instrument_order:
            attrs["order"] = self.instrument_order.index(measure_id)

        instrument = utils.safe_ops.derive_instrument(**attrs)
        if attrs.get("test_requirement_type") and attrs["test_requirement_type"] != "all-pass":
            self.log_info(
                f"Creating instrument for {attrs['measure']!r} with condition.test "
                f"type of {attrs['test_requirement_type']!r}"
            )

        originating_suggested_responses = list(instrument.suggested_responses.all())

        # Set up suggested responses and our extended attributes
        suggested_responses = self.get_suggested_responses(self.role, measure_id)
        flags = self.get_suggested_response_flags(self.role, measure_id)

        if flags:
            self.log_info(f"Using {self.role} flags for {measure_id}: {flags}")
        for data in suggested_responses:
            axis_attrs = flags.get(data, {})
            suggested_response = utils.safe_ops.derive_suggested_response(data)
            utils.safe_ops.derive_bound_suggested_response(
                collection_instrument=instrument,
                suggested_response=suggested_response,
                **axis_attrs,
            )
            if suggested_response in originating_suggested_responses:
                index = originating_suggested_responses.index(suggested_response)
                originating_suggested_responses.pop(index)

        for suggested_response in originating_suggested_responses:
            suggested_response_set = suggested_response.axisboundsuggestedresponse_set
            response_policies = suggested_response_set.filter(collection_instrument=instrument)
            response_policy = response_policies.get()
            self.log_warning(f"Removing unused response policy {response_policy}")
            response_policy.delete()

        return instrument

    def build_type(self, measure):
        type_id = self.get_type(self.role, measure)
        return utils.safe_ops.derive_type(type_id)

    def build_response_policy(self, measure_id):
        # Axis cannot yet leverage 'restrict=False' if there are choices, so for now it's the same
        restrict = bool(self.get_suggested_responses(self.role, measure_id))
        multiple = self.get_is_multiple(self.role, measure_id)
        attrs = {
            "nickname": None,
            "required": measure_id not in self.optional_measures,
            "restrict": restrict,
            "multiple": multiple,
        }

        self.log_debug(f"Setting response policy for {measure_id}: {attrs}")
        return utils.safe_ops.derive_response_policy(**attrs)

    def build_conditions(self, groups):
        for resolver_type in ["instrument", "simulation", "rem"]:  # TODO REMOVE REM
            for group, instruments in groups.items():
                for instrument in instruments:
                    conditions = self.get_conditions(
                        self.role, resolver_type, instrument.measure_id
                    )
                    if conditions:
                        self.log_debug(f"Building {len(conditions)} conditions for {instrument}")
                    for trigger_spec, value_specs in conditions.items():
                        for value_spec in value_specs:
                            self.build_condition(
                                resolver_type, trigger_spec, value_spec, instrument
                            )

    def build_condition(self, resolver_type, resolve_spec, answer, enabled_instrument):
        answer_shorthand = ["*", "!"]  # simple operators that might be used instead of a value
        match_type_shorthand = {
            "*": "any",
            "!": "none",
            "=": "match",
            "!=": "mismatch",
            ">": "greater_than",
            "<": "less_than",
        }
        match_type_symbols = {v: k for k, v in match_type_shorthand.items()}

        data_getter = f"{resolver_type}:{resolve_spec}"

        match_type = "match"
        if answer in answer_shorthand:
            match_type = match_type_shorthand[answer]
            answer = ""
        elif isinstance(answer, tuple):
            match_type, answer = answer

        if isinstance(answer, enum.Enum):
            answer = answer.value

        match_type = match_type_shorthand.get(match_type, match_type)

        # Get ConditionGroup
        source = resolve_spec.split(".")[-1]
        operator = match_type_symbols.get(match_type, f" {match_type} ")
        nickname = f"{resolver_type}({source}{operator}{answer})"[:100]
        group_attrs = {
            "nickname": nickname,
            "requirement_type": "all-pass",
        }
        condition_group = utils.safe_ops.derive_condition_group(**group_attrs)

        initial_cases = condition_group.cases.count()
        initial_groups = condition_group.child_groups.count()

        # Get Case
        case_attrs = {
            "match_type": match_type,
            "match_data": answer,
        }
        case = utils.safe_ops.derive_case(**case_attrs)

        from django_input_collection.models import Case

        if Case.objects.filter(match_data__iexact=answer, match_type=match_type).count() > 1:
            raise AttributeError(f"Case bug! - {enabled_instrument} - {answer!r}")
            # Note if you find yourself here look in the match data for something case
            # insensitive identical match..

        through_model = condition_group.cases.through._meta.model
        through_obj, create = through_model.objects.get_or_create(
            case=case, conditiongroup=condition_group
        )

        # Get Condition
        condition = utils.safe_ops.derive_condition(
            instrument=enabled_instrument, condition_group=condition_group, data_getter=data_getter
        )

        self.log_info(
            f"Built conditional ({condition.id}) for measure {enabled_instrument.measure_id!r} to "
            f"Instrument {enabled_instrument.text!r} ({enabled_instrument.id}) using condition "
            f"group {condition_group} ({condition_group.id})"
        )

        from django_input_collection.models import ConditionGroup

        final_cg = ConditionGroup.objects.get(pk=condition_group.pk)
        final_cases = final_cg.cases.count()
        final_groups = final_cg.child_groups.count()

        if initial_cases and initial_cases != final_cases:
            self.log_error(
                f"Cases changed {initial_cases} → {final_cases} on instrument {enabled_instrument}"
            )
        elif initial_cases and initial_cases == final_cases:
            self.log_debug(f"Retaining {initial_cases} Cases on instrument {enabled_instrument}")

        if initial_groups and initial_groups != final_groups:
            self.log_error(
                f"Child groups changed {initial_groups} → {final_groups} on instrument {enabled_instrument}"
            )
        elif initial_groups and initial_groups == final_groups:
            self.log_debug(
                f"Retaining {initial_cases} child groups on instrument {enabled_instrument}"
            )


class ProgramCloner(ProgramBuilder):
    slug = None
    base_program = None
    qa_base_program = None
    convert_to_collection = True
    instrument_types_from_question_types = {
        "int": "integer",
        "integer": "integer",
        "float": "float",
        "csv": "csv",
        # 'kvfloatcsv': ,
    }
    rules = []
    exclude_measures = []

    @deprecated("This is no longer to be used.  Please use ProgramBuilder")
    def __new__(self):
        pass

    def get_base_program(self):
        from axis.eep_program.models import EEPProgram

        return EEPProgram.objects.get(slug=self.slug)

    def get_existing_program(self):
        from axis.eep_program.models import EEPProgram

        return EEPProgram.objects.filter(slug=self.slug).first()

    def get_type(self, role, measure_id):
        queryset = Question.objects.filter(slug=measure_id)
        question_type = queryset.values_list("type", flat=True).first()
        legacy_type = self.instrument_types_from_question_types.get(question_type, question_type)
        if legacy_type:
            return legacy_type
        return super(ProgramCloner, self).get_type(role, measure_id)

    def build(self, *roles, **kwargs):
        programs = []
        if not roles:
            roles = list(self.measures.keys())
        for role in roles:
            self.setup(role=role)
            self.setup(attrs=self.unpack_settings())

            # # FIXME: Fix role_settings to make this work correctly on sequential runs
            # if role == 'qa':
            #     self.slug = self.qa_slug
            #     self.name = self.qa_name

            original = self.get_base_program()
            existing = self.get_existing_program()

            cloned = utils.clone_program(
                original,
                self.rules,
                **{
                    "exclude_measures": self.exclude_measures,
                    "convert_to_collection": bool(existing.collection_request is None),
                },
            )

            # Copy processed attributes to self so super() can find it as the target program
            self.owner = cloned.owner.slug
            for k, info in self.program_settings.items():
                if k == info:
                    value = getattr(cloned, k) or getattr(original, k)
                    if hasattr(self, k) and getattr(self, k) and getattr(self, k) != value:
                        self.log_info(f"Updating {k} : {value!r} > {getattr(self, k)}")
                    else:
                        setattr(self, k, value)

            self.cleanup(cloned, cloned.collection_request)
            program = super(ProgramCloner, self).build(role, **kwargs)
            programs.append(program)

        return programs
