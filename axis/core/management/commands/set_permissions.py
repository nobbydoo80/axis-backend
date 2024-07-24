"""set_permissions.py: Django core"""

import importlib
import inspect
import logging
import re
import sys

from django.apps import apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import QuerySet

__author__ = "Steven Klass"
__date__ = "4/5/16 10:12"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from axis.core.utils import get_user_perm_cache_key

log = logging.getLogger(__name__)


class AppPermission:
    """This will allow you to specify perms at the application level.
    The way Axis is architected to support
    permissions is as follows.

    There are two permission levels (admin/general), which apply to any company.
    Permissions are broadly applied
    to whether a company is sponsored, the type of company (company.company_type),
    and whether they are a customer.
    The general guidelines apply

    - In general admins are allowed to add, edit, delete objects.
    - Non-Admins are simply given view permissions.

    When assigning the appropriate level of permissions for a company, a file located in
    an application directory
    named permissions.py is referenced.  This file should contain at least one subclassed
    AppPermission class.
    That file needs to specify the app model(s) to which it applies.  That is all that is needed.
    Doing this
    will allow admins add, change and delete capability and non-admins view capability.
    However, if you want to
    fine tune the permissions the following class methods are used in a first found applies manner.

    get_<company.slug>_permissions * Only applicable for company with slug
    get_customer_<company_type>_permissions * Only applicable for company type that is customer
    get_customer_permissions * Only applicable if company is customer

    get_sponsored_<sponsor.slug>_<company.company_type>_permissions * Only applicable if
    company type is sponsored

    get_sponsored_<sponsor.slug>_permissions * Only applicable if company
    is sponsored by ONE company

    get_sponsored_multiple_sponsors_permissions * Only applicable for
    companies with multiple sponsors

    get_sponsored_<company.company_type>_permissions * Only applicable for companies
    with company type that have a sponsor

    get_sponsored_permissions * Only applicable for companies that have a sponsor.
    By default it is OR between all sponsored_ permissions

    get_<company.company_type>_permissions * Only applicable for company type

    Each one of these methods will return a two tuple list corresponding to the (admin, non-admin)
    permissions associated with the method.
    """

    label = "{app_label}.{ability}_{model_name}"
    default_abilities = ["view"]
    default_admin_abilities = ["view", "add", "change", "delete"]

    @property
    def models(self):
        # log.warning(f'models attribute for class {self.__class__} '
        #             f'is not defined. get_models method is deprecated')
        return self.get_models()

    def _translate_abilities_to_permissions(self, abilities):
        """
        Convert list of short strings to Django Model Permissions object
        :param abilities:
        :return:
        """
        result = []
        for model in self.models:
            model_ct = ContentType.objects.get_for_model(model, for_concrete_model=False)
            permission_labels = []
            for ability in set(abilities):
                permission_label = self.label.format(
                    app_label=model_ct.app_label,
                    ability=ability,
                    model_name=model_ct.model,
                )
                permission_labels.append(permission_label.split(".")[-1])
            permissions = Permission.objects.filter(
                codename__in=permission_labels, content_type=model_ct
            )
            if len(permission_labels) != len(permissions):
                diff = list(set(permission_labels) - set(permissions.values_list("codename")))
                raise ValueError(f"Permission label not found {diff}")
            result += list(permissions)

        return result

    def _get_company_permissions(self, company):
        if not company.is_active or company.users.count() == 0:
            return [], []

        formatted_slug = re.sub(r"-", "_", company.slug)
        sponsor_slugs = company.sponsors.values_list("slug", flat=True)
        formatted_sponsor_slugs = [re.sub(r"-", "_", slug) for slug in sponsor_slugs]

        # add all sponsor methods to list to create an OR condition between their abilities
        possible_get_sponsored_method_names = [
            f"get_sponsored_{formatted_sponsor_slug}_{company.company_type}_permissions"
            for formatted_sponsor_slug in formatted_sponsor_slugs
        ]

        possible_get_sponsored_method_names += [
            f"get_sponsored_{formatted_sponsor_slug}_permissions"
            for formatted_sponsor_slug in formatted_sponsor_slugs
        ]

        methods = [
            {
                "name": f"get_{formatted_slug}_permissions",
            },
            {
                "name": f"get_customer_{company.company_type}_permissions",
                "condition": company.is_customer,  # apply only if company is customer
            },
            {
                "name": "get_customer_permissions",
                "condition": company.is_customer,  # apply only if company is customer
            },
            {
                "name": possible_get_sponsored_method_names,
                # apply only if company has only ONE sponsor
                "condition": len(formatted_sponsor_slugs) == 1,
            },
            {
                "name": "get_multiple_sponsored_permissions",
                # apply only if company has multiple sponsors
                "condition": len(formatted_sponsor_slugs) > 1,
            },
            {
                "name": f"get_sponsored_{company.company_type}_permissions",
                "condition": len(formatted_sponsor_slugs) > 0,  # apply only if company has sponsors
            },
            {
                "name": "get_sponsored_permissions",
                "condition": len(formatted_sponsor_slugs) > 0,  # apply only if company has sponsors
            },
            {"name": f"get_{company.company_type}_permissions"},
        ]

        # set apply all sponsored methods as default for
        # get_multiple_sponsored_permissions
        if "get_multiple_sponsored_permissions" not in dir(self):
            setattr(
                self,
                "get_multiple_sponsored_permissions",
                lambda: self._get_multiple_sponsored_permissions(
                    list_of_methods=possible_get_sponsored_method_names,
                    rest_of_methods=methods[5:],
                ),
            )

        try:
            admin_perms, default_perms = self._apply_methods(methods=methods)
        except AttributeError:
            admin_perms = self.default_admin_abilities
            default_perms = self.default_abilities

        return self._translate_abilities_to_permissions(
            admin_perms
        ), self._translate_abilities_to_permissions(default_perms)

    def _apply_methods(self, methods):
        """
        :param methods: list of methods to check
        :return: Tuple with (admin, default) abilities with the first method found
        """
        for method in methods:
            if not method.get("condition", True):
                continue

            if type(method["name"]) == str:
                try:
                    return self._apply_str_method(method_name=method["name"])
                except AttributeError:
                    pass
            elif type(method["name"]) == list:
                try:
                    return self._apply_list_of_str_methods(list_of_methods=method["name"])
                except AttributeError:
                    pass
            else:
                raise NotImplementedError
        raise AttributeError

    def _apply_str_method(self, method_name):
        perms = getattr(self, method_name)()
        if type(perms) is tuple:
            admin_perms, default_perms = perms
        else:
            admin_perms = perms
            default_perms = perms
        return admin_perms, default_perms

    def _apply_list_of_str_methods(self, list_of_methods):
        """
        :param list_of_methods:
        :raise AttributeError when all methods failed
        :return:
        """
        final_admin_perms = []
        final_default_perms = []
        methods_failed = 0
        for method_name in list_of_methods:
            try:
                admin_perms, default_perms = self._apply_str_method(method_name=method_name)
                final_admin_perms += admin_perms
                final_default_perms += default_perms
            except AttributeError:
                methods_failed += 1

        if len(list_of_methods) == methods_failed:
            raise AttributeError

        final_admin_perms = list(set(final_admin_perms))
        final_default_perms = list(set(final_default_perms))
        return final_admin_perms, final_default_perms

    def _get_multiple_sponsored_permissions(self, list_of_methods, rest_of_methods):
        """
        This method sums all SPONSORED_ methods and in case of fail apply rest of methods

        :param list_of_methods: list of sponsored methods
        :param rest_of_methods: list or methods to check in case
        of sponsored_method for some sponsor is not exist
        :raise AttributeError when all SPONSORED methods failed.
        This means that we do not define any sponsored permissions in our class
        :return:
        """
        final_admin_perms = []
        final_default_perms = []
        methods_failed = 0
        for method_name in list_of_methods:
            try:
                admin_perms, default_perms = self._apply_str_method(method_name=method_name)
                final_admin_perms += admin_perms
                final_default_perms += default_perms
            except AttributeError:
                methods_failed += 1
                try:
                    admin_perms, default_perms = self._apply_methods(methods=rest_of_methods)
                except AttributeError:
                    admin_perms = self.default_admin_abilities
                    default_perms = self.default_abilities
                final_admin_perms += admin_perms
                final_default_perms += default_perms

        if len(list_of_methods) == methods_failed:
            raise AttributeError

        final_admin_perms = list(set(final_admin_perms))
        final_default_perms = list(set(final_default_perms))
        return final_admin_perms, final_default_perms


class AxisPermissionsGenerator(object):
    """This will generate setup the permissions for a Axis Apps."""

    def get_app_permision_modules(self, package_name=None):
        """Get all the permissions modules"""
        app_permissions = []
        for app in apps.get_app_configs():
            module = None
            try:
                module = app.module.permissions
            except AttributeError:
                # This should only happen while appConfigs are not used.
                try:
                    module = importlib.import_module("{}.permissions".format(app.name))
                except ImportError:
                    if len(list(app.models)):
                        if app.module.__package__ and app.module.__package__.startswith("axis."):
                            if package_name and app.module.__package__ == package_name:
                                log.error(
                                    "No permissions app for {}".format(app.module.__package__)
                                )
                            elif not package_name:
                                log.warning(
                                    "No permissions app for {}".format(app.module.__package__)
                                )
            if module:
                if package_name and app.label != package_name:
                    continue
                for name in dir(module):
                    item = getattr(module, name)
                    if (
                        inspect.isclass(item)
                        and item is not AppPermission
                        and issubclass(item, AppPermission)
                    ):
                        app_permissions.append(item)
        if package_name and not len(app_permissions):
            raise KeyError("Unable to find any permissions associated with %s" % package_name)
        return app_permissions

    def build_perms(self, companies=None, app_name=None):
        """Build up the list of perms which should be used"""
        from axis.company.models import Company, COMPANY_MODELS

        if isinstance(companies, int):
            company_ids = [companies]
        elif isinstance(companies, COMPANY_MODELS):
            company_ids = [companies.id]
        elif isinstance(companies, (list, tuple)):
            company_ids = [x.id for x in companies]
        elif isinstance(companies, QuerySet):
            company_ids = companies.values_list("id", flat=True)
        else:
            company_ids = Company.objects.filter(is_active=True).values_list("id", flat=True)

        companies = (
            Company.objects.filter(id__in=company_ids) if companies else Company.objects.all()
        )
        perm_modules = self.get_app_permision_modules(app_name)
        if app_name and not len(perm_modules):
            log.error("No permissions found matching app name of {}".format(app_name))
        permissions = {}

        count = companies.count()
        for idx, company in enumerate(companies.all().prefetch_related("sponsors"), start=1):
            if count > 1:
                print("Working on {}/{} - {}".format(idx, count, company))
            permissions[company] = {"admin": [], "default": [], "models": []}
            for perm_module in perm_modules:
                (
                    expected_admin,
                    expected_default,
                ) = perm_module()._get_company_permissions(company)
                permissions[company]["models"] += perm_module().models
                permissions[company]["default"] += expected_default
                permissions[company]["admin"] += expected_admin
        return permissions

    def analyze(self, company, expected, confirm=True, report_only=False, show_retained=True):
        """Analyze what different"""

        default_perms = list(company.group.permissions.all())
        default_perms = [
            x for x in default_perms if x.content_type.model_class() in expected.get("models", [])
        ]
        admin_perms = list(company.get_admin_group().permissions.all())
        admin_perms = [
            x for x in admin_perms if x.content_type.model_class() in expected.get("models", [])
        ]

        data = {}
        data["admin_add"] = sorted(
            list(set(expected["admin"]) - set(admin_perms)),
            key=lambda x: (x.content_type.app_label, x.content_type.model, x.codename),
        )
        data["admin_remove"] = sorted(
            list(set(admin_perms) - set(expected["admin"])),
            key=lambda x: (x.content_type.app_label, x.content_type.model, x.codename),
        )
        data["admin_retained"] = sorted(
            list(set(admin_perms) & set(expected["admin"])),
            key=lambda x: (x.content_type.app_label, x.content_type.model, x.codename),
        )
        data["default_add"] = sorted(
            list(set(expected["default"]) - set(default_perms)),
            key=lambda x: (x.content_type.app_label, x.content_type.model, x.codename),
        )
        data["default_remove"] = sorted(
            list(set(default_perms) - set(expected["default"])),
            key=lambda x: (x.content_type.app_label, x.content_type.model, x.codename),
        )
        data["default_retained"] = sorted(
            list(set(default_perms) & set(expected["default"])),
            key=lambda x: (x.content_type.app_label, x.content_type.model, x.codename),
        )
        data["update_perms"] = False

        active, customer = (
            "✓" if company.is_active else "-",
            "✓" if company.is_customer else "-",
        )
        sponsored = "✓" if company.sponsors.count() else "-"
        no_change_txt = ""
        if (
            not len(data.get("admin_add"))
            and not len(data.get("admin_remove"))
            and not len(data.get("default_add"))
            and not len(data.get("default_remove"))
        ):
            no_change_txt = "No permissions changes required"

        msg = "{} ({}) [{}] Active: {} Customer: {} Sponsored: {} Users: {}.  Admin perms retained: {}".format(
            company,
            company.slug,
            company.id,
            active,
            customer,
            sponsored,
            company.users.count(),
            len(data["admin_retained"]),
        )
        msg += "Adding: {}".format(len(data["admin_add"])) if len(data["admin_add"]) else ""
        msg += (
            " Removing: {}".format(len(data["admin_remove"])) if len(data["admin_remove"]) else ""
        )
        msg += ".  Default perms retained: {}".format(len(data["default_retained"]))
        msg += "Adding: {}".format(len(data["default_add"])) if len(data["default_add"]) else ""
        msg += (
            " Removing: {}".format(len(data["default_remove"]))
            if len(data["default_remove"])
            else ""
        )
        msg += ". {}".format(no_change_txt)
        data["summary"] = msg

        if confirm or report_only:
            print("=" * 10 + data["summary"] + "=" * 10)
            if len(data.get("admin_add")) or len(data.get("admin_remove")):
                print("  - Admin Group Changes")
                for perm in data["admin_add"]:
                    print("    - add perm {}".format(perm))
                for perm in data["admin_remove"]:
                    print("    - remove perm {}".format(perm))

            if show_retained and len(data.get("admin_retained")):
                print("  - Admin Group Retained")
                for perm in data["admin_retained"]:
                    print("    - retained perm {}".format(perm))

            if len(data.get("default_add")) or len(data.get("default_remove")):
                print("\n  - Default Group Changes")
                for perm in data["default_add"]:
                    print("    - add perm {}".format(perm))
                for perm in data["default_remove"]:
                    print("    - remove perm {}".format(perm))

            if show_retained and len(data.get("default_retained")):
                print("  - Default Group Retained")
                for perm in data["default_retained"]:
                    print("    - retained perm {}".format(perm))

            if (
                len(data.get("admin_add"))
                or len(data.get("admin_remove"))
                or len(data.get("default_add"))
                or len(data.get("default_remove"))
            ):
                if confirm:
                    while True:
                        _data = input("Please confirm these changes [y/n]: ")
                        if _data.lower()[0] not in ("y", "n"):
                            print(" Not an appropriate choice.")
                        else:
                            data["update_perms"] = _data.lower()[0] == "y"
                            break

        else:
            msg = "{} will need to have {} {}perms added and {} {}perms removed; retaining {}"
            log.debug(
                msg.format(
                    company,
                    len(data["admin_add"]),
                    "admin ",
                    len(data["admin_remove"]),
                    "admin ",
                    len(data["admin_retained"]),
                )
            )
            log.debug(
                msg.format(
                    company,
                    len(data["default_add"]),
                    "",
                    len(data["default_remove"]),
                    "",
                    len(data["default_retained"]),
                )
            )
            if (
                len(data.get("admin_add"))
                or len(data.get("admin_remove"))
                or len(data.get("default_add"))
                or len(data.get("default_remove"))
            ):
                data["update_perms"] = True

        return data

    def update_groups(
        self,
        companies=None,
        app=None,
        confirm=True,
        report_only=False,
        show_retained=True,
    ):
        base_perms = self.build_perms(companies, app)

        total = len(base_perms.keys())
        for idx, (company, perms) in enumerate(base_perms.items(), start=1):
            updates = self.analyze(company, perms, confirm, report_only, show_retained)

            if report_only:
                continue
            # This is just a good practice.  Remove admins if they aren't a customer.
            if not company.is_customer and not company.sponsors.count():
                for idx, user in enumerate(company.users.filter(is_company_admin=True)):
                    if idx == 0:
                        log.debug(
                            "Removing all %s admins for unsponsored non-customer",
                            company,
                        )
                    user.is_company_admin = False
                    user.save()

            if updates.get("update_perms"):
                default_group = company.group
                if len(updates.get("default_remove")):
                    default_group.permissions.remove(*list(updates.get("default_remove")))
                if len(updates.get("default_add")):
                    default_group.permissions.add(*list(updates.get("default_add")))

                admin_group = company.get_admin_group()
                if len(updates.get("admin_remove")):
                    admin_group.permissions.remove(*list(updates.get("admin_remove")))
                if len(updates.get("admin_add")):
                    admin_group.permissions.add(*list(updates.get("admin_add")))
                log.debug("Updated perms for {}".format(company))
                if total > 1:
                    print("{}/{} Updated perms for {}".format(idx, total, company))
                    if company.users.count():
                        from django.core.cache import cache

                        for user in company.users.all():
                            cache_key = get_user_perm_cache_key(user=user)
                            cache.set(cache_key, None, 5)
                        print("Reset caches on %d users" % company.users.count())
            else:
                log.debug("Skipping perms update for {}".format(company))
                if total > 1:
                    print("{}/{} No perm changes for {}".format(idx, total, company))

        if total == 1 and not report_only:
            return updates["summary"]


class Command(BaseCommand):
    help = "Analyze and update permissions for companies"
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--no-confirm",
            action="store_true",
            dest="no_confirm",
            help="Do not prompt for confirmation",
        ),
        parser.add_argument(
            "-c",
            "--company-id",
            action="store",
            dest="company_id",
            type=int,
            help="Provide the company ID to update",
        ),
        parser.add_argument(
            "-a",
            "--app-name",
            action="store",
            dest="app",
            help="Provide the app to work on to update",
        ),
        parser.add_argument(
            "-r",
            "--report-only",
            action="store_true",
            dest="report_only",
            help="Only show the report",
        ),
        parser.add_argument(
            "-R",
            "--show-retained",
            action="store_true",
            dest="show_retained",
            help="Show retained perms",
        ),

    def set_options(self, **options):
        self.verbosity = int(options.get("verbosity", 0))

        self.report_only = options.get("report_only", False)
        self.show_retained = options.get("show_retained", False)

        self.fix_customers = options.get("fix_customers", False)

        if self.report_only:
            self.confirm = False
        else:
            no_confirm = options.get("no_confirm", False)
            self.confirm = not no_confirm

        self.company_id = options.get("company_id")
        self.app = options.get(
            "app",
        )

        level_map = {
            0: logging.ERROR,
            1: logging.WARNING,
            2: logging.INFO,
            3: logging.DEBUG,
        }

        self.log_level = level_map.get(self.verbosity, 0)

        logging.basicConfig(
            format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            datefmt="%d/%b/%Y %H:%M:%S",
            level=self.log_level,
            stream=sys.stderr,
        )

    def handle(self, *args, **options):
        self.set_options(**options)

        from axis.company.models import Company

        if self.company_id:
            try:
                company = Company.objects.get(id=self.company_id)
            except Company.DoesNotExist:
                print("Company ID {} does not exist".format(self.company_id))
                return

            try:
                company.update_permissions(
                    app=self.app,
                    confirm=self.confirm,
                    show_retained=self.show_retained,
                    report_only=self.report_only,
                )
            except KeyboardInterrupt:
                print("\nYou killed me.")

        else:
            perm_gen = AxisPermissionsGenerator()
            perm_gen.update_groups(
                app=self.app,
                confirm=self.confirm,
                show_retained=self.show_retained,
                report_only=self.report_only,
            )
