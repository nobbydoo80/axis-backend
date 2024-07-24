"""Auto-discovered admin registration."""


import logging

from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html

from .utils import import_certification, normalize_address

__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# pylint: disable=no-self-use
class CertificationAdmin(admin.ModelAdmin):
    """For Certification models from an app's `import_certifications` command."""

    search_fields = [
        "id",
        "home__id",
        "registry_id",
        "street_line1",
        "city",
        "state_abbreviation",
        "zipcode",
        "certification_date",
        "home_type",
        "software",
        "software_version",
        "construction_year",
        "conditioned_area",
        "conditioned_volume",
        "conditioned_floors",
        "number_bedrooms",
        "hers_index",
        "registration_type",
        "total_energy_use",
        "total_energy_cost",
        "num_cooling_systems",
        "num_heating_systems",
        "cooling_energy_use",
        "cost_cooling",
        "cooling_rated_output",
        "num_hot_water_systems",
        "hot_water_energy_use",
        "cost_hot_water",
        "lighting_app_energy_use",
        "cost_lighting",
        "on_site_generation",
        "annual_electricity",
        "annual_gas",
        "agw_wall_construction_type",
        "ach50",
        "ventilation_type",
        "duct_leakage",
        "duct_leakage_total",
        "duct_leakage_tightness_test",
        "duct_leakage_units",
        "high_efficiency_lights_percent",
        "furnace_fuel",
        "water_heater_type",
        "water_heater_fuel",
        "ducts_conditioned",
        "is_zerh",
        "energy_star_version",
    ]
    list_display = [
        "_street_line1",
        # 'builder',
        "_geo",
        "certification_date",
        "_home",
        "import_error",
    ]
    list_filter = [
        "import_failed",
        "import_error",
    ]
    date_hierarchy = "certification_date"

    actions = ["find_axis_home"]

    raw_id_fields = ("home",)

    def _street_line1(self, instance):
        # Gives some of the worse street_line1 values a chance to linebreak
        return instance.street_line1.replace("/", " / ")

    def _geo(self, instance):
        return "{}, {} ({})".format(instance.city, instance.state_abbreviation, instance.county)

    def _home(self, instance):
        if instance.home:
            return format_html('<a href="{}">{}</a>', instance.home.get_absolute_url(), "View")
        elif instance.candidates.count():
            return format_html(
                '<a style="color: red" href="{}">{}</a>',
                "/admin/%s/candidate/?certification_id=%d"
                % (
                    instance._meta.app_label,
                    instance.id,
                ),
                "FIX",
            )
        return "-"

    def find_axis_home(self, request, queryset):
        """Attempt an on-demand import of a Certification as a full Home."""
        n_items = queryset.count()
        n_errors = 0
        for instance in queryset:
            try:
                import_certification(instance)
            except Exception as exception:  # pylint: disable=broad-except
                log.exception("Error transforming to Axis home.")
                messages.error(request, str(exception))
                n_errors += 1

        if n_items - n_errors > 0:
            messages.success(request, "%d certifications matched." % (n_items - n_errors))
        if n_errors:
            messages.warning(request, "%d certifications not matched to Axis homes." % n_errors)

    find_axis_home.short_description = """Re-attempt import of selected certifications"""


class CandidateAdmin(admin.ModelAdmin):
    """Django admin bindings for Candidates created by ambiguous imports."""

    search_fields = [
        "certification_id",
        "home__id",
        "certification__street_line1",
        "home__street_line1",
        "certification__state_abbreviation",
        "certification__city",
    ]
    list_display = [
        "certification",
        "ranking",
        "_home",
        "profile_delta",
    ]
    list_select_related = [
        "certification",
        "home",
    ]
    actions = [
        "select",
        "reject",
        "scan",
    ]
    readonly_fields = [
        "certification",
        "home",
    ]

    def has_add_permission(self, request):
        """Return false to prevent manual instance creations."""
        return False

    def get_queryset(self, request):
        """Return false to prevent manual instance creations."""
        queryset = super(CandidateAdmin, self).get_queryset(request)
        print("I", queryset.count())
        print(queryset.filter(certification__home=None).count())
        print(
            queryset.filter(certification__home=None)
            .exclude(certification__certification_date=None)
            .count()
        )
        queryset = (
            queryset.filter(certification__home=None)
            .exclude(certification__certification_date=None)
            .order_by("certification_id", "levenshtein_distance")
        )

        print(queryset.count())
        return queryset

    def select(self, request, queryset):  # pylint: disable=unused-argument
        """Confirm the first selected item as the Candidate for which to base a Home."""
        instance = queryset.first()
        instance.certification.ensure_axis_home(home=instance.home)

    select.short_description = """Finalize this 1 selected candidate"""

    def reject(self, request, queryset):  # pylint: disable=unused-argument
        """Reject the Candidate pool and make a new Home from the original Certification fields."""
        certification = queryset.first().certification
        certification.ensure_axis_home(home=False)  # skip checks and go straight to creation

    reject.short_description = (
        """Reject all candidates in the selected group and create new Axis home"""
    )

    def scan(self, request, queryset):  # pylint: disable=unused-argument
        """Re-run matching and Candidate-creation logic for selected Candidates."""
        from axis.customer_hirl.models import Certification

        for certification in Certification.objects.filter(candidates__in=queryset).distinct():
            certification.find_axis_home()

    scan.short_description = """Check selected certifications for new candidates"""

    def _home(self, instance):
        rank = self._rank(instance)
        href = """<a href="{}"%s>{}</a>""" % (' style="font-weight: bold"' if rank >= 80 else "",)
        return format_html(href, instance.home.get_absolute_url(), "{}".format(instance.home))

    def ranking(self, instance):
        """Display ranking information for street_line1 similarity."""
        rank = self._rank(instance)
        if rank >= 95:
            key = """<strong style="color: green;">{}%</strong>"""
        elif rank >= 85:
            key = """<strong style="color: blue;">{}%</strong>"""
        elif rank >= 75:
            key = """<span style="color: orange;">{}%</span>"""
        elif rank >= 50:
            key = """<span style="color: #666;">{}%</span>"""
        elif rank >= 20:
            key = """<span style="color: #aaa;">{}%</span>"""
        else:
            key = """<span style="color: #ccc;">{}%</span>"""
        return format_html(key, int(rank))

    ranking.admin_order_field = "levenshtein_distance"

    def _rank(self, instance):
        street_line1 = normalize_address(instance.certification.street_line1)

        # Assign a rating on a 100% scale.
        # Using len(street_line1) as the divisor when we have a single-digit levenshtein threshold
        # inflates a lot of the percentages up past 50%, which is questionable for the average-sized
        # address.  Using len(street_line1)/2 pushes the percentages down while keeping good
        # candidates relatively high.
        distance = instance.levenshtein_distance
        levenshtein_percentage = 100 - (100.0 * distance / (len(street_line1) / 2))
        return max(levenshtein_percentage, 0)  # divisor trickery allows negative values now
