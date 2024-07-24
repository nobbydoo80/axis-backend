"""Global Collector utilities"""
import enum
from collections import OrderedDict
import logging

from django.core.exceptions import ValidationError

from django_input_collection.collection import Collector
from django_input_collection.api.restframework.collection import RestFrameworkCollector
from django_input_collection.models import get_input_model, CollectionRequest

from . import methods as axis_methods

__author__ = "Autumn Valenta"
__date__ = "2018-10-08 1:49 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


CollectedInput = get_input_model()  # pylint: disable=invalid-name


def get_breakdown(queryset, field):
    """
    Returns a dict of unique ``field`` values in this queryset, mapped to the sub-queryset
    with that value.

    Example: get_breakdown('group_id') => {'Section A': [...], 'Section B': [...]}
    Example: get_breakdown('user_role') => {'rater': [...], 'qa': [...]}
    Example: get_breakdown('instrument') => {1: [...], 2: [...]}
    """
    values = queryset.values_list(field, flat=True)
    return OrderedDict(((value, queryset.filter(**{field: value})) for value in values))


def get_user_role_for_program(eep_program, user):
    is_qa_program = eep_program.is_qa_program
    qa_program = eep_program.get_qa_program()

    if qa_program and qa_program.user_can_certify(user):
        if is_qa_program:
            return "qa"
        return None

    return "rater"


def get_user_role_for_homestatus(home_status, user):
    # Gather hints
    rater_program = home_status.eep_program.get_rater_program()
    if home_status.eep_program == rater_program:
        rater_home_status = home_status
        qa_home_status = None
    else:
        qa_home_status = home_status
        rater_home_status = home_status.home.homestatuses.filter(eep_program=rater_program).first()

    if rater_home_status and user.company_id == rater_home_status.company_id:
        return "rater"

    # Try to find other matches
    qa_program = home_status.eep_program.get_qa_program()
    if qa_program and qa_home_status:
        if user.company_id == qa_home_status.company_id:
            return "qa"
        return None

    return None


class AxisCollectorMixin(object):
    """Global collector method implementations for the Axis CollectedInput model."""

    __version__ = (1, 0, 0)

    method_mixins = {
        # BaseCascadingSelectMethod: {'prefix': 'Some', 'mixin': SomeMixin},
    }
    type_methods = {
        # NOTE: GET SPECIFIC WHEN VALIDATIONS ARE IMPORTANT, E.G., 'r-value'
        "open": axis_methods.CharMethod,
        "integer": axis_methods.IntegerMethod,
        "float": axis_methods.DecimalMethod,
        "date": axis_methods.DateMethod,
    }
    measure_methods = {
        "equipment-furnace": axis_methods.trc_eps.CascadingFurnacePickerMethod,
        "equipment-furnace-2": axis_methods.trc_eps.CascadingFurnacePickerMethod,
        "equipment-heat-pump": axis_methods.trc_eps.CascadingHeatPumpPickerMethod,
        "equipment-heat-pump-2": axis_methods.trc_eps.CascadingHeatPumpPickerMethod,
        "equipment-water-heater": axis_methods.trc_eps.CascadingWaterHeaterPickerMethod,
        "equipment-refrigerator": axis_methods.trc_eps.CascadingRefrigeratorPickerMethod,
        "equipment-dishwasher": axis_methods.trc_eps.CascadingDishwasherPickerMethod,
        "equipment-clothes-washer": axis_methods.trc_eps.CascadingClothesWasherPickerMethod,
        "equipment-clothes-dryer": axis_methods.trc_eps.CascadingClothesDryerPickerMethod,
        "equipment-ventilation-balanced": axis_methods.trc_eps.CascadingBalancedVentilationPickerMethod,
        "equipment-ventilation-exhaust": axis_methods.trc_eps.CascadingExhaustVentilationPickerMethod,
        "equipment-ventilation-hrv-erv": axis_methods.trc_eps.CascadingBalancedVentilationPickerMethod,
    }

    def __init__(self, *args, **kwargs):
        """Generate broader context so that users can see across users and companies."""
        super(AxisCollectorMixin, self).__init__(*args, **kwargs)

        self.user = self.context.get("user")
        if self.is_bound and self.user and not self.user.is_superuser:
            self.expand_context()

    # Internal helpers
    def get_user_role(self, user):
        if self.is_bound:
            return get_user_role_for_homestatus(self.home_status, user)
        return get_user_role_for_program(self.eep_program, user)

    def expand_context(self):
        """Replaces the 'user' context entry with a 'company_id__in' list."""

        home_status = self.collection_request.eepprogramhomestatus

        if self.user:
            company = self.user.company
        elif home_status:
            company = home_status.company
        else:
            raise ValueError(
                "Can't determine a company reference for collection_request %d and context %r"
                % (
                    self.collection_request.id,
                    self.context,
                )
            )

        company_ids = (
            home_status.home.relationships.get_orgs()
            .filter_by_company(company)
            .values_list("id", flat=True)
        )

        del self.context["user"]
        self.context["user__company_id__in"] = [company.id] + list(company_ids)

    @property
    def is_bound(self):
        return bool(getattr(self.collection_request, "eepprogramhomestatus", None))

    @property
    def home_status(self):
        if self.is_bound:
            return self.collection_request.eepprogramhomestatus
        return None

    @property
    def eep_program(self):
        if self.is_bound:
            return self.collection_request.eepprogramhomestatus.eep_program
        return self.collection_request.eepprogram

    def _compose_methods(self, methods):
        methods = methods.copy()
        for k, method in list(methods.items()):
            for base, info in self.method_mixins.items():
                if base in method.__mro__:
                    methods[k] = self._compose_method(method, **info)
        return methods

    def _compose_method(self, method, mixin, prefix=None):
        name = method.__name__
        if prefix is not None:
            name = str(prefix) + name
        return type(name, (mixin, method), {})

    # Overrides & supporting internals
    @property
    def specification(self):
        specification = super(AxisCollectorMixin, self).specification

        home_status = None
        segment_role = "rater"

        if self.is_bound:
            home_status = self.collection_request.eepprogramhomestatus
            eep_program = home_status.eep_program
            specification["name"] = eep_program.name
            specification["eep_program_id"] = eep_program.id

        if eep_program.is_qa_program:
            segment_role = "qa"

        # Prescribe a user_role value for this context
        user_role = self.get_user_role(self.user)
        specification["user_role"] = user_role
        specification["read_only"] = any(
            (
                (segment_role != user_role),
                (home_status.state == "complete"),
            )
        )

        return specification

    def get_breakdown(self, queryset, field_name):
        return get_breakdown(queryset, field_name)

    def get_type_methods(self):
        methods = super(AxisCollectorMixin, self).get_type_methods()
        return self._compose_methods(methods)

    def get_measure_methods(self):
        methods = super(AxisCollectorMixin, self).get_measure_methods()
        return self._compose_methods(methods)

    def extract_data_input(self, data):
        """Returns data['input'] as our primitive data instead of the whole data structure."""
        return data["input"]

    def is_input_allowed(self, instrument, user=None):
        if user is None:
            user = self.user  # Patch in the original user so that context['user'] isn't used
        return super(AxisCollectorMixin, self).is_input_allowed(instrument, user=user)

    def make_payload(self, instrument, data, extra={}, **kwargs):
        if isinstance(data, dict) and "input" in data:
            # FIXME: This should not be happening, but xls uploads make their own payloads before
            # store(), which ends up sending a full payload as 'data'
            payload = data.copy()
            data = payload.pop("input")
            extra = dict(extra, **payload)
        data = self.make_payload_data(instrument, data, **extra)

        payload = {
            "instrument": instrument,
            "data": data,
            # Disallow data integrity funnybusiness
            "collection_request": instrument.collection_request,
            # WARNING: self.user is set from original context during init and could be stale if
            # some funnybusiness has gone on around the collection_request or context values.
            "user": self.context.get("user", self.user),
            # NOTE: Copied from djinco base collector.  We're having trouble calling super().
            # Disallow data integrity funnybusiness
            "collector_class": ".".join(
                filter(
                    bool,
                    (
                        self.__class__.__module__,
                        self.__class__.__name__,
                    ),
                )
            ),
            "collector_id": self.get_identifier(),
            "collector_version": ".".join(["{}".format(x) for x in self.__version__]),
            "version": ".".join(["{}".format(x) for x in Collector.__version__]),
        }
        payload.update(kwargs)

        return payload

    def make_payload_data(self, instrument, data, hints=None, comment=None, **kwargs):
        is_blank = data is None

        if isinstance(data, enum.Enum):
            data = data.value

        data = {
            "input": data,
        }
        if hints is None:
            hints = self.get_data_hints(instrument, data, **kwargs)

        if hints:
            data["hints"] = hints
        if comment:
            data["comment"] = comment

        if not is_blank and not self.is_instrument_allowed(instrument):
            if not hints:
                data["hints"] = {}
            data["hints"]["SPECULATIVE"] = True

        return data

    def get_data_hints(self, instrument, data, SPECULATIVE=False, **kwargs):
        hints = {}

        # Avoid having this treated as a model field value by traping it and inserting to data
        if SPECULATIVE:
            hints["SPECULATIVE"] = True

        return hints

    def clean_payload(self, payload, **kwargs):
        # Trigger forced entry when flag is present
        if (payload["data"].get("hints") or {}).get("SPECULATIVE"):
            kwargs["skip_availability"] = True

        bound_responses = self.get_suggested_responses(
            **{
                "instrument": payload.get("instrument"),
                "measure": payload.get("measure"),
            }
        )
        bound_lookups = {response.data: response for response in bound_responses}
        if isinstance(payload["data"]["input"], dict):  # Prevent unhashable lookup error
            suggested_response = None
        else:
            suggested_response = bound_lookups.get(payload["data"]["input"])
            if suggested_response:
                payload["data"]["input"] = suggested_response.data

        expected_documents = payload.pop("expected_documents", [])
        if suggested_response:
            if suggested_response.comment_required and not payload["data"].get("comment"):
                raise ValidationError("Comment Required")
            requires_document = (
                suggested_response.document_required or suggested_response.photo_required
            )
            if requires_document and not expected_documents:
                raise ValidationError("Upload Required")

        return super(AxisCollectorMixin, self).clean_payload(payload, **kwargs)

    def clean_input(self, instrument, data):
        """Clean only the 'input' part of data, since data contains extra response payload."""

        # Clean inner 'input' component of wrapper object
        input = data["input"]
        input = super(AxisCollectorMixin, self).clean_input(instrument, input)

        # Support 2-arg return for updating the wrapper object
        if isinstance(input, tuple):
            input, extra = input
            for k, info in extra.items():
                if (k not in data) or (data[k] is None):
                    data[k] = info.copy()
                else:
                    data[k].update(info)

        data["input"] = input

        return data

    def store(self, instrument, data, **kwargs):
        """Inject extra model field values before save."""
        user_role = self.get_user_role(kwargs["user"])

        home_status = self.home_status
        kwargs.update(
            {
                "home": home_status.home,
                "home_status": home_status,
                "user_role": user_role,
            }
        )
        # Don't store multiple answers.
        if "instance" not in kwargs and instrument.response_policy.multiple is False:
            kwargs["instance"] = (
                CollectedInput.objects.filter(
                    home_status=home_status,
                    home=home_status.home,
                    collection_request=home_status.collection_request,
                    instrument=instrument,
                )
                .order_by("id")
                .last()
            )

        return super(AxisCollectorMixin, self).store(instrument, data, **kwargs)

    def remove_child_instruments(self, instrument, **context):
        """Recursively remove collected input"""
        for child_instruments in instrument.get_child_instruments():
            self.remove_child_instruments(child_instruments)
        collected_input = CollectedInput.objects.filter_for_context(**context).filter(
            instrument_id=instrument.pk
        )
        collected_input.delete()

    def remove(self, instrument, instance):
        """Removes all inputs matching this context for child instruments to ``instrument``."""
        for child_instrument in instrument.get_child_instruments():
            self.remove_child_instruments(child_instrument, **self.context)
        super(AxisCollectorMixin, self).remove(instrument, instance)

    def raise_error(self, exception):
        raise ValidationError(
            {
                "data": exception,
            }
        )

    def get_inputs(self, instrument=None, measure=None, cooperative_requests=None):
        """Measure-based query for inputs, accepting fallback inputs from CollectionRequests
        in `cooperative_requests`.  If `cooperative_requests` is True,
        """
        if instrument or measure:
            if instrument and measure:
                raise ValueError("Can't specify both 'instrument' and 'measure'")

        # Tidy as lists
        instruments = instrument
        if instrument and not isinstance(instruments, (list, tuple)):
            instruments = [instrument]
        measures = measure
        if measure and not isinstance(measures, (list, tuple)):
            measures = [measure]

        # Convert to instrument references
        if instrument:
            measures = [instrument.measure_id for instrument in instruments]

        if cooperative_requests:
            if self.is_bound and cooperative_requests is True:
                cooperative_requests = CollectionRequest.objects.filter(
                    id__in=self.home_status.home.homestatuses.filter(
                        company=self.home_status.company
                    ).values("collection_request_id")
                )
            elif cooperative_requests:
                cooperative_requests = [
                    (obj.collection_request if hasattr(obj, "collection_request") else obj)
                    for obj in cooperative_requests
                ]
            queryset = CollectedInput.objects.filter(collection_request__in=cooperative_requests)
        else:
            queryset = self.collection_request.collectedinput_set.all()

        # Enforce filtering when filtering was requested.  An empty instruments list might not mean
        # that no filter was requested at all.
        if not measures and not (instrument or measure):
            return queryset

        return queryset.filter_for_context(instrument__measure_id__in=measures, **self.context)


class APICollectorMixin(RestFrameworkCollector):
    pagination_classes = {
        "instrument": None,  # Disable pagination, show everything
    }


class ChecklistCollector(AxisCollectorMixin, Collector):
    segment = "checklist"


# class AnnotationsCollector(AxisCollectorMixin, Collector):
#     segment = 'annotations'
