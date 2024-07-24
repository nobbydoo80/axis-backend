"""mixins.py - Axis"""

__author__ = "Steven K"
__date__ = "2/8/22 09:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.company.strings import COMPANY_TYPES
from axis.relationship.models import Relationship

log = logging.getLogger(__name__)


class CompaniesAndUsersTestMixin:
    include_company_types = dict(COMPANY_TYPES).keys()
    include_superuser = True
    include_unrelated_companies = True
    include_noperms_user = True

    @classmethod
    def build_company_relationships(cls, city, include_types=None, **kwargs):
        from axis.core.tests import pop_kwargs

        from axis.company.models import Company
        from axis.core.tests.factories import (
            rater_user_factory,
            rater_admin_factory,
            provider_user_factory,
            provider_admin_factory,
            eep_user_factory,
            eep_admin_factory,
            builder_user_factory,
            builder_admin_factory,
            utility_user_factory,
            utility_admin_factory,
            hvac_user_factory,
            hvac_admin_factory,
            qa_user_factory,
            qa_admin_factory,
            general_user_factory,
            general_admin_factory,
            general_super_user_factory,
            developer_admin_factory,
            developer_user_factory,
            architect_user_factory,
            architect_admin_factory,
            communityowner_admin_factory,
            communityowner_user_factory,
        )

        factories_map = {
            Company.BUILDER_COMPANY_TYPE: {
                "user_factory": builder_user_factory,
                "admin_factory": builder_admin_factory,
            },
            Company.PROVIDER_COMPANY_TYPE: {
                "user_factory": provider_user_factory,
                "admin_factory": provider_admin_factory,
            },
            Company.RATER_COMPANY_TYPE: {
                "user_factory": rater_user_factory,
                "admin_factory": rater_admin_factory,
            },
            Company.EEP_COMPANY_TYPE: {
                "user_factory": eep_user_factory,
                "admin_factory": eep_admin_factory,
            },
            Company.QA_COMPANY_TYPE: {
                "user_factory": qa_user_factory,
                "admin_factory": qa_admin_factory,
            },
            Company.DEVELOPER_COMPANY_TYPE: {
                "user_factory": developer_admin_factory,
                "admin_factory": developer_user_factory,
            },
            Company.ARCHITECT_COMPANY_TYPE: {
                "user_factory": architect_user_factory,
                "admin_factory": architect_admin_factory,
            },
            Company.GENERAL_COMPANY_TYPE: {
                "user_factory": general_user_factory,
                "admin_factory": general_admin_factory,
            },
            Company.COMMUNITY_OWNER_COMPANY_TYPE: {
                "user_factory": communityowner_user_factory,
                "admin_factory": communityowner_admin_factory,
            },
            Company.HVAC_COMPANY_TYPE: {
                "user_factory": hvac_user_factory,
                "admin_factory": hvac_admin_factory,
            },
            Company.UTILITY_COMPANY_TYPE: {
                "user_factory": utility_user_factory,
                "admin_factory": utility_admin_factory,
            },
        }

        include = include_types if include_types else cls.include_company_types

        users, companies = [], []
        data = {}

        for company_type in include:
            user_factory = factories_map[company_type]["user_factory"]
            admin_factory = factories_map[company_type]["admin_factory"]
            _kw = pop_kwargs(f"{company_type}__", kwargs)
            user = user_factory(username=f"{company_type}user", company__city=city, **_kw)
            users.append(user)
            _kw = {k: v for k, v in _kw.items() if not k.startswith("company__")}
            admin = admin_factory(username=f"{company_type}admin", company=user.company, **_kw)
            users.append(admin)
            if company_type == "general" and cls.include_superuser:
                admin = general_super_user_factory(username="admin", company=user.company, **_kw)
                users.append(admin)
            companies.append(admin.company)
            data[company_type] = admin.company

            active_only = None
            if cls.include_unrelated_companies:
                active_only = user_factory(
                    username=f"unrelated_{company_type}_user",
                    company__name=f"unrelated_{company_type}",
                    company__city=city,
                    company__is_customer=False,
                )
                active_only.is_company_admin = False
                active_only.save()

            if (
                active_only
                and cls.include_noperms_user
                and company_type == Company.GENERAL_COMPANY_TYPE
            ):
                active_only.username = "noperm_user"
                active_only.is_company_admin = False
                active_only.is_active = False
                active_only.save()
                active_only.company.is_active = False
                active_only.company.save()
                assert not len(
                    active_only.get_all_permissions()
                ), "In-Active Customers shouldn't have perms"

        Relationship.objects.create_mutual_relationships(*companies)
        return data

    @classmethod
    def setUpTestData(cls):
        from axis.geographic.tests.factories import real_city_factory
        from axis.geographic.models import City

        cls.city = City.objects.first()
        if cls.city is None:
            cls.city = real_city_factory(name="Gilbert", state="AZ")

        cls.build_company_relationships(city=cls.city)
