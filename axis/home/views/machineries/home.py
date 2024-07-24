"""Home Examine Machinery"""

from django.apps import apps
from django.urls import reverse, reverse_lazy

from axis.core.views.machinery import AxisGeocodedMachineryMixin, AxisPrimaryMachinery
from axis.examine import ReadonlyMachinery, PanelMachinery
from axis.home.api import HomeViewSet
from axis.home.forms import HomeForm
from axis.home.models import Home
from axis.home.utils import get_inheritable_settings_form_info
from axis.home.views.utils import _get_home_contributor_flag
from .aps_home import APSHomeExamineMachinery
from .home_blg_creation import HomeBLGCreationExamineMachinery

__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class HomeExamineMachinery(AxisGeocodedMachineryMixin, AxisPrimaryMachinery):
    """The home machinery"""

    model = Home
    form_class = HomeForm
    type_name = "home"
    api_provider = HomeViewSet

    detail_template = "examine/home/home_detail.html"
    form_template = "examine/home/home_form.html"

    delete_success_url = reverse_lazy("home:list")

    restricted_by_sampling = False
    restricted_by_ipp = False
    restricted_by_homestatus_state = False
    restricted_edit = False
    is_contributor = False

    def get_verbose_names(self, instance, form=None, serializer=None, **kwargs):
        """Update for Multi-Family"""
        verbose_names = super(HomeExamineMachinery, self).get_verbose_names(
            instance, form, serializer, **kwargs
        )
        if instance and instance.is_multi_family:
            if instance.subdivision and instance.subdivision.is_multi_family:
                verbose_names["subdivision"] = "MF Development"
            elif instance.subdivision is None:
                verbose_names["subdivision"] = "MF Development"
        return verbose_names

    def configure_for_instance(self, instance):
        """Configures this for the home"""
        if instance.pk:
            is_edit_locked = instance.has_locked_homestatuses(include_samplesets=False)
            has_no_certifications = (
                instance.homestatuses.exclude(state="complete").exists()
                and not instance.homestatuses.filter(state="complete").exists()
            )

            self.restricted_by_sampling = instance.has_sampling_lock()
            self.restricted_by_ipp = is_edit_locked  # default assumption is an ipp lock
            self.restricted_by_homestatus_state = is_edit_locked and has_no_certifications
            self.restricted_edit = self.restricted_by_sampling or self.restricted_by_ipp
            self.is_contributor = _get_home_contributor_flag(instance, self.context["request"].user)

    def can_edit_object(self, instance, user=None):
        """Can this be edited"""
        if not self.is_contributor:
            return False
        return super(HomeExamineMachinery, self).can_edit_object(instance, user)

    def get_object_name(self, instance):
        """Say my name!"""
        if instance.pk is not None:
            return instance.get_addr(company=self.context["request"].user.company)

        return super(HomeExamineMachinery, self).get_object_name(instance)

    def get_form_kwargs(self, instance):
        """Form KWargs"""
        kwargs = {
            "user": self.context["request"].user,
        }
        if hasattr(self, "restricted_by_sampling"):
            kwargs["restricted_by_sampling"] = self.restricted_by_sampling
        if hasattr(self, "restricted_by_ipp"):
            kwargs["restricted_by_ipp"] = self.restricted_by_ipp
        if hasattr(self, "restricted_by_homestatus_state"):
            kwargs["restricted_by_homestatus_state"] = self.restricted_by_homestatus_state
        return kwargs

    def get_default_actions(self, instance):
        """Default Actions"""
        actions = super(HomeExamineMachinery, self).get_default_actions(instance)
        if self.restricted_edit:
            for action in actions:
                if action["instruction"] == "edit":
                    action["icon"] = "unlock-alt"

        cog_actions = []

        request = self.context.get("request")
        if instance.pk and request and request.user.is_superuser:
            cog_actions.append(
                {
                    "name": "Export fixture",
                    "icon": "cog",
                    "href": reverse(
                        "apiv2:dumpdata",
                        kwargs={
                            "label": "home.home",
                            "pk": instance.pk,
                        },
                    ),
                }
            )

        if cog_actions:
            actions.insert(
                0,
                self.Action(
                    name="", icon="cog", instruction=None, type="dropdown", items=cog_actions
                ),
            )

        return actions

    def get_helpers(self, instance):
        """Helpers on the home"""
        helpers = super(HomeExamineMachinery, self).get_helpers(instance)

        if self.context.get("lightweight"):
            return helpers

        helpers["restricted_by_sampling"] = self.restricted_by_sampling
        helpers["restricted_by_ipp"] = self.restricted_by_ipp
        helpers["restricted_by_homestatus_state"] = self.restricted_by_homestatus_state
        helpers["restricted_edit"] = self.restricted_edit

        helpers["machinery"] = {}

        # Deferred blg upload region
        context = self.context.copy()
        context["lightweight"] = True

        if self.create_new:
            blg_upload_machinery = HomeBLGCreationExamineMachinery(
                instance=instance, context=context
            )
            helpers["machinery"]["home_blg"] = blg_upload_machinery.get_summary()

        user = context["request"].user
        if user.company.slug == "aps" or user.is_superuser:
            if hasattr(instance, "apshome"):
                apshome_machinery = APSHomeExamineMachinery(
                    instance=instance.apshome, context=context
                )
                helpers["machinery"]["apshome"] = apshome_machinery.get_summary()

        helpers["page_title"] = "{} {}".format(self.get_verbose_name(instance), instance)

        hillsboro_helper = self.get_hillsboro_helper(instance)
        if hillsboro_helper:
            helpers["permitandoccupancysettings"] = hillsboro_helper

        return helpers

    def get_hillsboro_helper(self, instance):
        """Return dict for permit and occupancy settings and form."""

        from axis.customer_eto.forms import PermitAndOccupancySettingsForm
        from axis.customer_eto.strings import COMPLIANCE_LONGFORM_HTML_CHOICES

        customer_eto_app = apps.get_app_config("customer_eto")

        user = self.context["request"].user
        if not all(
            [
                not self.create_new,
                user.has_perm("customer_eto.change_permitandoccupancysettings"),
                (
                    instance.subdivision
                    and instance.subdivision.community
                    and (
                        instance.subdivision.community.slug
                        in customer_eto_app.CITY_OF_HILLSBORO_COMMUNITY_SLUGS
                    )
                ),
            ]
        ):
            return None

        helper = get_inheritable_settings_form_info(
            user.company,
            instance,
            "permitandoccupancysettings_set",
            form_class=PermitAndOccupancySettingsForm,
            settings_action_url="eto-compliance-option",
            document_action_url="eto-compliance-document",
        )
        helper["html_choices"] = COMPLIANCE_LONGFORM_HTML_CHOICES
        helper["form"] = self.serialize_form_spec(instance, helper["form"])

        # Contextualize buttons based on internal state info
        settings_obj = instance.permitandoccupancysettings_set.get_for_user(user)
        documents = instance.customer_documents.filter(company=user.company)
        helper["report_button_name"] = None
        helper["no_button_status"] = None
        if documents.filter(description=customer_eto_app.OCCUPANCY_DESCRIPTION).first():
            if settings_obj and settings_obj.signed_certificate_of_occupancy:
                helper["no_button_status"] = "Occupancy Report<br>Has Been Completed"
            else:
                helper["no_button_status"] = "Occupancy Report<br>Has Been Requested"
        elif documents.filter(description=customer_eto_app.PERMIT_DESCRIPTION).first():
            if settings_obj and settings_obj.signed_building_permit:
                helper["report_button_name"] = "Sign Occupancy Report"
            else:
                helper["no_button_status"] = "Building Permit Report<br>Has Been Requested"
        else:
            helper["report_button_name"] = "Sign Building Permit Report"

        return helper


class HomeDocumentActionsMachinery(PanelMachinery, ReadonlyMachinery):
    model = Home
    type_name = "home_document_actions"
    api_provider = HomeViewSet
    region_template = "examine/home/home_document_actions_region.html"
    detail_template = "examine/home/home_document_actions_detail.html"

    def get_static_actions(self, instance):
        """Return static actions with contextual additions for the current state."""

        # Extra actions
        actions = super(HomeDocumentActionsMachinery, self).get_static_actions(instance)

        request = self.context.get("request", None)
        user = request.user if request else None

        if user and user.is_customer_hirl_company_member():
            actions[:0] = [
                {
                    "name": "Sync Documents Across Batch",
                    "instruction": "customer_hirl_sync_documents_across_batch",
                    "style": "primary btn-xs",
                    "description": "Sync Across Batch",
                }
            ]

        return actions

    def get_helpers(self, instance):
        helpers = super(HomeDocumentActionsMachinery, self).get_helpers(instance)
        if instance and instance.pk:
            helpers["customer_hirl_sync_documents_across_batch_endpoint"] = reverse(
                "apiv2:home-customer-hirl-sync-documents-across-batch", kwargs={"pk": instance.pk}
            )
        return helpers
