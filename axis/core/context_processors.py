"""context_processors.py: Django core"""

__author__ = "Steven Klass"
__date__ = "11/3/11 1:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


import logging

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.shortcuts import get_current_site
from django.urls import resolve, Resolver404, NoReverseMatch, reverse_lazy, reverse
from django.utils.functional import SimpleLazyObject

from axis.certification.models import Workflow
from axis.company.strings import COMPANY_TYPES_PLURAL
from .git_utils import get_stored_version_info
from .menu_data import MENU_ITEMS


log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")
customer_neea_app = apps.get_app_config("customer_neea")


def server_configuration(request):
    """Return the current server configuration"""

    data = {
        "protocol": "http",
        "site_root": None,
        "server_type": None,
        "docker_enabled": False,
        "neea_enabled": False,
        "home_innovation_enabled": False,
    }

    if not request:
        return data

    site = SimpleLazyObject(lambda: get_current_site(request))
    data["protocol"] = "https" if request.is_secure() else "http"
    data["site_root"] = SimpleLazyObject(lambda: "{0}://{1}".format(data["protocol"], site.domain))

    if "neea." in site.domain or "neea." in request.get_host():
        data["neea_enabled"] = True

    if "homeinnovation." in site.domain or "homeinnovation." in request.get_host():
        data["home_innovation_enabled"] = True

    try:
        data["docker_enabled"] = settings.DOCKER_ENABLED
    except AttributeError:
        pass

    return data


def current_build_number(request):
    """Simply get me the build number"""
    if not request.user.is_authenticated or request.user.company_id is None:
        return {"git_ref": None}

    version_info = get_stored_version_info("base", full=True)
    return {"git_{}".format(k): v for k, v in version_info._asdict().items()}


def map_api_keys(request):
    """Google Map IP KEY"""
    return {"GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY}


class MenuObj(object):
    """Our Menu Object"""

    def __init__(self, **kwgs):
        self.active = kwgs.pop("active", False)
        self.has_perms = kwgs.pop("has_perms", False)
        self.children = kwgs.pop("children", [])
        self.attrs = kwgs.pop("url_attrs", {})
        self.add_divider = kwgs.pop("add_divider", False)
        self.add_header = kwgs.pop("add_header", None)
        for k, v in kwgs.items():
            setattr(self, k, v)

    def __repr__(self):
        path = getattr(self, "path", "-")
        title = getattr(self, "title", "-")
        try:
            value = str(
                "{}: dict('title': '{}', path: '{}', active: {}, has_perms: {}, "
                "children: '{}', attrs: '{}')"
            )
            return value.format(
                self.__class__.__name__,
                title,
                path,
                self.active,
                self.has_perms,
                self.children,
                self.attrs,
            )
        except UnicodeEncodeError:
            value = str(
                "{}: dict('title': '{}', path: '{}', active: {}, has_perms: {}, "
                "children: '{}', attrs: '{}')"
            )
            return value.format(
                self.__class__.__name__,
                title,
                path,
                self.active,
                self.has_perms,
                "[.. unicode ..]",
                self.attrs,
            )

    def url_attrs(self):  # pylint: disable=inconsistent-return-statements
        """Map for URL attrs"""
        data = ""
        for k, v in self.attrs.items():
            data += "{}={}".format(k, v)
        if data:
            return data

    def get_url(self):
        """
        Check that a path is valid or can be made valid.
        # FIXME: make a better docstring, what makes something invalid.
        :return string
        """
        try:
            resolve(self.path)
        except AttributeError:
            return "#"
        except TypeError:
            return self.path if self.path else "#"
        except Resolver404:
            try:
                return str(reverse_lazy(self.path))
            except NoReverseMatch:
                return self.path
        else:
            return self.path

    def as_dict(self):
        return {
            "title": self.title,
            "url": self.get_url(),
            "active": self.active,
            "has_perms": bool(self.has_perms),
            "children": [item.as_dict() for item in self.children],
            "attrs": self.attrs,
            "add_divider": self.add_divider,
            "add_header": self.add_header,
            "add_indent": self.add_indent,
        }


class BaseMenuContextProcessor(object):
    """Context processor for the menu."""

    def __init__(self, *args, **kwgs):
        self._request = kwgs.get("request", dict())
        default_path = self._request.path if hasattr(self._request, "path") else "/"
        default_domain = self._request.domain if hasattr(self._request, "domain") else None
        default_user = self._request.user if hasattr(self._request, "user") else AnonymousUser()

        self._path = kwgs.get("path", default_path)
        self._domain = kwgs.get("domain", default_domain)
        self._user = kwgs.get("user", default_user)
        self._authenticated = kwgs.get("authenticated", self._user.is_authenticated)
        if (
            self._authenticated
            and self._user.company
            and self._user.company.company_type == "utility"
        ):
            self._has_neea_affiliation = self._user.company.sponsors.filter(slug="neea").exists()
        else:
            self._has_neea_affiliation = False

        for k, v in kwgs.items():
            if not hasattr(self, k):
                setattr(self, k, v)

        self.menu = MENU_ITEMS(user=self._user, path=self._path, **kwgs)

    def get_menu_item(self, item, header=None, divider=False, indent=False, **kwgs):
        """A single menu item"""
        if item not in self.menu:
            return None
        _menu = self.menu[item].copy()
        if header:
            _menu["add_header"] = header
        if divider:
            _menu["add_divider"] = True
        if indent:
            _menu["add_indent"] = True
        for k, v in kwgs.items():
            _menu[k] = v
        return _menu

    def _build_menu_element(self, *args, **kwgs):  # pylint: disable=inconsistent-return-statements
        """The element level switch"""
        conditions = kwgs.get("conditions", True) or self._user.is_superuser
        if conditions or kwgs.get("show_perms"):
            kwgs.pop("show_perms", "children")
            kwgs["has_perms"] = kwgs.pop("conditions", True)
            kwgs["add_indent"] = kwgs.pop("add_indent", False)
            element = MenuObj(**kwgs)
            try:
                element.active = element.get_url().split("?")[0] == self._path.split("?")[0]
            except (NoReverseMatch, AttributeError):
                element.active = False
            return element

    def _build_structure(self, menu_elements, *args, **kwgs):
        """Builds the basic structure updating any args"""
        result = []
        for element in menu_elements:
            if element is None:
                log.warning("Invalid Element - None?")
                continue
            children = element.pop("children", [])
            element.update(kwgs)
            if children:
                kkwgs = kwgs.copy()
                if element.get("conditions") is False:
                    kkwgs["conditions"] = False
                children = self._build_structure(menu_elements=children, *args, **kkwgs)
            item = self._build_menu_element(**element)
            if item:
                if children:
                    item.children = children
                    if item.active is False and True in [child.active for child in children]:
                        item.active = True
                result.append(item)
        return result

    def _print_item(self, *arg, **kwgs):
        kwgs["padding"] = kwgs.get("depth", 0) * " " + "↳"
        kwgs["visible"] = ""
        if kwgs.get("show_perms", False):
            kwgs["visible"] = " Display: {vis}".format(vis=kwgs.get("has_perms", True))
        kwgs["active"] = "*" if kwgs.get("active") else ""
        kwgs["path"] = " ({path})".format(path=kwgs.get("url")) if kwgs.get("url") else ""
        kwgs["indent"] = "  " if kwgs.get("indent") else ""
        if kwgs["divider"]:
            print("{padding}".format(**kwgs) + " -" * 20)
        if kwgs["header"]:
            print("{padding}".format(**kwgs) + " ** " + kwgs["header"] + " **")
        print("{padding} {indent}{active}{title}{path}{visible}".format(**kwgs))
        for child in kwgs.get("children", []):
            url = child.get_url()
            child = child.__dict__.copy()
            child["depth"] = kwgs.get("depth", 0) + 2
            child["show_perms"] = kwgs.get("show_perms", False)
            child["url"] = url
            self._print_item(**child)

    def print_menu(self, show_perms=False, **kwgs):
        """Print this out."""
        _menu = self.build_menu(show_perms=show_perms, **kwgs)
        for item in _menu:
            url = item.get_url()
            item = item.__dict__.copy()
            item["show_perms"] = show_perms
            item["url"] = url
            self._print_item(**item)

    def build_unauthenticated_menu(self, *args, **kwgs):
        """Return the unauthenticated menu"""
        return self._build_structure(
            menu_elements=[
                self.menu.get("index"),
                self.menu.get("products"),
                self.menu.get("pricing"),
                self.menu.get("news"),
                self.menu.get("about"),
                self.menu.get("contact"),
            ],
            *args,
            **kwgs,
        )

    def get_menu(self, *args, **kwgs):
        """Return the menu"""
        if not self._authenticated:
            return self.build_unauthenticated_menu(*args, **kwgs)
        return self.build_menu(*args, **kwgs)

    def build_menu(self, *args, **kwgs):
        """Builde the menu"""
        raise NotImplementedError("You need to build this menu..")


class BootstrapMenuContextProcessor(BaseMenuContextProcessor):
    """Bootstrap version"""

    def _get_companies_menu(self):
        """The general companies menu."""
        children = []

        if not self._has_neea_affiliation:
            for x in COMPANY_TYPES_PLURAL.keys():
                children.append(self.get_menu_item("{}_list".format(x)))

        use_divider = True
        if self._has_neea_affiliation:
            use_divider = False

        children.append(self.get_menu_item("my_profile", divider=use_divider))
        children.append(self.get_menu_item("my_company"))
        return {"title": "Companies", "children": children}

    def _get_places_menu(self):
        children = [
            self.get_menu_item("community_list"),
            self.get_menu_item("subdivision_list"),
            self.get_menu_item("home_list"),
            self.get_menu_item("floorplan_list"),
        ]

        # pylint: disable=deprecated-lambda
        vanilla_children = filter(lambda item: item.get("conditions"), children)
        workflows = Workflow.objects.filter_by_user(self._user)
        num_workflows = workflows.count() + (1 if vanilla_children else 0)  # Treat Home as workflow
        for workflow in workflows:
            children.extend(
                self._get_workflow_types(
                    workflow,
                    num_workflows,
                    **{"add_mode": False, "url_mode": "list", "use_plural": True},
                )
            )

        if self.company_slug == "aps" or self._user.is_superuser:
            children.append(
                self.get_menu_item("aps_legacy_builder_list", header="APS Legacy", divider=True)
            )
            children.append(self.get_menu_item("aps_legacy_subdivision_list"))
            children.append(self.get_menu_item("aps_legacy_home_list"))
        if "neea" in self.sponsor_slugs or self._user.is_superuser:
            children.append(
                self.get_menu_item("neea_legacy_partners_list", header="NEEA Legacy", divider=True)
            )
            children.append(self.get_menu_item("neea_legacy_home_list"))
        if self._user.is_superuser:
            children.append(self.get_menu_item("cities", header="Geographic", divider=True))
        return {"title": "Places", "children": children}

    def _get_workflow_types(self, workflow, num_workflows, add_mode, url_mode, use_plural):
        def _get_default_url(object_type):
            return reverse(
                "certification:object:{url_type}".format(url_type=url_mode),
                kwargs={"type": object_type},
            )

        name_key = "name_plural" if use_plural else "name"

        title_prefix = ""
        if add_mode:
            title_prefix = "Add "

        config = workflow.get_config()
        items = [
            {
                "title": title_prefix + type_spec[name_key],
                "path": config.get_object_url(
                    object_type=typename, url_type=url_mode, default=_get_default_url(typename)
                ),
            }
            for typename, type_spec in config.get_object_type_specs().items()
        ]

        if num_workflows > 1:
            header = config.get_name()
            for i, item in enumerate(items):
                if i == 0:
                    item["add_divider"] = True
                    item["add_header"] = header

        return items

    def _get_indented_menu(self, header, divider=True, *items):
        data = []
        for item in items:
            if self.menu.get(item):
                pick = self.get_menu_item(item, indent=True)
                if not data:
                    pick = self.get_menu_item(item, header=header, divider=divider, indent=True)
                data.append(pick)
        return data

    def _get_tasks_menu(self):
        children = []

        if not self._has_neea_affiliation:
            children.extend(
                self._get_indented_menu(
                    "Add",
                    False,
                    *(
                        "home_add",
                        "floorplan_add",
                        "subdivision_add",
                        "community_add",
                    ),
                )
            )

            children += [self.get_menu_item("eto_wcc_project_tracker", header="ETO", divider=True)]

            # pylint: disable=deprecated-lambda
            vanilla_children = filter(lambda item: item.get("conditions"), children)
            workflows = Workflow.objects.filter_by_user(self._user)
            num_workflows = workflows.count() + (1 if vanilla_children else 0)
            for workflow in workflows:
                children.extend(
                    self._get_workflow_types(
                        workflow,
                        num_workflows,
                        **{"add_mode": True, "url_mode": "add", "use_plural": False},
                    )
                )

        children += list(
            filter(
                bool,
                [
                    self.get_menu_item("provider_dashboard"),
                    self.get_menu_item("single_home_upload")
                    if not self._has_neea_affiliation
                    else None,
                    self.get_menu_item("bulk_completed_checklist_upload"),
                    self.get_menu_item("eto_washington_code_credit_upload"),
                    self.get_menu_item("eep_program_list"),
                    self.get_menu_item("hirl_builder_enrollment"),
                    self.get_menu_item("hirl_builder_agreement_list"),
                    self.get_menu_item("hirl_verifier_agreement_enrollment"),
                    self.get_menu_item("builder_agreement_list"),
                    self.get_menu_item("hirl_verifier_agreement_list"),
                    self.get_menu_item("hirl_project_control_center"),
                    self.get_menu_item("hirl_project_registration_control_center"),
                    self.get_menu_item("hirl_project_invoice_item_groups"),
                    self.get_menu_item("hirl_project_invoices"),
                    self.get_menu_item("hirl_qa_dashboard"),
                    self.get_menu_item("hirl_scoring_upload"),
                    self.get_menu_item("ipp_control_center"),
                    self.get_menu_item("incentive_payments_status"),
                    self.get_menu_item("aps_meterset_import"),
                    self.get_menu_item("hirl_rpc_updater_request_list"),
                    # self.get_menu_item('sampling_list'),
                    self.get_menu_item("sampling_control")
                    if not self._has_neea_affiliation
                    else None,
                    self.get_menu_item("accreditation_approvals"),
                    self.get_menu_item("equipment_approvals"),
                    self.get_menu_item("training_approvals"),
                    self.get_menu_item("inspection_grade_approvals"),
                    self.get_menu_item("certification_metric_approvals"),
                    self.get_menu_item("scheduling_tasks"),
                    self.get_menu_item("message_list"),
                    self.get_menu_item("associations_dashboard"),
                    self.get_menu_item("hirl_jamis_dashboard"),
                    self.get_menu_item("user_add"),
                    self.get_menu_item("hirl_copy_move_ca_coi"),
                    self.get_menu_item("sponsor_preferences_create"),
                ],
            )
        )
        return {"title": "Tasks", "children": children}

    def _get_reports_menu(self):
        children = list(
            filter(
                bool,
                [
                    self.get_menu_item("home_status_report"),
                    self.get_menu_item("builder_signed_report"),
                    self.get_menu_item("processed_documents_list"),
                    self.get_menu_item("remrate_list") if not self._has_neea_affiliation else None,
                    self.get_menu_item("ekotrope_list") if not self._has_neea_affiliation else None,
                    self.get_menu_item("ipp_checks_list"),
                    self.get_menu_item("ipp_pending_failure_report"),
                    self.get_menu_item("neea_utility_report"),
                    self.get_menu_item("custom_data_export"),
                    self.get_menu_item("hirl_bulk_certificate_download"),
                ],
            )
        )
        children += self._get_indented_menu(
            "Printing",
            True,
            *list(
                filter(
                    bool,
                    [
                        "estar_labels",
                        "eto_eps_report",
                        "home_certs",
                        "energy_costs" if not self._has_neea_affiliation else None,
                    ],
                )
            ),
        )

        if self.company_slug == "neea" or self._user.is_superuser:
            children.append(self.get_menu_item("builder_contact_report", divider=True))
            children.append(self.get_menu_item("provider_contact_report"))
            children.append(self.get_menu_item("rater_contact_report"))
            children.append(self.get_menu_item("utility_contact_report"))
            children.append(self.get_menu_item("qa_contact_report"))
            children.append(self.get_menu_item("hvac_contact_report"))

        if not self._has_neea_affiliation:
            search_title = "Search Database"
        else:
            search_title = "Advanced Search"
        children.append(self.get_menu_item("search", title=search_title, divider=True))
        return {"title": "Reports", "children": children}

    def _get_support_menu(self):
        children = [
            self.get_menu_item("support"),
            self.get_menu_item("admin"),
            self.get_menu_item("impersonate"),
            self.get_menu_item("system_messenger"),
            self.get_menu_item("rabbitmq"),
            self.get_menu_item("splunk"),
            self.get_menu_item("status"),
            self.get_menu_item("analytics"),
            self.get_menu_item("webmaster_tools"),
            self.get_menu_item("ec2", header="Amazon Console", divider=True, indent=True),
            self.get_menu_item("rds", indent=True),
            self.get_menu_item("elasticache", indent=True),
            self.get_menu_item("route_53", indent=True),
            self.get_menu_item("cloud_watch", indent=True),
            self.get_menu_item("production_load", header="CPU Loading", divider=True, indent=True),
            self.get_menu_item("beta_load", indent=True),
            self.get_menu_item("demo_load", indent=True),
            self.get_menu_item("staging_load", indent=True),
        ]
        if self._user.is_superuser:
            children.append(self.get_menu_item("logout", divider=True))
        return {"title": "Support", "children": children}

    def build_menu(self, *args, **kwgs):
        """Build the menu"""
        _menu = list(
            filter(
                bool,
                [
                    self._get_companies_menu(),
                    self._get_places_menu() if not self._has_neea_affiliation else None,
                    self._get_tasks_menu(),
                    self._get_reports_menu(),
                ],
            )
        )

        # resources menu
        resource_menu_sponsors = [customer_neea_app.CUSTOMER_SLUG, customer_hirl_app.CUSTOMER_SLUG]
        if (
            any(slug in resource_menu_sponsors for slug in self.sponsor_slugs)
            or self.company_slug in resource_menu_sponsors
        ):
            children = []

            if (
                customer_neea_app.CUSTOMER_SLUG in self.sponsor_slugs
                or self.company_slug == customer_neea_app.CUSTOMER_SLUG
            ):
                children += [
                    self.get_menu_item("neea_model_requirements_15p7p1"),
                    self.get_menu_item("neea_remrate_library_15p7p1"),
                    self.get_menu_item("neea_modeling_flowchart"),
                    self.get_menu_item("neea_betterbuiltNW_website"),
                    self.get_menu_item("neea_water_heater_list"),
                    self.get_menu_item("neea_clothes_dryer"),
                    self.get_menu_item("neea_calculator_v2"),
                    self.get_menu_item("neea_calculator_v3", divider=True),
                ]
            if (
                customer_hirl_app.CUSTOMER_SLUG in self.sponsor_slugs
                or self.company_slug == customer_hirl_app.CUSTOMER_SLUG
            ):
                children += [
                    self.get_menu_item("hirl_verifier_central"),
                    self.get_menu_item("hirl_builder_central"),
                    self.get_menu_item("ngbs_scoring_tools"),
                    self.get_menu_item("ngbs_marketing_materials"),
                    self.get_menu_item("ngbs_green_site"),
                    self.get_menu_item("ngbs_training_site"),
                    self.get_menu_item("ngbs_metrics"),
                ]

            _menu.append({"title": "Resources", "children": children})

        _menu.append(self._get_support_menu())
        return self._build_structure(menu_elements=_menu, *args, **kwgs)


def menu(request):
    """Get the menu"""
    if not request or request.headers.get("x-requested-with") == "XMLHttpRequest":
        return {"menu": []}

    cached_company = request.company
    cached_perms = request.user_permissions

    try:
        sponsor_slugs = [x.get("slug") for x in cached_company.sponsor_info]
    except AttributeError:
        from axis.company.middleware import assign_cached_attributes

        cached_company = assign_cached_attributes(request.user.company, force=True)
        sponsor_slugs = [x.get("slug") for x in cached_company.sponsor_info]

    kwargs = {
        "company_id": cached_company.id,
        "company_slug": cached_company.slug,
        "company_name": cached_company.name,
        "company_type": cached_company.company_type,
        "company_is_eep_sponsor": cached_company.is_eep_sponsor,
        "sponsor_slugs": sponsor_slugs,
        "permissions": cached_perms,
    }

    _menu = BootstrapMenuContextProcessor(request=request, **kwargs)
    return {"menu": _menu.get_menu()}
