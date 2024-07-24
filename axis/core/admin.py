"""admin.py: Django core admin container"""

__author__ = "Steven Klass"
__date__ = "2011/06/22 09:56:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.forms import FlatpageForm
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.admin.sites import NotRegistered
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin, GroupAdmin as AuthGroupAdmin
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model

from axis.company.admin import CompanyAccessInlineAdmin
from axis.core.admin_utils import RelatedDropdownFilter
from axis.core.forms import UserAdminChangeForm, UserAdminCreationForm
from axis.core.models import (
    RaterRole,
    RecentlyViewed,
    AxisFlatPage,
    ContactCard,
    ContactCardPhone,
    ContactCardEmail,
)
from axis.ekotrope.models import EkotropeAuthDetails

User = get_user_model()

EXCLUDED_PERMISSION_CONTENT_TYPES = [
    "aec_remrate",
    "admin",
    "request",
    "mailer",
    "registration",
    "sessions",
    "sites",
    "contenttypes",
    "flatpages",
]


def _exclude_persmissions(queryset):
    """
    Filters away historical permissions and those included in EXCLUDED_PERMISSION_CONTENT_TYPES.
    """
    return queryset.exclude(
        Q(name__icontains="historical")
        | Q(content_type__app_label__in=EXCLUDED_PERMISSION_CONTENT_TYPES)
    )


class EkotropeAuthDetailsTabularInlineAdmin(admin.TabularInline):
    model = EkotropeAuthDetails


class UserAdmin(AuthUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_company_admin",
        "company",
        "is_staff",
        "is_superuser",
        "is_active",
        "is_approved",
        "last_login",
    )
    list_filter = (
        "is_company_admin",
        "is_staff",
        "is_superuser",
        "is_active",
        "is_approved",
        ("site", RelatedDropdownFilter),
    )
    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "site__domain",
        "company__name",
    )
    raw_id_fields = ("company",)
    ordering = ("username", "company")
    inlines = (EkotropeAuthDetailsTabularInlineAdmin, CompanyAccessInlineAdmin)

    # form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    fieldsets = (
        (
            None,
            {
                "fields": ("username", "password"),
            },
        ),
        (
            _("User Profile"),
            {
                "fields": ("first_name", "last_name", "email"),
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_approved",
                    "is_superuser",
                ),
            },
        ),
        (
            _("General"),
            {
                "fields": (
                    "title",
                    "department",
                    "work_phone",
                    "cell_phone",
                    "is_public",
                    "is_company_admin",
                    "site",
                    "company",
                    "date_joined",
                )
            },
        ),
        (_("Rater"), {"fields": ("rater_roles", "rater_id")}),
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Forces use of a custom widget for certain m2m fields."""
        # FIXME: I don't think I like this very much... It's not clear what fields we think we're
        # modifying.  This setting is discarded for m2m fields using raw_id_fields and
        # filter_horizontal and filter_verical, etc.
        # TODO: Figure out which fields we intend to be overriding here, and make them explicitly
        # use this widget via the ModelAdmin.formfield_overrides setting.
        # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.formfield_overrides

        kwargs["widget"] = FilteredSelectMultiple(verbose_name=db_field.name, is_stacked=False)
        return super(UserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class GroupAdmin(AuthGroupAdmin):
    """Tweak the Group Permissions to exclude historical permissions."""

    def get_form(self, request, obj=None, **kwargs):
        """Modifies the queryset for permissions to exclude historical and others."""
        form = super(GroupAdmin, self).get_form(request, obj, **kwargs)
        permissions = form.base_fields["permissions"]
        permissions.queryset = _exclude_persmissions(permissions.queryset)
        return form


class RaterRoleAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_hidden")
    prepopulated_fields = {"slug": ("title",)}


class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ("content_object", "user", "updated_at")
    search_fields = ("user__first_name", "user__last_name")
    raw_id_fields = ("user",)


class AxisFlatPageForm(FlatpageForm):
    class Meta:
        model = AxisFlatPage
        fields = "__all__"


class AxisFlatPageAdmin(FlatPageAdmin):
    form = AxisFlatPageForm
    fieldsets = ((None, {"fields": ("url", "title", "content", "sites", "order", "created_at")}),)
    list_display = ("url", "title", "order", "created_at")


class ContactCardPhoneTabularInlineAdmin(admin.TabularInline):
    model = ContactCardPhone
    extra = 1


class ContactCardEmailTabularInlineAdmin(admin.TabularInline):
    model = ContactCardEmail
    extra = 1


class ContactCardAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "protected")
    raw_id_fields = ("user", "company")
    search_fields = ("company__name", "user__first_name", "user__last_name")
    inlines = [ContactCardPhoneTabularInlineAdmin, ContactCardEmailTabularInlineAdmin]


try:
    admin.site.unregister(User)
except NotRegistered:
    pass

try:
    admin.site.unregister(Group)
except NotRegistered:
    pass

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(RaterRole, RaterRoleAdmin)
admin.site.register(RecentlyViewed, RecentlyViewedAdmin)
admin.site.unregister(FlatPage)
admin.site.register(AxisFlatPage, AxisFlatPageAdmin)
admin.site.register(ContactCard, ContactCardAdmin)
