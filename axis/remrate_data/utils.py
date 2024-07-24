"""utils.py: Django remrate_data"""


import logging
import re
from collections import namedtuple

from django.core.exceptions import ObjectDoesNotExist

try:
    from django.apps import apps

    get_models = apps.get_models
except:
    from django.db.models import get_models

__author__ = "Steven Klass"
__date__ = "3/8/13 9:48 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def _convert_cfm_50_to_ach50(cfm_value, volume):
    """Convert from CFM50 to ACH50"""
    return (float(cfm_value) * 60.0) / float(volume)


def _convert_cfm_25_to_ach50(cfm_value, volume):
    """Convert from CFM50 to ACH50"""
    # 1.6 is had from http://www.cedaorg.net/www2/Assets/RFPs/RFP_02162010_Attachments.pdf
    return _convert_cfm_50_to_ach50(float(cfm_value) * 1.6, volume)


def get_ACH50_string_value(value, unit_label, volume):
    from axis.remrate_data.strings import INFILTRATION_UNITS

    ach50_label = next((x[1] for x in INFILTRATION_UNITS if x[0] == 3))
    StrVal = namedtuple("ACH50Value", "as_string, value, unit")
    if unit_label == 3:
        label = ach50_label
    elif unit_label == 1:
        value = _convert_cfm_50_to_ach50(value, volume)
        label = ach50_label
    elif unit_label == 2:
        value = _convert_cfm_25_to_ach50(value, volume)
        label = ach50_label
    else:
        label = next((x[1] for x in INFILTRATION_UNITS if x[0] == unit_label), unit_label)

    as_string = "-"
    if value and label:
        as_string = "{value:.2f} {label}".format(value=value, label=label)

    return StrVal(as_string, value, label)


def find_value(simulation, regex):
    """This will find a search for a value all the models"""
    models = [m for m in get_models() if m._meta.app_label == "remrate_data"]
    for model_obj in models:
        kwargs = dict()
        field_names = [x.name for x in model_obj._meta.fields]
        if "simulation" in field_names:
            kwargs.update({"simulation": simulation})
        if "building" in field_names:
            kwargs.update({"building": simulation.building})
        if not len(kwargs.keys()):
            log.info("Skipping %s", model_obj._meta.verbose_name)
            continue
        model_sets = model_obj.objects.filter(**kwargs)
        for model in model_sets:
            for field in model._meta.fields:
                try:
                    value = str(getattr(model, "get_{}_display".format(field.name))())
                except AttributeError:
                    value = str(getattr(model, field.name))
                accepted = [
                    "DateField",
                    "FloatField",
                    "IntegerField",
                    "BooleanField",
                    "CharField",
                    "TextField",
                ]
                if value and field.__class__.__name__ in accepted:
                    if re.search(regex, value) or re.search(regex, field.name):
                        print(
                            "{:<20} {:<20} {}".format(model_obj._meta.model_name, field.name, value)
                        )


EXCLUDE_FIELDS = ["building", "simulation", "last_update", "created_on"]


class RemRateDataSet(object):
    def __init__(self, simulation_id, **kwargs):
        from axis.remrate_data.models import Simulation, Building

        self._simulation_id = simulation_id

        self._simulation = Simulation.objects.get(id=self._simulation_id)
        self._building = Building.objects.get(simulation=self._simulation)
        self.ignore_fields = kwargs.pop("ignore_fields", [])

        self.tree = {}
        self._build_structure()

    def _get_fields(self, model, exclude_fields=EXCLUDE_FIELDS, exclude_regex="_.*"):
        """Just pulls the fields we care about out"""
        fields = []
        if exclude_fields:
            assert isinstance(exclude_fields, (list, tuple)), "Excluded fields must be a list"

        if self.ignore_fields:
            exclude_fields += self.ignore_fields

        for field in model._meta.fields:
            if field.get_internal_type() == "AutoField":
                continue
            if re.match(exclude_regex, field.name):
                continue
            if field.name in exclude_fields:
                continue
            fields.append(field)
        return fields

    def _get_item_dict_for_compare(self, field_dict, model):
        """We need to tweak the FK's for existance only not the values.."""
        _models = [m for m in get_models() if m._meta.app_label == "remrate_data"]
        model_obj = next((x for x in _models if x._meta.object_name == model))
        fields = self._get_fields(model_obj)

        cmp_dict = dict()
        for key, value in field_dict.items():
            field = next((f for f in fields if f.name == key))
            if field.get_internal_type() in ["ForeignKey", "OneToOneField"]:
                value = 1 if value else None
            cmp_dict[key] = value
        return cmp_dict

    def _get_likely_choice(self, target, choices):
        """Identify the most likely candidate for comparison"""
        if target in choices:
            return target

        likely_match = None
        for choice in choices:
            found = 0
            for k, v in target.items():
                if choice[k] == v:
                    found += 1
            if likely_match is None or found > likely_match[1]:
                likely_match = choice, found
        if likely_match:
            return likely_match[0]
        log.warning("Unable to find %s in %s", choices)

    def get_delta(self, other):
        """Diff two of these things"""
        DiffItem = namedtuple("ErrItem", ["model", "field", "value", "value2", "message"])
        delta = []
        if set(self.tree.keys()) != set(other.tree.keys()):
            missing_right = list(set(self.tree.keys()) - set(other.tree.keys()))
            if missing_right:
                msg = "Models missing in other".format(", ".join(missing_right))
                delta.append(DiffItem(None, None, None, None, msg))
                log.warning(msg)
            missing_left = list(set(self.tree.keys()) - set(other.tree.keys()))
            if missing_right:
                msg = "Additional models in other".format(", ".join(missing_left))
                delta.append(DiffItem(None, None, None, None, msg))
                log.warning(msg)

        _model_counts, _field_counts = 0, 0
        for model, values in self.tree.items():
            log.debug("Reviewing %s", model)
            if len(values) != len(other.tree[model]):
                msg = "Expecting {} {} sets other has {}".format(
                    len(values), model, len(other.tree[model])
                )
                delta.append(DiffItem(model, None, None, None, msg))
                log.warning(msg)
                continue
            # This builds up a basic set of data ignoring the values of FK and Auto
            val_set = [self._get_item_dict_for_compare(i, model) for i in values]
            other_val_set = [self._get_item_dict_for_compare(i, model) for i in other.tree[model]]

            for val in val_set:
                _model_counts += 1
                other_set = self._get_likely_choice(val, other_val_set)
                other_val_set.pop(other_val_set.index(other_set))
                for field, value in val.items():
                    _field_counts += 1
                    if other_set[field] != value:
                        msg = "{}.{} - {} != {}".format(model, field, value, other_set[field])
                        delta.append(DiffItem(model, field, value, other_set[field], msg))
                        log.warning(msg)
        log.info(
            "Reviewed %s models and %s model objects %s (%s fields) deltas found",
            len(self.tree.keys()),
            _model_counts,
            len(delta),
            _field_counts,
        )
        return delta

    def __eq__(self, other):
        if len(self.get_delta(other)):
            return False
        return True

    def _build_structure(self):
        """Builds a structure to hold all of this data"""
        models = [m for m in get_models() if m._meta.app_label == "remrate_data"]
        for model in models:
            fields = self._get_fields(model)
            if "simulation" in [f.name for f in model._meta.get_fields()]:
                models = model.objects.filter(simulation=self._simulation)
            elif "building" in [f.name for f in model._meta.get_fields()]:
                models = model.objects.filter(building=self._building)
            if models.count():
                results = []
                for item in models.values(*[f.name for f in fields]):
                    results.append(item)
                self.tree[model._meta.object_name] = results

    def find_value(self, regex):
        """Finds a value"""
        for model_name in self.tree:
            model = next(
                (
                    m
                    for m in get_models()
                    if m._meta.app_label == "remrate_data" and m._meta.object_name == model_name
                )
            )
            for data in self.tree[model_name]:
                for key, value in data.items():
                    field = next((f for f in model._meta.fields if f.name == key))
                    if value is None or field.get_internal_type() in [
                        "ForeignKey",
                        "OneToOneField",
                    ]:
                        continue
                    if re.search(r"%s" % regex, str(value)):
                        print("{:<20} {:<20} {}".format(model_name, key, value))

    def pprint(self):
        """Prints a value"""
        for model, values in self.tree.items():
            print("Model: {} ({}) total".format(model, len(values)))
            for item in values:
                print("  - - -")
                for key, value in item.items():
                    print("   {:<20} {:<20}".format(key, value))
            print("")


def remrate_compare(source_id=None, source2_id=None):
    if source_id is None and source2_id is None:
        from axis.remrate_data.models import Simulation

        sims = list(Simulation.objects.all().order_by("-id"))
        source_id, source2_id = sims[0].id, sims[1].id

    source = RemRateDataSet(simulation_id=source_id)
    source2 = RemRateDataSet(simulation_id=source2_id)
    print(
        "Comparing ({}/{}) {}/{}".format(
            source_id, source2_id, source._simulation, source2._simulation
        )
    )
    delta = source.get_delta(source2)
    for item in delta:
        print(
            "{:<20} {:<20} {:<20} {:<20} -- {}".format(
                str(item.model) if item.model else "",
                str(item.field) if item.field else "",
                str(item.value) if item.value else "",
                str(item.value2) if item.value2 else "",
                str(item.message) if item.message else "",
            )
        )
    if not len(delta):
        print("Identical")


def compare_values(remdata, compare_to, type=str):
    if type == str:
        remdata = remdata.strip().lower() if remdata and len(remdata.strip()) else None
        compare_to = compare_to.strip().lower() if compare_to and len(compare_to.strip()) else None
    elif type == int:
        remdata = int(round(float(remdata), 0)) if remdata else None
        compare_to = int(round(float(compare_to), 0)) if compare_to else None
    elif type == float:
        remdata = round(float(remdata), 1) if remdata else None
        compare_to = round(float(compare_to), 1) if compare_to else None

    return remdata == compare_to


def compare_sets(elements):
    issues = {"success": [], "warning": [], "error": []}
    for element in elements:
        try:
            cmp1, cmp2, _type, label, error_type = element
        except ValueError:
            cmp1, cmp2, _type, label = element
            error_type = "warning"
        if cmp2 is None:  # If we don't have a checklist answer move along.
            continue
        success = compare_values(cmp1, cmp2, _type)
        if success:
            issues["success"].append(label)
        else:
            issues[error_type].append(label)
    return issues


def find_bad_references(max_count=None, verbose=False, simulation_ids=None, auto_correct=False):
    from .models import Simulation

    mis_certified = []
    correctable = []

    sims = Simulation.objects.filter(references__isnull=False)
    if simulation_ids:
        sims = sims.filter(id__in=simulation_ids)

    for idx, rem in enumerate(sims.distinct()):
        if max_count and idx > max_count:
            break
        if rem.references.all().count() == 1:
            continue
        true_references = []
        for ref in rem.references.all():
            if ref.building.filename == rem.building.filename:
                true_references.append(ref)
        if verbose:
            print(
                "Simulation {} has {} references but only {} are real".format(
                    rem, rem.references.all().count(), len(true_references)
                )
            )
        if set([x.id for x in true_references]) != set([x.id for x in ref.references.all()]):
            can_be_corrected = False
            try:
                if rem.floorplan.homestatuses.filter(
                    certification_date__isnull=False, eep_program__owner__slug="eto"
                ).count():
                    # This is taken directly from the eps calculator #L1057
                    if (
                        len(true_references) == 1
                        and rem.references.all().order_by("-id")[0] == true_references[0]
                    ):
                        can_be_corrected = True
                        correctable.append(rem)
                    else:
                        mis_certified.append(rem)
                else:
                    can_be_corrected = True
                    correctable.append(rem)
            except ObjectDoesNotExist:
                correctable.append(rem)
                can_be_corrected = True
            if verbose:
                print("Assigned:")
                for i in rem.references.all():
                    print("  - {}".format(i))
                print("Actual:")
                for i in true_references:
                    print("  - {}".format(i))
            if auto_correct and can_be_corrected:
                rem.references.clear()
                for _ref in true_references:
                    rem.references.add(_ref)

    print(
        "Total of {} simulations reviewed.  {} can be corrected without issue. "
        "{} are potential certification issues".format(
            idx + 1, len(correctable), len(mis_certified)
        )
    )

    return (correctable, mis_certified)


def find_in_process_bad_refs(tolerance=0.01):
    from axis.home.models import EEPProgramHomeStatus
    from axis.customer_eto.calculator.eps.calculator import EPSCalculator
    from axis.customer_eto.calculator.eps import get_eto_calculation_completed_form

    stats = EEPProgramHomeStatus.objects.filter(
        eep_program__owner__slug="eto", floorplan__remrate_target__isnull=False
    ).distinct()

    inprogress = stats.filter(certification_date__isnull=True).distinct()

    print("{} Total homes for ETO with REM/Rate datasets".format(stats.count()))

    big_issue = []
    incorrect, incorrect_certified = [], []

    file = open("ETO Report.csv", "w")
    keys, header_done = None, False
    for stat in stats:
        remrate = stat.floorplan.remrate_target
        reference = remrate.references.all().order_by("-id")[0]
        if remrate.building.filename != reference.building.filename:
            true_reference = remrate.references.filter(building__filename=remrate.building.filename)
            if not true_reference.count():
                big_issue.append(stat)
                continue
            true_reference = true_reference.order_by("-id")[0]
            calculations_form = get_eto_calculation_completed_form(stat)
            if not calculations_form.is_valid():
                big_issue.append(stat)
                continue

            data = calculations_form.cleaned_data
            assert int(data.get("simulation").id) == int(remrate.id), "Hmmm"

            actual_eps = EPSCalculator(**data)
            updated_eps = EPSCalculator(reference=true_reference, **data)

            keys = actual_eps.final_result().keys() if keys is None else keys

            is_equal = True
            updated_results = updated_eps.final_result()
            for k, v in actual_eps.final_result().items():
                if abs(v - updated_results[k]) == 0:
                    continue
                try:
                    delta = abs(abs(v - updated_results[k]) / float(v))
                    if delta > tolerance:
                        is_equal = False
                        break
                except ZeroDivisionError:
                    pass

            if not is_equal:
                if stat.certification_date:
                    incorrect_certified.append(stat)
                    ctype = "Certified"
                else:
                    incorrect.append(stat)
                    ctype = "-"

                if not header_done:
                    attrs = [
                        "Home ID",
                        "Address",
                        "City",
                        "State",
                        "Zip",
                        "Certified",
                        "Company",
                        "Simulation ID",
                        "Reference ID",
                        "True Reference ID",
                    ]
                    attrs += keys + ["True {}".format(x) for x in keys]
                    file.write(",".join(attrs) + "\n")
                    header_done = True

                vals = [
                    str(stat.home.id),
                    stat.home.street_line1,
                    stat.home.city.name,
                    stat.home.state,
                    stat.home.zipcode,
                    ctype,
                    re.sub(r",", "", stat.company.name),
                    str(remrate.id),
                    str(reference.id),
                    str(true_reference.id),
                ]
                actual_results = actual_eps.final_result()
                for k in keys:
                    vals.append(str(actual_results[k]))

                updated_results = updated_eps.final_result()
                for k in keys:
                    vals.append(str(updated_results[k]))

                file.write(",".join(vals) + "\n")
    file.close()

    print("{} Total homes for ETO with REM/Rate datasets".format(stats.count()))
    print("{} homes are in progress for ETO with REM/Rate datasets".format(inprogress.count()))
    print("{} certified homes would have the EPS Score affected.".format(len(incorrect_certified)))
    print("{} active homes would have the EPS Score affected.".format(len(incorrect)))
    print("{} other issues".format(len(big_issue)))


if __name__ == "__main__":
    # remrate_testing(5745)
    find_in_process_bad_refs()
