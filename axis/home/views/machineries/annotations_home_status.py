from axis.examine.machinery import ExamineMachinery
from axis.home.api import HomeStatusAnnotationsViewSet
from axis.home.models import EEPProgramHomeStatus
from axis.home.utils import get_required_annotations_form
from axis.examine.utils import template_url

__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class AnnotationsHomeStatusExamineMachinery(ExamineMachinery):
    model = EEPProgramHomeStatus
    type_name = "home_status_annotations"
    api_provider = HomeStatusAnnotationsViewSet

    region_template = "examine/home/annotations_region.html"

    # Used in template getters to build a correct Annotations form
    annotations_templates = {
        None: "examine/home/annotations/default.html",
        "*": {
            "ngbs-": "examine/home/annotations/ngbs.html",
        },
        "ngbs-land-development-2020-new": "examine/home/annotations/ngbs_land_development_2020.html",
        "ngbs-sf-new-construction-2020-new": "examine/home/annotations/ngbs_rough_final.html",
        "ngbs-mf-new-construction-2020-new": "examine/home/annotations/ngbs_rough_final.html",
        "ngbs-sf-new-construction-2015-new": "examine/home/annotations/ngbs_rough_final.html",
        "ngbs-mf-new-construction-2015-new": "examine/home/annotations/ngbs_rough_final.html",
        "ngbs-sf-new-construction-2012-new": "examine/home/annotations/ngbs_rough_final.html",
        "ngbs-mf-new-construction-2012-new": "examine/home/annotations/ngbs_rough_final.html",
        "ngbs-sf-certified-2020-new": "examine/home/annotations/ngbs_rough_final.html",
        "ngbs-sf-whole-house-remodel-2012-new": "examine/home/annotations/ngbs_rough_final.html",
        "ngbs-mf-whole-house-remodel-2012-new": "examine/home/annotations/ngbs_rough_final.html",
        "ngbs-sf-whole-house-remodel-2015-new": "examine/home/annotations/ngbs_rough_final.html",
        "ngbs-mf-whole-house-remodel-2015-new": "examine/home/annotations/ngbs_rough_final.html",
        "ngbs-sf-whole-house-remodel-2020-new": "examine/home/annotations/ngbs_rough_final.html",
        "ngbs-mf-whole-house-remodel-2020-new": "examine/home/annotations/ngbs_rough_final.html",
        "ngbs-mf-wri-2021": "examine/home/annotations/ngbs_mf_wri_2021.html",
        "ngbs-sf-wri-2021": "examine/home/annotations/ngbs_sf_wri_2021.html",
        "neea-energy-star-v3": "examine/home/annotations/neea_basic.html",
        "neea-energy-star-v3-performance": "examine/home/annotations/neea_performance.html",
        "neea-performance-2015": "examine/home/annotations/neea_performance_2015.html",
        "neea-prescriptive-2015": "examine/home/annotations/neea_prescriptive_2015.html",
        "neea-efficient-homes": "examine/home/annotations/neea_efficient_homes.html",
        "built-green-tri-cities": "examine/home/annotations/built_green.html",
        "built-green-tri-cities1": "examine/home/annotations/built_green.html",
        "built-green-tri-cities-4": "examine/home/annotations/built_green.html",
        "built-green-wa-prescriptive": "examine/home/annotations/built_green_wa.html",
        "built-green-wa-performance": "examine/home/annotations/built_green_wa.html",
        "neea-bpa": "examine/home/annotations/neea_bpa.html",
        "neea-bpa-v3": "examine/home/annotations/neea_bpa.html",
        "wa-code-study": "examine/home/annotations/wa_code_study.html",
        "resnet-registry-data": "examine/home/annotations/resnet_registry_data.html",
        "wsu-hers-2020": "examine/home/annotations/wsu_certification_2020.html",
        "washington-code-credit": "examine/home/annotations/washington_code_credit.html",
    }

    def _get_template_url(self, instance):
        slug = instance.eep_program.slug
        name = self.annotations_templates.get(slug, None)
        if name is None:
            for search_slug, template_name in self.annotations_templates["*"].items():
                if search_slug in slug:
                    name = template_name
                    break
            else:
                # Use default template if no override
                name = self.annotations_templates[None]
        return name

    def get_detail_template_url(self, instance):
        name = self._get_template_url(instance)
        return template_url(name)

    def get_form_template_url(self, instance):
        name = self._get_template_url(instance)
        return template_url(name.replace(".html", "_form.html"))

    def get_form(self, instance):
        # We'll ignore local var "instance" in favor of self.instance, because sometimes the local
        # variable is None for the sake of getting the general form.  The instance program will
        # change the available annotations.  This wouldn't work quite so well if the machinery was
        # used in "many" mode.
        form = get_required_annotations_form(self.instance, user=self.context["request"].user)

        # Hack in some widget types not easily detected by the annotation form factory
        from django import forms

        for field in form.fields:
            if field in ["project-start", "project-start-nr", "project-end-nr", "move-in-date-nr"]:
                form.fields[field].widget = forms.DateInput()

            if field == "bop":
                if self.instance.eep_program.slug == "utility-incentive-v1-multifamily":
                    form.fields[field] = self.set_neea_bop_multifamily_choices(form.fields[field])

        return form

    def get_default_actions(self, instance):
        if instance.can_be_edited(self.context["request"].user):
            return [
                self.Action(
                    name="Edit annotations", instruction="edit", is_mode=True, style="primary"
                )
            ]
        return []

    def set_neea_bop_multifamily_choices(self, field):
        field.widget.choices = [
            choice for choice in field.widget.choices if ("MF" in choice[0]) or choice[0] == ""
        ]
        return field
