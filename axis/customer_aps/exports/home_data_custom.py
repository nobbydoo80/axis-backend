"""APS Custom Home Export"""
import inspect
import logging
import pprint
from collections import OrderedDict

from django.db.models import Sum

from axis.customer_aps.models import APSSmartThermostatOption
from axis.eep_program.models import EEPProgram
from axis.home.export_data import HomeDataXLSExport, CellObject
from axis.subdivision.models import FloorplanApproval
from axis.subdivision.models import Subdivision

__author__ = "Rajesh Pethe"
__date__ = "08/31/2020 16:43:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]

from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class APSHomeDataCustomExport(HomeDataXLSExport):
    """Custom Export"""

    def __init__(self, *args, **kwargs):
        kwargs["title"] = kwargs["subject"] = "APS Utility Export"
        kwargs["specified_columns"] = self.get_specified_columns()
        kwargs["retain_empty"] = True
        kwargs["report_on"] = [
            "subdivision",
            # 'eep_program',
            # 'community',
            # 'floorplan',
            # 'builderagreement',
        ]
        # kwargs['max_num'] = 50
        super(APSHomeDataCustomExport, self).__init__(*args, **kwargs)
        self.include_home_status_data = False
        self.include_builder_agreement_data = False

    def get_specified_columns(self):
        """Return specified Columns"""
        return [
            "home__subdivision__id",
            "home__subdivision__name",
            "home__subdivision__eep_program_name",
            # 'eep_program__name',
            "home__subdivision__builder_accounting_code",
            "home__subdivision__builder_org__id",
            "home__subdivision__builder_org__name",
            "home__subdivision__cross_roads",
            "home__subdivision__aps_thermostat_option__eligibility",
            "home__subdivision__aps_thermostat_option__models",
            "home__subdivision__city__name",
            "home__subdivision__community__id",
            "home__subdivision__community__name",
            "home__subdivision__community__cross_roads",
            "home__subdivision__all_electric",
            "home__subdivision__provider__id",
            "home__subdivision__provider__name",
            "subdivision__thermostat_qty",
            "floorplan__id",
            "floorplan__name",
            "floorplan__number",
            "floorplan__square_footage",
            "floorplan__is_custom_home",
            "floorplan__is_active",
            "floorplan__created_date",
            "floorplan__remrate_target__hers__score",
            # 'builderagreement__provider',
            # 'builderagreement__thermostat_qty',
            # 'builderagreement__all_electric',
            "builderagreement__start_date",
            "builderagreement__lots_paid",
            "builderagreement__total_lots",
            # 'builderagreement__eep_program',
            # 'builder',
            # 'rater',
            # 'hers__score',
            # 'electric_utility'
        ]

    def get_subdivision_data(self):
        """Pull all of the Sudivision Data"""

        replace_dict = OrderedDict(
            [
                ("id", "ID"),
                ("home__subdivision__id", "Subdivision ID"),
                ("home__subdivision__name", "Subdivision Name"),
                ("home__subdivision__builder_org__name", "Subdivision Builder Name"),
                ("home__subdivision__city__name", "Subdivision City"),
                ("home__subdivision__cross_roads", "Subdivision Cross Roads"),
                ("home__subdivision__aps_thermostat_option__models", "Smart Thermostat Eligible"),
                (
                    "home__subdivision__aps_thermostat_option__eligibility",
                    "Smart Thermostat Eligible",
                ),
                ("home__subdivision__community__name", "Community Name"),
                ("home__subdivision__community__cross_roads", "Community Cross Roads"),
            ]
        )

        from axis.customer_aps.models import SMART_TSTAT_MODELS, SMART_TSTAT_ELIGIBILITY

        def clean_eligibility(ident):
            """Gets the pretty name"""
            return dict(SMART_TSTAT_ELIGIBILITY).get(ident, "-")

        def clean_models(ident):
            """Gets the pretty name"""
            if ident is None:
                return "-"
            if ident and not isinstance(ident, set):
                ident = eval(ident)
            return ",".join([dict(SMART_TSTAT_MODELS).get(x, "-") for x in ident])

        clean_dict = {
            "home__subdivision__aps_thermostat_option__models": clean_models,
            "home__subdivision__aps_thermostat_option__eligibility": clean_eligibility,
        }

        structure = self.assign_basic(
            EEPProgramHomeStatus,
            include=list(replace_dict.keys()),
            drop_prefix="home__",
            section="subdivision",
            replace_dict=replace_dict,
            clean_dict=clean_dict,
        )

        select_related = [
            "__".join(item.attr.split("__")[:-1])
            for item in structure
            if len(item.attr.split("__")) > 1
        ]

        subdivision_id = self.kwargs.get("subdivision_id", None)
        if subdivision_id:
            objects = EEPProgramHomeStatus.objects.filter_by_user(user=self.user).filter(
                home__subdivision__id=subdivision_id
            )
            objects = objects.select_related(*select_related)
        else:
            objects = self.get_queryset().select_related(*select_related)

        objects = objects.prefetch_related("home__subdivision__eep_programs")

        objects = objects.prefetch_related("home__subdivision__floorplans")

        data = []
        seen = {}

        accounted = objects.order_by("home__subdivision_id")
        accounted_for = list(set(accounted.values_list("home__subdivision_id", flat=True)))
        log.info("Part 1 - starting with with %s", len(accounted_for))
        for ht in objects:
            subdivision = ht.home.subdivision
            if not subdivision:
                continue
            if subdivision.id in seen.keys():
                continue
            seen[subdivision.id] = 1

            tstat_option = APSSmartThermostatOption.objects.filter(subdivision=subdivision).first()
            if tstat_option:
                tstat_models = clean_models(tstat_option.models)
                tstat_eligibility = clean_eligibility(tstat_option.eligibility)
            else:
                tstat_models = clean_models(None)
                tstat_eligibility = clean_eligibility(None)

            thermostat_qty = FloorplanApproval.objects.filter(subdivision=subdivision).aggregate(
                Sum("thermostat_qty")
            )
            thermostat_qty = thermostat_qty["thermostat_qty__sum"]

            # All electric?
            # all_electric = 'Yes' if subdivision.get_fuel_types(self.user) == 'Electric' \
            #     else 'No'
            # self.log.debug('All Electric done!')

            # Rating proder
            provider = subdivision.relationships.filter_by_company_type("provider").first()
            provider_name = provider.company.name
            provider_id = provider.company.id

            program_ids = (
                subdivision.home_set.filter_by_user(self.user)
                .values_list("eep_programs__id", flat=True)
                .distinct()
            )

            programs_list = list(
                EEPProgram.objects.filter(id__in=program_ids).values_list("name", flat=True)
            )
            programs = ", ".join(programs_list)
            # for program in EEPProgram.objects.filter(id__in=program_ids):
            community_name = "-"
            community_cross_roads = "-"
            if subdivision.community:
                community_name = subdivision.community.name
                community_id = subdivision.community.id
                community_cross_roads = subdivision.community.cross_roads

            fp_data = self.get_aps_floorplan_data(subdivision)

            builder_agreements = self.get_aps_builder_agreement_data(subdivision)

            for fp in fp_data:
                for ba in builder_agreements:
                    data.append(
                        [
                            CellObject("id", "ID", None, "subdivision", ht.id, ht.id),
                            CellObject(
                                "home__subdivision__id",
                                "Subdivision ID",
                                None,
                                "subdivision",
                                subdivision.id,
                                subdivision.id,
                            ),
                            CellObject(
                                "home__subdivision__name",
                                "Subdivision Name",
                                None,
                                "subdivision",
                                subdivision.name,
                                subdivision.name,
                            ),
                            CellObject(
                                "home__subdivision__eep_program_name",
                                "Program name",
                                None,
                                "subdivision",
                                programs,
                                programs,
                            ),
                            CellObject(
                                "home__subdivision__builder_accounting_code",
                                "Builder Accounting Code",
                                None,
                                "subdivision",
                                subdivision.builder_name,
                                subdivision.builder_name,
                            ),
                            CellObject(
                                "home__subdivision__builder_org__id",
                                "Builder ID",
                                None,
                                "subdivision",
                                subdivision.builder_org.id,
                                subdivision.builder_org.id,
                            ),
                            CellObject(
                                "home__subdivision__builder_org__name",
                                "Builder Name",
                                None,
                                "subdivision",
                                subdivision.builder_org.name,
                                subdivision.builder_org.name,
                            ),
                            CellObject(
                                "home__subdivision__cross_roads",
                                "Subdivision Cross Roads",
                                None,
                                "subdivision",
                                subdivision.cross_roads,
                                subdivision.cross_roads,
                            ),
                            CellObject(
                                "home__subdivision__city__name",
                                "Subdivision City",
                                None,
                                "subdivision",
                                subdivision.city.name,
                                subdivision.city.name,
                            ),
                            CellObject(
                                "home__subdivision__aps_thermostat_option__models",
                                "Smart Thermostat Models",
                                None,
                                "subdivision",
                                tstat_models,
                                tstat_models,
                            ),
                            CellObject(
                                "home__subdivision__aps_thermostat_option__eligibility",
                                "Smart Thermostat Eligibility",
                                None,
                                "subdivision",
                                tstat_eligibility,
                                tstat_eligibility,
                            ),
                            # CellObject('home__subdivision__all_electric', 'All Electric', None, \
                            #     'subdivision', all_electric, all_electric),
                            CellObject(
                                "home__subdivision__provider__id",
                                "Rating Provider ID",
                                None,
                                "subdivision",
                                provider_id,
                                provider_id,
                            ),
                            CellObject(
                                "home__subdivision__provider__name",
                                "Rating Provider",
                                None,
                                "subdivision",
                                provider_name,
                                provider_name,
                            ),
                            # CellObject('subdivision__thermostat_qty', 'Thermostat Quantity', \
                            #     None, 'subdivision', thermostat_qty, thermostat_qty),
                            CellObject(
                                "home__subdivision__community__id",
                                "Community ID",
                                None,
                                "subdivision",
                                community_id,
                                community_id,
                            ),
                            CellObject(
                                "home__subdivision__community__name",
                                "Community Name",
                                None,
                                "subdivision",
                                community_name,
                                community_name,
                            ),
                            CellObject(
                                "home__subdivision__community__cross_roads",
                                "Community Crossroads",
                                None,
                                "subdivision",
                                community_cross_roads,
                                community_cross_roads,
                            ),
                        ]
                        + fp
                        + ba
                    )

        remainder = Subdivision.objects.filter_by_user(self.user).values_list("pk", flat=True)
        remainder = list(set(remainder) - set(accounted_for))
        sub_qs = Subdivision.objects.filter(id__in=remainder)
        log.warning("Part 2 - Finishing with %s", len(remainder))
        for idx, subdivision in enumerate(sub_qs, start=1000000):
            if subdivision.id in seen:
                continue
            seen[subdivision.id] = 1

            provider = subdivision.relationships.filter_by_company_type("provider").first()
            provider_name = provider.company.name
            provider_id = provider.company.id

            tstat_option = APSSmartThermostatOption.objects.filter(subdivision=subdivision).first()
            if tstat_option:
                tstat_models = clean_models(tstat_option.models)
                tstat_eligibility = clean_eligibility(tstat_option.eligibility)
            else:
                tstat_models = clean_models(None)
                tstat_eligibility = clean_eligibility(None)

            program_objects = subdivision.eep_programs.all()
            programs = ", ".join(program_objects.values_list("name", flat=True))
            ba = self.get_aps_builder_agreement_data(subdivision)
            ba = ba[0] if len(ba) else ba
            base = [
                CellObject("id", "ID", None, "subdivision", idx, idx),
                CellObject(
                    "home__subdivision__id",
                    "Subdivision ID",
                    None,
                    "subdivision",
                    subdivision.id,
                    subdivision.id,
                ),
                CellObject(
                    "home__subdivision__name",
                    "Subdivision Name",
                    None,
                    "subdivision",
                    subdivision.name,
                    subdivision.name,
                ),
                CellObject(
                    "home__subdivision__eep_program_name",
                    "Program name",
                    None,
                    "subdivision",
                    programs,
                    programs,
                ),
                CellObject(
                    "home__subdivision__builder_accounting_code",
                    "Builder Accounting Code",
                    None,
                    "subdivision",
                    subdivision.builder_name,
                    subdivision.builder_name,
                ),
                CellObject(
                    "home__subdivision__builder_org__id",
                    "Builder ID",
                    None,
                    "subdivision",
                    subdivision.builder_org.id,
                    subdivision.builder_org.id,
                ),
                CellObject(
                    "home__subdivision__builder_org__name",
                    "Builder Name",
                    None,
                    "subdivision",
                    subdivision.builder_org.name,
                    subdivision.builder_org.name,
                ),
                CellObject(
                    "home__subdivision__cross_roads",
                    "Subdivision Cross Roads",
                    None,
                    "subdivision",
                    subdivision.cross_roads,
                    subdivision.cross_roads,
                ),
                CellObject(
                    "home__subdivision__city__name",
                    "Subdivision City",
                    None,
                    "subdivision",
                    subdivision.city.name,
                    subdivision.city.name,
                ),
                CellObject(
                    "home__subdivision__aps_thermostat_option__models",
                    "Smart Thermostat Models",
                    None,
                    "subdivision",
                    tstat_models,
                    tstat_models,
                ),
                CellObject(
                    "home__subdivision__aps_thermostat_option__eligibility",
                    "Smart Thermostat Eligibility",
                    None,
                    "subdivision",
                    tstat_eligibility,
                    tstat_eligibility,
                ),
                CellObject(
                    "home__subdivision__provider__id",
                    "Rating Provider ID",
                    None,
                    "subdivision",
                    provider_id,
                    provider_id,
                ),
                CellObject(
                    "home__subdivision__provider__name",
                    "Rating Provider",
                    None,
                    "subdivision",
                    provider_name,
                    provider_name,
                ),
            ] + ba

            fp_qs = (
                subdivision.floorplans.filter(remrate_target__isnull=False)
                .select_related("remrate_target")
                .prefetch_related("remrate_target__installedequipment_set")
            )
            fuel_types = set(
                x.equipment.get_fuel_type_display()
                for f in fp_qs
                for x in f.remrate_target.get_installed_equipment()
            )
            fuel_types = sorted(fuel_types)
            fuel_types = ", ".join(fuel_types)
            all_electric = "Yes" if fuel_types == "Electric" else "No"

            for fp in subdivision.floorplans.all():
                # Catch axis.remrate_data.models.simulation.Simulation.hers.RelatedObjectDoesNotExist
                hers_score = fp.get_hers_score_for_program(
                    EEPProgram.objects.filter(owner__slug="aps").last()
                )

                thermostat_qty = (
                    FloorplanApproval.objects.filter(subdivision=subdivision, floorplan=fp)
                    .first()
                    .thermostat_qty
                )

                data.append(
                    base
                    + [
                        CellObject(
                            "home__subdivision__all_electric",
                            "All Electric",
                            None,
                            "subdivision",
                            all_electric,
                            all_electric,
                        ),
                        CellObject(
                            "subdivision__thermostat_qty",
                            "Thermostat Quantity",
                            None,
                            "subdivision",
                            thermostat_qty,
                            thermostat_qty,
                        ),
                        CellObject(
                            "floorplan__id", "Floorplan ID", None, "subdivision", fp.id, fp.id
                        ),
                        CellObject(
                            "floorplan__name",
                            "Floorplan Name",
                            None,
                            "subdivision",
                            fp.name,
                            fp.name,
                        ),
                        CellObject(
                            "floorplan__number",
                            "Floorplan Number",
                            None,
                            "subdivision",
                            fp.number,
                            fp.number,
                        ),
                        CellObject(
                            "floorplan__square_footage",
                            "Floorplan Square footage",
                            None,
                            "subdivision",
                            fp.square_footage,
                            fp.square_footage,
                        ),
                        CellObject(
                            "floorplan__is_custom_home",
                            "Floorplan is a Custom Home",
                            None,
                            "subdivision",
                            fp.is_custom_home,
                            "Yes" if fp.is_custom_home else "No",
                        ),
                        CellObject(
                            "floorplan__is_active",
                            "Floorplan Is active",
                            None,
                            "subdivision",
                            fp.is_active,
                            "Yes" if fp.is_active else "No",
                        ),
                        CellObject(
                            "floorplan__created_date",
                            "Floorplan Created date",
                            self.get_formatted_date,
                            "subdivision",
                            fp.created_date,
                            self.get_formatted_date(fp.created_date),
                        ),
                        CellObject(
                            "floorplan__remrate_target__hers__score",
                            "HERS Score",
                            None,
                            "subdivision",
                            hers_score,
                            hers_score,
                        ),
                    ]
                )

            else:
                data.append(base)

        return data

    def get_aps_builder_agreement_data(self, subdivision):
        from axis.builder_agreement.models import BuilderAgreement

        data = []

        agreements = BuilderAgreement.objects.filter(subdivision=subdivision)
        if not agreements:
            return data
        for ba in agreements.all():
            ba_start_date = ba.start_date
            ba_lots_paid = ba.lots_paid
            ba_total_lots = ba.total_lots

            data.append(
                [
                    CellObject(
                        "builderagreement__start_date",
                        "Builder Agreement Start Date",
                        self.get_formatted_date,
                        "subdivision",
                        ba_start_date,
                        self.get_formatted_date(ba_start_date),
                    ),
                    CellObject(
                        "builderagreement__lots_paid",
                        "Builder Agreement Total Lots Paid",
                        None,
                        "subdivision",
                        ba_lots_paid,
                        ba_lots_paid,
                    ),
                    CellObject(
                        "builderagreement__total_lots",
                        "Builder Agreement Total Lots Signed",
                        None,
                        "subdivision",
                        ba_total_lots,
                        ba_total_lots,
                    ),
                ]
            )

        return data

    def get_aps_floorplan_data(self, subdivision):
        from axis.subdivision.models import FloorplanApproval

        floorplans = subdivision.floorplans
        data = []
        if not subdivision:
            return data

        # Fuel types - All Electric?
        fp_qs = (
            floorplans.filter(remrate_target__isnull=False)
            .select_related("remrate_target")
            .prefetch_related("remrate_target__installedequipment_set")
        )
        fuel_types = set(
            x.equipment.get_fuel_type_display()
            for f in fp_qs
            for x in f.remrate_target.get_installed_equipment()
        )
        fuel_types = sorted(fuel_types)
        fuel_types = ", ".join(fuel_types)
        all_electric = "Yes" if fuel_types == "Electric" else "No"

        for fp in floorplans.all():
            # Catch axis.remrate_data.models.simulation.Simulation.hers.RelatedObjectDoesNotExist
            subdivision.eep_programs.all()
            hers_score = fp.get_hers_score_for_program(
                EEPProgram.objects.filter(owner__slug="aps").last()
            )

            thermostat_qty = (
                FloorplanApproval.objects.filter(subdivision=subdivision, floorplan=fp)
                .first()
                .thermostat_qty
            )

            data.append(
                [
                    CellObject(
                        "home__subdivision__all_electric",
                        "All Electric",
                        None,
                        "subdivision",
                        all_electric,
                        all_electric,
                    ),
                    CellObject(
                        "subdivision__thermostat_qty",
                        "Thermostat Quantity",
                        None,
                        "subdivision",
                        thermostat_qty,
                        thermostat_qty,
                    ),
                    CellObject("floorplan__id", "Floorplan ID", None, "subdivision", fp.id, fp.id),
                    CellObject(
                        "floorplan__name", "Floorplan Name", None, "subdivision", fp.name, fp.name
                    ),
                    CellObject(
                        "floorplan__number",
                        "Floorplan Number",
                        None,
                        "subdivision",
                        fp.number,
                        fp.number,
                    ),
                    CellObject(
                        "floorplan__square_footage",
                        "Floorplan Square footage",
                        None,
                        "subdivision",
                        fp.square_footage,
                        fp.square_footage,
                    ),
                    CellObject(
                        "floorplan__is_custom_home",
                        "Floorplan is a Custom Home",
                        None,
                        "subdivision",
                        fp.is_custom_home,
                        "Yes" if fp.is_custom_home else "No",
                    ),
                    CellObject(
                        "floorplan__is_active",
                        "Floorplan Is active",
                        None,
                        "subdivision",
                        fp.is_active,
                        "Yes" if fp.is_active else "No",
                    ),
                    CellObject(
                        "floorplan__created_date",
                        "Floorplan Created date",
                        self.get_formatted_date,
                        "subdivision",
                        fp.created_date,
                        self.get_formatted_date(fp.created_date),
                    ),
                    CellObject(
                        "floorplan__remrate_target__hers__score",
                        "HERS Score",
                        None,
                        "subdivision",
                        hers_score,
                        hers_score,
                    ),
                ]
            )
        return data

    def munge_data(self, result_dict, new_data, key="id", verbose=False):
        """
        Takes each list in ``new_data`` and extends the corresponding running data pile at
        ``result_dict[id]``, where the appropriate id is available in each ``new_data`` list.
        """

        if verbose:
            if len(new_data):
                log.debug(pprint.pformat(new_data[-1]))
            log.debug("Result Keys: %r", list(result_dict.keys()))
        rn = 1
        for item in new_data:
            if not len(item):
                log.warning("Zero length item found..")
                continue
            try:
                _id = next((x for x in item if x.attr == key)).value
            except StopIteration:
                print(item)
                raise
            if verbose and new_data.index(item) == len(new_data) - 1:
                log.debug("ID %r", _id)
                log.debug("Initial Length %r", len(result_dict[_id]))

            if _id not in result_dict and self.user.company.slug != "aps":
                raise ValueError(
                    "Unexpected {id_key} {id!r} after '{caller_function}' "
                    "gathered data for queryset. (valid {id_key} list={id_list!r})"
                    " '(data={data!r})".format(
                        **{
                            "id_key": key,
                            "id": _id,
                            "id_list": list(sorted(result_dict.keys())),
                            "data": item,
                            "caller_function": inspect.stack()[1][3],
                        }
                    )
                )

            if self.user.company.slug == "aps":
                if result_dict.get(rn):
                    result_dict[rn] += item
                else:
                    result_dict.update({rn: item})
                rn += 1
            else:
                result_dict[_id] += item

            if verbose and new_data.index(item) == len(new_data) - 1:
                log.debug("ID %r", _id)
                log.debug("Final Length %r", len(result_dict[_id]))
                log.debug("Result item: %s", pprint.pformat(result_dict[_id]))
        return result_dict
