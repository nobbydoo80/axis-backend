"""admin.py: Django home"""

import logging

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django_input_collection.models import get_input_model

from axis.annotation.models import Annotation, Type
from axis.core.fields import AxisJSONField
from axis.customer_eto.admin import FastTrackSubmissionStackedInline
from axis.geographic.admin import PlaceSaveMixin
from axis.home.models import Home, EEPProgramHomeStatus, HomePhoto
from axis.home.tasks import update_home_states
from axis.relationship.admin import RelationshipTabularInline

__author__ = "Steven Klass"
__date__ = "3/5/12 1:35 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

CollectedInput = get_input_model()


# NOT SURE WHY I CAN'T IMPORT THIS FROM ANNOTATION DIRECTLY..
class AnnotationInlineForm(forms.ModelForm):
    class Meta:
        model = Annotation
        fields = ("type", "content")

    def __init__(self, *args, **kwargs):
        super(AnnotationInlineForm, self).__init__(*args, **kwargs)
        if getattr(self, "instance", None) and self.instance:
            try:
                initial = self.instance.content
                annotation_type = self.instance.type
            except ObjectDoesNotExist:
                pass
            else:
                required = annotation_type.is_required
                self.fields["type"].queryset = Type.objects.filter(id=annotation_type.id)
                self.fields["type"].widget.attrs["editable"] = False

                if annotation_type.data_type == "multiple-choice":
                    choices = [("", "---------")]
                    choices += zip(*(annotation_type.get_valid_multiplechoice_values(),) * 2)
                    self.fields["content"] = forms.ChoiceField(
                        choices=choices,
                        label=annotation_type.name,
                        required=required,
                        initial=initial,
                    )
                elif annotation_type.data_type == "integer":
                    self.fields["content"] = forms.IntegerField(required=required)
                elif annotation_type.data_type == "float":
                    self.fields["content"] = forms.FloatField(required=required)
                else:
                    self.fields["content"] = forms.CharField(
                        label=annotation_type.name, required=required, initial=initial
                    )


class AnnotationAdmin(GenericTabularInline):
    """Inline Document"""

    form = AnnotationInlineForm
    model = Annotation
    extra = 0


class HomeStatusAdmin(admin.StackedInline):
    """Inline Document"""

    model = EEPProgramHomeStatus
    extra = 0

    raw_id_fields = (
        "company",
        "floorplan",
        "collection_request",
        "customer_hirl_rough_verifier",
        "customer_hirl_final_verifier",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "company",
                    "eep_program",
                    "collection_request",
                    ("floorplan",),
                    ("state", "certification_date"),
                )
            },
        ),
        (
            "Advanced options",
            {
                "classes": ("collapse",),
                "fields": (
                    (
                        "pct_complete",
                        "is_billable",
                        "customer_hirl_rough_verifier",
                        "customer_hirl_final_verifier",
                    ),
                ),
            },
        ),
    )


class ShortForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    def label_and_url_for_value(self, value):
        lable, url = super(ShortForeignKeyRawIdWidget, self).label_and_url_for_value(value)
        return "", url


class CollectedInputInline(admin.TabularInline):
    model = CollectedInput
    extra = 0
    raw_id_fields = ("home_status",)
    readonly_fields = ("user", "instrument", "date_created")
    fields = [
        "home_status",
        "user",
        "user_role",
        "instrument",
        "data",
    ]

    formfield_overrides = {
        AxisJSONField: {"widget": forms.TextInput(attrs={"style": "width: 400px;"})},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "home_status":
            db = kwargs.get("using")
            kwargs["widget"] = ShortForeignKeyRawIdWidget(
                db_field.remote_field, self.admin_site, using=db
            )
            kwargs["queryset"] = db_field.remote_field.model.objects.filter_by_user(request.user)
            return db_field.formfield(**kwargs)
        return super(CollectedInputInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )


class HomePhotoTabularInline(admin.TabularInline):
    model = HomePhoto
    extra = 0


class HomeAdmin(PlaceSaveMixin, admin.ModelAdmin):
    """City use ID only please"""

    model = Home
    list_display = ("lot_number", "street_line1", "city", "modified_date", "confirmed_address")
    search_fields = ["lot_number", "street_line1", "city__name", "state", "zipcode"]
    list_filter = ["state"]
    raw_id_fields = ("subdivision", "city", "county")
    exclude = (
        "users",
        "geocode_response",
        "place",
    )
    inlines = (
        HomeStatusAdmin,
        HomePhotoTabularInline,
        RelationshipTabularInline,
        CollectedInputInline,
    )
    actions = ["reassign_historical_relationships", "update_automatch"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "lot_number",
                    "street_line1",
                    "street_line2",
                    "city",
                    "zipcode",
                    ("is_custom_home", "subdivision"),
                    (
                        "confirmed_address",
                        "address_override",
                        "is_multi_family",
                    ),
                )
            },
        ),
        (
            "Advanced options",
            {
                "classes": ("collapse",),
                "fields": (
                    ("is_active", "bulk_uploaded"),
                    ("latitude", "longitude"),
                    "county",
                    "alt_name",
                ),
            },
        ),
    )

    def reassign_historical_relationships(self, request, queryset):
        """This will provide a way to look in the history and reassign relationships"""
        results = {}
        for home in queryset.all():
            # Current relationships
            from axis.relationship.models import Relationship
            from axis.company.models import Company

            ct = ContentType.objects.get_for_model(home)

            current_relationships = Relationship.objects.filter(object_id=home.id, content_type=ct)
            current_relationships = current_relationships.values_list("company", flat=True)
            current_companies = Company.objects.filter(id__in=current_relationships)

            HistoricalRelationship = Relationship.history.model
            historical = HistoricalRelationship.objects.filter(
                object_id=home.id, content_type=ct.id
            )
            historical_relationships = list(set(historical.values_list("company", flat=True)))
            historical_companies = Company.objects.filter(id__in=historical_relationships)

            adder_companies = []

            for company in historical_companies:
                if home not in results.keys():
                    results[home] = []
                if company not in current_companies:
                    results[home].append(
                        "Adding back {} {}".format(company.get_company_type_display(), company)
                    )
                    adder_companies.append(company)
                else:
                    results[home].append(
                        "Retaining existing {} {}".format(
                            company.get_company_type_display(), company
                        )
                    )
            for company in adder_companies:
                Relationship.objects.get_or_create_implied(
                    company=company, object_id=home.id, content_type=ct
                )

        msg = "<ul>"
        for k, v in results.items():
            msg += "<li>{}</li><ul><li>".format(k)
            msg += "</li><li>".join(v) + "</li></ul>"
        msg += "</ul>"
        self.message_user(request, mark_safe(msg))

    reassign_historical_relationships.description = "Reassign all historical relationships"

    def update_automatch(self, request, queryset):
        """Update a companies groups"""
        from axis.customer_aps.utils import update_apshomes

        confirmations = update_apshomes(lots=queryset)

        total_lots = len(queryset)
        total_confirmations = len(confirmations)
        try:
            pct = total_confirmations / total_lots
        except ZeroDivisionError:
            pct = 0.0
        msg = "Total lots analyzed: {} ; New Confirmations: {} ({}%)".format(
            total_lots, total_confirmations, pct
        )
        print(msg)
        # self.message_user(request, msg)

    update_automatch.short_description = "Run APS Meterset Automatch"


class EEProgramHomeStatusAdmin(admin.ModelAdmin):
    """City use ID only please"""

    model = Home
    list_display = ("home", "eep_program", "floorplan", "pct_complete", "certification_date")
    search_fields = [
        "home__lot_number",
        "eep_program__name",
        "floorplan__name",
        "home__street_line1",
    ]
    list_filter = ["eep_program"]
    actions = [
        "update_stats",
        "decertify",
        "send_fake_certification_email",
        "send_fake_bpa_certification_email",
        "send_fake_certification_pending_email",
    ]
    inlines = (AnnotationAdmin, FastTrackSubmissionStackedInline)

    raw_id_fields = (
        "company",
        "floorplan",
        "floorplans",
        "home",
        "customer_hirl_rough_verifier",
        "customer_hirl_final_verifier",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "company",
                    "eep_program",
                    ("floorplan", "floorplans"),
                    ("state", "certification_date"),
                    "home",
                )
            },
        ),
        (
            "Advanced options",
            {
                "classes": ("collapse",),
                "fields": (
                    (
                        "pct_complete",
                        "is_billable",
                        "customer_hirl_rough_verifier",
                        "customer_hirl_final_verifier",
                    ),
                ),
            },
        ),
    )

    def update_stats(self, request, queryset):
        """Update a companies groups"""
        for stat in queryset.all():
            stat.update_stats()
        update_home_states(eepprogramhomestatus_ids=list(queryset.values_list("id", flat=True)))
        if queryset.count() == 1:
            message_bit = "1 Project"
        else:
            message_bit = "%s Projects" % len(queryset.count())
        self.message_user(request, "%s successfully updated." % message_bit)

    update_stats.short_description = "Update Stats"

    def decertify(self, request, queryset):
        msgs = []
        for stat in queryset.all():
            msgs.append(stat.decertify(user=request.user, check_only=False, report=True))
            from django.contrib.admin.models import LogEntry, CHANGE

            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(stat).pk,
                object_id=stat.pk,
                object_repr="{}".format(stat),
                action_flag=CHANGE,
                change_message="decertify",
            )

        self.message_user(request, msgs)

    decertify.short_description = "Decertify Program"

    def send_fake_certification_email(self, request, queryset):
        """
        Manually trigger home/task -new_certification_daily_email- with custom queryset.
        Emails will only be sent to admins.
        """
        from axis.home.tasks import new_certification_daily_email_task

        new_certification_daily_email_task.delay(
            superusers_only=True, stats_list=list(queryset.values_list("pk", flat=True))
        )

    send_fake_certification_email.short_description = "Send Fake Certification Email"

    def send_fake_bpa_certification_email(self, request, queryset):
        """
        Manuall trigger home/task -new_bpa_certification_daily_email- with custom queryset.
        Emails will only be sent to admins.
        """
        from axis.home.tasks import new_bpa_certification_daily_email_task

        new_bpa_certification_daily_email_task.delay(
            superusers_only=True, stats_list=list(queryset.values_list("pk", flat=True))
        )

    send_fake_bpa_certification_email.short_description = "Send Fake BPA Certification Email"

    def send_fake_certification_pending_email(self, request, queryset):
        """
        Manually trigger home/task -pending_certification_daily_email with custom queryset
        Emails will only be sent to admins.
        """
        from axis.home.tasks import pending_certification_daily_email_task

        pending_certification_daily_email_task.delay(
            superusers_only=True, stats_list=list(queryset.values_list("pk", flat=True))
        )

    send_fake_certification_pending_email.short_description = (
        "Send Fake Certification " "Pending Email"
    )


admin.site.register(Home, HomeAdmin)
admin.site.register(EEPProgramHomeStatus, EEProgramHomeStatusAdmin)
